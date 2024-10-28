import pygame.image
from pygame.math import Vector2
import random


def load_sprite(name, with_alpha=True):
    """Helper method to load img of a sprite.
            :param name: name of the sprite img.
            :param with_alpha: bool - enables transparent colors.
            :return: bool - Placement of score (x), using backspaces
            """
    img_path = f'assets/sprites/{name}.png'
    loaded_sprite = pygame.image.load(img_path)
    if with_alpha:
        # Convert_alpha is to handle transparent color but is a bit slower
        return loaded_sprite.convert_alpha()
    else:
        return loaded_sprite.convert()


def get_random_position(surface):
    """Helper method to give a random position inside the screen borders.
            :param surface: screen.
            :return: Vector position.
            """
    return Vector2(
        random.randrange(70, surface.get_width()) - 70,
        random.randrange(70, surface.get_height() - 70)
    )


def menu_get_random_position(surface):
    """Helper method to give a random position inside the screen borders in the menu.
            :param surface: screen.
            :return: Vector position.
            """
    return Vector2(random.randrange(100, surface.get_width() - 100), random.randrange(100, surface.get_height() // 2))


def get_random_velocity(min_speed, max_speed):
    """Helper method to give a random speed at a random direction.
            :param min_speed: minimum speed.
            :param max_speed: maximum speed.
            :return: Vector speed .
            """
    speed = random.randint(min_speed, max_speed)
    angle = random.randint(0, 360)
    # The random angle changes the direction of th speed and the x / y are not really important to have a value over 0.
    return Vector2(0, speed).rotate(angle)

