import pygame
import pygame.freetype
from pygame.sprite import Sprite
from pygame.rect import Rect
from enum import Enum
from math import cos, sin, pi, atan2
from UI import UIElement

#colors
BLACK = (0,0,0)
WHITE = (255,255,255)
DARK_GREEN = (57,67,32)
WATER_BLUE = (71, 75, 139)
SPRITE_BACKGROUND = (206, 229, 241)
RADAR_COLOR = (241, 242, 39)

#walls for blocks
walls = {
    '1' : pygame.image.load('stone.png'),
    '2' : pygame.image.load('stone.png'),
    '3' : pygame.image.load('pumpkin.png'),
    '4' : pygame.image.load('green.png'),
    '5' : pygame.image.load('fumace.png')
    }

evil_mods = [{"x": 150, "y": 320,"texture" : pygame.image.load('creeper.jpg')},
            {"x": 300,"y": 225,"texture" : pygame.image.load('skeleton.jpg')},
            {"x": 298,"y": 400,"texture" : pygame.image.load('enderman.png')},
            {"x": 120,"y": 150,"texture" : pygame.image.load('enderman.png')}     
    ]

# Raycaster class
class Raycaster(object):
    def __init__(self,screen):
        self.screen = screen
        _, _, self.width, self.height = screen.get_rect()

        self.map = []
        self.zbuffer = [-float('inf') for z in range(int(self.width / 2))]
        self.blocksize = 50
        self.wallHeight = 50
        self.stepSize = 5

        self.player = {
            "x" : 340,
            "y" : 175,
            "angle" : 130,
            "fov" : 60
            }

    # Upload level from map
    def load_map(self, filename):
        with open(filename) as f:
            for line in f.readlines():
                self.map.append(list(line))

    # Draw the walls from the level
    def drawRect(self, x, y, tex):
        tex = pygame.transform.scale(tex, (self.blocksize, self.blocksize))
        rect = tex.get_rect()
        rect = rect.move( (x,y) )
        self.screen.blit(tex, rect)

    # Draw the player in the level
    def drawPlayerIcon(self,color):
        rect = (self.player['x'] - 2, self.player['y'] - 2, 5, 5)
        self.screen.fill(color, rect)

    # Draw sprites (used for enemies)
    def drawSprite(self, sprite, size):
        spriteDist = ((self.player['x'] - sprite['x'])**2 + (self.player['y'] - sprite['y'])**2) ** 0.5
        
        spriteAngle = atan2(sprite['y'] - self.player['y'], sprite['x'] - self.player['x'])

        aspectRatio = sprite["texture"].get_width() / sprite["texture"].get_height()
        spriteHeight = (self.height / spriteDist) * size
        spriteWidth = spriteHeight * aspectRatio

        angleRads = self.player['angle'] * pi / 180
        fovRads = self.player['fov'] * pi / 180

        startX = (self.width * 3 / 4) + (spriteAngle - angleRads)*(self.width/2) / fovRads - (spriteWidth/2)
        startY = (self.height / 2) - (spriteHeight / 2)
        startX = int(startX)
        startY = int(startY)

        for x in range(startX, int(startX + spriteWidth)):
            for y in range(startY, int(startY + spriteHeight)):
                if (self.width / 2) < x < self.width:
                    if self.zbuffer[ x - int(self.width/2)] >= spriteDist:
                        tx = int( (x - startX) * sprite["texture"].get_width() / spriteWidth )
                        ty = int( (y - startY) * sprite["texture"].get_height() / spriteHeight )
                        texColor = sprite["texture"].get_at((tx, ty))
                        if texColor[3] > 128 and texColor != SPRITE_BACKGROUND:
                            self.screen.set_at((x,y), texColor)
                            self.zbuffer[ x - int(self.width/2)] = spriteDist
    # cast the radar for the player
    def castRay(self, a):
        rads = a * pi / 180
        dist = 0
        while True:
            x = int(self.player['x'] + dist * cos(rads))
            y = int(self.player['y'] + dist * sin(rads))

            i = int(x/self.blocksize)
            j = int(y/self.blocksize)

            if self.map[j][i] != ' ':
                hitX = x - i*self.blocksize
                hitY = y - j*self.blocksize

                if 1 < hitX < self.blocksize - 1:
                    maxHit = hitX
                else:
                    maxHit = hitY

                tx = maxHit / self.blocksize

                return dist, self.map[j][i], tx

            self.screen.set_at((x,y), RADAR_COLOR)

            dist += 2
    
    #render the game and the elements in it
    def render(self):

        halfWidth = int(self.width / 2)
        halfHeight = int(self.height / 2)

        for x in range(0, halfWidth, self.blocksize):
            for y in range(0, self.height, self.blocksize):
                
                i = int(x/self.blocksize)
                j = int(y/self.blocksize)

                if self.map[j][i] != ' ':
                    self.drawRect(x, y, walls[self.map[j][i]])

        self.drawPlayerIcon(WHITE)

        for i in range(halfWidth):
            angle = self.player['angle'] - self.player['fov'] / 2 + self.player['fov'] * i / halfWidth
            dist, wallType, tx = self.castRay(angle)
            self.zbuffer[i] = dist
            x = halfWidth + i 

            # perceivedHeight = screenHeight / (distance * cos( rayAngle - viewAngle) * wallHeight ----- Formula para el alto de las paredes
            h = self.height / (dist * cos( (angle - self.player['angle']) * pi / 180 )) * self.wallHeight

            start = int( halfHeight - h/2)
            end = int( halfHeight + h/2)
            #carga de imagenes para los bloques
            img = walls[wallType]
            tx = int(tx * img.get_width())

            for y in range(start, end):
                ty = (y - start) / (end - start)
                ty = int(ty * img.get_height())
                texColor = img.get_at((tx, ty))
                self.screen.set_at((x, y), texColor)

        for mod in evil_mods:
            self.screen.fill(pygame.Color("white"), (mod['x'], mod['y'], 3,3))
            self.drawSprite(mod, 30)


        for i in range(self.height):
            self.screen.set_at( (halfWidth, i), BLACK)
            self.screen.set_at( (halfWidth+1, i), BLACK)
            self.screen.set_at( (halfWidth-1, i), BLACK)

# Used to keep control of the game. code exracted from code extracted from https://programmingpixels.com/handling-a-title-screen-game-flow-and-buttons-in-pygame.html
class GameState(Enum):
    QUIT = -1
    MAIN_MENU = 0
    GAME = 1

def main():
    pygame.init()

    screen = pygame.display.set_mode((1000,500))
    game_state = GameState.MAIN_MENU

    while True:
        pygame.mixer.music.load('background_music.mp3')
        pygame.mixer.music.play(0)
        if game_state == GameState.MAIN_MENU:
            game_state = mainMenu(screen)
        if game_state == GameState.GAME:
            game_state = play(screen)
        if game_state == GameState.QUIT:
            pygame.quit()
            return

def mainMenu(screen):
    background=pygame.image.load('bg.jpg')
    background = pygame.transform.scale(background, (1000, 500))

    play_btn = UIElement(
        center_position=(500, 240),
        font_size=50,
        bg_rgb=WATER_BLUE,
        text_rgb=WHITE,
        text="Play",
        action=GameState.GAME,
    )

    quit_btn = UIElement(
        center_position=(500, 300),
        font_size=50,
        bg_rgb=WATER_BLUE,
        text_rgb=WHITE,
        text="Quit",
        action=GameState.QUIT,
    )

    credits_btn = UIElement(
        center_position=(500, 450),
        font_size=35,
        bg_rgb=DARK_GREEN,
        text_rgb=WHITE,
        text="Made by: Luis Urbina",
    )

    buttons = [play_btn, quit_btn, credits_btn]

    while True:
        screen.blit(background, (0,0))
        mouse_up = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_up = True

        for button in buttons:
            ui_action = button.update(pygame.mouse.get_pos(), mouse_up)
            if ui_action is not None:
                return ui_action
            button.draw(screen)

        pygame.display.flip()

def play(screen):
    
    return_btn = UIElement(
        center_position=(850, 475),
        font_size=24,
        bg_rgb=BLACK,
        text_rgb=WHITE,
        text="Back to main menu",
        action=GameState.MAIN_MENU,
    )
    pygame.init()

    screen = pygame.display.set_mode((1000,500), pygame.DOUBLEBUF | pygame.HWACCEL)
    screen.set_alpha(None)
    pygame.display.set_caption('Minecraft')
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Ubuntu Mono", 34)

    def updateFPS():
        fps = str(int(clock.get_fps()))
        fps = font.render(fps, 1, pygame.Color("white"))
        return fps

    r = Raycaster(screen)

    r.load_map('map2.txt')

    isRunning = True

    while isRunning:
        mouse_up=False
        return_btn.draw(screen)

        for ev in pygame.event.get():
            
            if ev.type == pygame.QUIT:
                isRunning = False
            if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                mouse_up = True

            ui_action = return_btn.update(pygame.mouse.get_pos(), mouse_up)
            if ui_action is not None:
                return ui_action
            
            pygame.display.flip()

            newX = r.player['x']
            newY = r.player['y']

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    isRunning = False
                elif ev.key == pygame.K_w:
                    newX += cos(r.player['angle'] * pi / 180) * r.stepSize
                    newY += sin(r.player['angle'] * pi / 180) * r.stepSize

                elif ev.key == pygame.K_s:
                    newX -= cos(r.player['angle'] * pi / 180) * r.stepSize
                    newY -= sin(r.player['angle'] * pi / 180) * r.stepSize

                elif ev.key == pygame.K_a:
                    newX -= cos((r.player['angle'] + 90) * pi / 180) * r.stepSize
                    newY -= sin((r.player['angle'] + 90) * pi / 180) * r.stepSize

                elif ev.key == pygame.K_d:
                    newX += cos((r.player['angle'] + 90) * pi / 180) * r.stepSize
                    newY += sin((r.player['angle'] + 90) * pi / 180) * r.stepSize

                i = int(newX / r.blocksize)
                j = int(newY / r.blocksize)

                if r.map[j][i] == ' ':
                    r.player['x'] = newX
                    r.player['y'] = newY
            if ev.type == pygame.MOUSEBUTTONDOWN or ev.type == pygame.MOUSEBUTTONUP:
                if ev.button == 4:
                    r.player['angle'] -= 5
                if ev.button == 5:
                    r.player['angle'] += 5

        screen.fill(pygame.Color(57,67,32, 255))

        #Color for the sky
        screen.fill(pygame.Color("skyblue"), (int(r.width / 2), 0, int(r.width / 2),int(r.height / 2)))
        
        #Color of the grass
        screen.fill(pygame.Color(57,67,32, 255), (int(r.width / 2), int(r.height / 2), int(r.width / 2),int(r.height / 2)))

        r.render()
        
        screen.fill(pygame.Color("black"), (0,0,30,30))
        screen.blit(updateFPS(), (0,0))
        clock.tick(30)  
        
        pygame.display.update()
    
    pygame.quit()

if __name__ == "__main__":
    main()