import pygame, math, entities, gamemapping, pygame.font, colordefs, preloading

last_frame = pygame.event.get().copy() #stores the events from last frame
last_frame_mouse = pygame.mouse.get_pressed()

scrollspeed = 25

locked = False

select_box_start = None
blitPoint = None

select_box = None

def mouse_clicked(button_index):
    return not pygame.mouse.get_pressed()[button_index] and last_frame_mouse[button_index] == True

def get_selection(gameMap):
    global select_box_start
    global select_box
    global blitPoint
    selection = []

    shift = (blitPoint[0] - gameMap.rect.x, blitPoint[1] - gameMap.rect.y)

    for entity in entities.all_entities:
        if entity.rect.colliderect(select_box.get_rect().move(shift[0], shift[1])):
            selection.append(entity)

    select_box_start = None

    print("selection:")
    for e in selection:
        print(e)
    return selection
    

def update_selection_box(screen):
    global select_box_start
    global blitPoint
    global select_box
    
    if select_box_start == None:
        select_box_start = [pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]]
    
    width = abs(pygame.mouse.get_pos()[0] - select_box_start[0])
    height = abs(pygame.mouse.get_pos()[1] - select_box_start[1])

    select_box = pygame.Surface((width, height), pygame.SRCALPHA)
    select_box.fill((100, 100, 100, 150))

    blitPoint = [select_box_start[0], select_box_start[1]]
    mousePos = pygame.mouse.get_pos()

    if mousePos[0] < blitPoint[0] and mousePos[1] < blitPoint[1]:
        blitPoint[0] -= width
        blitPoint[1] -= height
    elif mousePos[0] < blitPoint[0]:
        blitPoint[0] -= width
    elif mousePos[1] < blitPoint[1]:
        blitPoint[1] -= height

    screen.blit(select_box, blitPoint)


class Button(pygame.sprite.Sprite):

    #colors should be a list of two colors, the first color is the background
    #color and the second color is the foreground (text) color.
    def __init__(self, colors, deminsions, text = None, image = None):
        super().__init__()

        self.image = None

        if text is not None:
            print("button with text")
            font = pygame.font.SysFont('', 16)
            self.image = pygame.Surface((deminsions[2], deminsions[3]))
            buttonpane = font.render(text, False, colordefs.WHITE)
            self.image.blit(buttonpane, (2, self.image.get_rect()[1]/2 - buttonpane.get_rect()[1]/2))
        if image is not None:
            print("button with image")
            self.image = image

        self.rect = self.image.get_rect()
        self.rect.move(deminsions[0], deminsions[1])
        print(deminsions)
        print(self.image.get_rect())
    

