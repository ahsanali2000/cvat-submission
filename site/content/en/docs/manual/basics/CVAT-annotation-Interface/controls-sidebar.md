---
title: 'Controls sidebar'
linkTitle: 'Controls sidebar'
weight: 2
description: 'Offers tools for navigating within the image, annotation tools, and additional options to merge, split, and group labels.'
---

## Navigation

**Navigation block** - contains tools for moving and rotating images.
|Icon |Description |
|-- |-- |
|![Cursor icon](/images/image148.jpg)|`Cursor` (`Esc`)- a basic annotation editing tool. |
|![Move icon](/images/image149.jpg)|`Move the image`- a tool for moving around the image without<br/> the possibility of editing.|
|![Rotate icon](/images/image102.jpg)|`Rotate`- two buttons to rotate the current frame<br/> a clockwise (`Ctrl+R`) and anticlockwise (`Ctrl+Shift+R`).<br/> You can enable `Rotate all images` in the settings to rotate all the images in the job|

---

## Zoom

**Zoom block** - contains tools for image zoom.
|Icon |Description |
|-- |-- |
|![Fit image icon](/images/image151.jpg)|`Fit image`- fits image into the workspace size.<br/> Shortcut - double click on an image|
|![Select region icon](/images/image166.jpg)|`Select a region of interest`- zooms in on a selected region.<br/> You can use this tool to quickly zoom in on a specific part of the frame.|

---

## Shapes

**Shapes block** - contains all the tools for creating shapes.
|Icon |Description |Links to section |
|-- |-- |-- |
|![AI Tools icon](/images/image189.jpg)|`AI Tools`|{{< ilink "/docs/manual/advanced/ai-tools" "AI Tools" >}}|
|![OpenCV icon](/images/image201.jpg)|`OpenCV`|{{< ilink "/docs/manual/advanced/ai-tools" "OpenCV" >}}|
|![Rectangle icon](/images/image167.jpg)|`Rectangle`|{{< ilink "/docs/manual/basics/shape-mode-basics" "Shape mode" >}}; {{< ilink "/docs/manual/basics/track-mode-basics" "Track mode" >}};<br/> {{< ilink "/docs/manual/advanced/annotation-with-rectangles" "Drawing by 4 points" >}}|
|![Polygon icon](/images/image168.jpg)|`Polygon`|{{< ilink "/docs/manual/advanced/annotation-with-polygons" "Annotation with polygons" >}}; {{< ilink "/docs/manual/advanced/annotation-with-polygons/track-mode-with-polygons" "Track mode with polygons" >}}|
|![Polyline icon](/images/image169.jpg)|`Polyline`|{{< ilink "/docs/manual/advanced/annotation-with-polylines" "Annotation with polylines" >}}|
|![Points icon](/images/image170.jpg)|`Points`|{{< ilink "/docs/manual/advanced/annotation-with-points" "Annotation with points" >}}|
|![Ellipses icon](/images/image241.jpg)|`Ellipses`|{{< ilink "/docs/manual/advanced/annotation-with-ellipses" "Annotation with ellipses" >}}|
|![Cuboid icon](/images/image176.jpg)|`Cuboid`|{{< ilink "/docs/manual/advanced/annotation-with-cuboids" "Annotation with cuboids" >}}|
|![Brushing tools icon](/images/brushing_tools_icon.png)|`Brushing tools`|{{< ilink "/docs/manual/advanced/annotation-with-brush-tool" "Annotation with brushing" >}}|
|![Tag icon](/images/image171.jpg)|`Tag`|{{< ilink "/docs/manual/advanced/annotation-with-tags" "Annotation with tags" >}}|
|![Open issue icon](/images/image195.jpg)|`Open an issue`|{{< ilink "/docs/manual/advanced/analytics-and-monitoring/manual-qa" "Review" >}} (available only in review mode)|

---

## Edit

**Edit block** - contains tools for editing tracks and shapes.
|Icon |Description |Links to section |
|-- |-- |-- |
|![Merge shapes icon](/images/image172.jpg)|`Merge Shapes`(`M`) - starts/stops the merging shapes mode. |{{< ilink "/docs/manual/basics/track-mode-basics" "Track mode (basics)" >}}|
|![Group shapes icon](/images/image173.jpg)|`Group Shapes` (`G`) - starts/stops the grouping shapes mode.|{{< ilink "/docs/manual/advanced/shape-grouping" "Shape grouping" >}}|
|![Split icon](/images/image174.jpg)|`Split` - splits a track. |{{< ilink "/docs/manual/advanced/track-mode-advanced" "Track mode (advanced)" >}}|
|![Join labels icon](/images/join-masks-icon.jpg)|Joins multiple labels into one |{{< ilink "/docs/manual/advanced/slice-and-join#joining-cvat-labels" "**Joining mask tool**" >}}|
|![Slice label icon](/images/slicing-tool-icon.jpg)|Slices one label into several.|{{< ilink "/docs/manual/advanced/slice-and-join#slicing-cvat-labels" "**Slice mask/polygon**" >}}|

---

## Move image

Switching between user interface modes.

![Part of user interface with open menu for switching interface modes](/images/image145.jpg)

1. Use arrows below to move to the next/previous frame.
   Use the scroll bar slider to scroll through frames.
   Almost every button has a shortcut.
   To get a hint about a shortcut, just move your mouse pointer over an UI element.

1. To navigate the image, use the button on the controls sidebar.
   Another way an image can be moved/shifted is by holding the left mouse button inside
   an area without annotated objects.
   If the `Mouse Wheel` is pressed, then all annotated objects are ignored. Otherwise the
   a highlighted bounding box will be moved instead of the image itself.

   ![Part of user interface with highlighted "Move the image" button](/images/image136.jpg)

1. You can use the button on the sidebar controls to zoom on a region of interest.
   Use the button `Fit the image` to fit the image in the workspace.
   You can also use the mouse wheel to scale the image
   (the image will be zoomed relatively to your current cursor position).

   ![Part of user interface with highlighted buttons for fitting the image and selecting region](/images/image137.jpg)
