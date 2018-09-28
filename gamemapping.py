import pygame, math, noise, colordefs, random, entities
from pygame.sprite import Sprite
from pygame import Rect
from entities import Entity

squ_width = 3

#set thresholds for terrain:
water = (0.1, 0.1999)
grassland = (0.2, 0.2999)
mountain_low = (0.3, 0.3999)
mountain_mid = (0.4, 0.5999)
mountain_high = (0.6, 0.7)

def within(val, tuple):
        return val >= tuple[0] and val <= tuple[1]

def generate_map(size):

    width = size[0]
    height = size[1]
    vmap = [0.0 for i in range(width*height)]

    #generate a noisy map:
    noiseYOff = random.randint(0, 100000)
    noiseXOff = random.randint(0, 100000)
    for x in range(0, width):
        for y in range(0, height):
            #the following math is kinda just spitballing (after perlin noise) to get height values I like
            value = noise.pnoise2(float((x + noiseXOff)/width), float((y + noiseYOff)/height), 6)
            value = math.sin(value) + 0.5
            if value < 0.0: value = 0.0
            if value > 1.0: value = 1.0
            
            #normalize all the values:
            if value < 0.5: value = water[0]
            elif value < 0.70: value = grassland[0]
            elif value < 0.75: value = mountain_low[0]
            elif value < 0.80: value = mountain_mid[0]
            else: value = mountain_high[0]
            
            #set the value
            vmap[x*height + y] = value

    return vmap

class GameMap(pygame.sprite.Sprite):

    def __init__(self, size):
        super().__init__()
        self.valMap = generate_map(size)
        
        self.width = size[0]*squ_width #width in pixels, not squares
        self.height = size[1]*squ_width

        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()

        self.__color()
        #base image and map don't have any entities on them. Used for erasing and entity from the main image and buffer image.
        self.baseImage = self.image.copy()
        self.baseMap = self.valMap.copy()
        
        self.__add_trees()

    def __color(self):
        vmapWidth = int(self.width/squ_width)
        vmapHeight = int(self.height/squ_width)

        for x in range(vmapWidth):
            for y in range(vmapHeight):
                
                value = self.valMap[x*vmapHeight + y]
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

                if value > 0.4 and value < 0.7 and within(self.valMap[x*vmapHeight + y], grassland) and random.randint(0, 10000) > 9996: 
                    entity = Entity("TREE", (x*squ_width, y*squ_width), random.randint(10, 50))
                    entities.add_entity(entity) #this works janky 
                    self.drawEntity(entity)
                elif value >= 0.7 and within(self.valMap[x*vmapHeight + y], grassland) and random.randint(0, 10000) > 9990: 
                    entity = Entity("TREE", (x*squ_width, y*squ_width), random.randint(20, 50))
                    entities.add_entity(entity) #this works janky 
                    self.drawEntity(entity)

    def is_traversable(self, pos):
        val = self.valMap[int(pos[0]/squ_width)*self.height + int(pos[1]/squ_width)]
        return within(val, grassland)

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
        Rect(entity.rect.x, entity.rect.y, entity.rect.width, entity.rect.height)

        #get a subsurface from the baseImage in the area of the entity to be erased:
        subsurface = self.baseImage.subsurface(Rect(dimensions[0], dimensions[1], dimensions[2], dimensions[3])).copy()

        #erase all entities within the area:
        self.image.blit(subsurface, (entity.rect.x, entity.rect.y))

        #re-blit all entities on the subsurface except the one to be erased:
        for e in entities.all_entities:
            if e.rect.colliderect(entity.rect):
                self.drawEntity(e)

