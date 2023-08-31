# Dungeon game, based on Adafruit's "Tile Game"

import random
import stage
import ugame
import board
import neopixel
import microcontroller
import random
import collectable_facts

# Frames per second
FPS = 6
# Lifetime of rose in seconds
RS_LIFETIME = 3
# I-Frames - delay (seconds) hero can't take damage after getting hit
I_FRAMES = 1
# Mob move delay (ticks)
MB_MOVE_DELAY = 9
# 1 Tile is 16 pixels. Movement functions use raw pixel values, so this makes it easier
TILE = 16
# List of the play area bounds, in integer tile locations x1, y1, x2, y2
PLAY_AREA_BOUNDS = [1,1,9,6]
# Starting Health
HEALTH = 5
#Neopixel brightness
NPBRIGHTNESS = 0.05
# RGB color code for heart pink
HRTPINK = (100, 0, 70)
# RGB color code for black (off for LED)
BLACK = (0,0,0)

# Helper classes

# Rose shot classes
class Rose(stage.Sprite):
     # roseType = 0 for blue and 1 for red
     def __init__(self,x,y,roseType,isInverted):
          self.rose = roseType
          if roseType == 0:
               if isInverted:
                    super().__init__(rosCofBank,0,x,y,0,7)
               else:
                    super().__init__(rosCofBank,0,x,y,0,3)

          elif roseType == 1:
               if isInverted:
                    super().__init__(rosCofBank,5,x,y,0,7)
               else:
                    super().__init__(rosCofBank,5,x,y,0,3)
          
          # Life time of the rose
          # 6 frames per second
          self.lifetime = FPS * RS_LIFETIME
          self.isDead = False
          self.isInvert = isInverted
     
     def update(self, heroX, heroY, isInverted, mobs):
          super().update()
          # Update frame

          if self.rose == 0:
               self.set_frame(self.frame % 5 + 1)

          if self.rose == 1:
               # Set the rotation on the red rose, because the player
               # can change facing left or right, and the rose needs 
               # to be properly oriented

               if isInverted:
                    self.set_frame((self.frame % 5 + 1) + 5, 1)
               else:
                    self.set_frame((self.frame % 5 + 1) + 5, 3)

          # Move
          if self.rose == 0:
               if not self.isInvert:
                    self.move(self.x + TILE, self.y)
               else:
                    self.move(self.x - TILE, self.y)

          if self.rose == 1:
               if not isInverted:
                    self.move(heroX + TILE, self.y)
               else:
                    self.move(heroX - TILE, self.y)
               
               self.y = heroY

          # Check for colliding with a mob
          for mob in mobs:
               if stage.collide(self.x, self.y, self.x + 8, self.y + 8, mob.x, mob.y) and mob.mob < 2:
                    mob.kill(mobs)
                    gameState["killCount"] += 1

          # Update lifetime
          self.lifetime -= 1

          if self.lifetime == 0:
               self.isDead = True

# Use a class to control mobs
class Mob(stage.Sprite):
     # 0 for coffee, 1 for choco, 2 for scroll
     def __init__(self,x,y,mobType):
          self.mob = mobType
          if mobType == 0:
               super().__init__(rosCofBank,12,x,y)

          elif mobType == 1:
               super().__init__(scrlChocBank,1,x,y)
          
          elif mobType == 2:
               super().__init__(scrlChocBank,0,x,y)
          
          self.moveCounter = 0
     
     def update(self, heroX, heroY):
          # Is the mob a scroll or does it move?
          if self.mob == 2:
               pass
          else:
               # Do we reset the move timer?
               if self.moveCounter == MB_MOVE_DELAY:
                    self.moveCounter = 0
               # can the mob move?
               if self.moveCounter == 0:
                    #25% chance to reverse movement and go away from hero
                    if random.randrange(0,3) == 0:
                         if not self.x == PLAY_AREA_BOUNDS[0]:
                              if self.x < heroX:
                                   self.move(self.x - TILE/2, self.y)
                         if not self.x == PLAY_AREA_BOUNDS[2]:
                              if self.x > heroX:
                                   self.move(self.x + TILE/2, self.y)
                         if not self.y == PLAY_AREA_BOUNDS[1]:
                              if self.y < heroY:
                                   self.move(self.x, self.y - TILE/2)
                         if not self.y == PLAY_AREA_BOUNDS[3]:
                              if self.y > heroY:
                                   self.move(self.x, self.y + TILE/2)
                    else:
                    # Mob should get closer to hero
                         if self.x > heroX:
                              self.move(self.x - TILE/2, self.y)
                         if self.x < heroX:
                              self.move(self.x + TILE/2, self.y)
                         if self.y > heroY:
                              self.move(self.x, self.y - TILE/2)
                         if self.y < heroY:
                              self.move(self.x, self.y + TILE/2)

               self.moveCounter += 1
     def kill(self, mobList):
          # Remove the mob from the mob list
          try:
               mobList.remove(self)
          except:
               pass
          # We need to keep track of active mobs, so take one off when dead
          gameState["mobs"] -= 1

     def onCollide(self):
          # What should happen when the mob collides with us
          # if it's a scroll, then needs to show a menu with some text
          if self.mob == 2:
               gameState["scrollCollide"] = True
          else:
               pass

# Use a class for the hero
class Hero(stage.Sprite):
     def __init__(self,x,y):
          super().__init__(heroBank,0,x,y)
          self.invertWeapon = False
          self.iframectr = FPS * I_FRAMES
     
     def update(self, curBtn, prevBtn, roseLayer, mobList, healthBar,stg):
          super().update()
          
          if gameState["isHurt"]:
               self.iframectr -= 1

          # Move first 
          if (curBtn & ugame.K_RIGHT) and not (prevBtn & ugame.K_RIGHT):
               if self.x < 134:
                    self.move(self.x + 8, self.y)
                    self.invertWeapon = False

          if (curBtn & ugame.K_LEFT) and not (prevBtn & ugame.K_LEFT):
               if self.x > 16:
                    self.move(self.x - 8, self.y)
                    self.invertWeapon = True

          if (curBtn & ugame.K_UP) and not (prevBtn & ugame.K_UP):
               if self.y > 16:
                    self.move(self.x, self.y - 8)
               if (gameState["room"] == 0 or gameState["room"] == 2) and gameState["mobs"] == 0 and self.y == 16:
                    if self.x >= 48 and self.x <= 96:
                         if gameState["room"] == 0:
                              gameState["room"] = 1
                         else:
                              gameState["room"] = 0

          if (curBtn & ugame.K_DOWN) and not (prevBtn & ugame.K_DOWN):
               if self.y < 96:
                    self.move(self.x, self.y + 8)
               if (gameState["room"] == 0 or gameState["room"] == 1) and gameState["mobs"] == 0 and self.y == 96:
                    if self.x >= 48 and self.x <= 96:
                         if gameState["room"] == 0:
                              gameState["room"] = 2
                         else:
                              gameState["room"] = 0

          if (curBtn & ugame.K_O) and not (prevBtn & ugame.K_O) and not gameState["isAttack"]:
               gameState["isAttack"] = True
               if self.invertWeapon:
                    self.redRose = Rose(self.x - TILE, self.y, 1, True)
               else:
                    self.redRose = Rose(self.x + TILE, self.y, 1, False)
               roseLayer.insert(0,self.redRose)

          if (curBtn & ugame.K_X) and not (prevBtn & ugame.K_X) and not gameState["activeArrow"]:
               gameState["activeArrow"] = True
               if self.invertWeapon:
                    self.blueRose = Rose(self.x - TILE, self.y, 0, True)
               else:
                    self.blueRose = Rose(self.x + TILE, self.y, 0, False)
               roseLayer.insert(0,self.blueRose)

          if gameState["activeArrow"]:
               self.blueRose.update(self.x, self.y, self.invertWeapon, mobList)
               if self.blueRose.isDead:
                    try:
                         roseLayer.remove(self.blueRose)
                    except:
                         pass
                    gameState["activeArrow"] = False

          if gameState["isAttack"]:
               self.redRose.update(self.x, self.y, self.invertWeapon, mobList)
               if self.redRose.isDead:
                    try:
                         roseLayer.remove(self.redRose)
                    except:
                         pass
                    gameState["isAttack"] = False

          # We need to check if we've been hit / touched the scroll
          for mob in mobList:
               if stage.collide(self.x, self.y, self.x + 8, self.y + 8, mob.x, mob.y) and mob.mob < 2 and not gameState["isHurt"]:
                    healthBar.update(stg)
                    gameState["isHurt"] = True
               elif stage.collide(self.x, self.y, self.x + 8, self.y + 8, mob.x, mob.y) and mob.mob == 2:
                    mob.onCollide()

          if gameState["isHurt"] and self.iframectr == 0:
               gameState["isHurt"] = False
               self.iframectr = FPS * I_FRAMES


     def kill():
          return

#### CLASS IS BROKEN RIGHT NOW ###
#### PLACEHOLDER ####
# Menu class to spawn some stuff for text
# Can expand by adding different menuTypes
# 0 - Pause/Quit menu
# 1 - Scroll Text UI
# 2 - Game Over
class Menu(stage.Grid):
     def __init__(self, menuType, layer):
          super().__init__(uiBank,8,6)
          self.type = menuType
          self.move(TILE,TILE)

          # Load in some text
          if menuType == 0:
               self.header = stage.Text(20,2)
               self.bodyText = stage.Text(16,2)
               self.header.move(TILE*1.25,TILE)
               self.bodyText.move(TILE*1.25,TILE*3)
               self.bodyText.text("Select - Resume\n  Start - Quit  ")
               self.header.text("Do you want to\nquit?")
               layer.append(self.header)
               layer.append(self.bodyText)
               layer.append(self)

          elif menuType == 1:
               rawMessage = random.choice(collectable_facts.FACTS)
               chunks = rawMessage.split('\n')
               if len(chunks) == 1:
                    self.bodyText = stage.Text(20,2)
                    self.bodyText.move(TILE*1.25,TILE)
                    self.bodyText.text(rawMessage)
                    layer.append(self.bodyText)
               elif len(chunks) == 2:
                    self.bodyText = stage.Text(20,2)
                    self.body2Text = stage.Text(20,2)
                    self.bodyText.move(TILE*1.25,TILE)
                    self.body2Text.move(TILE*1.25,TILE*2)
                    self.bodyText.text(chunks[0])
                    self.body2Text.text(chunks[1])
                    layer.append(self.bodyText)
                    layer.append(self.body2Text)
               elif len(chunks) == 3:
                    self.bodyText = stage.Text(20,2)
                    self.body2Text = stage.Text(20,2)
                    self.body3Text = stage.Text(20,2)
                    self.bodyText.move(TILE*1.25,TILE)
                    self.body2Text.move(TILE*1.25,TILE*2)
                    self.body3Text.move(TILE*1.25,TILE*3)
                    self.bodyText.text(chunks[0])
                    self.body2Text.text(chunks[1])
                    self.body3Text.text(chunks[2])
                    layer.append(self.bodyText)
                    layer.append(self.body2Text)
                    layer.append(self.body3Text)
               elif len(chunks) == 4:
                    self.bodyText = stage.Text(20,2)
                    self.body2Text = stage.Text(20,2)
                    self.body3Text = stage.Text(20,2)
                    self.body4Text = stage.Text(20,2)
                    self.bodyText.move(TILE*1.25,TILE)
                    self.body2Text.move(TILE*1.25,TILE*2)
                    self.body3Text.move(TILE*1.25,TILE*3)
                    self.body4Text.move(TILE*1.25,TILE*4)
                    self.bodyText.text(chunks[0])
                    self.body2Text.text(chunks[1])
                    self.body3Text.text(chunks[2])
                    self.body4Text.text(chunks[3])
                    layer.append(self.bodyText)
                    layer.append(self.body2Text)
                    layer.append(self.body3Text)
                    layer.append(self.body4Text)
               layer.append(self)
          
          elif menuType == 2:
               self.header = stage.Text(20,2)
               self.bodyText = stage.Text(20,2)
               self.body2Text = stage.Text(20, 2)
               self.header.move(TILE*2.75,TILE*1.25)
               self.bodyText.move(TILE,TILE*3)
               self.body2Text.move(TILE,TILE*5)
               self.bodyText.text("You destroyed "+ str(gameState["killCount"]) + "\n  gross things!")
               self.body2Text.text("Press any key to\n    continue!")
               self.header.text("GAME OVER")
               layer.append(self.header)
               layer.append(self.bodyText)
               layer.append(self.body2Text)
               layer.append(self)

          gameState["inMenu"] = True

     def kill(self, layer):
          if self.type == 1:
               try:
                    layer.remove(self.bodyText)
                    layer.remove(self.body2Text)
                    layer.remove(self.body3Text)
                    layer.remove(self.body4Text)
               except:
                    pass
               finally:
                    layer.remove(self)

          if self.type != 1:
               layer.remove(self)
               layer.remove(self.header)
               layer.remove(self.bodyText)

          gameState["inMenu"] = False
          gameState["scrollCollide"] = False

class HealthBar(stage.Grid):
     # note there is a bug
     # health bar should be a 5x1 grid, so use the health constant to set the width
     # but if the width is 5, for some reason an extra tile is appended that can't be changed
     # if it's 4, there's no issue; if it's 6, there's also no issue
     # but if it's 1,5,7, or 9 there is an issue
     # odd numbers aren't working????
     # work around is make the grid 6 long, then just set tile[5] to be transparent
     def __init__(self, layer, ledPin):
          super().__init__(bgBank,HEALTH+1,1)
          for x in range(HEALTH):
               self.tile(x,0,9)
          self.tile(5,0,10)

          self.ledBar = neopixel.NeoPixel(ledPin, HEALTH)
          self.ledBar.brightness = NPBRIGHTNESS
          self.ledBar.fill(HRTPINK)

          layer.append(self)

     def update(self,stg):
          if gameState["health"] > 0:
               self.tile(gameState["health"]-1,0,10)
               stg.render_block(0,0,TILE*5,TILE)
               self.ledBar[gameState["health"] - 1] = BLACK
               gameState["health"] -= 1
          
# Set up initial states and create the objects needed for the game
gameState = {"room":0,"health":5,"isDead":False,"mobs":0,"spawnedScroll":False,"isAttack":False,"activeArrow":False, "isHurt": False, "isMoving": False, "inMenu":False, "killCount":0, "scrollCollide": False}

bgBank = stage.Bank.from_bmp16("/art/dungeon_floor.bmp")
background = stage.Grid(bgBank, 10, 8)

uiBank = stage.Bank.from_bmp16("/art/scroll_ui.bmp")

heroBank = stage.Bank.from_bmp16("/art/syd_hero.bmp")
rosCofBank = stage.Bank.from_bmp16("/art/rose_cof.bmp")
scrlChocBank = stage.Bank.from_bmp16("/art/scroll_choco.bmp")

# Set the initial room grid
# corners
background.tile(0,0,0) # upper left
background.tile(9,0,2) # upper right
background.tile(0,7,6) # lower left
background.tile(9,7,8) # lower right

# top / bottom walls
for x in range(1, 9):
    background.tile(x,0,1) # top
    background.tile(x,7,7) # bottom

# left / right walls
for y in range(1,7):
    background.tile(0,y,3) # left
    background.tile(9,y,5) # right

# floor
for x in range(1,9):
    for y in range(1,7):
            background.tile(x,y,4)

# add floor for spots player can go
for x in range(1,5):
    background.tile(x+2,0,4)
    background.tile(x+2,7,4)

# Set the room up and spawn appropriate mobs
def setRoom(room, hero, bg, mb):
     # In any case we need to reset the scroll spawn status
     if gameState["spawnedScroll"]:
          gameState["spawnedScroll"] = False

     if room == 0:
          # Set the initial game states
          gameState["mobs","isAttack","activeArrow", "isMoving", "inMenu", "scrollCollide"] = 0, False, False, False, False, False

          # Set the initial room grid
          # corners
          bg.tile(0,0,0) # upper left
          bg.tile(9,0,2) # upper right
          bg.tile(0,7,6) # lower left
          bg.tile(9,7,8) # lower right

          # top / bottom walls
          for x in range(1, 9):
               bg.tile(x,0,1) # top
               bg.tile(x,7,7) # bottom

          # left / right walls
          for y in range(1,7):
               bg.tile(0,y,3) # left
               bg.tile(9,y,5) # right

          # floor
          for x in range(1,9):
               for y in range(1,7):
                    bg.tile(x,y,4)

          # add floor for spots player can go
          for x in range(1,5):
               bg.tile(x+2,0,4)
               bg.tile(x+2,7,4)

          hero.move(5 * TILE, 4 * TILE)

          # make sure the mob list is empty
          mb.clear()

     if room == 1:
          # Set the initial room grid
          # corners
          bg.tile(0,0,0) # upper left
          bg.tile(9,0,2) # upper right
          bg.tile(0,7,6) # lower left
          bg.tile(9,7,8) # lower right

          # top / bottom walls
          for x in range(1, 9):
               bg.tile(x,0,1) # top
               bg.tile(x,7,7) # bottom

          # left / right walls
          for y in range(1,7):
               bg.tile(0,y,3) # left
               bg.tile(9,y,5) # right

          # floor
          for x in range(1,9):
               for y in range(1,7):
                    bg.tile(x,y,4)

          hero.move(5 * TILE, 4 * TILE)

          # Spawn Mobs
          for mob in range(1,random.randrange(1,6)):
               mb.append(Mob((random.randrange(1, 9)*TILE), (random.randrange(1,7)*TILE), 0))
               #print(str(mob))
          # We need to keep track of how many mobs we have
          # It is entirely possible that no mobs spawn, and we need to account for that
          if len(mb) == 0:
               mb.append(Mob((random.randrange(1, 9)*TILE), (random.randrange(1,7)*TILE), 0))

     if room == 2:
          # Set the initial room grid
          # corners
          bg.tile(0,0,0) # upper left
          bg.tile(9,0,2) # upper right
          bg.tile(0,7,6) # lower left
          bg.tile(9,7,8) # lower right

          # top / bottom walls
          for x in range(1, 9):
               bg.tile(x,0,1) # top
               bg.tile(x,7,7) # bottom

          # left / right walls
          for y in range(1,7):
               bg.tile(0,y,3) # left
               bg.tile(9,y,5) # right

          # floor
          for x in range(1,9):
               for y in range(1,7):
                    bg.tile(x,y,4)

          hero.move(5 * TILE, 4 * TILE)

          # Spawn Mobs
          for mob in range(1,random.randrange(1,6)):
               mb.append(Mob((random.randrange(1, 9)*TILE), (random.randrange(1,7)*TILE), 1))
               #print(str(mob))
          # We need to keep track of how many mobs we have
          # It is entirely possible that no mobs spawn, and we need to account for that
          if len(mb) == 0:
               mb.append(Mob((random.randrange(1, 9)*TILE), (random.randrange(1,7)*TILE), 1))
               gameState["mobs"] = len(mb)

     # Set the number of mobs in our state
     gameState["mobs"] = len(mb)

# Create and spawn our hero
hero = Hero(5*TILE, 4*TILE)
# Display Stuff
gameStage = stage.Stage(ugame.display, FPS)
sprites = [hero]
mobs = []
uiLayer = []
hpBar = HealthBar(uiLayer, board.NEOPIXEL)
gameStage.layers = uiLayer + sprites + [background]
gameStage.render_block()
prevPad = ugame.buttons.get_pressed()
prevRoom = 0

while True:
     # Get the buttons
     curPad = ugame.buttons.get_pressed()
     
     # Enter the pause menu 
     if (curPad & ugame.K_SELECT) and not (prevPad & ugame.K_SELECT):
          pMenu = Menu(0,uiLayer)
          gameStage.layers = uiLayer + sprites + mobs + [background]
          gameStage.render_block()
          prevPad = curPad
          gameStage.tick()
          gameStage.tick()
          gameStage.tick()
          gameStage.tick()

          while(gameState["inMenu"]):
               print("menu logic here!")
               curPad = ugame.buttons.get_pressed()

               if (curPad & ugame.K_SELECT) and not (prevPad & ugame.K_SELECT):
                    pMenu.kill(uiLayer)
                    gameStage.layers = uiLayer + sprites + mobs + [background]
                    gameStage.render_block()

               if (curPad & ugame.K_START) and not (prevPad & ugame.K_START):
                    microcontroller.reset()


               gameStage.render_block()
               gameStage.tick()

               prevPad = curPad

     # Update the hero, who can also spawn new layers
     # We are constantly checking for updates to the layers
     # so we're rendering what's current
     hero.update(curPad, prevPad, sprites, mobs, hpBar,gameStage)
     for mob in mobs:
          mob.update(hero.x, hero.y)

     gameStage.layers = uiLayer + sprites + mobs + [background]

     # redraw the whole screen if something dies (to clear dead sprites)
     # shave some time by only redrawing the area that can have sprites
     # but in this context there's enough moving around the screen
     # frequently enough that we get artifacts if we redraw only when the 
     # the rose dies
     gameStage.render_block(16,16,144,112)

     # Render all the sprites
     gameStage.render_sprites(sprites)

     gameStage.tick()

     # Logic to control when switching rooms
     # We can't switch rooms until the number of mobs is 0
     # 0 = starting room
     # 1 = up room
     # 2 = down room
     if gameState["room"] != prevRoom:
          if gameState["room"] == 0:
               setRoom(0, hero, background, mobs)
               gameStage.render_sprites(sprites)
               gameStage.render_block()
               gameStage.tick()
          elif gameState["room"] == 1:
               setRoom(1, hero, background, mobs)
               gameStage.render_sprites(sprites)
               gameStage.render_block()
               gameStage.tick()
               gameState["mobs"] = len(mobs)
          elif gameState["room"] == 2:
               setRoom(2, hero, background, mobs)
               gameStage.render_sprites(sprites)
               gameStage.render_block()
               gameStage.tick()
               gameState["mobs"] = len(mobs)

     # If the room is empty, we need to add the ability to leave it
     # We should also spawn the scroll
     if gameState["mobs"] == 0 and gameState["room"] != 0 and not gameState["spawnedScroll"]:
          if gameState["room"] == 1:
               # For the top room, you need to go down
               for x in range(1,5):
                    background.tile(x+2,7,4)
     
          if gameState["room"] == 2:
               # For the bottom room you need to go up
               for x in range(1,5):
                    background.tile(x+2,0,4)
          
          # Spawn the scroll
          mobs.append(Mob((random.randrange(1, 9)*TILE), (random.randrange(1,7)*TILE), 2))
          gameState["spawnedScroll"] = True
                   
          # Render the update
          gameStage.render_block()

     if gameState["scrollCollide"]:
          pMenu = Menu(1,uiLayer)
          gameStage.layers = uiLayer + sprites + mobs + [background]
          gameStage.render_block()
          prevPad = curPad
          gameStage.tick()
          gameStage.tick()
          gameStage.tick()
          gameStage.tick()

          while(gameState["inMenu"]):
               curPad = ugame.buttons.get_pressed()
               
               if (curPad & ugame.K_SELECT) and not (prevPad & ugame.K_SELECT):
                    gameState["room"] = 0
                    setRoom(0, hero, background, mobs)
                    pMenu.kill(uiLayer)
                    gameStage.layers = uiLayer + sprites + mobs + [background]
                    gameStage.render_block()

               if (curPad & ugame.K_START) and not (prevPad & ugame.K_START):
                    gameState["room"] = 0
                    setRoom(0, hero, background, mobs)
                    pMenu.kill(uiLayer)
                    gameStage.layers = uiLayer + sprites + mobs + [background]
                    gameStage.render_block()

               if (curPad & ugame.K_X) and not (prevPad & ugame.K_X):
                    gameState["room"] = 0
                    setRoom(0, hero, background, mobs)
                    pMenu.kill(uiLayer)
                    gameStage.layers = uiLayer + sprites + mobs + [background]
                    gameStage.render_block()

               if (curPad & ugame.K_O) and not (prevPad & ugame.K_O):
                    gameState["room"] = 0
                    setRoom(0, hero, background, mobs)
                    pMenu.kill(uiLayer)
                    gameStage.layers = uiLayer + sprites + mobs + [background]
                    gameStage.render_block()

               gameStage.tick()

               prevPad = curPad
     
     if gameState["health"] == 0:
          pMenu = Menu(2,uiLayer)
          gameStage.layers = uiLayer + sprites + mobs + [background]
          gameStage.render_block()
          prevPad = curPad
          gameStage.tick()
          gameStage.tick()
          gameStage.tick()
          gameStage.tick()

          while(gameState["inMenu"]):
               curPad = ugame.buttons.get_pressed()
               
               if (curPad & ugame.K_SELECT) and not (prevPad & ugame.K_SELECT):
                    microcontroller.reset()

               if (curPad & ugame.K_START) and not (prevPad & ugame.K_START):
                    microcontroller.reset()

               if (curPad & ugame.K_X) and not (prevPad & ugame.K_X):
                    microcontroller.reset()

               if (curPad & ugame.K_O) and not (prevPad & ugame.K_O):
                    microcontroller.reset()

               gameStage.tick()

               prevPad = curPad
     
     ### DEBUG SECTION ###
     # print(str(gameStage.layers))
     # print(str(gameState["refreshScreen"])) 
     # print(str(hero.x))
     # print(str(gameState["room"]))
     # print(str(mobs))
     # print(str(gameState["mobs"]))
     # print(str(gameState["scrollCollide"]), str(gameState["spawnedScroll"]), str(gameState["inMenu"]))
     
     # Update pressed buttons
     prevPad = curPad

     # Store the previous room we were in for comparison
     prevRoom = gameState["room"]
