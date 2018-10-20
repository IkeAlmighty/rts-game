import pygame, preloading, math, random, pygame.time
from pygame.sprite import Sprite
from pygame import Surface, Rect
import gamemapping

all_entities = []

outdated_entities = []

def add_entity(entity):
    if entity not in all_entities:
        all_entities.append(entity)

def remove_entity(entity):
    if entity in all_entities:
        all_entities.remove(entity)

def draw_all(gamemap):
    for e in all_entities:
        gamemap.drawEntity(e)

def flag_for_update(entity):
    if entity not in outdated_entities:
        outdated_entities.append(entity)

def update():
    for entity in outdated_entities:
        entity.update()

class Entity(pygame.sprite.Sprite):

    #the entity location should be passed as the topleft of the entity, but is corrected to be
    #the graphical center when the entity is created.
    def __init__(self, image, location, speed = 0):
        super().__init__()
        self.image_not_selected = image
        self.image = self.image_not_selected

        self.options = []

        self.location = [int(location[0] - self.image.get_rect().width/2), int(location[1] - self.image.get_rect().height/2)]

        self.path = []
        self.speed = speed
        self.speed_tstamp = pygame.time.get_ticks()

        self.rect = self.image.get_rect()
        self.rect = self.rect.move(self.location[0], self.location[1])

        self.image_selected = Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.image_selected.fill((57, 57, 69, 100))
        self.image_selected.blit(self.image_not_selected, (0, 0))

        self.is_selected = False

    def set_selected(self, isSelected):
        self.is_selected = isSelected
        if isSelected:
            self.image = self.image_selected
        else:
            self.image = self.image_not_selected

    #returns a path to the location in the form 
    #of an array of points.
    def create_path(self, gamemap, dest):
        path = []

        #create the starting path point:
        path_point = (self.location[0], self.location[1])
        while(dest not in path):
            #Create an array rerpresenting the 8 
            #squares adjacent to the entity. Weight 
            #each square based on how close it is to the 
            #destination, zeroing out any that are not
            #traversable.
            adj = [0.0 for i in range(8)]
            def index_to_pos(index, center_pos):
                if index == 0: return (center_pos[0] - 1, center_pos[1] - 1)
                elif index == 1: return (center_pos[0], center_pos[1] - 1)
                elif index == 2: return (center_pos[0] + 1, center_pos[1] - 1)
                elif index == 3: return (center_pos[0] - 1, center_pos[1])
                elif index == 4: return (center_pos[0] + 1, center_pos[1])
                elif index == 5: return (center_pos[0] - 1, center_pos[1] + 1)
                elif index == 6: return (center_pos[0], center_pos[1] + 1)
                else: return (center_pos[0] + 1, center_pos[1] + 1)

            for pos_i in range(8):
                x = index_to_pos(pos_i, path_point)[0]
                y = index_to_pos(pos_i, path_point)[1]
                #trav is 0.0 when is_traversable returns False, 1.0 if True
                trav = float(self.can_traverse(gamemap, index_to_pos(adj[pos_i], path_point)))
                distance = math.sqrt((dest[0] - x)**2 + (dest[1] - y)**2) + 0.0000001
                adj[pos_i] += trav*(1.0/distance)

            #if the highest weighted position has value of 0.0, then break the loop:
            if max(adj) == 0.0:
                break

            #find the highest weighted position's (which should be the closest) index 
            highest_value_index = adj.index(max(adj))
            #add the position to the path.
            path.append(index_to_pos(highest_value_index, path_point))
            
            #set the path_point:
            path_point = path[len(path) - 1]

        #repeat until there are no traversable squares or
        #until path includes the destination.

        return path

    def set_dest(self, gamemap, dest):
        dest = (dest[0] - int(self.rect.width/2), dest[1] - int(self.rect.height/2))
        self.path = self.create_path(gamemap, dest)
    
    def update(self):
        if len(self.path) > 0:
            for i in range(0, self.speed):
                if len(self.path) > 0:
                    pos = self.path.pop(0)
                    self.move_to(pos)

    def can_traverse(self, gamemap, pos): 
        return True

    def move_to(self, position):
        self.rect = Rect(position[0], position[1], self.rect.width, self.rect.height)
        self.location = position

class Unit(Entity):

    def __init__(self, owner, location, unit_type_num):
        super().__init__(preloading.default_unit, location, 3)
        self.location = location
        self.owner = owner
        self.unit_type_id = unit_type_num

        self.options = ["Sacrifice", "Upgrade", "Rename"]

class Shipwreck(Entity):

    def __init__(self, location):
        super().__init__(preloading.ship_reck_image, location, 6)
        self.location = location

        self.options = ["DESTROY"]

class Tree(Entity):
    def __init__(self, location, value):
        image = None
        if random.randint(0, 100) > 60:
            image = preloading.tree_image
        else:
            image = preloading.tree_small_image
        super().__init__(image, location)

        self.value = value
        self.location = location

    def __str__(self):
        return "TREE: " + (self.location[0]*gamemapping.squ_width, self.location[1]*gamemapping.squ_width).__str__() + ", value: " + self.value.__str__()