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
        self.base_image = image
        self.image = self.base_image.copy()

        self.options = []

        self.x_off = -1*self.image.get_rect().width/2
        self.y_off = -1*self.image.get_rect().height/2
        self.location = [int(location[0] + self.x_off), int(location[1] + self.y_off)]

        self.path = []
        self.speed = speed
        self.speed_tstamp = pygame.time.get_ticks()

        self.rect = self.image.get_rect()
        self.rect = self.rect.move(self.location[0], self.location[1])

        self.base_image_selected = Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.base_image_selected.fill((57, 57, 69, 100))
        self.base_image_selected.blit(self.base_image, (0, 0))

        self.image_selected = self.base_image_selected.copy()

        self.is_selected = False

    def set_selected(self, isSelected):
        print("selected!")
        self.is_selected = isSelected
        if isSelected:
            self.image = self.image_selected
        else:
            self.image = self.base_image

    def __find_traversable_point(self, start_point, gamemap):

        def neighbors(point):
            neighbors = []
            for x in range(-1, 2):
                for y in range(-1, 2):
                    if (x*gamemapping.squ_width, y*gamemapping.squ_width) != (0, 0) and gamemap.is_valid_pixel_pos((point[0] + x*gamemapping.squ_width, point[1] + y*gamemapping.squ_width)):
                        neighbors.append((point[0] + x*gamemapping.squ_width, point[1] + y*gamemapping.squ_width))
            return neighbors

        visited = {}
        frontier = []
        current_point = (int(start_point[0]), int(start_point[1]))

        frontier.append(current_point)

        while len(frontier) > 0:

            if self.can_traverse(current_point, gamemap):
                return current_point

            for neighbor in neighbors(current_point):
                if neighbor not in frontier and visited.get(neighbor) == None:
                    frontier.insert(0, neighbor)

            visited[current_point] = True
            current_point = frontier.pop()

        return current_point
            

    #returns a path to the location in the form 
    #of an array of points.
    def create_path(self, dest, gamemap):

        if not gamemap.is_valid_pixel_pos(dest):
            return []

        if not self.can_traverse(dest, gamemap):
            dest = self.__find_traversable_point(dest, gamemap)

        def neighbors(point):
            neighbors = []
            for x in range(-1, 2):
                for y in range(-1, 2):
                    if (x*gamemapping.squ_width, y*gamemapping.squ_width) != (0, 0) and gamemap.is_valid_pixel_pos((point[0] + x*gamemapping.squ_width, point[1] + y*gamemapping.squ_width)):
                        neighbors.append((point[0] + x*gamemapping.squ_width, point[1] + y*gamemapping.squ_width))
            return neighbors

        def heuristic(point, dest):
            return math.sqrt((point[0] - dest[0])**2 + (point[1] - dest[1])**2)

        def collide_squ_width(a, b):
            return a[0] >= b[0] and a[1] >= b[1] and a[0] <= b[0] + gamemapping.squ_width and a[1] <= b[1] + gamemapping.squ_width

        came_from = {}
        cost_so_far = {}
        start_point = (int(self.location[0]), int(self.location[1]))
        current_point = start_point

        came_from[start_point] = None
        cost_so_far[start_point] = 0

        frontier = PriorityQueue()
        frontier.put(start_point, 0)

        while not frontier.is_empty():
            # print("path finding...")
            current_point = frontier.pop()

            # print("current point = ", current_point, " dest = ", dest, " ", current_point == dest)

            if collide_squ_width(current_point, dest):
                break

            for neighbor in neighbors(current_point):
                # print("neighbor ", neighbor)
                new_cost = cost_so_far[current_point] + self.get_traverse_cost(neighbor, gamemap)
                if (neighbor not in cost_so_far.keys() or new_cost < cost_so_far[neighbor]) and self.can_traverse(neighbor, gamemap):
                    cost_so_far[neighbor] = new_cost
                    priority = cost_so_far[neighbor] + heuristic(neighbor, dest)
                    frontier.put(neighbor, priority)
                    came_from[neighbor] = current_point
            
            # rel_point = (gamemap.rect.x + current_point[0], gamemap.rect.y + current_point[1])
            # screen.set_at(rel_point, (0, 0, 0))
            # pygame.display.flip()

        if not collide_squ_width(current_point, dest):
            return []

        path = []
        while current_point != start_point:
            # print("path construction...")
            path.insert(0, current_point)
            current_point = came_from[current_point]            

        return path

    def set_dest(self, gamemap, dest):
        self.path = self.create_path(dest, gamemap)

    #returns the angle between two vectors
    def __get_theta(self, vec):
        mag = math.sqrt(vec[0]**2 + vec[1]**2)
        unit_vec = (vec[0]/mag, vec[1]/mag)

        offset = 45

        if unit_vec[0] == 0 and unit_vec[1] < 0:
            return offset

        if unit_vec[0] == 0 and unit_vec[1] > 0:
            return offset + 180

        if unit_vec[0] < 0 and unit_vec[1] == 0:
            return offset + 90

        if unit_vec[0] > 0 and unit_vec[1] == 0:
            return offset + 270

        if unit_vec[0] < 0 and unit_vec[1] < 0:
            return offset + 45

        if unit_vec[0] < 0 and unit_vec[1] > 0:
            return offset + 135

        if unit_vec[0] > 0 and unit_vec[1] > 0:
            return offset + 225

        if unit_vec[0] > 0 and unit_vec[1] < 0:
            return offset + 315   

        raise Exception("vec of (0,0) passed to entity.__get_theta(vec)")
    
    def update(self):
        if len(self.path) > 0:
            for i in range(0, self.speed):
                if len(self.path) > 0:
                    pos = self.path.pop(0)
                    #turn the ship image to face the direction it is moving:
                    # TODO: Make this work (with selected image as well)
                    vec = (pos[0] - self.location[0], pos[1] - self.location[1])
                    theta = self.__get_theta(vec)
                    print(theta)
                    self.image = pygame.transform.rotate(self.base_image, theta)
                    self.image_selected = pygame.transform.rotate(self.base_image_selected, theta)
                    self.rect = self.image.get_rect()
                    self.move_to(pos)

    def can_traverse(self, position, gamemap): 
        return gamemap.is_valid_pixel_pos(position)
    
    def get_traverse_cost(self, point, gamemap):
        return 1

    def move_to(self, position):
        self.rect = Rect(position[0] + self.x_off, position[1] + self.y_off, self.rect.width, self.rect.height)
        self.location = position

class Unit(Entity):

    def __init__(self, owner, location, unit_type_num):
        super().__init__(preloading.default_unit, location, 3)
        self.location = location
        self.owner = owner
        self.unit_type_id = unit_type_num

        self.options = ["Sacrifice", "Upgrade", "Rename"]

    def can_traverse(self, position, gamemap):
        land_type = gamemap.get_pixel_land_type(position)
        return land_type == "grassland" and gamemap.is_valid_pixel_pos(position)


class Shipwreck(Entity):

    def __init__(self, location):
        super().__init__(preloading.ship_wreck_image, location)
        self.location = location

        self.options = ["DESTROY"]

    def get_traverse_cost(self, dest_point, gamemap):
        land_type = gamemap.get_pixel_land_type(dest_point)
        if land_type == "water": return 1
        
        return 10

    def can_traverse(self, position, gamemap):
        return gamemap.get_pixel_land_type(position) == "water" and gamemap.is_valid_pixel_pos(position)

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

class Ship(Entity):

    def __init__(self, location, health=20):
        image = preloading.ship_image
        super().__init__(image, location, speed=1)
        self.health = health

    def can_traverse(self, position, gamemap):
        return gamemap.get_pixel_land_type(position) == "water"