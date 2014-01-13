#!/usr/bin/env python
'''
Photoshop CS7
A simple photoshop clone written in Python 3.2.3.
Includes tools, colour selection, colorkey layers, file loading and saving,
program information, and filters.
Runs using the pygame (http://pygame.org) graphics library.

'''

## .......~Imports~....... ##

from tkinter import filedialog as filedialog
from random import randrange
from time import sleep
from math import hypot
import os
# Sets display to open at top right corner
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"

try:
    import numpy
    from scipy import ndimage, signal
    numsci = True
except:
    numsci = False

from pygame import *
init()

from colours import cmyk
from stamps import stamps

## .......~MetaData~....... ##

__author__ = "Christopher Gregorian"
__copyright__ = "Copyright 2013-2014, ICS-3U"
__email__ = "csgregorian@gmail.com"
__status__  = "Development"



## .......~Global Function Definitions~....... ##

def tm():
    """Location of mouse on screen"""
    return mouse.get_pos()

def cm():
    """Location of mouse on canvas"""
    return (mouse.get_pos()[0] - 100, mouse.get_pos()[1] - 100)


## .......~Tool Classes~....... ##
class Tool:
    """Default tool class.
    Every tool must have a canvasDown/Hold/Up method to be called at the appropriate event."""

    def __init__(self, Image, hImage, pImage, loc, size):
        self.images = [image.load(Image), image.load(hImage), image.load(pImage)]
        self.loc = loc
        self.rect = Rect(loc[0], loc[1], size[0], size[1])
    def canvasDown(self):
        pass
    def canvasHold(self):
        pass
    def canvasUp(self):
        pass

class lineTool(Tool):
    """Draws a line from one point to another"""
    def canvasDown(self):
        global toolLoc
        toolLoc = cm()
    def canvasHold(self):
        global layers
        layers[currentLayer] = cover.copy()
        self.m = (cm()[1] - toolLoc[1])/(cm()[0] - toolLoc[0] + (1 if cm()[0] - toolLoc[0] == 0 else 0))
        self.b = cm()[1] - (self.m * cm()[0])
        if abs(cm()[0] - toolLoc[0]) > abs(cm()[1] - toolLoc[1]):
            if cm()[0] < toolLoc[0]:
                for i in range(cm()[0], toolLoc[0]):
                    draw.circle(layers[currentLayer], currentColour, (i, round(self.m*i + self.b)), size)
            else:
                for i in range(toolLoc[0], cm()[0]):
                    draw.circle(layers[currentLayer], currentColour, (i, round(self.m*i + self.b)), size)
        else:
            if cm()[1] < toolLoc[1]:
                for i in range(cm()[1], toolLoc[1]):
                    draw.circle(layers[currentLayer], currentColour, (round((i-self.b)/self.m)
                        if self.m != 0 else round(self.b), i), size)
            else:
                for i in range(toolLoc[1], cm()[1]):
                    draw.circle(layers[currentLayer], currentColour, (round((i-self.b)/self.m)
                        if self.m != 0 else round(self.b), i), size)

class rectTool(Tool):
    """Draws a rectangle from one corner to another"""
    def canvasDown(self):
        global toolLoc
        toolLoc = cm()
    def canvasHold(self):
        global layers
        layers[currentLayer] = cover.copy()

        w = cm()[0] - toolLoc[0]
        h = cm()[1] - toolLoc[1]

        self.filled = 0

        if key.get_pressed()[K_LCTRL] or key.get_pressed()[K_RCTRL]:
            self.filled = 1
        else:
            self.filled = 0

        if key.get_pressed()[K_LSHIFT] or key.get_pressed()[K_RSHIFT]:
            self.size = min(abs(w), abs(h))
            draw.rect(layers[currentLayer], currentColour, (toolLoc[0], toolLoc[1], #  MAGIC
            self.size if w > 1 else -self.size,                                     #  DO NOT
            self.size if h > 1 else -self.size), 0 < self.filled < abs(self.size))  #  TOUCH
        else:
            draw.rect(layers[currentLayer], currentColour, (toolLoc[0], toolLoc[1], w, h), 0 < self.filled < abs(max(w, h)))

class brushTool(Tool):
    """Draws continuous circles at a given size"""
    def canvasDown(self):
        global toolLoc
        toolLoc = cm()
    def canvasHold(self):
        global layers
        global toolLoc
        self.m = (cm()[1] - toolLoc[1])/(cm()[0] - toolLoc[0] + (1 if cm()[0] - toolLoc[0] == 0 else 0))
        self.b = cm()[1] - (self.m * cm()[0])
        if abs(cm()[0] - toolLoc[0]) > abs(cm()[1] - toolLoc[1]):
            if cm()[0] < toolLoc[0]:
                for i in range(cm()[0], toolLoc[0]):
                    draw.circle(layers[currentLayer], currentColour, (i, round(self.m*i + self.b)), size)
            else:
                for i in range(toolLoc[0], cm()[0]):
                    draw.circle(layers[currentLayer], currentColour, (i, round(self.m*i + self.b)), size)
        else:
            if cm()[1] < toolLoc[1]:
                for i in range(cm()[1], toolLoc[1]):
                    draw.circle(layers[currentLayer], currentColour, (round((i-self.b)/self.m) if self.m != 0 else round(self.b), i), size)
            else:
                for i in range(toolLoc[1], cm()[1]):
                    draw.circle(layers[currentLayer], currentColour, (round((i-self.b)/self.m) if self.m != 0 else round(self.b), i), size)
        toolLoc = cm()

class pencilTool(Tool):
    """Draws a 1px wide line following the mouse"""
    def canvasDown(self):
        global toolLoc
        toolLoc = cm()
    def canvasHold(self):
        global layers
        global toolLoc
        draw.line(layers[currentLayer], currentColour, cm(), toolLoc, 1)
        toolLoc = cm()

class eraserTool(Tool):
    """White brush"""
    def canvasDown(self):
        global toolLoc
        toolLoc = cm()
    def canvasHold(self):
        global layers
        global toolLoc
        self.m = (cm()[1] - toolLoc[1])/(cm()[0] - toolLoc[0] + (1 if cm()[0] - toolLoc[0] == 0 else 0))
        self.b = cm()[1] - (self.m * cm()[0])
        if abs(cm()[0] - toolLoc[0]) > abs(cm()[1] - toolLoc[1]):
            if cm()[0] < toolLoc[0]:
                for i in range(cm()[0], toolLoc[0]):
                    draw.circle(layers[currentLayer], white, (i, round(self.m*i + self.b)), size)
            else:
                for i in range(toolLoc[0], cm()[0]):
                    draw.circle(layers[currentLayer], white, (i, round(self.m*i + self.b)), size)
        else:
            if cm()[1] < toolLoc[1]:
                for i in range(cm()[1], toolLoc[1]):
                    draw.circle(layers[currentLayer], white, (round((i-self.b)/self.m) if self.m != 0 else round(self.b), i), size)
            else:
                for i in range(toolLoc[1], cm()[1]):
                    draw.circle(layers[currentLayer], white, (round((i-self.b)/self.m) if self.m != 0 else round(self.b), i), size)
        toolLoc = cm()

class dropperTool(Tool):
    """Picks colour from canvas"""
    def canvasHold(self):
        global colourLoc
        global currentColour
        global layers
        colourLoc = tm()
        currentColour = screen.get_at(colourLoc)
        layers[currentLayer] = cover.copy()

class fillTool(Tool):
    """Fills an area bounded by different colours"""
    def canvasDown(self):
        self.points = set()
        pixarray = PixelArray(layers[currentLayer])
        self.pixel(pixarray[cm()[0]][cm()[1]], cm()[0], cm()[1], pixarray)
    def pixel(self, colour, x, y, pixarray):
        spots = [(x, y)]
        while len(spots) > 0:
            fx, fy = spots.pop()
            if 0 <= fx < 1080 and 0 <= fy < 660:
                if pixarray[fx][fy] == colour:
                    pixarray[fx][fy] = currentColour
                    spots.append((fx+1, fy))
                    spots.append((fx-1, fy))
                    spots.append((fx, fy+1))
                    spots.append((fx, fy-1))
        return pixarray

class circleTool(Tool):
    """Draws a circle from the centre"""
    def canvasDown(self):
        global toolLoc
        toolLoc = cm()
    def canvasHold(self):
        global layers
        layers[currentLayer] = cover.copy()
        self.w = abs(cm()[0] - toolLoc[0])
        self.h = abs(cm()[1] - toolLoc[1])
        self.filled = False
        if key.get_pressed()[K_LCTRL] or key.get_pressed()[K_RCTRL]:
            self.filled = True
        else:
            self.filled = False
        if key.get_pressed()[K_LSHIFT] or key.get_pressed()[K_RSHIFT]:
            draw.circle(layers[currentLayer], currentColour, toolLoc, round(hypot(cm()[0]-toolLoc[0], cm()[1]-toolLoc[1])), 0 < self.filled < round(hypot(cm()[0]-toolLoc[0], cm()[1]-toolLoc[1])))
        else:
            draw.ellipse(layers[currentLayer], currentColour, (min(toolLoc[0], cm()[0]), min(toolLoc[1], cm()[1]), self.w, self.h), 0 < self.filled < min(self.w, self.h))


class cropTool(Tool):
    """Chooses an area and moves it to a different location"""
    chosen = False
    def canvasDown(self):
        global toolLoc
        global layers
        if not self.chosen:
            toolLoc = cm()
        else:
            layers[currentLayer].blit(self.section, cm())

    def canvasHold(self):
        global layers
        if not self.chosen:
            self.section = layers[currentLayer].copy()
            layers[currentLayer] = cover.copy()
            draw.rect(layers[currentLayer], (0, 0, 0), (toolLoc[0], toolLoc[1], cm()[0]-toolLoc[0], cm()[1]-toolLoc[1]), 1)
        else:
            layers[currentLayer] = cover.copy()
            layers[currentLayer].blit(self.section, cm(), (min(toolLoc[0], toolLoc2[0]), min(toolLoc[1], toolLoc2[1]),
                abs(toolLoc2[0]-toolLoc[0]), abs(toolLoc2[1]-toolLoc[1])))

    def canvasUp(self):
        global layers
        global toolLoc2
        if not self.chosen:
            layers[currentLayer] = cover.copy()
            toolLoc2 = cm()
            self.section = layers[currentLayer].copy()
            draw.rect(layers[currentLayer], (255, 0, 255), (min(toolLoc[0], toolLoc2[0]), min(toolLoc[1], toolLoc2[1]),
                abs(toolLoc2[0]-toolLoc[0]), abs(toolLoc2[1]-toolLoc[1])))
        self.chosen = not self.chosen

class sprayTool(Tool):
    """Spray tool in a circle"""
    def canvasHold(self):
        for i in range(round(6.18*size/3)):
            while True:
                x, y = (randrange(cm()[0]-size, cm()[0]+size),
                    randrange(cm()[1]-size, cm()[1]+size))

                if hypot(cm()[0]-x, cm()[1]-y) <= size:
                    layers[currentLayer].set_at((x,y), currentColour)
                    break

class textTool(Tool):
    text = ""
    size = 10
    colour = (255, 0, 0)
    def canvasDown(self):
        global toolLoc
        self.size = size
        self.text = ""
        self.colour = currentColour
        toolLoc = cm()

class stampTool(Tool):
    def canvasHold(self):
        global layers
        layers[currentLayer] = cover.copy()
        layers[currentLayer].blit(transform.scale(stamps[currentStamp].convert_alpha(), (size*4, size*4)), (cm()[0] - size*2, cm()[1]-size*2))



## .......~Filter Functions~....... ##
def gaussianBlur(surf):
    numpyarray = surfarray.array3d(surf)
    result = ndimage.filters.gaussian_filter(numpyarray, (8, 8, 0))
    return surfarray.make_surface(result)

def sobel(surf):
    numpyarray = surfarray.array3d(surf)
    result = ndimage.filters.sobel(numpyarray)
    return surfarray.make_surface(result)

def invert(surf):
    pixelarray = surfarray.pixels2d(surf)
    pixelarray ^= 2**32 - 1



## .......~Global Var Definitions~....... ##

# Creates display and runs intro
screen = display.set_mode((1280, 1024), NOFRAME)
screen.blit(image.load("resources/intro.jpg"), (150, 40))
display.flip()
sleep(1)

# Stores all tool objects
tools = {
        "line"   : lineTool   ("Tools/Line.png",    "Tools/hLine.png",    "Tools/pLine.png",    (3,  52), (32, 24)),
        "rect"   : rectTool   ("Tools/Rect.png",    "Tools/hRect.png",    "Tools/pRect.png",    (3,  80), (32, 24)),
        "brush"  : brushTool  ("Tools/Brush.png",   "Tools/hBrush.png",   "Tools/pBrush.png",   (3, 108), (32, 24)),
        "pencil" : pencilTool ("Tools/Pencil.png",  "Tools/hPencil.png",  "Tools/pPencil.png",  (3, 136), (32, 24)),
        "eraser" : eraserTool ("Tools/Eraser.png",  "Tools/hEraser.png",  "Tools/pEraser.png",  (3, 164), (32, 24)),
        "dropper": dropperTool("Tools/Dropper.png", "Tools/hDropper.png", "Tools/pDropper.png", (3, 192), (32, 24)),
        "fill"   : fillTool   ("Tools/Fill.png",    "Tools/hFill.png",    "Tools/pFill.png",    (3, 220), (32, 24)),
        "circle" : circleTool ("Tools/Ellipse.png", "Tools/hEllipse.png", "Tools/pEllipse.png", (3, 248), (32, 24)),
        "marquee": cropTool   ("Tools/Crop.png",    "Tools/hCrop.png",    "Tools/pCrop.png",    (3, 276), (32, 24)),
        "spray"  : sprayTool  ("Tools/Spray.png",   "Tools/hSpray.png",   "Tools/pSpray.png",   (3, 304), (32, 24)),
        "text"   : textTool   ("Tools/Text.png",    "Tools/hText.png",    "Tools/pText.png",    (3, 332), (32, 24)),
        "stamp"  : stampTool  ("Tools/Stamp.png",   "Tools/hStamp.png",   "Tools/pStamp.png",   (3, 360), (32, 24))
}

# Stores all rects
rects = {
    "canvas" : Rect(100, 100, 1080, 660),
    "palette": Rect(1050, 793, 228, 228),
    "hue": Rect(1006, 793, 43, 228),
    "toolbar" : screen.blit(image.load("resources/pstool.png"), (0, 28)),
    "title" : screen.blit(image.load("resources/pstitle.png"), (0, 0)),
    "undo" : Rect(0, 0, 20, 20),
    "exit" : Rect(1232, 0, 40, 18),
    "save" : screen.blit(image.load("resources/File.png"), (39, 4)),
    "properties" : Rect(79, 818, 71, 16),
    "info" : Rect(40, 818, 39, 16)
}

# Stores all images
images = {
    "pExit" : image.load("resources/pExit.png"),
    "hExit" : image.load("resources/hExit.png"),
    "Exit"  : image.load("resources/Exit.png"),
    "pFile" : image.load("resources/pFile.png"),
    "hFile" : image.load("resources/hFile.png"),
    "File"  : image.load("resources/File.png"),
    "info"  : image.load("resources/info.png"),
    "layerbox" : image.load("resources/layerbox.png"),
    "properties":image.load("resources/properties.png"),
    "colorbox" : image.load("resources/colorbox.png"),
    "palette" : image.load("resources/palette.png"),
    "title" : image.load("resources/pstitle.png"),
    "toolbar"  : image.load("resources/pstool.png")
}




# Standard tool values
currentTool = "line"
toolLoc = (0, 0)
toolLoc2 = (0, 0)
size = 4

# Colour information
currentColour = (255, 0, 0)
paletteHue = (255, 0, 0)
colourLoc = (1277, 793)

# Stamp image (from stamp module)
currentStamp = 265

# Location of mouse at the last mouse_down
lastclick = "tool"
# Show infobox or properties
displayInfo = True

# Standardizes new layer
newLayer = Surface((1080, 660))
# Colorkey makes #FF00FF transparent
newLayer.set_colorkey((255, 255, 255))
newLayer.fill((255, 255, 255))

# List of layers
layers = [newLayer.copy()]
# Active layer in the list: a pointer would be nice here
currentLayer = 0

# Action History
states = [([x.copy() for x in layers], currentLayer)]
# Active state
currentState = 0

# Creates screen
screen.fill((80, 80, 80))
screen.blit(image.load("resources/colorbox.png"), (1004, 760))
draw.rect(screen, paletteHue, (1050, 793, 228, 228))
screen.blit(image.load("resources/palette.png"), (1050, 793))

cover = newLayer.copy()

# Segoe UI System Font
segoeui = font.SysFont("Segoe UI", 12)
white = (255, 255, 255)


## .......~Main Loop~....... ##

fpsTrack = time.Clock()
running = True

while running:
    # Resets the screen
    draw.rect(screen, (80, 80, 80), (41, 29, 200, 800))
    screen.blit(images["title"], (0, 0))
    screen.blit(images["toolbar"], (0, 28))


    for ev in event.get():
        if ev.type == QUIT:
            running = False
            
        elif ev.type == MOUSEBUTTONDOWN:
            if ev.button == 1:
                # checks if mouse clicked on canvas
                if rects["canvas"].collidepoint(tm()):
                    lastclick = "canvas"
                    # creates a cover
                    cover = layers[currentLayer].copy()
                    # runs current tool's click method
                    tools[currentTool].canvasDown()

                elif rects["toolbar"].collidepoint(tm()):
                    lastclick = "tool"
                    for keyz in tools:
                        if tools[keyz].rect.collidepoint(tm()):
                            currentTool = keyz

                elif rects["palette"].collidepoint(tm()):
                    lastclick = "palette"
                elif rects["hue"].collidepoint(tm()):
                    lastclick = "hue"

                elif rects["exit"].collidepoint(tm()):
                    screen.blit(images["pExit"], (1231, 0))
                    running = False

                elif rects["save"].collidepoint(tm()):
                    screen.blit(images["pFile"], rects["save"])
                    savedFile = Surface((1080, 660))
                    savedFile.fill((255, 255, 255))
                    for i in layers:
                        savedFile.blit(i, (0, 0))
                    loadname = filedialog.asksaveasfilename()
                    if loadname:
                        image.save(savedFile, loadname + ".png")
                        print(loadname)

                elif rects["properties"].collidepoint(tm()):
                    displayInfo = False
                elif rects["info"].collidepoint(tm()):
                    displayInfo = True

                else:
                    lastclick = "screen"

            elif ev.button == 3:
                if rects["save"].collidepoint(tm()):
                    filename = filedialog.askopenfilename()
                    if filename:
                        layers = [newLayer.copy()]
                        currentLayer = 0
                        states = []
                        currentState = 0
                        layers[currentLayer].blit(image.load(filename), (0, 0))

            elif ev.button == 4:
                size += 2

            elif ev.button == 5:
                size -= 2 if size > 1 else 0

        elif ev.type == MOUSEBUTTONUP:
            if lastclick == "canvas" and ev.button == 1:
                del states[currentState + 1::]
                states.append(([x.copy() for x in layers], currentLayer))
                currentState = len(states) - 1
                if rects["canvas"].collidepoint(tm()):
                    tools[currentTool].canvasUp()

        elif ev.type == KEYDOWN:
            if 256 <= ev.key <= 265:
                currentStamp = ev.key

            if currentTool == "text":
                if ev.unicode.isalnum() or ev.unicode in "!@#$%^&*()~`-=_+[]{}|\:;,./<>? ":
                    tools["text"].text += ev.unicode
                elif ev.key == K_BACKSPACE:
                    tools["text"].text = tools["text"].text[:-1]

            else:
                if mouse.get_pressed()[0] == False:
                    if ev.key == K_SPACE and len(layers) < 8:
                        layers.insert(currentLayer, newLayer.copy())
                        currentLayer += 1

                        del states[currentState + 1::]
                        states.append(([x.copy() for x in layers], currentLayer))
                        currentState = len(states) - 1
                    elif ev.key == K_DELETE:
                        if len(layers) > 1:
                            del layers[currentLayer]
                            currentLayer -= 1 if currentLayer == len(layers) else 0

                            del states[currentState + 1::]
                            states.append(([x.copy() for x in layers], currentLayer))
                            currentState = len(states) - 1


                    elif ev.key == K_UP:
                        currentLayer += 1 if currentLayer + 1 < len(layers) else 0
                    elif ev.key == K_DOWN:
                        currentLayer -= 1 if currentLayer > 0 else 0

                    elif ev.key == K_LEFT:
                        if currentState > 0:
                            currentState -= 1
                            layers = [x.copy() for x in states[currentState][0]]
                            currentLayer = states[currentState][1]
                    elif ev.key == K_RIGHT:
                        if currentState + 1 < len(states):
                            currentState += 1
                            layers = [x.copy() for x in states[currentState][0]]
                            currentLayer = states[currentState][1]

                    elif ev.key == K_MINUS:
                        scaled = transform.smoothscale(layers[currentLayer], (layers[currentLayer].get_width()//2, layers[currentLayer].get_height()//2))
                        layers[currentLayer] = newLayer.copy()
                        layers[currentLayer].blit(scaled, (0, 0))

                    elif ev.key == K_EQUALS:
                        scaled = transform.smoothscale(layers[currentLayer], (layers[currentLayer].get_width()*2, layers[currentLayer].get_height()*2))
                        layers[currentLayer] = newLayer.copy()
                        layers[currentLayer].blit(scaled, (0, 0))

                    elif ev.key == K_1:
                        if numsci:
                            layers[currentLayer] = gaussianBlur(layers[currentLayer])
                        else:
                            layers[currentLayer] = transform.smoothscale(transform.smoothscale(layers[currentLayer], (270, 115)), (1080, 660))
                    elif ev.key == K_2 and numsci:
                        layers[currentLayer] = sobel(layers[currentLayer])
                    elif ev.key == K_3 and numsci:
                        invert(layers[currentLayer])




    if mouse.get_pressed()[0]:
        # canvas check
        if rects["canvas"].collidepoint(tm()) and lastclick == "canvas":
            # runs current tool's hold method
            tools[currentTool].canvasHold()

        elif rects["hue"].collidepoint(tm()) and lastclick == "hue":
            screen.blit(images["colorbox"], (1004, 760))
            draw.rect(screen, paletteHue, rects["palette"])
            screen.blit(images["palette"], rects["palette"])
            paletteHue = screen.get_at(tm())
            currentColour = screen.get_at(colourLoc)
            draw.circle(screen, (0, 0, 0), colourLoc, 5, 1)

        elif rects["palette"].collidepoint(tm()) and lastclick == "palette":
            screen.blit(images["colorbox"], (1004, 760))
            colourLoc = tm()
            draw.rect(screen, paletteHue, rects["palette"])
            screen.blit(images["palette"], rects["palette"])
            currentColour = screen.get_at(colourLoc)
            draw.circle(screen, (0, 0, 0), colourLoc, 5, 1)

    if currentTool == "text":
        layers[currentLayer].blit(cover, (0, 0))
        layers[currentLayer].blit(font.SysFont("Segoe UI", tools["text"].size).render(tools["text"].text, True, tools["text"].colour), toolLoc)
    else:
        tools["text"].text = ""

    draw.rect(screen, (0, 0, 0), (10, 726, 28, 28))
    draw.rect(screen, (255, 255, 255), (11, 727, 26, 26))
    draw.rect(screen, (0, 0, 0), (12, 728, 24, 24))

    draw.rect(screen, (0, 0, 0), (2, 718, 28, 28))
    draw.rect(screen, (255, 255, 255), (3, 719, 26, 26))
    draw.rect(screen, currentColour, (4, 720, 24, 24))


    infobox = images["info"].copy()
    layerbox = images["layerbox"].copy()

    if displayInfo:
        infobox.blit(segoeui.render(str(currentColour[0]), True, white), (70, 35))
        infobox.blit(segoeui.render(str(currentColour[1]), True, white), (70, 50))
        infobox.blit(segoeui.render(str(currentColour[2]), True, white), (70, 65))

        infobox.blit(segoeui.render(str(cm()[0]), True, white), (70, 125))
        infobox.blit(segoeui.render(str(cm()[1]), True, white), (70, 140))

        infobox.blit(segoeui.render(str(round(cmyk(currentColour)[0], 1)), True, white), (180, 35))
        infobox.blit(segoeui.render(str(round(cmyk(currentColour)[1], 1)), True, white), (180, 50))
        infobox.blit(segoeui.render(str(round(cmyk(currentColour)[2], 1)), True, white), (180, 65))
        infobox.blit(segoeui.render(str(round(cmyk(currentColour)[3], 1)), True, white), (180, 80))

        infobox.blit(segoeui.render(str(size), True, white), (180, 125))
        infobox.blit(segoeui.render(str(size), True, white), (180, 140))

        infobox.blit(segoeui.render("Current FPS: " + str(1000//fpsTrack.get_time()), True, white), (32, 170))
        screen.blit(infobox, (39, 805))
    else:
        screen.blit(images["properties"], (39, 805))



    if rects["exit"].collidepoint(tm()):
        screen.blit(images["hExit"], rects["exit"])
    else:
        screen.blit(images["Exit"], rects["exit"])

    if rects["save"].collidepoint(tm()):
        screen.blit(images["hFile"], rects["save"])
    else:
        screen.blit(images["File"], rects["save"])

    for i in range(len(layers)):
        draw.rect(layerbox, (80, 80, 80), (0, 90+50*(len(layers)-i-1), 100, 49))
        layerbox.blit(transform.scale(layers[i], (100, 51)), (0, 90+(50*(len(layers)-i-1))))
    draw.rect(layerbox, (255, 0, 0), (0, 90+50*(len(layers)-currentLayer-1), 100, 49), 2)
    screen.blit(layerbox, (1180, 100))



    screen.fill(white, (100, 100, 1080, 660))


    for layer in layers:
        screen.blit(layer, (100, 100))

    for keyz in tools:
        if tools[keyz].rect.collidepoint(tm()):
            if not mouse.get_pressed()[0]:
                screen.blit(tools[keyz].images[1], tools[keyz].loc)
        else:
            screen.blit(tools[keyz].images[0], tools[keyz].loc)

    screen.blit(tools[currentTool].images[2], tools[currentTool].loc)

    fpsTrack.tick()
    display.flip()
quit()
