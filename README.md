# draw - Simple vector drawing application using PyQt5

© 2018 Raphael Wimmer <raphael.wimmer@ur.de>
portions © 2014 Florian Echtler <floe@butterbrot.org>

Released into the public domain / licensed under the Creative Commons Zero license
(feel free to reuse snippets)

Work in (slow) progress

## Features

- supports Wacom pens and pressure sensitivity (if Qt recognizes them)
- automatically saves to SVG file and Pickle file

## Notes

- Point format: (x, y, pressure)
- Shape format: [points]

## TO DO:

- extend shape format with color, line style
- auto-close shapes
- eraser
- auto-shapes (circle, rectangle) using $1 recognizer
- resample / optimize shapes
