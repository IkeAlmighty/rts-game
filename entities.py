#NOTES ON ENTITY VALUES IN THE VAL MAP:
# a value on the game value map follows: 0.abcdefg
# 'a' signifies the landtype. 1 = water, 2 = grassland, 3 = mountains
# 'b' signifies what general entity type is on the tile. 0 = None, 1 = building, 2 = unit
# 'c' signifies the owner of any object on the tile. 
# 'defg' signify the index number of the object in the entities.all_entities list.


import pygame, preloading
from pygame.sprite import Sprite

all_entities = []


#Returns the entity val map number with 0 as the landtype.
#This works real janky like with the value map so that
#both the value map and the entity list can updated at the 
#same time.
def add_entity(entity):
    valMapNum = 0.0
    index = len(all_entities) + 1
    valMapNum += float(entity.get_owner()) / 1000
    valMapNum += float(entity.get_structure_type()) / 100
    valMapNum += float(index) / 10000000

    all_entities.append(entity)

    return valMapNum

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

    return image

class Entity(pygame.sprite.Sprite):

    #the entity location should be passed as the topleft of the entity, but is corrected to be
    #the graphical center when the entity is created.
    def __init__(self, entity_type, location, value = 0, structure_type = 0, owner = 0):
        super().__init__()
        self.image = get_entity_type_image(entity_type, owner)
        self.value = value
        self.owner = owner

        self.location = (location[0] - self.image.get_rect().width/2, location[1] - self.image.get_rect().height/2)

        self.entity_type = entity_type

        self.structure_type = structure_type #TODO rename this

        self.rect = self.image.get_rect()
        self.rect = self.rect.move(self.location[0], self.location[1])
    
    def get_owner(self):
        return self.owner

    def get_structure_type(self):
        return self.structure_type

    def set_selected(self, isSelected):
        #TODO: implement the selection color change
        if isSelected:
            s = Surface((self.rect.width, self.rect.height))
        else:
            """"""
            


    def __str__(self):
        return self.entity_type.__str__() + " val:(" + self.value.__str__() + ") pos:" + self.location.__str__()

    def __eq__(self, other):
        return isinstance(other, type(self)) and other.location[0] == self.location[0] and other.location[1] == self.location[1]

    def __ne__(self, other):
        return not other == self