Paint_Project
=============

## A photoshop clone written in Python 3.
Includes tools, colour selection, colorkey layers, file loading and saving, program information, and filters.
Runs using the pygame (http://pygame.org) graphics library.

Developed, designed, and maintained by Christopher Gregorian.
All project history and resources can be found at: https://github.com/csgregorian/Paint_Project.
Some images used and modified without permission from Adobe Photoshop CS6.


### Tools
Click on a tool in the toolbar to select it.
Left-click or right-click on the canvas to use.
Scroll to change the tool size.
#### Line
Click and drag to draw a line between two points.
Hold ALT to cycle colours.
#### Rectangle
Click and drag to draw a rectangle.
Hold SHIFT to draw a square.
Hold CTRL to draw an unfilled rectangle.
Hold ALT to cycle colours.
#### Brush
Hold to draw.
Hold ALT to cycle colours.
#### Pencil
Hold to draw 1 pixel wide.
Hold ALT to cycle colours.
#### Eraser
Hold to erase.
#### Eyedropper
Click to choose a colour from the canvas.
#### Fill Bucket
Click to fill a contiguous area.
#### Ellipse
Click and drag to draw an ellipse.
Hold SHIFT to draw a circle from the centre.
Hold CTRL to draw an unfilled ellipse.
Hold ALT to cycle colours.
#### Crop
Click and drag to choose a selection, then click to stamp the selection.
Allows transferring selection between layers.
#### Spray
Hold to colour random pixels within a certain radius.
Hold ALT to cycle colours.
#### Text
Click to choose a starting point.  Type to insert text.
#### Stamp
Click to stamp an image.  Change stamps with the numpad.
#### Gradient
Click to apply a horizontal gradient to fill a contiguous area.
Hold CTRL to apply a vertical gradient.
Hold ALT to apply a radial gradient.

### Filters
Click on a filter to apply it to the current layer.
- Gaussian Blur
- Pixelate
- Sobel (Numpy/Scipy)
- Oversaturate
- Invert
- Vertical Flip
- Grayscale
- Tint
- Noise Generation
- Fill
- Grow
- Shrink

### Layers
Pyshop supports up to 8 layers.
A large amount of layers may reduce stability and speed.
Add a new layer with SPACE and delete the current layer with DELETE.
Move between layers with the UP and DOWN arrow keys.

### Colours
Change left-click and right-click colours by clicking on the palette or hue bar.
Reset colours by pressing D.
Switch colours by pressing X.

### Undo and Redo
Pyshop stores an unlimited number of history states.
Undo and redo with the LEFT and RIGHT arrow keys.
Not available when the text tool is active.

### Saving and Loading
Click on the file button in the tool bar to save your image.
Right-click to load an image.
Images can be BMP, PNG, JPEG, TIFF, etc.
Images cannot be loaded from libraries (Windows 7+).
On some operating systems, the file dialog may only be controllable with the keyboard.

### Information and Properties
The info box provides essential runtime information, such as the current colour in RGB/CMYK representations,
the cursor location, the tool size, and the framerate.


