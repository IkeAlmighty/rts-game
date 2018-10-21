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