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

    button = Button(None, (100, 100, 40, 30), text="button")
    buttonGroup = Group()
    buttonGroup.add(button)

    ###
    mapSize = (500, 500) #mapsize * squ_width is the pixel size (squ_width is defined in the mapping module)
    startTime = pygame.time.get_ticks()
    gameMap = GameMap(mapSize)
    bufferImage = gameMap.image.copy()
    print("generated ", mapSize[0]*mapSize[1], " pixel map in ", pygame.time.get_ticks() - startTime, " ms")
    ###

    entities.add_entity(Entity("UNIT", (100, 100)))

    clock = pygame.time.Clock()
    running = True

    def draw_screen():
        screen.fill((0,0,0))

        screen.blit(gameMap.image, gameMap.rect.topleft)

        #display mouse position relative to the game map
        rel_mouse_pos = [pygame.mouse.get_pos()[0] - gameMap.rect.x, pygame.mouse.get_pos()[1] - gameMap.rect.y]
        pos_pane = font.render(rel_mouse_pos.__str__(), False, colordefs.WHITE, colordefs.BLACK)
        screen.blit(pos_pane, (0, 0))

        buttonGroup.draw(screen)

        if controls.mouse_clicked(0):
            selection = controls.get_selection(gameMap)
            for entity in selection:
                gameMap.eraseEntity(entity)

        if pygame.mouse.get_pressed()[0]:
            controls.update_selection_box(screen)

        pygame.display.flip()
    

    #event loop:
    while(running):

        #update controls:
        controls.update()

        if controls.key_is_pressed(pygame.K_SPACE):
            if controls.locked == False:
                controls.locked = True
                bufferImage = gameMap.image.copy()
                miniWidth = int(gameMap.width*scr_height/gameMap.height)
                gameMap.image = pygame.transform.scale(gameMap.image, (miniWidth, scr_height))
                gameMap.rect.x = int(scr_width/2) - (miniWidth/2)
                gameMap.rect.y = 0
            elif controls.locked == True:
                controls.locked = False
                gameMap.image = bufferImage
                #TODO: set the x and y to center on the mouse, with the new res
                        

        if controls.key_is_pressed(pygame.K_q):
            running = False

        ####
        if not controls.locked:
            mouseX = pygame.mouse.get_pos()[0]
            mouseY = pygame.mouse.get_pos()[1]

            if mouseX < 5 and gameMap.rect.x < 500:
                gameMap.rect.x += controls.scrollspeed
                if controls.select_box_start != None:
                    controls.select_box_start[0] += controls.scrollspeed

            if mouseX > scr_width - 5 and gameMap.rect.x + gameMap.width > scr_width - 500:
                gameMap.rect.x -= controls.scrollspeed
                if controls.select_box_start != None:
                    controls.select_box_start[0] -= controls.scrollspeed

            if mouseY < 5 and gameMap.rect.y < 500:
                gameMap.rect.y += controls.scrollspeed
                if controls.select_box_start != None:
                    controls.select_box_start[1] += controls.scrollspeed

            if mouseY > scr_height - 5 and gameMap.rect.y + gameMap.height > scr_width - 500:
                gameMap.rect.y -= controls.scrollspeed
                if controls.select_box_start != None:
                    controls.select_box_start[1] -= controls.scrollspeed
        ####

        draw_screen()

        #mouse events need to be processed before this copy:
        controls.last_frame_mouse = pygame.mouse.get_pressed()

        clock.tick(60)

if __name__ == '__main__': main()
