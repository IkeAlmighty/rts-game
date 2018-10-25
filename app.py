import pygame, pygame.sprite, os, sys, random
import broadcasting, network, gamemapping, colordefs, preloading, entities, controls
from entities import Entity

scr_width = 800
scr_height = 600

map_size = (300, 300)

font = None

gamemap = None

unit_slot_buttons = None
building_slot_buttons = None
slot_buttons = None

entity_options_buttons = None

rel_mouse_pos = None

selection = []

def init_gamemap():
    global gamemap
    global map_size
    start_time = pygame.time.get_ticks()
    gamemap = gamemapping.GameMap(map_size,0.2, 0.3, 0.5)
    print("generated ", map_size[0]*map_size[1], " block map in ", pygame.time.get_ticks() - start_time, " ms")

def init_slot_buttons():
    global unit_slot_buttons
    global building_slot_buttons
    global slot_buttons

    unit_slot_buttons = pygame.sprite.Group()
    building_slot_buttons = pygame.sprite.Group()
    slot_buttons = unit_slot_buttons

    bttn_pos = [scr_width - 50, scr_height - 50]
    for i in range(0, 10):
        unit_text = "UNIT " + i.__str__()
        building_text = "BUILD " + i.__str__()

        unit_button = controls.Button((bttn_pos[0], bttn_pos[1], 48, 48), text=unit_text)
        building_button = controls.Button((bttn_pos[0], bttn_pos[1], 48, 48), text=building_text, colors = (colordefs.WHITE, colordefs.BROWN))

        bttn_pos[0] -= 50
        unit_slot_buttons.add(unit_button)
        building_slot_buttons.add(building_button)

def center_on_mouse_from_minimap():
    global gamemap
    global rel_mouse_pos

    #find the width of the minimap
    mini_width = int(gamemap.width*scr_height/gamemap.height)
    minimap_x = int(scr_width/2) - (mini_width/2)
    
    rel_pos_minimap = (pygame.mouse.get_pos()[0] - minimap_x, pygame.mouse.get_pos()[1])
    minimap_size = (mini_width, scr_height)

    x = rel_pos_minimap[0] * gamemap.width / minimap_size[0]
    y = rel_pos_minimap[1] * gamemap.height / minimap_size[1]

    gamemap.rect.x = -1*x + scr_width/2
    gamemap.rect.y = -1*y + scr_height/2

def update_rel_mouse_pos():
    global rel_mouse_pos
    
    rel_mouse_pos = [pygame.mouse.get_pos()[0] - gamemap.rect.x, pygame.mouse.get_pos()[1] - gamemap.rect.y]

def update_map_position():
    global gamemap
    global scr_width
    global scr_height

    mouse_x = pygame.mouse.get_pos()[0]
    mouse_y = pygame.mouse.get_pos()[1]

    if mouse_x < 5 and gamemap.rect.x < 500:
        gamemap.rect.x += controls.scrollspeed
        if controls.select_box_start != None:
            controls.select_box_start[0] += controls.scrollspeed

    if mouse_x > scr_width - 5 and gamemap.rect.x + gamemap.width > scr_width - 500:
        gamemap.rect.x -= controls.scrollspeed
        if controls.select_box_start != None:
            controls.select_box_start[0] -= controls.scrollspeed

    if mouse_y < 5 and gamemap.rect.y < 500:
        gamemap.rect.y += controls.scrollspeed
        if controls.select_box_start != None:
            controls.select_box_start[1] += controls.scrollspeed

    if mouse_y > scr_height - 5 and gamemap.rect.y + gamemap.height > scr_width - 500:
        gamemap.rect.y -= controls.scrollspeed
        if controls.select_box_start != None:
            controls.select_box_start[1] -= controls.scrollspeed

def update_button_set_animation(button_set):
    if button_set == None: return
    for button in button_set:
        rect = pygame.Rect(pygame.mouse.get_pos()[0] - 1, pygame.mouse.get_pos()[1] - 1, 3, 3)
        if button.rect.colliderect(rect):
            button.set_selected(True)
        else:
            button.set_selected(False)

def draw_minimap(screen):
    global gamemap
    global scr_width
    global scr_height

    minimap = gamemap.image.copy() #the minimap is recreated call to capture entity movement.
    minimap.set_alpha(220)
    mini_width = int(gamemap.width*scr_height/gamemap.height)
    minimap = pygame.transform.scale(minimap, (mini_width, scr_height))
    x = int(scr_width/2) - (mini_width/2)
    y = 0
    screen.blit(minimap, (x, y))

def draw_mouse_pos_panel(screen):
    global gamemap
    global font

    pos_pane = font.render(rel_mouse_pos.__str__(), False, colordefs.WHITE, colordefs.BLACK)
    screen.blit(pos_pane, (0, 0))

def draw_info_panel(screen, selection):
    global entity_options_buttons
    global scr_height

    entity_options_buttons = pygame.sprite.Group()
    x = 0
    y = scr_height - 50
    if len(selection) > 0:
        for option in selection[0].options:
            if x >= 150:
                x = 0
                y -= 50
            button = controls.Button((x, y, 48, 48), ident=option, text=option, colors=(colordefs.WHITE, colordefs.BLACK))
            entity_options_buttons.add(button)
            x += 50

def set_entities_selected(selection):
    global gamemap

    for entity in selection:
        entity.set_selected(True)
        gamemap.eraseEntity(entity)
        gamemap.drawEntity(entity)
    for entity in entities.all_entities:
        if entity not in selection and entity.is_selected:
            entity.set_selected(False)
            gamemap.eraseEntity(entity)
            gamemap.drawEntity(entity)

def update_outdated_entities():
    global gamemap

    for e in entities.outdated_entities:
        gamemap.eraseEntity(e)
    entities.update()
    for e in entities.outdated_entities:
        gamemap.drawEntity(e)
        if len(e.path) == 0:
            entities.outdated_entities.remove(e)

def draw_gamemap_value(screen):
    global rel_mouse_pos
    global gamemap

    land_type = None
    try:
        land_type = gamemap.get_pixel_land_type(rel_mouse_pos)
    except Exception: 
        land_type = "None"

    terrain_pane = font.render(land_type, True, colordefs.WHITE, colordefs.BLACK)

    screen.blit(terrain_pane, (100, 0))