import pygame, os, sys, random
import broadcasting, network, gamemapping, colordefs, preloading, entities
from pygame import Rect
from gamemapping import GameMap
from pygame.sprite import Group
from entities import Entity

def main():

    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 0)
    pygame.init()

    import app
    import controls

    screen = pygame.display.set_mode((app.scr_width, app.scr_height))
    app.font = pygame.font.SysFont('', 16)

    app.init_gamemap()

    app.init_slot_buttons()

    unit = Entity("UNIT", (300, 300), value=10, speed=1)
    while not unit.can_traverse(app.gamemap, unit.location):
        if unit.location[0] > app.gamemap.width: unit.move_to((0, unit.location[1] + 1))
        else: unit.move_to((unit.location[0] + 1, unit.location[1]))
    print("unit location: ", unit.location, "traversable = ", unit.can_traverse(app.gamemap, unit.location))
    entities.add_entity(unit)
    app.gamemap.drawEntity(unit)

    relic = Entity("RELIC", (200, 100))
    entities.add_entity(relic)
    app.gamemap.drawEntity(relic)

    shipwreck = Entity("SHIP_WRECK", (300, 100))
    entities.add_entity(shipwreck)
    app.gamemap.drawEntity(shipwreck)

    clock = pygame.time.Clock()
    running = True

    #event loop:
    while(running):

        app.update_rel_mouse_pos()

        #consumes and stores the events in entities.events
        controls.update()

        #check for program quit events:
        if controls.key_released(pygame.K_ESCAPE):
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
                app.center_on_mouse_from_minimap()
        
        #toggle the unit/building slot buttons on when alt key is pressed:
        if controls.key_released(pygame.K_LALT) or controls.key_released(pygame.K_RALT):
            if app.slot_buttons == app.unit_slot_buttons:
                app.slot_buttons = app.building_slot_buttons
            else:
                app.slot_buttons = app.unit_slot_buttons

        #Map Scrolling:
        if not controls.locked:
            app.update_map_position()
        ##

        app.update_button_set_animation(app.unit_slot_buttons)
        app.update_button_set_animation(app.entity_options_buttons)

        #clear screen so that the UI and gamemap can be redrawn.
        screen.fill((0,0,0))

        screen.blit(app.gamemap.image, app.gamemap.rect.topleft)

        if controls.locked: #show the mini map if controls are locked
            app.draw_minimap(screen)
            app.gamemap.image.set_alpha(50)
        else:
            if app.gamemap.image.get_alpha() != 255:
                app.gamemap.image.set_alpha(255)
            app.slot_buttons.draw(screen) #draws every frame so that animations can properly happen
            if app.entity_options_buttons != None:
                app.entity_options_buttons.draw(screen)

        #display mouse position relative to the game map
        app.draw_mouse_pos_panel(screen)

        #test display on the wood resource icon:
        screen.blit(preloading.wood_resource_image, (app.scr_width - 200, 0))
        screen.blit(preloading.relic_resource_image, (app.scr_width - 120, 0))

        #do things with selected entities.
        if controls.mouse_clicked(0):
            app.selection = controls.get_selection(app.gamemap)
            
            #set up the entity option panel to reflect selection[0]:
            app.draw_info_panel(screen, app.selection)

            #outline transparent borders of entities that are selected:
            app.set_entities_selected(app.selection)
            

        # call update() method on outdated entities.
        app.update_outdated_entities()

        # set destination for all selected entities.   
        if controls.mouse_clicked(2):
            for entity in app.selection:
                entity.set_dest(app.gamemap, (app.rel_mouse_pos[0], app.rel_mouse_pos[1]))
                entities.flag_for_update(entity)

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
