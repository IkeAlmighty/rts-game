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

    return image

class Entity(pygame.sprite.Sprite):

    #the entity location should be passed as the topleft of the entity, but is corrected to be
    #the graphical center when the entity is created.
    def __init__(self, entity_type, location, value = 0, speed = 2, owner = 0):
        super().__init__()
        self.image_not_selected = get_entity_type_image(entity_type, owner)
        self.image = self.image_not_selected

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
    #of an array of points. Calls itself recursively 
    #with a waypoint if there are objects blocking the path.
    def create_path(self, gamemap, end_point):

        def in_range_of(num, range_of):
            return num > range_of - 1 and num < range_of + 1

        def get_simple_path(start_point, end_point):
            simple_path = []
            dx = end_point[0] - start_point[0]
            dy = end_point[1] - start_point[1]
            magnitude = math.sqrt(dx**2 + dy**2)
            search_vector = (dx/magnitude, dy/magnitude)

            current_point = [start_point[0], start_point[1]]

            while not (in_range_of(current_point[0], end_point[0]) and in_range_of(current_point[1], end_point[1])):
                current_point[0] += search_vector[0]
                current_point[1] += search_vector[1]
                simple_path.append(current_point.copy())
            
            return simple_path

        def get_waypoint_path(start_point, waypoint, end_point):
            waypoint_path = []
            subpath1 = get_simple_path(start_point, waypoint)
            subpath2 = get_simple_path(waypoint, end_point)
            for p in subpath1:
                waypoint_path.append(p)
            for p in subpath2:
                waypoint_path.append(p)
            return waypoint_path

        def get_combined_paths(paths):
            combined_path = []
            for path in paths:
                for point in path:
                    combined_path.append(point)
            return combined_path
        
        def get_unit_perp(vector):
            theta = math.atan(vector[1]/vector[0])
            theta += 90*math.pi/180
            return (math.cos(theta), math.sin(theta))

        start_point = (self.location[0], self.location[1])

        path = get_simple_path(start_point, end_point)

        possible_paths = []

        for point in path:
            if not self.can_traverse(point, gamemap):
                start_index = point.index()
                end_index = point.index() + 1
                while not end_index < len(simple_path) and self.can_traverse(path[end_index], gamemap):
                    end_index += 1
                center_index = int((start_index + end_index)/2)

                dx = path[end_index][0] - path[start_index][0]
                dy = path[end_index][1] - path[start_index][1]
                magnitude = math.sqrt(dx**2 + dy**2)
                search_vector = (dx/magnitude, dy/magnitude)
                search_vector = get_unit_perp(search_vector)
                

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

    def can_traverse(self, position, gamemap): 
        center = (int(position[0] + self.rect.width/2), int(position[1] + self.rect.height/2))
        return int(gamemapping.within(gamemap.val_at(center), gamemapping.grassland))


    def move_to(self, position):
        self.rect = Rect(position[0], position[1], self.rect.width, self.rect.height)
        self.location = position

    def __str__(self):
        return self.entity_type.__str__() + " val:(" + self.value.__str__() + ") pos:" + self.location.__str__()

    def __eq__(self, other):
        return isinstance(other, type(self)) and other.location[0] == self.location[0] and other.location[1] == self.location[1]

    def __ne__(self, other):
        return not other == self