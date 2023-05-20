#!/usr/bin/env python3
import numpy as np
from pprint import pprint
from dataclasses import dataclass
import arcade

# Constants
SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Car Game"


@dataclass
class CarState(object):
    yaw: float = 0.
    x: float = 0.
    y: float = 0.
    lvel: float = 5.0     # Car linear velocity
    l_front: float = 1.5  # CoG distance to front wheels
    l_rear: float = 2.0   # CoG distance to rear wheels
    yaw_rate: float = 0   # CoG distance to rear wheels
    steering_angle: float = 0.

    def turn(self, direction):
        self.steering_angle = direction * np.radians(50)

    def update(self, dt):
        self.yaw_rate = self.steering_angle
        self.yaw += dt * self.yaw_rate
        self.x += dt*self.lvel * np.cos(self.yaw)
        self.y += dt*self.lvel * np.sin(self.yaw)
        # pprint(self)

    def center(self):
        return np.array([self.x, self.y, 1.0])


class CarGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.scene = None
        self.car_sprite = None
        self.left_pressed = False
        self.right_pressed = False
        self.pixels_per_meter = 100 / 4
        self.car = CarState()
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        self.scene = arcade.Scene()
        self.scene.add_sprite_list("Player")

        self.car_sprite = arcade.Sprite("car_sprite.png")
        self.car_sprite.center_x = SCREEN_WIDTH / 2
        self.car_sprite.center_y = SCREEN_HEIGHT / 2
        self.car_sprite.radians = 0.25 * np.pi
        self.world_to_screen = np.zeros(shape=(2, 3), dtype=np.float32)
        self.world_to_screen[0, 0] = self.pixels_per_meter
        self.world_to_screen[1, 1] = self.pixels_per_meter
        self.world_to_screen[0, 2] = SCREEN_WIDTH / 2
        self.world_to_screen[1, 2] = SCREEN_HEIGHT / 2

        self.scene.add_sprite("Player", self.car_sprite)

    def on_draw(self):
        """Render the screen."""

        self.clear()
        # Code to draw the screen goes here
        self.scene.draw()

    def on_key_press(self, key, modifiers):
        """Called when the user presses a key."""
        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False

    def steering_sign(self):
        """
        Returns 1 if only self is pressed, -1 if only right is pressed or 0 in all other cases
        """
        return int(self.left_pressed) - int(self.right_pressed)

    def recenter_camera(self, car_pixel_pos):
        if car_pixel_pos[0] < 0:
            self.world_to_screen[0, 2] += SCREEN_WIDTH
        elif car_pixel_pos[0] >= SCREEN_WIDTH:
            self.world_to_screen[0, 2] -= SCREEN_WIDTH

        if car_pixel_pos[1] < 0:
            self.world_to_screen[1, 2] += SCREEN_HEIGHT
        elif car_pixel_pos[1] >= SCREEN_HEIGHT:
            self.world_to_screen[1, 2] -= SCREEN_HEIGHT

    def on_update(self, dt):
        self.car.turn(self.steering_sign())
        self.car.update(dt)
        pixels_pos = np.matmul(self.world_to_screen, self.car.center())
        pprint(pixels_pos)
        self.car_sprite.center_x = pixels_pos[0]
        self.car_sprite.center_y = pixels_pos[1]
        self.car_sprite.radians = self.car.yaw
        self.recenter_camera(pixels_pos)


def main():
    """Main function"""
    window = CarGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
