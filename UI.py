import pygame
import pygame.freetype
from pygame.rect import Rect
from pygame.sprite import Sprite

# Used to create a surface with some text on it code extracted from https://programmingpixels.com/handling-a-title-screen-game-flow-and-buttons-in-pygame.html
def createSurfaceWithText(text, font_size, text_rgb, bg_rgb):
    font = pygame.freetype.SysFont("Ubuntu Mono", font_size, bold=False)
    surface, _ = font.render(text=text, fgcolor=text_rgb, bgcolor=bg_rgb)
    return surface.convert_alpha()

# Used to render UI elements, code extracted from https://programmingpixels.com/handling-a-title-screen-game-flow-and-buttons-in-pygame.html
class UIElement(Sprite):

    def __init__(self, center_position, text, font_size, bg_rgb, text_rgb, action=None):
        self.mouse_over = False

        default_image = createSurfaceWithText(
            text=text, font_size=font_size, text_rgb=text_rgb, bg_rgb=bg_rgb
        )

        highlighted_image = createSurfaceWithText(
            text=text, font_size=font_size * 1.2, text_rgb=text_rgb, bg_rgb=bg_rgb
        )

        self.images = [default_image, highlighted_image]
        self.rects = [
            default_image.get_rect(center=center_position),
            highlighted_image.get_rect(center=center_position),
        ]

        self.action = action

        super().__init__()

    @property
    def image(self):
        return self.images[1] if self.mouse_over else self.images[0]

    @property
    def rect(self):
        return self.rects[1] if self.mouse_over else self.rects[0]

    def update(self, mouse_pos, mouse_up):
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
            if mouse_up:
                return self.action
        else:
            self.mouse_over = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)
