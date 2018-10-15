import pygame
from pygame.sprite import Sprite
import colordefs

#pre loaded images:
tree_image = pygame.image.load("assets/tree_1.png")
tree_small_image = pygame.image.load("assets/tree.png")
relic_image = pygame.image.load("assets/artifacts/artifact_1.png")
default = pygame.image.load("assets/default.png")
default_unit = pygame.image.load("assets/default_unit.png")
wood_resource_image = pygame.image.load("assets/wood_small.png")
relic_resource_image = pygame.image.load("assets/artifact_small_4.png")
ship_reck_image = pygame.image.load("assets/ship_wreck_2.png")
dot_image = pygame.Surface((4, 4))