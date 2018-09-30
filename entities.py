import pygame, preloading, math
from pygame.sprite import Sprite
from pygame import Surface
import gamemapping

all_entities = []

def add_entity(entity):
    if entity not in all_entities:
        all_entities.append(entity)

def remove_entity(entity):
    if entity in all_entities:
        all_entities.remove(entity)

def draw_all(gamemap):
    for e in all_entities:
        gamemap.drawEntity(e)



def get_entity_type_image(entity_type, owner):
    
    image = preloading.default

    if entity_type == "TREE":
        image = preloading.tree_image
    elif entity_type == "UNIT":
        if owner == 0:
            image = preloading.default_unit
    elif entity_type == "RELIC":
        image = preloading.relic_image

    return image

class Entity(pygame.sprite.Sprite):

    #the entity location should be passed as the topleft of the entity, but is corrected to be
    #the graphical center when the entity is created.
    def __init__(self, entity_type, location, value = 0, structure_type = 0, owner = 0):
        super().__init__()
        self.image_not_selected = get_entity_type_image(entity_type, owner)
        self.image = self.image_not_selected

        self.value = value
        self.owner = owner

        self.location = [location[0] - self.image.get_rect().width/2, location[1] - self.image.get_rect().height/2]

        self.entity_type = entity_type

        self.structure_type = structure_type #TODO rename this

        self.rect = self.image.get_rect()
        self.rect = self.rect.move(self.location[0], self.location[1])

        self.image_selected = Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.image_selected.fill((57, 57, 69, 100))
        self.image_selected.blit(self.image_not_selected, (0, 0))

        self.is_selected = False
    
    def get_owner(self):
        return self.owner

    def get_structure_type(self):
        return self.structure_type

    def set_selected(self, isSelected):
        self.is_selected = isSelected
        if isSelected:
            self.image = self.image_selected
        else:
            self.image  =  self.image_not_selected

    #returns a path to the location in the form 
    #of an array of points.
    # TODO: make this work
    def create_path(self, gamemap, dest):
        path = []

        pos = [int(self.location[0]), int(self.location[1])]
        while pos != dest:
            possible_pos = []
            for x in range(int(pos[0] - 1), int(pos[0] + 1)):
                for y in range(int(pos[1] - 1), int(pos[1] + 1)):
                    print( gamemap.is_traversable((x, y)) and [x, y] != pos)
                    if gamemap.is_traversable((x, y)) and [x, y] != pos:
                        possible_pos.append((x, y))
            
            if len(possible_pos) == 0:
                print("0 possible points")
                return path

            closest_pos = possible_pos[0]
            closest_dist = math.sqrt((dest[0] - possible_pos[0][0])**2 + (dest[1] - possible_pos[0][1])**2)
            for p in possible_pos:
                distance = math.sqrt((dest[0] - p[0])**2 + (dest[1] - p[1])**2)
                if distance < closest_dist:
                    closest_pos = p
                    closest_dist = distance
            
            path.append(closest_pos)
            pos = closest_pos

        return path

    def __str__(self):
        return self.entity_type.__str__() + " val:(" + self.value.__str__() + ") pos:" + self.location.__str__()

    def __eq__(self, other):
        return isinstance(other, type(self)) and other.location[0] == self.location[0] and other.location[1] == self.location[1]

    def __ne__(self, other):
        return not other == self