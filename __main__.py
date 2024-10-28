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

""" Fix asteroids going out of borders right side and down side"""

# Welcome to 'Destroyds' game! (Destroy asteroids...)
# The rules of game are simple - destroy all asteroids and survive (your ship must stay alive to win)
# Menu:
# In the menu you can toggle easy/hard mode -
# Easy mode gives you extra life but the score is halved (0.5 for each asteroid)! Powerups spawn quicker
# Hard mode gives you 1 point for each asteroid, slightly more time between powerups, and 1 life only.
# Score table - gives you the top three high scores. Note that your score is saved only when you win or lose!
# Change spaceship - you have 4 different options!
# Quit game - well..

# How to play:
# Controls:
# Up arrow - accelerate to where the cannon points to. (Or slow down if facing opposite side). No breaks!
# Left/right arrow - turn the spaceship, accordingly.
# Space - shoot! You can shoot up to 3 bullets (that are flying on screen)
# Game:
# You spawn with 6 asteroids, each split 2 time to 2 medium ones, and they split to 2 small ones.
# Every small period of time there will spawn 2 powerups-
# Slow motion - a red snail. All current asteroids are slowed down for a brief moment.
# 5 powerup - you can shoot up to 5 bullets for a short time.
# Walls - when you hit the wall it deflects you. Watch out!
