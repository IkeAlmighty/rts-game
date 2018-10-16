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
                print("adj: ", adj[pos_i])

            #if the highest weighted position has value of 0.0, then break the loop:
            if max(adj) == 0.0:
                break

            #find the highest weighted position's (which should be the closest) index 
            highest_value_index = adj.index(max(adj))
            #add the position to the path.
            path.append(index_to_pos(highest_value_index, path_point))
            
            return path

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