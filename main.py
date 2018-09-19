import pygame, os, broadcasting, network, gamemapping, colordefs, preloading, entities
from gamemapping import GameMap
from pygame.sprite import Group
from entities import Entity

def main():

    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 0)

    scr_width = 800
    scr_height = 600

    pygame.init()

    import controls
    from controls import Button

    screen = pygame.display.set_mode((scr_width, scr_height))

    font = pygame.font.SysFont('', 16)

    buttonGroup = Group()
    unit_bttns = []
    bttn_pos = [scr_width - 50, scr_height - 50]
    for i in range(0, 10):
        text = "SLOT " + i.__str__()
        button = Button(None, (bttn_pos[0], bttn_pos[1], 48, 48), text=text)
        bttn_pos[0] -= 50
        buttonGroup.add(button)

    ###
    mapSize = (1000, 1000) #mapsize * squ_width is the pixel size (squ_width is defined in the mapping module)
    startTime = pygame.time.get_ticks()
    gamemap = GameMap(mapSize)
    print("generated ", mapSize[0]*mapSize[1], " block map in ", pygame.time.get_ticks() - startTime, " ms")
    ###

    unit = Entity("UNIT", (100, 100))
    entities.add_entity(unit)
    gamemap.drawEntity(unit)

    clock = pygame.time.Clock()
    running = True

    #event loop:
    while(running):

        #update controls:
        controls.update()

        if controls.key_released(pygame.K_SPACE):
            if controls.locked == False:
                controls.locked = True
            elif controls.locked == True:
                controls.locked = False
                #TODO: set the x and y to center on the mouse, with the new res

        if controls.key_released(pygame.K_q):
            running = False

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

        screen.fill((0,0,0))

        screen.blit(gamemap.image, gamemap.rect.topleft)

        if controls.locked: #show the mini map if controls are locked
            minimap = gamemap.image.copy()
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
            buttonGroup.draw(screen) #draws every frame so that animations can properly happen

        #display mouse position relative to the game map
        rel_mouse_pos = [pygame.mouse.get_pos()[0] - gamemap.rect.x, pygame.mouse.get_pos()[1] - gamemap.rect.y]
        pos_pane = font.render(rel_mouse_pos.__str__(), False, colordefs.WHITE, colordefs.BLACK)
        screen.blit(pos_pane, (0, 0))

        if controls.mouse_clicked(0):
            selection = controls.get_selection(gamemap)
            for entity in selection:
                gamemap.eraseEntity(entity)
                entities.remove_entity(entity)

        if pygame.mouse.get_pressed()[0]:
            controls.update_selection_box(screen)

        pygame.display.flip()

        #mouse events need to be processed before this copy:
        controls.last_frame_mouse = pygame.mouse.get_pressed()

        clock.tick(60)

if __name__ == '__main__': main()
