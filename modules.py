import random

import pygame
from pygame.math import Vector2
from pygame.mixer import Sound
from pygame.transform import rotozoom
from pygame import font, mixer

from utils import load_sprite, get_random_velocity

# Variables
UP = Vector2(0, -1)
asteroid_imgs = ['asteroid', 'asteroid1', 'asteroid2']


class GameObject:
    """ This class is the basic model for sprites. Enables to draw them, move inside the game screen and check if
    they collide with anything else.
            :param position: vector.
            :param sprite: image of the sprite.
            :param vel: vector - initial speed.
            """

    def __init__(self, position, sprite, vel):
        self.position = Vector2(position)  # if only one number is given, will be used as double - (position, position)
        self.sprite = sprite
        self.radius = sprite.get_width() / 2
        self.velocity = Vector2(vel)
        self.acceleration = Vector2(0, 0)

    def draw(self, surface):
        """Draws the sprite on the screen.
                :param surface: screen it draws on
                """
        blit_position = self.position - Vector2(self.radius)
        surface.blit(self.sprite, blit_position)

    def move(self):
        """Moves the sprite inside the screen according to its speed.
                """
        self.position = self.position + self.velocity

    def collides_with(self, other_obj):
        """Helper method to check if two sprites collide.
                :param other_obj: the obj you check the distance to
                :return: bool - Placement of score (x), using backspaces
                """
        distance = self.position.distance_to(other_obj.position)
        return distance < self.radius + other_obj.radius


class Spaceship(GameObject):
    """ This class is a subclass. Adds unique mechanics for the spaceship - movement control, shoot and 'death'.
                :param position: vector.
                :param shield: bool - depends on game mode easy/hard.
                :param create_bullet_callback: type Class, Bullet
                :param create_explosion_callback: type Class, Explosion
                :param spaceship_img: loads spaceship image.
                """
    MANEUVERABILITY = 5  # How fast can rotate - represents the angle change with each frame
    ACCELERATION = 0.2  # How fast the spaceship gets quicker
    FRICTION = -0.015  # Deceleration when no movement.
    MAX_SPEED = 11
    BULLET_SPEED = 9.5
    bullet_vel = 0

    def __init__(self, position, shield, create_bullet_callback, create_explosion_callback, spaceship_img):
        self.sprite = rotozoom(load_sprite(spaceship_img), 0, 0.07)
        self.direction = Vector2(UP)  # Initially the same as UP but will be modified (Makes a copy of UP)
        self.create_bullet_callback = create_bullet_callback
        self.create_explosion_callback = create_explosion_callback
        self.shield = shield
        super().__init__(position, self.sprite, vel=Vector2(0))

    def rotate(self, clockwise=True):
        """Spaceship rotation using angle change (left/right clockwise)
                :param clockwise: bool - according to left/right arrows.
                """
        if clockwise:
            angle = self.MANEUVERABILITY
        else:
            angle = self.MANEUVERABILITY * -1
        self.direction.rotate_ip(angle)  # This changes the angle of the vector

    def __acceleration_change(self):
        """Spaceship rotation using angle change (left/right clockwise).
                """
        self.velocity += self.direction * self.ACCELERATION
        self.velocity = Vector2(self.velocity)

        # Acceleration change to create smooth and easy movement.
        if self.velocity.length() < 0.5:
            self.velocity += self.direction * self.ACCELERATION * 2

        elif 9.5 < self.velocity.length() < self.MAX_SPEED:
            self.velocity += self.direction * (self.ACCELERATION * 0.8)

        elif self.velocity.length() >= self.MAX_SPEED:
            self.velocity.scale_to_length(self.MAX_SPEED)

    def accelerate(self):
        """Method to accelerate the spaceship.
                """
        self.__acceleration_change()

    def friction(self):
        """Slows down the spaceship when it doesn't move (deceleration).
                """
        self.velocity += Vector2(self.velocity) * self.FRICTION

    def spaceship_bounce(self, surface):
        """Constrains the ship from going out of screen.
                :param surface: the screen (background).
                """
        x, y = self.velocity
        w, h = surface.get_size()
        if self.position.x >= w:
            self.velocity = (-5, y)
        if self.position.y >= h:
            self.velocity = (x, -5)
        if self.position.x <= 0:
            self.velocity = (5, y)
        if self.position.y <= 0:
            self.velocity = (x, 5)

    def shoot(self, powerup):
        """Spaceship rotation using angle change (left/right clockwise)
                :param powerup: bool - checks if powerup was taken.
                """
        # Bullet speed mechanic to make sure it doesn't go too fast or too slow because is based on the ship's movement.
        mini = self.direction.copy()
        self.velocity = Vector2(self.velocity)

        if 0 <= self.velocity.length() <= 3:
            mini.scale_to_length(6)
            bullet_vel = mini * 1.2 + self.velocity
            if bullet_vel.length() < 5.5:
                mini.scale_to_length(7)
                bullet_vel = mini * 1.2 + self.velocity

        elif 3 < self.velocity.length() <= 6:
            mini.scale_to_length(5.5)
            bullet_vel = mini + self.velocity
            if bullet_vel.length() < 5:
                mini.scale_to_length(7)
                bullet_vel = mini * 1.4 + self.velocity

        elif 6 < self.velocity.length() <= 10:
            mini.scale_to_length(4)
            bullet_vel = mini + self.velocity

        elif 10 < self.velocity.length():
            mini.scale_to_length(3)
            bullet_vel = mini + self.velocity

        else:
            bullet_vel = self.direction * 3 + self.velocity

        if bullet_vel.length() < self.velocity.length():

            if bullet_vel.length() <= 5.5:
                if bullet_vel.length() > 6:
                    mini.scale_to_length(7)
                    bullet_vel = (mini * 1.8 + self.velocity)
                else:
                    mini.scale_to_length(8.5)
                    bullet_vel = (mini * 1.6 + self.velocity)
            elif 5.5 < bullet_vel.length() <= 8:
                mini.scale_to_length(6)
                bullet_vel = (mini * 1.8 + self.velocity)

            elif bullet_vel.length() > 8:
                mini.scale_to_length(5)
                bullet_vel = (mini * 1.8 + self.velocity)

            if bullet_vel.length() < 4.6:
                mini.scale_to_length(10)
                bullet_vel = (mini * 1.9 + self.velocity)

            elif bullet_vel.length() > 8.5:
                mini.scale_to_length(6)
                bullet_vel = (mini * 1.5 + self.velocity)

        # When powered up - changes bullet to red
        if powerup:
            bullet = Bullet(self.position, rotozoom(load_sprite('bullet1'), 1, 0.2), bullet_vel, True)
        else:
            bullet = Bullet(self.position, load_sprite('bullet'), bullet_vel)
        Sounds().shoot_sound()
        self.bullet_vel = bullet_vel
        self.create_bullet_callback(bullet)  # Equals to self.bullets.append(bullet)

    def bullet_speed(self):
        """Spaceship rotation using angle change (left/right clockwise)
                :return: int - bullet speed length.
                """
        return self.bullet_vel.length()

    def explosion(self):
        """Handles the 'death' of the spaceship using explosion class.
                """
        explosion_icon = rotozoom(load_sprite("explosion"), 0, 0.15)
        explosion = Explosion(self.position, explosion_icon)
        self.create_explosion_callback(explosion)

    def draw(self, surface):
        """Handles the change of angle to rotate the image of the spaceship, adds shield if easy mode and draws the ship
                :param surface: the screen.
                """
        angle = self.direction.angle_to(UP)  # Calculates the angle to a given vector
        rotated_surface = rotozoom(self.sprite, angle, 1.0)  # 1.0 same scale # This rotates the object
        rotated_surface_size = Vector2(rotated_surface.get_size())
        self.spaceship_bounce(surface)
        blit_position = self.position - rotated_surface_size * 0.5  # Takes the centre of the rect as the position
        if self.shield:
            pygame.draw.circle(surface, color='mediumvioletred', center=self.position,
                               radius=(self.radius + 8), width=5)
        surface.blit(rotated_surface, blit_position)


class Asteroid(GameObject):
    """ This class is a subclass. Adds unique mechanics for the asteroid - movement, split and menu/game mechanics.
            :param position: vector.
            :param create_asteroid_callback: type Class, Asteroid.
            :param size: int - size of Asteroid.
            :param menu_state: bool - menu on/off.
            """
    def __init__(self, position, create_asteroid_callback, size=3, menu_state=True):
        self.create_asteroid_callback = create_asteroid_callback
        self.size = size
        self.menu_state = menu_state
        self.ast_direction = Vector2(UP)
        self.rotation_direction = random.choice([-1, 1])
        self.rotation_speed = random.choice([0.3, 0.4])
        size_scale = {
            3: 2.1,
            2: 1.2,
            1: 0.7
        }
        scale = size_scale[size]
        self.sprite = rotozoom(load_sprite(random.choice(asteroid_imgs)), angle=0, scale=scale)
        # A method to scale the rect
        super().__init__(position, self.sprite, vel=get_random_velocity(4, 6))
        # The scale is passed before "super" in order to calculate radius and other stuff

    def split(self):
        """Handles the split of the asteroid mechanic.
                """
        if self.size > 1:
            for a in range(2):
                asteroid = Asteroid(self.position, self.create_asteroid_callback, self.size - 1)
                self.create_asteroid_callback(
                    asteroid)  # This "creates" the option for splitting the asteroid in the original one.
                # When .split() is used, the asteroid is appended to the game_objects based on the asteroid before.

    def change_menu_state(self, state):
        """Handles the state of menu, if on or off, in order to change the movement to whole screen and not half.
                :param state: bool.
                """
        self.menu_state = state
        return self.menu_state

    def asteroid_bounce(self, surface):
        """Spaceship rotation using angle change (left/right clockwise)
                        :param surface: screen.
                        """
        x, y = self.velocity
        # In order to deal with different radius due to different sizes, the border is changed
        if self.size == 3:
            w = surface.get_width() - 50
            w_o = 50
            h = surface.get_height() - 50
            y_o = 50

        elif self.size == 2:
            w = surface.get_width() - 35
            w_o = 35
            h = surface.get_height() - 35
            y_o = 35

        else:
            w = surface.get_width() - 25
            w_o = 25
            h = surface.get_height() - 25
            y_o = 25

        if self.position.x > w:
            self.position.x = w - 5
            self.velocity = (-x, y)
        if self.position.x < w_o:
            self.position.x = w_o + 5
            self.velocity = (-x, y)  # Needs to receive reverse current speed
        if self.position.y < y_o:
            self.position.y = y_o + 5
            self.velocity = (x, -y)
        if self.menu_state is False:
            if self.position.y > h:
                self.position.y = h - 5
                self.velocity = (x, -y)
        elif self.menu_state:
            if self.position.y > (h + 50) / 2:
                self.velocity = (x, -y)

    def random_rotation(self):
        """rotates randomly the asteroids.
                """
        self.ast_direction.rotate_ip(self.rotation_direction * self.rotation_speed)

    def draw(self, surface):
        """Handles the drawing of the asteroids according to movement mechanics.
                :param surface: screen,
                """
        self.asteroid_bounce(surface)
        angle = self.ast_direction.angle_to(UP)
        rotated_surface = rotozoom(self.sprite, angle, 1.0)  # 1.0 same scale # This rotates the object
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size * 0.5  # Takes the centre of the rect as the position
        surface.blit(rotated_surface, blit_position)


class Bullet(GameObject):
    """ This class is a subclass. Adds the bullet sprite.
        :param position: vector.
        :param bullet: sprite, bullet image.
        :param vel: Vector - speed ot the bullet.
        :param powerup: bool - powered up or not.
    """
    def __init__(self, position, bullet, vel, powerup=False):
        super().__init__(position, bullet, vel)
        self.powerup = powerup
        self.bullet = bullet


class Explosion(GameObject):
    """ This class is a subclass. Adds the explosion sprite.
        :param position: vector.
        :param sprite: the explosion image.
        """
    def __init__(self, position, sprite):
        super().__init__(position, sprite, 0)


class BulletPowerUp(GameObject):
    """ This class is a subclass. Adds the 'more bullets' powerup sprite.
            :param position: vector.
        """
    def __init__(self, position):
        self.sprite = rotozoom(load_sprite("bullets"), 0, 0.1)
        super().__init__(position, self.sprite, 0)

    def powerup(self):
        """A method to return the image of power up.
                :return: the image of power up.
                """
        return self.sprite


class SlowMotionPowerUp(GameObject):
    """ This class is a subclass. Adds the 'slow motion' powerup sprite.
            :param position: vector.
        """
    def __init__(self, position):
        self.sprite = rotozoom(load_sprite("slow_motion"), 0, 0.1)
        super().__init__(position, self.sprite, 0)

    def powerup(self):
        """A method to return the image of power up.
                :return: the image of the power up.
                """
        return self.sprite


class Text:
    """ This class enables the creation of text and positioning it.
            :param surface: screen.
            :param font_style: from pygame.
        """
    def __init__(self, surface, font_style):
        font.init()
        self.surface = surface
        self.font = font_style
    
    def show_text(self, text, color, position=None, center=True):
        """Draws the text on screen.
            :param text: str - the writing itself.
            :param color: str - color.
            :param position: None or tuple (x, y).
            :param center: bool - Whether to center the text at the given position or align top-left.
            :return: pygame.rect
        """
        text_surface = self.font.render(text, True, color)
        rect = text_surface.get_rect()  # Creates a rect without specific coordinates (size only)

        if position is None:
            # Default: Center on screen (a bit higher)
            rect.center = (self.surface.get_width() // 2, self.surface.get_height() // 2)
        elif center:
            # If center is True, position is the center
            rect.center = position
        else:
            # Custom position using top-left alignment
            rect.topleft = position

        self.surface.blit(text_surface, rect)
        return rect


    def create_table(self, table_x, table_y):
        """Draws the score table.
                :param table_x: x position.
                :param table_y: y position.
                :return: surfaces of drawings.
                """
        table = pygame.draw.lines(self.surface, 'gray84', True,
                                  [(table_x, table_y),  # top line
                                   (table_x, table_y + 250),  # bottom line
                                   (table_x + 375, table_y + 250),  # right line
                                   (table_x + 375, table_y)])  # left line
        line_1 = pygame.draw.line(self.surface, 'gray84', (table_x + 150, table_y + 115),
                                  (table_x + 240, table_y + 115))
        line_2 = pygame.draw.line(self.surface, 'gray84', (table_x + 150, table_y + 165),
                                  (table_x + 240, table_y + 165))
        line_3 = pygame.draw.line(self.surface, 'gray84', (table_x + 150, table_y + 215),
                                  (table_x + 240, table_y + 215))

        return table, line_1, line_2, line_3


class Sounds:
    """ This class handles all the sounds in the game.
        """
    lose_sounds = ["l_sound1", "l_sound2", "l_sound3"]
    ast_impact_sounds = ['ast_impact', 'ast_impact2']
    mixer.init()

    @staticmethod
    def load_sound(file):
        """Loads the file as pygame.sound.
                :param file: str - name of file.
                :return: pygame.sound type
                """
        path = f'assets/sounds/{file}.wav'
        sound = Sound(path)
        sound.set_volume(1)
        return sound

    @staticmethod
    def load_music(file):
        """Loads the file as pygame.mixer - music.
                :param file: str - name of file.
                :return: pygame.mixer type
                """
        path = f'assets/sounds/{file}.mp3'
        return mixer.music.load(path)

    def win_event_sound(self):
        """Stops music and plays win sound.
                """
        mixer.music.fadeout(600)
        self.load_sound("win_sound").play(0)

    def shoot_sound(self):
        """Plays shoot sound.
                """
        sound = self.load_sound("shoot")
        sound.set_volume(0.5)
        sound.play()

    def lose_event_sound(self):
        """Stops music, plays explosion sound and then plays lose sound.
                """
        mixer.music.fadeout(600)
        sound_channel = mixer.Channel(1)
        sound_channel.set_volume(1)
        sound_channel.play(self.load_sound('spaceship_die'), maxtime=1200)
        sound_channel.queue(self.load_sound(random.choice(self.lose_sounds)))

    def init_background_music(self, file):
        """Plays music in background.
                """
        self.load_music(file)
        mixer.music.play(0)
        mixer.music.set_volume(0.1)
        mixer.music.set_pos(34.2)

    def ast_impact(self):
        """Plays asteroid destruction sound.
                :return: pygame.sound type
                """
        sounds = self.load_sound(random.choice(self.ast_impact_sounds))
        return sounds.play()

    def shield_explosion(self):
        """Plays explosion sound of shield.
                """
        explosion_sound = self.load_sound('shield_explosion')
        explosion_sound.set_volume(1)
        explosion_sound.play()

    def powerup_sound(self):
        """Plays power up sound..
                :return: pygame.sound type
                """
        sound = self.load_sound('powerup')
        return sound.play()
