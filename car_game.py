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
    yaw: float = 0.       # Orientation of vehicle in world (radians)
    x: float = 0.         # meters
    y: float = 0.         # meters
    lvel: float = 15.0     # Car linear velocity
    # CoG distance to front/rear axle
    l_front: float = 1.5
    l_rear: float = 2.0
    # Vehicle Yaw rate
    yaw_rate: float = 0
    # Side slip angle (beta) (Radians)
    slip_angle: float = 0
    # Front/Rear axle cornering stiffness. tyre model:(Fy = C*a)
    C_front: float = 10000
    C_rear: float = 10000
    # Moment of inertia around Z (kg*m^2)
    Iz: float = 900
    # Vehicle mass (kg)
    mass: float = 1500
    # Angle of driving wheels (commanded by driver)
    steering_angle: float = 0.

    # State-space representation:
    # X : [y, slip_angle, yaw, yaw_rate]
    # X' = A_lat * X + B_lat*steering_angle
    A_lat: np.array = None
    B_lat: np.array = None

    def __post_init__(self):
        # Just for brevity
        V = self.lvel
        Cf = self.C_front
        Cr = self.C_rear
        Iz = self.Iz
        m = self.mass
        lf = self.l_front
        lr = self.l_rear
        self.A_lat = np.float32([
            [0, self.lvel, self.lvel, 0],
            [0, -(Cr+Cf)/(m*V), 0, ((Cr*lr - Cf*lf)/(m*V**2)) - 1],
            [0, 0, 0, 1],
            [0, (Cr*lr - Cf*lf)/Iz, 0, -(Cr*lr**2 + Cf*lf**2)/(Iz * V)]
        ])

        self.B_lat = np.float32([0, Cf/(m*V), 0, (Cf*lf)/Iz])

    def turn(self, direction):
        self.steering_angle = direction * np.radians(50)

    def update(self, dt):
        X = np.float32((0, self.slip_angle, self.yaw, self.yaw_rate))
        Xdot = np.matmul(self.A_lat, X) + self.steering_angle * self.B_lat
        self.slip_angle += dt * Xdot[1]
        self.yaw += dt * Xdot[2]
        self.yaw_rate += dt * Xdot[3]
        motion_dir = self.yaw + self.slip_angle
        self.x += dt*self.lvel * np.cos(motion_dir)
        self.y += dt*self.lvel * np.sin(motion_dir)
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
