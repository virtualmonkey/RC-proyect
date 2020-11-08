import pygame

from math import cos, sin, pi
# Si estan en C++, pueden utilizar SDL

BLACK = (0,0,0)
WHITE = (255,255,255)
BACKGROUND = (64,64,64)

textures = {
    '1' : pygame.image.load('stone.png'),
    '2' : pygame.image.load('stone.png'),
    '3' : pygame.image.load('pumpkin.png'),
    '4' : pygame.image.load('fumace.png'),
    '5' : pygame.image.load('green.png')
    }

class Raycaster(object):
    def __init__(self,screen):
        self.screen = screen
        _, _, self.width, self.height = screen.get_rect()

        self.map = []
        self.blocksize = 50
        self.wallHeight = 50

        self.stepSize = 5

        self.player = {
            "x" : 75,
            "y" : 175,
            "angle" : 0,
            "fov" : 60
            }

    def load_map(self, filename):
        with open(filename) as f:
            for line in f.readlines():
                self.map.append(list(line))

    def drawRect(self, x, y, tex):
        tex = pygame.transform.scale(tex, (self.blocksize, self.blocksize))
        rect = tex.get_rect()
        rect = rect.move( (x,y) )
        self.screen.blit(tex, rect)

    def drawPlayerIcon(self,color):

        rect = (int(self.player['x'] - 2), int(self.player['y'] - 2), 5, 5)
        self.screen.fill(color, rect)

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

            self.screen.set_at((x,y), WHITE)

            dist += 2

    def render(self):

        halfWidth = int(self.width / 2)
        halfHeight = int(self.height / 2)

        for x in range(0, halfWidth, self.blocksize):
            for y in range(0, self.height, self.blocksize):
                
                i = int(x/self.blocksize)
                j = int(y/self.blocksize)

                if self.map[j][i] != ' ':
                    self.drawRect(x, y, textures[self.map[j][i]])

        self.drawPlayerIcon(BLACK)

        for i in range(halfWidth):
            angle = self.player['angle'] - self.player['fov'] / 2 + self.player['fov'] * i / halfWidth
            dist, wallType, tx = self.castRay(angle)

            x = halfWidth + i 

            # perceivedHeight = screenHeight / (distance * cos( rayAngle - viewAngle) * wallHeight
            h = self.height / (dist * cos( (angle - self.player['angle']) * pi / 180 )) * self.wallHeight

            start = int( halfHeight - h/2)
            end = int( halfHeight + h/2)

            img = textures[wallType]
            tx = int(tx * img.get_width())

            for y in range(start, end):
                ty = (y - start) / (end - start)
                ty = int(ty * img.get_height())
                texColor = img.get_at((tx, ty))
                self.screen.set_at((x, y), texColor)

        for i in range(self.height):
            self.screen.set_at( (halfWidth, i), BLACK)
            self.screen.set_at( (halfWidth+1, i), BLACK)
            self.screen.set_at( (halfWidth-1, i), BLACK)


pygame.init()
screen = pygame.display.set_mode((1000,500), pygame.DOUBLEBUF | pygame.HWACCEL) #, pygame.FULLSCREEN)
screen.set_alpha(None)
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 30)

def updateFPS():
    fps = str(int(clock.get_fps()))
    fps = font.render(fps, 1, pygame.Color("white"))
    return fps

r = Raycaster(screen)
r.load_map('map2.txt')

isRunning = True
while isRunning:

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            isRunning = False

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
            elif ev.key == pygame.K_q:
                r.player['angle'] -= 5
            elif ev.key == pygame.K_e:
                r.player['angle'] += 5


            i = int(newX / r.blocksize)
            j = int(newY / r.blocksize)

            if r.map[j][i] == ' ':
                r.player['x'] = newX
                r.player['y'] = newY

    screen.fill(pygame.Color("gray")) #Fondo

    #Techo
    screen.fill(pygame.Color("saddlebrown"), (int(r.width / 2), 0, int(r.width / 2),int(r.height / 2)))
    
    #Piso
    screen.fill(pygame.Color("dimgray"), (int(r.width / 2), int(r.height / 2), int(r.width / 2),int(r.height / 2)))

    r.render()
    
    # FPS
    screen.fill(pygame.Color("black"), (0,0,30,30))
    screen.blit(updateFPS(), (0,0))
    clock.tick(30)  
    
    pygame.display.update()

pygame.quit()
