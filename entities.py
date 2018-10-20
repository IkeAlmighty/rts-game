import pygame, preloading, math, random, pygame.time, datastructures
from datastructures import PriorityQueue
from pygame.sprite import Sprite
from pygame import Surface, Rect
import gamemapping

all_entities = []

outdated_entities = []

screen = None

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

        global screen

        def collide_with(point_a, point_b):
            return point_a[0] <= point_b[0] + gamemapping.squ_width and point_a[0] > point_b[0] and point_a[1] <= point_b[1] + gamemapping.squ_width and point_a[1] > point_b[1]
        
        def neighbors(point):
            return [
                (point[0] - gamemapping.squ_width, point[1]),
                (point[0] + gamemapping.squ_width, point[1]),
                (point[0], point[1] + gamemapping.squ_width), 
                (point[0], point[1] - gamemapping.squ_width)
            ]
        
        def heuristic(point_a, point_b):
            return abs(point_a[0] - point_b[0]) + abs(point_a[1] - point_b[1])


        start_point = (int(self.location[0]), int(self.location[1]))
        current_point = start_point

        visited_by = {}
        cost_so_far = {}
        frontier = datastructures.PriorityQueue()

        cost_so_far[start_point] = 0
        visited_by[start_point] = None

        while not collide_with(current_point, dest) and not frontier.is_empty():
            print(frontier)

            for neighbor in neighbors(current_point):
                new_cost = cost_so_far[current_point] + self.get_traverse_cost(gamemap, neighbor)
                if neighbor not in cost_so_far or new_cost < cost_so_far[current_point]:
                    cost_so_far[neighbor] = new_cost
                    frontier.put(neighbor, new_cost)
                    visited_by[neighbor] = current_point
                    
            current_point = frontier.pop()

        path = []
        while current_point != None and not collide_with(current_point, start_point):
            path.insert(0, current_point)
            current_point = visited_by[current_point]

        print(path)

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

        try:
            if self.entity_type == "UNIT":
                return int(gamemap.get_land_type(gamemap.val_at(center)) == "grassland")
            else:
                return int(gamemap.get_land_type(gamemap.val_at(center)) == "water")
        except: return False

    def get_traverse_cost(self, gamemap, point):
        if not self.can_traverse(gamemap, point):
            return 1000 #returns a super high number if it can't traverse the region at all.
        
        #todo make costs for all entity types

        return 1

    def move_to(self, position):
        self.rect = Rect(position[0], position[1], self.rect.width, self.rect.height)
        self.location = position

    def __str__(self):
        return self.entity_type.__str__() + " val:(" + self.value.__str__() + ") pos:" + self.location.__str__()

    def __eq__(self, other):
        return isinstance(other, type(self)) and other.location[0] == self.location[0] and other.location[1] == self.location[1]

    def __ne__(self, other):
        return not other == self