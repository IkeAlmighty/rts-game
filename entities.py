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

def get_entity_type_image(entity_type, owner):
    
    image = preloading.default

    if entity_type == "TREE":
        if random.randint(0, 1) == 0:
            image = preloading.tree_image
        else: 
            image = preloading.tree_small_image
    elif entity_type == "UNIT":
        if owner == 0:
            image = preloading.default_unit
    elif entity_type == "RELIC":
        image = preloading.relic_image
    elif entity_type == "DOT":
        image = preloading.dot_image
    elif entity_type == "SHIP_WRECK":
        image = preloading.ship_reck_image

    return image

def match_options_to_type(entity_type):

    if entity_type == "TREE":
        return ["Chop", "Grow", "Eat", "Burn"]

    return [] #empty options list.

class Entity(pygame.sprite.Sprite):

    #the entity location should be passed as the topleft of the entity, but is corrected to be
    #the graphical center when the entity is created.
    def __init__(self, entity_type, location, value = 0, speed = 0, owner = 0):
        super().__init__()
        self.image_not_selected = get_entity_type_image(entity_type, owner)
        self.image = self.image_not_selected

        self.options = match_options_to_type(entity_type)

        self.value = value
        self.owner = owner

        self.location = [int(location[0] - self.image.get_rect().width/2), int(location[1] - self.image.get_rect().height/2)]

        self.path = []
        self.speed = speed
        self.speed_tstamp = pygame.time.get_ticks()

        self.entity_type = entity_type

        self.rect = self.image.get_rect()
        self.rect = self.rect.move(self.location[0], self.location[1])

        self.image_selected = Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.image_selected.fill((57, 57, 69, 100))
        self.image_selected.blit(self.image_not_selected, (0, 0))

        self.is_selected = False
    
    def get_owner(self):
        return self.owner

    def set_selected(self, isSelected):
        self.is_selected = isSelected
        if isSelected:
            self.image = self.image_selected
        else:
            self.image = self.image_not_selected

    #returns a path to the location in the form 
    #of an array of points.
    def create_path(self, gamemap, dest):

        visited = {}
        frontier = []

        start_point = (int(self.location[0]), int(self.location[1]))
        current_point = start_point
        visited.put(current_point, True)

        while current_point != dest:
            #add the neighbors of the current point to the frontier
            for x in range(current_point[0] - 1, current_point[0] + 1):
                for y in range(current_point[1] - 1, current_point[1] + 1):
                    if gamemap.get_land_type(gamemap.val_at((x, y))) != "water" and not visited[(x, y)]:
                        frontier.insert(0, (x, y)) 
            
            visited.put(current_point, True)
            current_point = frontier.pop()
        
        #now that we have visited points up to the destination,
        #work backwards from the destination through the 
        #visited list, taking the points closest to the start location:
        path = []
        while current_point != start_point:
            options = []
            for x in range(current_point[0] - 1, current_point[0] + 1):
                for y in range(current_point[1] - 1, current_point[1] + 1):
                    if visited[(x, y)]:
                        options.append(((x, y), math.sqrt((start_point[0] - x)**2 + (start_point[1] - y)**2))
            
            max_distance = 0
            final_option = None
            for option in options:
                if option[1] > max_distance:
                    final_option = option[0]
            
            path.append(final_option)

        return path

    def set_dest(self, gamemap, dest):
        dest = (dest[0] - int(self.rect.width/2), dest[1] - int(self.rect.height/2))
        self.path = self.create_path(gamemap, dest)
        # print(self.path)
    
    def update(self):
        if len(self.path) > 0:
            for i in range(0, self.speed):
                if len(self.path) > 0:
                    pos = self.path.pop(0)
                    self.move_to(pos)

    def can_traverse(self, gamemap, pos): 
        center = (int(pos[0] + self.rect.width/2), int(pos[1] + self.rect.height/2))
        return int(gamemap.get_land_type(gamemap.val_at(center)) == "grassland")


    def move_to(self, position):
        self.rect = Rect(position[0], position[1], self.rect.width, self.rect.height)
        self.location = position

    def __str__(self):
        return self.entity_type.__str__() + " val:(" + self.value.__str__() + ") pos:" + self.location.__str__()

    def __eq__(self, other):
        return isinstance(other, type(self)) and other.location[0] == self.location[0] and other.location[1] == self.location[1]

    def __ne__(self, other):
        return not other == self