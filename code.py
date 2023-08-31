# Main code for vday games. This is a menu that launches into the mini-games

# We need to import libraries 
import board
import displayio
import adafruit_imageload
import terminalio
import supervisor
import neopixel
import pygamer_keypad
from rainbowio import colorwheel
from adafruit_display_text import label

# Create the display
display = board.DISPLAY

# Create the joystick and keypad
gamepad = pygamer_keypad.pygamerpad(board.JOYSTICK_X, board.JOYSTICK_Y, board.BUTTON_CLOCK, board.BUTTON_OUT, board.BUTTON_LATCH, 8, True)

# Load the background
backgroundImg, backPalette = adafruit_imageload.load("art/background.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)

# Load the UI element and set its transparency
uiImg, uiPalette = adafruit_imageload.load("art/ui_element.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)
uiPalette.make_transparent(2)

# Load the game icons and set the transparency
g1Img, g1Palette = adafruit_imageload.load("art/dungeon_ico.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)
g2Img, g2Palette = adafruit_imageload.load("art/cute_cupid.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)
g2Palette.make_transparent(0)

# Create the background TileGrid
backTileGrid = displayio.TileGrid(backgroundImg, pixel_shader=backPalette)

# Create the UI Element TileGrid
ui1TileGrid = displayio.TileGrid(uiImg, pixel_shader=uiPalette)
ui2TileGrid = displayio.TileGrid(uiImg, pixel_shader=uiPalette)

# Create the Game Icon TileGrids
g1IcoTileGrid = displayio.TileGrid(g1Img, pixel_shader=g1Palette)
g2IcoTileGrid = displayio.TileGrid(g2Img, pixel_shader=g2Palette)

# Make the labels and give them text
g1Text = "Dungeon <3"
g2Text = "Cute Cupid :3"

font = terminalio.FONT

color = 0xCCCCCC

g1Label = label.Label(font, text=g1Text, color=color)
g2Label = label.Label(font, text=g2Text, color=color)

# color bar / led stuff
colorBar = neopixel.NeoPixel(board.NEOPIXEL, 5)
colorBar.brightness = 0.05
cbCounter = 0

# Create a group to hold the sprite and add it
backgroundGroup = displayio.Group()
backgroundGroup.append(backTileGrid)

# Create a group to hold the ui elements
g1UiGroup = displayio.Group()
g2UiGroup = displayio.Group()

# Append and organize the groups
g1UiGroup.append(ui1TileGrid)
g1UiGroup.append(g1IcoTileGrid)
g1UiGroup.append(g1Label)
g1IcoTileGrid.x = 34
g1IcoTileGrid.y = 6
g1Label.x = 30
g1Label.y = 74

g2UiGroup.append(ui2TileGrid)
g2UiGroup.append(g2IcoTileGrid)
g2UiGroup.append(g2Label)
g2IcoTileGrid.x = 34
g2IcoTileGrid.y = 6
g2Label.x = 18
g2Label.y = 74

# Keep track of if a level was loaded
isLevelLoad = False

# Make a group that holds the entire screen
screenGroup = displayio.Group()
screenGroup.append(backgroundGroup)
screenGroup.append(g1UiGroup)
screenGroup.append(g2UiGroup)

# Set the initial UI positions
g1UiGroup.x = 22
g1UiGroup.y = 16
g2UiGroup.x = 214
g2UiGroup.y = 16

# Add the UI groups to the display
display.show(screenGroup)

# refresh rate
refreshRate = 5

# Use initial button positions here
gamepad.calibrateJoy()
prevJoy = gamepad.getJoy()
prevBtns = gamepad.getButtons()

while True:

    # cbCounter = (cbCounter + 1) % 256
    # colorBar.fill(colorwheel(cbCounter))

    # We need to see if we're coming out of a level
    '''if isLevelLoad:
                print("back to main menu")
                isLevelLoad = False
                g1IcoTileGrid.x = 44
                g1IcoTileGrid.y = 10
                g1Label.x = 44
                g1Label.y = 88

                g2IcoTileGrid.x = 40
                g2IcoTileGrid.y = 4
                g2Label.x = 32
                g2Label.y = 88

                g1UiGroup.x = 48
                g1UiGroup.y = 64
                g2UiGroup.x = 240
                g2UiGroup.y = 64
                display.show(screenGroup)'''


    # Get the current button values
    curBtns = gamepad.getButtons()
    curJoy =  gamepad.getDigitalJoy()

    if not (prevJoy[0] == 1) and (curJoy[0] == 1):
        # We need to shift 192 pixels for the animation
        # Don't move back if we're on the first choice
        if g1UiGroup.x == 22:
            for x in range(6):
                g1UiGroup.x -= 32
                g2UiGroup.x -= 32
                display.refresh(target_frames_per_second=refreshRate)
        print("move ui forwards!")

    if not (prevJoy[0] == -1) and (curJoy[0] == -1):
        # We need to shift 192 pixels the other way
        if g2UiGroup.x == 22:
            for x in range(6):
                g1UiGroup.x += 32
                g2UiGroup.x += 32
                display.refresh(target_frames_per_second=refreshRate)
        print("shift ui backwards!")

    if not prevBtns and curBtns == "Pp":
        # Load the game based on what is selected
        if g1UiGroup.x == 22:
            print("load dungeon game")
            supervisor.set_next_code_file("/lib/dungeon.py")
            supervisor.reload()
        if g2UiGroup.x == 22:
            print("load cute cupid")
            supervisor.set_next_code_file("/lib/cutecupid.py")
            supervisor.reload()
            

    # update the previous gamepad values
    prevJoy.clear()
    prevBtns = curBtns

    for joy in curJoy:
        prevJoy.append(joy)