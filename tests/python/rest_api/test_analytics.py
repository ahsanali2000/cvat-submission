# Copyright (C) 2022 Intel Corporation
# Copyright (C) CVAT.ai Corporation
#
# SPDX-License-Identifier: MIT

import csv
import json
import uuid
from collections import Counter
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from io import StringIO
from time import sleep
from typing import Optional

import pytest
from cvat_sdk.api_client import ApiClient
from dateutil import parser as datetime_parser

import shared.utils.s3 as s3
from shared.utils.config import delete_method, get_method, make_api_client, server_get
from shared.utils.helpers import generate_image_files

from .utils import create_task, wait_and_download_v2, wait_background_request


class TestGetAnalytics:
    endpoint = "analytics"

    def _test_can_see(self, user):
        response = server_get(user, self.endpoint)

        assert response.status_code == HTTPStatus.OK

    def _test_cannot_see(self, user):
        response = server_get(user, self.endpoint)

        assert response.status_code == HTTPStatus.FORBIDDEN

    @pytest.mark.parametrize(
        "conditions, is_allow",
        [
            (dict(privilege="admin"), True),
            (dict(privilege="worker", has_analytics_access=False), False),
            (dict(privilege="worker", has_analytics_access=True), True),
            (dict(privilege="user", has_analytics_access=False), False),
            (dict(privilege="user", has_analytics_access=True), True),
        ],
    )
    def test_can_see(self, conditions, is_allow, find_users):
        user = find_users(**conditions)[0]["username"]

        if is_allow:
            self._test_can_see(user)
        else:
            self._test_cannot_see(user)


@pytest.mark.usefixtures("restore_db_per_class")
class TestGetAuditEvents:
    _USERNAME = "admin1"

    @staticmethod
    def _create_project(user, spec, **kwargs):
        with make_api_client(user) as api_client:
            (project, response) = api_client.projects_api.create(spec, **kwargs)
            assert response.status == HTTPStatus.CREATED
        return project.id, response.headers.get("X-Request-Id")

    @pytest.fixture(autouse=True)
    def setup(self, restore_clickhouse_db_per_function, restore_redis_inmem_per_function):
        project_spec = {
            "name": f"Test project created by {self._USERNAME}",
            "labels": [
                {
                    "name": "car",
                    "color": "#ff00ff",
                    "attributes": [
                        {
                            "name": "a",
                            "mutable": True,
                            "input_type": "number",
                            "default_value": "5",
                            "values": ["4", "5", "6"],
                        }
                    ],
                }
            ],
        }
        self.project_id, project_request_id = TestGetAuditEvents._create_project(
            self._USERNAME, project_spec
        )
        task_spec = {
            "name": f"test {self._USERNAME} to create a task",
            "segment_size": 2,
            "project_id": self.project_id,
        }
        task_ids = [
            create_task(
                self._USERNAME,
                task_spec,
                {
                    "image_quality": 10,
                    "client_files": generate_image_files(3),
                },
            ),
            create_task(
                self._USERNAME,
                task_spec,
                {
                    "image_quality": 10,
                    "client_files": generate_image_files(3),
                },
            ),
        ]

        self.task_ids = [t[0] for t in task_ids]

        assert project_request_id is not None
        assert all(t[1] is not None for t in task_ids)

        event_filters = [
            (
                (lambda e: json.loads(e["payload"])["request"]["id"], [project_request_id]),
                ("scope", ["create:project"]),
            ),
        ]
        for task_id in task_ids:
            event_filters.extend(
                (
                    (
                        (lambda e: json.loads(e["payload"])["request"]["id"], [task_id[1]]),
                        ("scope", ["create:task"]),
                    ),
                    (("scope", ["create:job"]),),
                )
            )
        self._wait_for_request_ids(event_filters)

    def _wait_for_request_ids(self, event_filters):
        MAX_RETRIES = 5
        SLEEP_INTERVAL = 2
        while MAX_RETRIES > 0:
            data = self._test_get_audit_logs_as_csv()
            events = self._csv_to_dict(data)
            if all(self._filter_events(events, filter) for filter in event_filters):
                break
            MAX_RETRIES -= 1
            sleep(SLEEP_INTERVAL)
        else:
            assert False, "Could not wait for expected request IDs"

    @staticmethod
    def _export_events(
        api_client: ApiClient,
        *,
        api_version: int,
        max_retries: int = 20,
        interval: float = 0.1,
        **kwargs,
    ) -> Optional[bytes]:
        if api_version == 1:
            endpoint = api_client.events_api.list_endpoint
            query_id = ""
            for _ in range(max_retries):
                (_, response) = endpoint.call_with_http_info(
                    **kwargs, query_id=query_id, _parse_response=False
                )
                if response.status == HTTPStatus.CREATED:
                    break
                assert response.status == HTTPStatus.ACCEPTED
                if not query_id:
                    response_json = json.loads(response.data)
                    query_id = response_json["query_id"]
                sleep(interval)

            assert response.status == HTTPStatus.CREATED

            (_, response) = endpoint.call_with_http_info(
                **kwargs, query_id=query_id, action="download", _parse_response=False
            )
            assert response.status == HTTPStatus.OK

            return response.data

        assert api_version == 2

        request_id, response = api_client.events_api.create_export(**kwargs, _check_status=False)
        assert response.status == HTTPStatus.ACCEPTED

        if "location" in kwargs and "cloud_storage_id" in kwargs:
            background_request, response = wait_background_request(
                api_client, rq_id=request_id.rq_id, max_retries=max_retries, interval=interval
            )
            assert background_request.result_url is None
            return None

        return wait_and_download_v2(
            api_client, rq_id=request_id.rq_id, max_retries=max_retries, interval=interval
        )

    @staticmethod
    def _csv_to_dict(csv_data):
        res = []
        with StringIO(csv_data.decode()) as f:
            reader = csv.DictReader(f)
            for row in reader:
                res.append(row)

        return res

    @staticmethod
    def _filter_events(events, filters):
        res = []
        get_value = lambda getter, e: getter(e) if callable(getter) else e.get(getter, None)
        for e in events:
            if all(get_value(getter, e) in expected_values for getter, expected_values in filters):
                res.append(e)

        return res

    def _test_get_audit_logs_as_csv(self, *, api_version: int = 2, **kwargs):
        with make_api_client(self._USERNAME) as api_client:
            return self._export_events(api_client, api_version=api_version, **kwargs)

    @pytest.mark.parametrize("api_version", [1, 2])
    def test_entry_to_time_interval(self, api_version: int):
        now = datetime.now(timezone.utc)
        to_datetime = now
        from_datetime = now - timedelta(minutes=3)

        query_params = {
            "_from": from_datetime.isoformat(),
            "to": to_datetime.isoformat(),
        }

        data = self._test_get_audit_logs_as_csv(api_version=api_version, **query_params)
        events = self._csv_to_dict(data)
        assert len(events)

        for event in events:
            event_timestamp = datetime_parser.isoparse(event["timestamp"])
            assert from_datetime <= event_timestamp <= to_datetime

    @pytest.mark.parametrize("api_version", [1, 2])
    def test_filter_by_project(self, api_version: int):
        query_params = {
            "project_id": self.project_id,
        }

        data = self._test_get_audit_logs_as_csv(api_version=api_version, **query_params)
        events = self._csv_to_dict(data)

        filtered_events = self._filter_events(events, [("project_id", [str(self.project_id)])])
        assert len(filtered_events)
        assert len(events) == len(filtered_events)

        event_count = Counter([e["scope"] for e in filtered_events])
        assert event_count["create:project"] == 1
        assert event_count["create:task"] == 2
        assert event_count["create:job"] == 4

    @pytest.mark.parametrize("api_version", [1, 2])
    def test_filter_by_task(self, api_version: int):
        for task_id in self.task_ids:
            query_params = {
                "task_id": task_id,
            }

            data = self._test_get_audit_logs_as_csv(api_version=api_version, **query_params)
            events = self._csv_to_dict(data)

            filtered_events = self._filter_events(events, [("task_id", [str(task_id)])])
            assert len(filtered_events)
            assert len(events) == len(filtered_events)

            event_count = Counter([e["scope"] for e in filtered_events])
            assert event_count["create:task"] == 1
            assert event_count["create:job"] == 2

    @pytest.mark.parametrize("api_version", [1, 2])
    def test_filter_by_non_existent_project(self, api_version: int):
        query_params = {
            "project_id": self.project_id + 100,
        }

        data = self._test_get_audit_logs_as_csv(api_version=api_version, **query_params)
        events = self._csv_to_dict(data)
        assert len(events) == 0

    @pytest.mark.parametrize("api_version", [1, 2])
    def test_user_and_request_id_not_empty(self, api_version: int):
        query_params = {
            "project_id": self.project_id,
        }
        data = self._test_get_audit_logs_as_csv(api_version=api_version, **query_params)
        events = self._csv_to_dict(data)

        for event in events:
            assert event["user_id"]
            assert event["user_name"]
            assert event["user_email"]

            payload = json.loads(event["payload"])
            request_id = payload["request"]["id"]
            assert request_id
            uuid.UUID(request_id)

    @pytest.mark.parametrize("api_version", [1, 2])
    def test_delete_project(self, api_version: int):
        response = delete_method("admin1", f"projects/{self.project_id}")
        assert response.status_code == HTTPStatus.NO_CONTENT

        event_filters = (
            (
                (
                    lambda e: json.loads(e["payload"])["request"]["id"],
                    [response.headers.get("X-Request-Id")],
                ),
                ("scope", ["delete:project"]),
            ),
            (
                (
                    lambda e: json.loads(e["payload"])["request"]["id"],
                    [response.headers.get("X-Request-Id")],
                ),
                ("scope", ["delete:task"]),
            ),
        )

        self._wait_for_request_ids(event_filters)

        query_params = {
            "project_id": self.project_id,
        }

        data = self._test_get_audit_logs_as_csv(api_version=api_version, **query_params)
        events = self._csv_to_dict(data)

        filtered_events = self._filter_events(events, [("project_id", [str(self.project_id)])])
        assert len(filtered_events)
        assert len(events) == len(filtered_events)

        event_count = Counter([e["scope"] for e in filtered_events])
        assert event_count["delete:project"] == 1
        assert event_count["delete:task"] == 2
        assert event_count["delete:job"] == 4

    @pytest.mark.with_external_services
    @pytest.mark.parametrize("api_version, allowed", [(1, False), (2, True)])
    @pytest.mark.parametrize("cloud_storage_id", [3])  # import/export bucket
    def test_export_to_cloud(
        self, api_version: int, allowed: bool, cloud_storage_id: int, cloud_storages
    ):
        query_params = {
            "api_version": api_version,
            "location": "cloud_storage",
            "cloud_storage_id": cloud_storage_id,
            "filename": "test.csv",
            "task_id": self.task_ids[0],
        }
        if allowed:
            data = self._test_get_audit_logs_as_csv(**query_params)
            assert data is None
            s3_client = s3.make_client(bucket=cloud_storages[cloud_storage_id]["resource"])
            data = s3_client.download_fileobj(query_params["filename"])
            events = self._csv_to_dict(data)
            assert len(events)
        else:
            response = get_method(self._USERNAME, "events", **query_params)
            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert (
                response.json()[0]
                == "This endpoint does not support exporting events to cloud storage"
            )
