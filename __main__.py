from game import Game, set_game_settings

######################################################
######################################################

# Change game settings:
SCALE_FACTOR = 0.75 # 0.4 <= SCALE_FACTOR < 1. Recommended: 0.75
asteriod_amount = 6
bullets_amount = 3
powered_up_bullets = 5

######################################################
######################################################

set_game_settings(SCALE_FACTOR, asteriod_amount, bullets_amount, powered_up_bullets)

if __name__ == '__main__':
    space_rocks = Game()
    space_rocks.main_loop()
