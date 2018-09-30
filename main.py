import pygame, os, sys, random
import broadcasting, network, gamemapping, colordefs, preloading, entities
from pygame import Rect
from gamemapping import GameMap
from pygame.sprite import Group
from entities import Entity

def main():

    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 0)
    pygame.init()

    scr_width = 800
    scr_height = 600

    import controls
    from controls import Button

    screen = pygame.display.set_mode((scr_width, scr_height))

    font = pygame.font.SysFont('', 16)

    unit_slot_bttns = Group()
    building_slot_bttns = Group()
    slot_buttons = unit_slot_bttns

    bttn_pos = [scr_width - 50, scr_height - 50]
    for i in range(0, 10):
        unit_text = "UNIT " + i.__str__()
        building_text = "BUILD " + i.__str__()

        unit_button = Button((bttn_pos[0], bttn_pos[1], 48, 48), text=unit_text)
        building_button = Button((bttn_pos[0], bttn_pos[1], 48, 48), text=building_text, colors = (colordefs.WHITE, colordefs.BROWN))

        bttn_pos[0] -= 50
        unit_slot_bttns.add(unit_button)
        building_slot_bttns.add(building_button)

    ###
    mapSize = (100, 100) #mapsize * squ_width is the pixel size (squ_width is defined in the mapping module)
    startTime = pygame.time.get_ticks()
    gamemap = GameMap(mapSize)
    print("generated ", mapSize[0]*mapSize[1], " block map in ", pygame.time.get_ticks() - startTime, " ms")
    ###

    unit_pos = (random.randint(0, gamemap.width - 1), random.randint(0, gamemap.height - 1))
    while not gamemap.is_traversable(unit_pos):
        unit_pos = (random.randint(0, gamemap.width - 1), random.randint(0, gamemap.height - 1))
    unit = Entity("UNIT", unit_pos)
    entities.add_entity(unit)
    gamemap.drawEntity(unit)
    print(unit.create_path(gamemap, (400, 200)))

    relic = Entity("RELIC", (200, 100))
    entities.add_entity(relic)
    gamemap.drawEntity(relic)

    clock = pygame.time.Clock()
    running = True

    #event loop:
    while(running):

        #consumes and stores the events in entities.events
        controls.update()

        #check for program quit events:
        if controls.key_released(pygame.K_q):
            running = False

        for event in controls.events:
            if event.type == pygame.QUIT:
                running = False
        
        #check status on control locking
        #space bar toggles control locking (and minimap display)
        if controls.key_released(pygame.K_SPACE):
            if controls.locked == False:
                controls.locked = True
            elif controls.locked == True:
                controls.locked = False
                #set the x and y to center on the mouse, with the new res
                miniWidth = int(gamemap.width*scr_height/gamemap.height)
                minimap_x = int(scr_width/2) - (miniWidth/2)
                
                rel_pos_minimap = (pygame.mouse.get_pos()[0] - minimap_x, pygame.mouse.get_pos()[1])
                minimap_size = (miniWidth, scr_height)

                x = rel_pos_minimap[0] * gamemap.width / minimap_size[0]
                y = rel_pos_minimap[1] * gamemap.height / minimap_size[1]

                gamemap.rect.x = -1*x + scr_width/2
                gamemap.rect.y = -1*y + scr_height/2
        
        #toggle the unit/building slot buttons on when alt key is pressed:
        if controls.key_released(pygame.K_LALT) or controls.key_released(pygame.K_RALT):
            if slot_buttons == unit_slot_bttns:
                slot_buttons = building_slot_bttns
            else:
                slot_buttons = unit_slot_bttns

        #MAP SCROLLING LOGIC:
        ####
        if not controls.locked:
            mouseX = pygame.mouse.get_pos()[0]
            mouseY = pygame.mouse.get_pos()[1]

            if mouseX < 5 and gamemap.rect.x < 500:
                gamemap.rect.x += controls.scrollspeed
                if controls.select_box_start != None:
                    controls.select_box_start[0] += controls.scrollspeed

            if mouseX > scr_width - 5 and gamemap.rect.x + gamemap.width > scr_width - 500:
                gamemap.rect.x -= controls.scrollspeed
                if controls.select_box_start != None:
                    controls.select_box_start[0] -= controls.scrollspeed

            if mouseY < 5 and gamemap.rect.y < 500:
                gamemap.rect.y += controls.scrollspeed
                if controls.select_box_start != None:
                    controls.select_box_start[1] += controls.scrollspeed

            if mouseY > scr_height - 5 and gamemap.rect.y + gamemap.height > scr_width - 500:
                gamemap.rect.y -= controls.scrollspeed
                if controls.select_box_start != None:
                    controls.select_box_start[1] -= controls.scrollspeed
        ####
        #END OF MAP SCROLLING LOGIC

        for button in slot_buttons:
            if button.rect.colliderect(Rect(pygame.mouse.get_pos()[0] - 1, pygame.mouse.get_pos()[1] - 1, 3, 3)):
                button.set_selected(True)
            else:
                button.set_selected(False)

        #clear screen so that the UI and gamemap can be redrawn.
        screen.fill((0,0,0))

        screen.blit(gamemap.image, gamemap.rect.topleft)

        if controls.locked: #show the mini map if controls are locked
            minimap = gamemap.image.copy() #the minimap is recreated each frame to capture entity movement.
            minimap.set_alpha(220)
            miniWidth = int(gamemap.width*scr_height/gamemap.height)
            minimap = pygame.transform.scale(minimap, (miniWidth, scr_height))
            x = int(scr_width/2) - (miniWidth/2)
            y = 0
            screen.blit(minimap, (x, y))
            gamemap.image.set_alpha(100)
        else:
            if gamemap.image.get_alpha() != 255:
                gamemap.image.set_alpha(255)
            slot_buttons.draw(screen) #draws every frame so that animations can properly happen

        #display mouse position relative to the game map
        rel_mouse_pos = [pygame.mouse.get_pos()[0] - gamemap.rect.x, pygame.mouse.get_pos()[1] - gamemap.rect.y]
        pos_pane = font.render(rel_mouse_pos.__str__(), False, colordefs.WHITE, colordefs.BLACK)
        screen.blit(pos_pane, (0, 0))

        #do things with selected entities.
        if controls.mouse_clicked(0):
            selection = controls.get_selection(gamemap)
            for entity in selection:
                entity.set_selected(True)
                gamemap.eraseEntity(entity)
                gamemap.drawEntity(entity)
            for entity in entities.all_entities:
                if entity not in selection and entity.is_selected:
                    entity.set_selected(False)
                    gamemap.eraseEntity(entity)
                    gamemap.drawEntity(entity)
                    

        #update the selection box graphic.
        if pygame.mouse.get_pressed()[0]:
            controls.update_selection_box(screen)

        #flip the display buffer and output everything to screen.
        pygame.display.flip()

        #mouse events need to be processed before this copy:
        controls.last_frame_mouse = pygame.mouse.get_pressed()

        clock.tick(60)
    
    #cleanup
    pygame.display.quit()
    pygame.quit()

if __name__ == '__main__': main()
