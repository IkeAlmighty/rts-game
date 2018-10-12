import pygame, math, noise, colordefs, random, entities
from pygame.sprite import Sprite
from pygame import Rect
from entities import Entity

squ_width = 3

#set thresholds for terrain:
water = (0.0, 0.5)
grassland = (0.5, 0.7)
mountain_low = (0.7, 0.75)
mountain_mid = (0.75, 0.8)
mountain_high = (0.8, 1.1)

def within(val, tuple):
        return val >= tuple[0] and val < tuple[1]

#creates a noise map of values between 0.0 and 1.0
def create_noise_map(size, octaves, max_val):
    value_map = [0.0 for i in range(size[0]*size[1])]
    x_off = (random.randint(0, size[0]), random.randint(0, size[0]))
    y_off = (random.randint(0, size[1]), random.randint(0, size[0]))
    for x in range(size[0]):
        for y in range(size[1]):

            value = noise.pnoise2(
                float((x + x_off[0])/size[0]), 
                float((y + y_off[0])/size[1]), 
                octaves
            )
            
            value = (max_val/2)*math.sin(value) + 0.5
            if value > max_val: value = max_val
            if value < 0: value = 0

            value_map[x*size[1] + y] = value
            
    return value_map

class GameMap(pygame.sprite.Sprite):

    def __init__(self, size):
        super().__init__()
        self.value_map = create_noise_map(size, 5, 1.0)

        print(max(self.value_map))
        
        self.width = size[0]*squ_width #width in pixels, not squares
        self.height = size[1]*squ_width

        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()

        self.__color_image()
        #base image and map don't have any entities on them. Used for erasing and entity from the main image and buffer image.
        self.baseImage = self.image.copy()
        self.baseMap = self.value_map.copy()
        
        self.__add_trees()



    def __color_image(self):
        map_width = int(self.width/squ_width)
        map_height = int(self.height/squ_width)

        for x in range(map_width):
            for y in range(map_height):
                
                value = self.value_map[x*map_height + y]
                rect = Rect(x*squ_width, y*squ_width, squ_width, squ_width)
                
                if within(value, water):
                    self.image.fill(colordefs.WATER, rect)
                elif within(value, grassland):
                    self.image.fill(colordefs.LOWLAND, rect)
                elif within(value, mountain_low):
                    self.image.fill(colordefs.MOUNTAIN_LOW, rect)
                elif within(value, mountain_mid):
                    self.image.fill(colordefs.MOUNTAIN_MID, rect)
                elif within(value, mountain_high):
                    self.image.fill(colordefs.MOUNTAIN_HIGH, rect)
                else:
                    self.image.fill(colordefs.RED, rect)

    def __add_trees(self):
        vmapWidth = int(self.width/squ_width)
        vmapHeight = int(self.height/squ_width)

        noiseYOff = random.randint(0, 100000)
        noiseXOff = random.randint(0, 100000)

        for x in range(0, vmapWidth):
            for y in range(0, vmapHeight):
                value = noise.pnoise2(float((x + noiseXOff)/vmapWidth), float((y + noiseYOff)/vmapHeight), 4)
                value = math.sin(value) + 0.5
                if value < 0.0: value = 0.0
                if value > 1.0: value = 1.0

                if value > 0.4 and value < 0.7 and (within(self.value_map[x*vmapHeight + y], grassland) or within(self.value_map[x*vmapHeight + y], mountain_low)) and random.randint(0, 10000) > 9996: 
                    entity = Entity("TREE", (x*squ_width, y*squ_width), random.randint(10, 50))
                    entities.add_entity(entity) #this works janky 
                    self.drawEntity(entity)
                elif value >= 0.7 and within(self.value_map[x*vmapHeight + y], grassland) and random.randint(0, 10000) > 9990: 
                    entity = Entity("TREE", (x*squ_width, y*squ_width), random.randint(20, 50))
                    entities.add_entity(entity) #this works janky 
                    self.drawEntity(entity)

    def __is_valid_pos(self, pos):
        x = int(pos[0] / squ_width)
        y = int(pos[1] / squ_width)
        return x >= 0 and x < self.width/squ_width and y >= 0 and y < self.height/squ_width

    #returns the value number of a position denoted by pixels (not squares)
    def val_at(self, pos):
        if not self.__is_valid_pos(pos):
            return -1.0

        x = int(pos[0] / squ_width)
        y = int(pos[1] / squ_width)

        return self.value_map[x*int(self.height/squ_width) + y]

    def drawEntity(self, entity):
        self.image.blit(entity.image, (entity.rect.x, entity.rect.y))

    def eraseEntity(self, entity):

        def fit_to_map(dimensions):
            if dimensions[0] < 0: dimensions[0] = 0
            if dimensions[1] < 0: dimensions[1] = 0
            if dimensions[0] >= self.width: dimensions[0] = self.width - 1
            if dimensions[1] >= self.height: dimensions[1] = self.height - 1
            if dimensions[0] + dimensions[2] >= self.width: dimensions[2] = self.width - 1 - dimensions[0]
            if dimensions[1] + dimensions[3] >= self.height: dimensions[3] = self.height - 1 - dimensions[1]
        
        dimensions = [entity.rect.x, entity.rect.y, entity.rect.width, entity.rect.height]
        fit_to_map(dimensions)
        # Rect(entity.rect.x, entity.rect.y, entity.rect.width, entity.rect.height)

        #get a subsurface from the baseImage in the area of the entity to be erased:
        subsurface = self.baseImage.subsurface(Rect(dimensions[0], dimensions[1], dimensions[2], dimensions[3])).copy()

        #erase all entities within the area:
        self.image.blit(subsurface, (entity.rect.x, entity.rect.y))

        #re-blit all entities on the subsurface except the one to be erased:
        for e in entities.all_entities:
            if e.rect.colliderect(entity.rect) and e != entity:
                self.drawEntity(e)

