import pygame, math, entities, gamemapping, pygame.font, colordefs, preloading, pygame.time

events = []

__keyPresses = []

# keypresses are popped off the keypress log list
# a set time after they are inserted into it. The popping
# happens within controls.update() method.
__keypress_log = [] 
__keypress_log_tstamps = []

# same as the keypress log.
__keyrelease_log = []
__keyrelease_log_tstamps = []

last_update = pygame.time.get_ticks()

last_frame_mouse = pygame.mouse.get_pressed()

scrollspeed = 25

locked = False

select_box_start = None
blitPoint = None

select_box = None

def update():
    global events
    events = pygame.event.get()
    # update key presses and key releases
    for event in events:
        if event.type == pygame.KEYDOWN:
            add_key_press(event.key)
        elif event.type == pygame.KEYUP:
            remove_key_press(event.key)
    
    # keypress_log popping
    tstamp_current = pygame.time.get_ticks()
    for key in __keypress_log:
        t_index = __keypress_log.index(key)
        if tstamp_current - __keypress_log_tstamps[t_index] > 10:
            __keypress_log.remove(key)
            __keypress_log_tstamps.pop(t_index)

    # keyrelease_log popping
    tstamp_current = pygame.time.get_ticks()
    for key in __keyrelease_log:
        t_index = __keyrelease_log.index(key)
        if tstamp_current - __keyrelease_log_tstamps[t_index] > 10:
            __keyrelease_log.remove(key)
            __keyrelease_log_tstamps.pop(t_index)

def add_key_press(key):
    if key not in __keyPresses:
        __keyPresses.append(key)
    __keypress_log.insert(0, key)
    __keypress_log_tstamps.insert(0, pygame.time.get_ticks())

def remove_key_press(key):
    if key in __keyPresses:
        __keyPresses.remove(key)
    __keyrelease_log.insert(0, key)
    __keyrelease_log_tstamps.insert(0, pygame.time.get_ticks())

def key_pressed(key):
    return key in __keyPresses 

def key_released(key):
    return key in __keyrelease_log

def mouse_clicked(button_index):
    return not pygame.mouse.get_pressed()[button_index] and last_frame_mouse[button_index] == True

def mouse_wheel_rolled_up():
    global events
    for event in events:
        print(event)
        if event == pygame.MOUSEBUTTONDOWN and event.button == 4:
            return True
    
    return False

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

    #TODO: remove the following prints for product version.
    print("selection:")
    for e in selection:
        print(e)
    return selection
    #####
    

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

    #colors should be a list of two colors, the first color is the foreground
    #color and the second color is the background (text) color.
    def __init__(self, deminsions, ident = None, text = None, image = None, colors = (colordefs.WHITE, colordefs.GREY_BLUE)):
        super().__init__()

        self.deminsions = deminsions

        self.image = None
        if ident == None and text != None:
            self.id = text
        else:
            self.id = ident

        if text is not None:
            font = pygame.font.SysFont('', 16)
            self.image_not_selected = pygame.Surface((deminsions[2], deminsions[3]))
            self.image_not_selected.fill(colors[1])
            buttonpane = font.render(text, False, colors[0])
            self.image_not_selected.blit(buttonpane, (5, self.image_not_selected.get_rect()[3]/2 - buttonpane.get_rect()[3]/2))
        if image is not None:
            print("button with image")
            self.image_not_selected = image

        self.image = self.image_not_selected
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(deminsions[0], deminsions[1])

        self.image_selected = pygame.Surface((deminsions[2], deminsions[3]))
        salpha = pygame.Surface((deminsions[2], deminsions[3]))
        salpha.fill(colordefs.WHITE)
        salpha.set_alpha(90)
        self.image_selected.blit(self.image_not_selected, (0, 0))
        self.image_selected.blit(salpha, (0, 0))

    def get_id(self):
        return self.id

    def set_selected(self, is_selected):
        self.is_selected = is_selected

        if is_selected:
            self.image = self.image_selected
        else:
            self.image = self.image_not_selected

