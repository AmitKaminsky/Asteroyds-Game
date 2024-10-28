import pygame
from utils import load_sprite, menu_get_random_position, get_random_position
from modules import Spaceship, Asteroid, Text, Sounds, BulletPowerUp, SlowMotionPowerUp
import random

# Images for assets
backgrounds = ['space', 'space2', 'space3', 'space4', 'space5']
bonus_background = ['spaghetti']
spaceship_imgs = ['spaceship0', 'spaceship1', 'spaceship2', 'spaceship3']

# Variables and helpers
WIN = 0
spaceship_kind = 0
shield_state = False  # Global param because that's how the shield stays when you restart
asteroid_amount = 6
bullets_amount = 3
powered_up_bullets = 5
SCALE_FACTOR = 0.5
base_pos = -50 * (1 + SCALE_FACTOR)

# Stats
Round = 0
fastest_bullet_speed = 0
time_played = 0


class Game:
    """ This class is the heart of the game, it uses all the other .pys to operate the gameplay.
    This is the class used to operate both the game and the menu.
            """

    # Game details > changeable here
    global asteroid_amount, bullets_amount, powered_up_bullets, SCALE_FACTOR
    target_fps = 60  # Fps of the game
    score_color = random.choice(['darkviolet', 'mediumorchid', 'mediumpurple'])

    # Counters
    score = 0
    score_list = []
    asteroids_destroyed = 0

    # [NEW] Scaling constraints
    MIN_WIDTH = 800
    MAX_WIDTH = 1920
    MIN_HEIGHT = 600
    MAX_HEIGHT = 1080
    MIN_SCALE = 0.5
    MAX_SCALE = 1.0

    # States of different aspects of the game, help change code during the loop
    win_option = False
    score_ready = True
    ast_slow_state = False

    # Time counters
    lose_time = 0
    invulnerability_time = 600
    powered_up_begin_time = 0
    power_up_option_interval_hard = 8000  # Seconds
    power_up_option_interval_easy = 5000  # Seconds
    powered_up_duration = 2000  # Seconds

    # DEFAULT display
    Screen_width = 800
    Screen_height = 600

    def __init__(self):
        """Class init. Initiates the game and different states/counters/images and sprites
                """
        self._init_pygame()
        self._init_screen_size(self)
        self.screen = pygame.display.set_mode((self.Screen_width, self.Screen_height))
        self.clock = pygame.time.Clock()
        self.background = pygame.transform.scale(load_sprite(random.choice(backgrounds), False),
                                                 (self.Screen_width, self.Screen_height))

        self.spaceship_init_pos = (self.Screen_width // 2, int(self.Screen_height * 0.77))
        self.table_x = self.Screen_width // 2
        self.table_y = self.Screen_height // 2
        self.asteroid_amount = asteroid_amount
        self.bullets_amount = bullets_amount
        self.powered_up_bullets = powered_up_bullets
        self.asteroids = []
        self.bullets = []
        self.explosion = []
        self.powerups = []
        self.spaceship_bullet_power = False
        self.spaceship_slow_power = False
        self.menu_state = True
        self.table_state = False
        self.game_mode = ''  # Easy or hard

        self.score_text, self.end_text = self._init_game_texts(self, self.screen)
        self.menu_title, self.menu_play, self.menu_toggle_mode, self.menu_score, \
            self.menu_change_spaceship, self.menu_quit = self._show_menu_text(self, self.screen)

        
        Sounds().init_background_music('Background_music')

        # Gives random position for each asteroid spawn
        while len(self.asteroids) < self.asteroid_amount:
            ast_post = menu_get_random_position(self.screen)
            self.asteroids.append(Asteroid(ast_post, self.asteroids.append)) 

    @staticmethod
    def _init_pygame():
        """Initiates pygame and sets name of game
                """
        pygame.init()
        pygame.display.set_caption('Space Rocks')

    @staticmethod
    def _init_screen_size(self):
        """Retrieve screen size and set the game screen size
                """
        # Set up the display
        display_info = pygame.display.Info()
        
        # Constrain SCALE_FACTOR
        global SCALE_FACTOR
        SCALE_FACTOR = max(min(SCALE_FACTOR, self.MAX_SCALE), self.MIN_SCALE)
        
        # Calculate scaled dimensions
        scaled_width = int(display_info.current_w * SCALE_FACTOR)
        scaled_height = int(display_info.current_h * SCALE_FACTOR)
        
        # Apply min/max constraints
        self.Screen_width = max(min(scaled_width, self.MAX_WIDTH), self.MIN_WIDTH)
        self.Screen_height = max(min(scaled_height, self.MAX_HEIGHT), self.MIN_HEIGHT)

    @staticmethod
    def _init_game_texts(self, surface):
        """Creates the text for score and "lose"
                :param: surface - the background, screen
                :return: Text surfaces
                """
        body_font_size = int(self.Screen_height * 0.05)
        header_font_size = int(self.Screen_height * 0.1)
        score_text = Text(surface, font_style=pygame.font.Font(None, body_font_size))
        end_text = Text(surface, font_style=pygame.font.Font(None, header_font_size))
        return score_text, end_text

    @staticmethod
    def _show_menu_text(self, surface):
        """Creates the text for the menu with proper spacing and alignment
                :param: surface - the background, screen
                :return: Text surfaces
        """
        # Calculate font sizes based on screen height
        body_font_size = int(self.Screen_height * 0.067)
        header_font_size = int(self.Screen_height * 0.175)
        
        # Create text objects
        menu_title_text = Text(surface, font_style=pygame.font.Font(None, header_font_size))
        menu_text = Text(surface, font_style=pygame.font.Font(None, body_font_size))
        
        # Calculate vertical spacing
        spacing = self.Screen_height * 0.08  # 8% of screen height for spacing
        title_offset = self.Screen_height * 0.2  # 20% from top for title
        
        # Calculate positions
        title_y = self.Screen_height * 0.15  # Title at 30% of screen height
        start_y = title_y + spacing * 2  # Start menu items below title
        
        # Create menu items with proper spacing
        menu_title = menu_title_text.show_text(
            "Destroyds", 
            'gray94', 
            (self.Screen_width // 2, title_y)
        )
        
        menu_play = menu_text.show_text(
            "Play!", 
            'gray87', 
            (self.Screen_width // 2, start_y)
        )
        
        menu_toggle_mode = menu_text.show_text(
            "Toggle hard/easy mode", 
            "gray87", 
            (self.Screen_width // 2, start_y + spacing)
        )
        
        menu_score = menu_text.show_text(
            "Score Table", 
            'gray88', 
            (self.Screen_width // 2, start_y + spacing * 2)
        )
        
        menu_change_spaceship = menu_text.show_text(
            "Change spaceship", 
            'gray89', 
            (self.Screen_width // 2, start_y + spacing * 3)
        )
        
        menu_quit = menu_text.show_text(
            "Quit game", 
            'gray90', 
            (self.Screen_width // 2, start_y + spacing * 4)
        )
        
        return menu_title, menu_play, menu_toggle_mode, menu_score, menu_change_spaceship, menu_quit

    @staticmethod
    def _chosen_spaceship(i):
        """Enables the "Change Spaceship" in the menu - changing image
                :param i: int (0-3)
                :return str: Image name from the list
                """
        return spaceship_imgs[i]

    @staticmethod
    def check_number_type(x):
        """Helper method to center the score numbers in the menu table score
                :param x: int (score)
                :return: str - Placement of score (x), using backspaces
                """
        if isinstance(x, int) and x < 10:
            return f'{" " * 18}{x}'
        elif isinstance(x, int) and x >= 10:
            return f'{" " * 17}{x}'
        elif isinstance(x, float) and x < 10:
            return f'{" " * 17}{x}'
        elif isinstance(x, float) and x >= 10:
            return f'{" " * 16}{x}'
        
    def _draw_score(self, score_text, position, score_value, x, y):
        """Helper method to draw individual scores with proper formatting"""
        return score_text.show_text(
            f"{position}{self.check_number_type(score_value)}", 
            'green' if position == 1 else 'white',
            (x, y))
    
    def _get_medium_score(self):
        """Helper method to get the medium score"""
        if len(self.score_list) < 3:
            return 0
            
        medium_score = sorted(self.score_list)[1]
        return medium_score

    def _scale_font_size(self, scale_factor):
        """Scales the font size based on the screen height and provided scale factor."""
        return int(self.Screen_height * scale_factor)


    def _show_score_table_text(self):
        """Score table text - shows using the menu
        :return: Score table title and individual score elements
        """
        # Calculate constrained font sizes
        title_size = self._scale_font_size(0.1)  # 10% of screen height
        score_size = self._scale_font_size(0.067)  # 6.7% of screen height

        # Create text elements for the score table
        score_table_title_text = Text(self.screen, font_style=pygame.font.Font(None, title_size))
        score_text = Text(self.screen, font_style=pygame.font.Font(None, score_size))

        # Position title on the left side of the screen
        title_x = int(self.Screen_width * 0.05)  # Set position closer to the left side (10% from the left)
        title_y = int(self.Screen_height * 0.25)  # Keep some margin from the top for better visibility

        # Draw the score table title
        score_table_title = score_table_title_text.show_text(
            "Score Table",
            'gray80',
            (title_x, title_y),
            center=False
        )

        # Calculate score positions
        score_x = title_x  # Align scores directly below the title
        score_y_base = title_y + int(120 * SCALE_FACTOR)  # Start scores below the title
        score_y_increment = int(100 * SCALE_FACTOR)  # Spacing between scores
        
        # Draw the table grid lines around the scores
        # Adjust the position and size for drawing the grid lines correctly
        grid_x = title_x - 10  # Adjust grid line position closer to the score values for better alignment
        grid_y = title_y + int(80 * SCALE_FACTOR)  # Adjusted to be slightly below the title
        grid_width = int(self.Screen_width * 0.25)  # Reduce grid width to make it smaller
        grid_height = int(280 * SCALE_FACTOR)  # Reduce grid height to make it fit scores properly
        pygame.draw.rect(self.screen, 'white', (grid_x, grid_y, grid_width, grid_height), 1)  # Draw the grid with adjusted positions and size

        # ########## CHANGED ##########
        # Draw underlines for the actual score
        underline_y_offset = 20  # Offset for drawing underline below each score
        for i in range(3):
            underline_y = score_y_base + i * score_y_increment + underline_y_offset
            pygame.draw.line(self.screen, 'white', (score_x + grid_width // 16 * 4, underline_y), (score_x + grid_width // 16 * 5.5, underline_y), 1)  # Draw underline with appropriate width


        # Draw scores with correct alignment and scaling, without placeholder duplicates
        score_1, score_2, score_3 = None, None, None 

        # Draw scores with correct alignment and scaling
        score_1 = score_text.show_text("1", 'green', (score_x, score_y_base))
        score_2 = score_text.show_text("2", 'white', (score_x, score_y_base + score_y_increment))
        score_3 = score_text.show_text("3", 'white', (score_x, score_y_base + score_y_increment * 2))

        # Handle score display logic and update scores
        if len(self.score_list) >= 1:
            score_1 = self._draw_score(score_text, 1, max(self.score_list), score_x, score_y_base)

        if len(self.score_list) >= 2:
            second_score = min(self.score_list) if len(self.score_list) == 2 else self._get_medium_score()
            score_2 = self._draw_score(score_text, 2, second_score, score_x, score_y_base + score_y_increment)

        if len(self.score_list) >= 3:
            score_3 = self._draw_score(score_text, 3, min(self.score_list), score_x, score_y_base + score_y_increment * 2)

        # Return all elements similar to the original code structure
        return score_table_title, score_1, score_2, score_3

    def main_loop(self):
        """The main loop of the game. Runs both the game loop or the menu loop.
                :return: None
                """
        while True:
            if self.menu_state:
                self._menu_handle_input()
                self._menu_process_game_logic()
                self._menu_draw()
            else:
                self._handle_input()
                self._process_game_logic()
                self._draw()

    def _handle_input(self):
        """The method handles all user clicks on keyboard, enables the game to quit using 'X' on top right and
             restart of the game by running the loop again.
                :return: None
                """
        global fastest_bullet_speed  # Saves the speed from all game rounds
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit()

            # Enables 'restart' using ESC
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                pygame.quit()
                space_rocks = Game()
                space_rocks.main_loop()

            # Handles different amount of bullets according to game state - default/powerup/end game
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and self.spaceship:
                if self.spaceship and len(self.asteroids) == 0:
                    self.spaceship.shoot(False)
                elif self.spaceship and len(self.asteroids) > 0 and self.spaceship_bullet_power is False:
                    if len(self.bullets) < self.bullets_amount:
                        self.spaceship.shoot(False)
                elif self.spaceship and len(self.bullets) < self.powered_up_bullets and self.spaceship_bullet_power:
                    self.spaceship.shoot(True)
                if self.spaceship.bullet_speed() > fastest_bullet_speed:
                    fastest_bullet_speed = self.spaceship.bullet_speed()

        # Handles movement of spaceship
        keys_pressed = pygame.key.get_pressed()
        if self.spaceship:
            if keys_pressed[pygame.K_RIGHT]:
                self.spaceship.rotate(True)
            if keys_pressed[pygame.K_LEFT]:
                self.spaceship.rotate(False)
            if keys_pressed[pygame.K_UP]:
                self.spaceship.accelerate()
            elif not keys_pressed[pygame.K_UP]:
                self.spaceship.friction()

    def _get_game_objects(self):
        """Captures all sprites to one list and returns it. Runs in the game loop.
                :return: list of sprites
                """
        for ast in self.asteroids:
            ast.change_menu_state(False)
        game_objects = [*self.asteroids, *self.bullets, *self.explosion, *self.powerups]
        if self.spaceship:
            game_objects.append(self.spaceship)
        return game_objects

    def _process_game_logic(self):
        """This method take cares of:
        1. All sprite movement.
        2. Score count and save.
        3. Powerups.
        4. Shield (if easy mode)
        5. Asteroid collision with ship.
        6. Asteroid splits.
        7. Bullets going out of borders.
                :return: None
                """
        global shield_state, time_played
        # All objects movement
        for game_object in self._get_game_objects():
            game_object.move()

        if self.spaceship:
            # Saves score only in the end of game (lose/win)
            if len(self.asteroids) == 0 and self.win_option and self.score_ready:
                if len(self.score_list) < 3:
                    self.score_list.append(self.score)
                else:
                    self.score_list.remove(min(self.score_list))
                    self.score_list.append(self.score)
                self.score_ready = False

            # Duration of powerup
            if pygame.time.get_ticks() - self.powered_up_begin_time > self.powered_up_duration:
                self.spaceship_bullet_power = False

            # Changes time between powerups according to game mode (easy/hard)
            if self.game_mode == 'easy':
                power_up_option_interval = self.power_up_option_interval_easy
            else:
                power_up_option_interval = self.power_up_option_interval_hard


            ######################### NEEDS SCALE AS WELL #######################################


            # Spawns the powerups according to interval, and makes sure only 2 and far from each other and spaceship.
            if pygame.time.get_ticks() - self.powered_up_begin_time > power_up_option_interval:
                while True:
                    bullet_powerup_position = get_random_position(self.screen)
                    slow_powerup_position = get_random_position(self.screen)
                    if bullet_powerup_position.distance_to(self.spaceship.position) > 100 \
                            and slow_powerup_position.distance_to(self.spaceship.position) > 100:
                        if len(self.powerups) == 0 and bullet_powerup_position.distance_to(slow_powerup_position) > 100:
                            break
                        elif len(self.powerups) == 1:
                            if isinstance(self.powerups[0], BulletPowerUp):
                                if self.powerups[0].position.distance_to(slow_powerup_position) > 100:
                                    break
                            elif isinstance(self.powerups[0], SlowMotionPowerUp):
                                if self.powerups[0].position.distance_to(bullet_powerup_position) > 100:
                                    break
                        elif len(self.powerups) == 2:
                            break

                # Makes sure to spawn up to 2 powerups and 1 of each
                if self.win_option is False:
                    bullet_powerup = BulletPowerUp(bullet_powerup_position)
                    slow_powerup = SlowMotionPowerUp(slow_powerup_position)
                    if len(self.powerups) == 0:
                        self.powerups.append(bullet_powerup)
                        self.powerups.append(slow_powerup)
                    elif len(self.powerups) == 1:
                        if not isinstance(self.powerups[0], BulletPowerUp):
                            self.powerups.append(bullet_powerup)
                        elif not isinstance(self.powerups[0], SlowMotionPowerUp):
                            self.powerups.append(slow_powerup)

            # Handles powerup taking
            if len(self.powerups) > 0:
                for powerup in self.powerups:
                    if self.spaceship.collides_with(powerup):
                        Sounds().powerup_sound()
                        self.powered_up_begin_time = pygame.time.get_ticks()
                        if isinstance(powerup, BulletPowerUp):
                            self.spaceship_bullet_power = True
                        elif isinstance(powerup, SlowMotionPowerUp):
                            self.spaceship_slow_power = True
                        self.powerups.remove(powerup)

            # Handles asteroid collision - both when easy mode and hard mode.
            for asteroid in self.asteroids:
                if asteroid.collides_with(self.spaceship):
                    # Shield break and sound.
                    if shield_state is True:
                        self.lose_time = pygame.time.get_ticks()
                        self.spaceship.shield = False
                        Sounds().shield_explosion()
                        self.spaceship.velocity *= -1.3
                        shield_state = False

                    # Spaceship can get hit and 'die' after sine invulnerability time.
                    elif pygame.time.get_ticks() > self.lose_time + self.invulnerability_time and shield_state is False:
                        Sounds().lose_event_sound()
                        self.spaceship.explosion()
                        self.spaceship = None
                        self.asteroids.remove(asteroid)
                        asteroid.split()
                        time_played = pygame.time.get_ticks()
                        print(self.game_stats())  # Prints round number, total time played, the fastest bullet speed and
                        # asteroids destroyed.

                        if len(self.score_list) < 3:
                            self.score_list.append(self.score)
                        else:
                            if self.score > min(self.score_list):
                                self.score_list.remove(min(self.score_list))
                                self.score_list.append(self.score)
                    break

        # The slow motion power up is not dependent on self.spaceship inorder to change even when you lose.
        if self.spaceship_slow_power:
            if self.ast_slow_state is False:
                for asteroid in self.asteroids:
                    asteroid.velocity = pygame.Vector2(asteroid.velocity) * 0.3
                self.ast_slow_state = True
            elif pygame.time.get_ticks() - self.powered_up_begin_time > self.powered_up_duration:
                for asteroid in self.asteroids:
                    if pygame.Vector2(asteroid.velocity).length() < 4:
                        asteroid.velocity = pygame.Vector2(asteroid.velocity) * 3.33
                self.spaceship_slow_power = False
                self.ast_slow_state = False

        # Handles bullet hitting asteroids and score counting.
        for asteroid in self.asteroids[:]:
            asteroid.random_rotation()
            for bullet in self.bullets[:]:
                if asteroid.collides_with(bullet):
                    self.asteroids.remove(asteroid)
                    self.bullets.remove(bullet)
                    asteroid.split()
                    if self.spaceship:
                        if self.game_mode == 'hard':
                            self.score += 1
                        else:
                            self.score += 0.5
                    self.asteroids_destroyed += 1
                    Sounds().ast_impact()
                    break

        # Makes sure there are no powerups when you 'lose'.
        if self.win_option or self.spaceship is None:
            self.powerups = []

        for bullet in self.bullets[:]:  # A copy of the list in order to not iterate on the original one
            if not self.screen.get_rect().collidepoint(bullet.position):  # The method checks if it's inside the rect
                self.bullets.remove(bullet)

    def _draw(self):
        """Handles the images 'drawn' on screen - background, score, sprites and win/lose text. Draws according to FPS.
                :return: None
                """
        self.screen.blit(self.background, (0, 0))
        self.score_text.show_text(f"Score: {self.score}", self.score_color, (0, 0), center=False)


        for game_object in self._get_game_objects():
            game_object.draw(self.screen)

        if self.spaceship is None:
            game_over_position = (self.Screen_width // 2, self.Screen_height * 0.3)
            restart_text_position = (self.Screen_width // 2, self.Screen_height * 0.3 + int(100 * SCALE_FACTOR))
            exit_text_position = (self.Screen_width // 2, self.Screen_height * 0.3 + int(175 * SCALE_FACTOR))

            self.end_text.show_text("GAME OVER!", 'lavender', game_over_position, center=True)
            self.score_text.show_text("Press F1 to restart", 'lavenderblush', restart_text_position, center=True)
            self.score_text.show_text("Press ESC to exit", 'lavenderblush', exit_text_position, center=True)

        # If game is won
        if self.win_option:
            you_win_position = (self.Screen_width // 2, self.Screen_height * 0.3)
            restart_text_position = (self.Screen_width // 2, self.Screen_height * 0.3 + int(100 * SCALE_FACTOR))
            exit_text_position = (self.Screen_width // 2, self.Screen_height * 0.3 + int(175 * SCALE_FACTOR))

            self.end_text.show_text("YOU WIN!", 'ivory', you_win_position, center=True)
            self.score_text.show_text("Press F1 to restart", 'lavenderblush', restart_text_position, center=True)
            self.score_text.show_text("Press ESC to exit", 'lavenderblush', exit_text_position, center=True)

        # Makes sure all stats for win are correct.
        elif not self.win_option and len(self.asteroids) == 0 and self.spaceship:
            self.win_option = True
            print(self.game_stats())
            Sounds().win_event_sound()

        self.clock.tick(self.target_fps)  # FPS
        pygame.display.flip()

    def _menu_process_game_logic(self):
        """Menu - moves asteroids on half screen and rotates them. Same asteroids continue in game.
                :return: None
                """
        for asteroid in [*self.asteroids]:
            asteroid.change_menu_state(True)
            asteroid.move()
            asteroid.random_rotation()

    def _menu_handle_input(self):
        """Menu - moves asteroids on half screen and rotates them. Same asteroids continue in game.
                :return: None
                """
        # Very similar to game loop.
        global spaceship_kind, shield_state
        for event in pygame.event.get():

            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                pygame.quit()
                space_rocks = Game()
                space_rocks.main_loop()

            # All the handles for pressing text in menu.
            if self.menu_state:
                if self.menu_play.collidepoint(pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN \
                        or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                    # Enables the change of the spaceship image.
                    self.spaceship = Spaceship(self.spaceship_init_pos, shield_state,
                                               self.bullets.append,
                                               self.explosion.append, self._chosen_spaceship(spaceship_kind))
                    self.menu_state = False
                    self.game_mode = 'easy' if shield_state else 'hard'
                    self.powered_up_begin_time = pygame.time.get_ticks()
                # Changes game mode.
                if self.menu_toggle_mode.collidepoint(pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN:
                    shield_state = not shield_state
                # Changes spaceship image.
                if self.menu_change_spaceship.collidepoint(
                        pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN:
                    spaceship_kind += 1
                    if spaceship_kind == 4:
                        spaceship_kind = 0
                # Shows score table.
                if self.menu_score.collidepoint(
                        pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN:
                    self.table_state = not self.table_state
                # Quits the code (game).
                if self.menu_quit.collidepoint(
                        pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN:
                    quit()

    def _menu_draw(self):
        """Menu draw. Similar to game loop but adds menu options.
                :return: None
                """
        self.screen.blit(self.background, (0, 0))
        self.menu_spaceship = Spaceship(self.spaceship_init_pos, shield_state, self.bullets.append,
                                        self.explosion.append, self._chosen_spaceship(spaceship_kind))
        self.menu_spaceship.draw(self.screen)

        for game_object in [*self.asteroids]:
            game_object.draw(self.screen)
        pygame.draw.line(self.screen, (91, 91, 91), (0, self.Screen_height / 2 + 100),
                         (self.Screen_width, self.Screen_height / 2 + 100))
        self._show_menu_text(self, self.screen)

        if self.table_state:
            self._show_score_table_text()
        # display.update vs flip > update can be used on a specific object while flip is for all

        self.clock.tick(self.target_fps)
        pygame.display.flip()

    def game_stats(self):
        """Shows end game stats - round number, time of round, the fastest bullet speed and asteroids destroyed.
                :return: Strings - game stats.
                """
        global Round
        Round += 1
        return f'Round {Round}:\n' \
               f''f'Total time played: {(time_played / 1000):.2f} seconds\n' \
               f'Fastest bullet speed: {fastest_bullet_speed:.2f} m/s\n' \
               f'Total asteroids destroyed: {self.asteroids_destroyed}\n' \
               f'{"#" * 30}'

def set_game_settings(scale, asteroids, bullets, powered_bullets):
    """Changes the setting in the game.
            :param asteroids: int
            :param bullets: int
            :param powered_up_bullets: int
            :return: None
            """
    global asteroid_amount, bullets_amount, powered_up_bullets, SCALE_FACTOR
    SCALE_FACTOR = scale
    asteroid_amount = asteroids
    bullets_amount = bullets
    powered_up_bullets = powered_bullets
