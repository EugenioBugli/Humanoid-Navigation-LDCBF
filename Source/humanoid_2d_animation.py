import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

from BaseAnimationHelper import BaseAnimationHelper

STEP_SIZE = 6
# The maximum number of previous CoM position to plot
NUMBER_OF_SHADOWS = 10
# The maximum number of previous footsteps to plot
NUMBER_OF_FOOTSTEPS_SHADOWS = NUMBER_OF_SHADOWS // 2
# The distance between the right and the left feet
FOOT_DISTANCE = 3
NUMBER_OF_FOOTSTEPS = 20


class HumanoidAnimationHelper(BaseAnimationHelper):
    # Assuming that the plot is a square, the minimum and maximum value that x and y coordinated can have
    MIN_COORD = -50
    MAX_COORD = +50
    # The length of the tick in the line representing the motion of the CoM
    TICK_LENGTH = 1

    def __init__(self, start_conf, goal_conf, fig=None, ax=None, following_com_position=None, following_left_foot=None,
                 following_right_foot=None):
        """
        Initializes a new instance of the utility to show the animation regarding the humanoid.

        :param start_conf: The start configuration of the humanoid, represented by a 3-components vector:
         X-coord, Y-coord, orientation.
        :param goal_conf: The goal configuration, represented by a 3-components vector: X-coord, Y-coord, orientation.
        :param fig: The first element returned by plt.subplots(). If either fig or axis is not provided, a new one
        is created.
        :param ax: The second element returned by plt.subplots(). If either fig or axis is not provided, a new one
        is created.
        :param following_com_position: The CoM positions starting from the configuration after the start configuration.
        :param following_left_foot: The left foot positions starting from the configuration after the start
         configuration.
        :param following_right_foot: The right foot positions starting from the configuration after the start
         configuration
        """
        super(HumanoidAnimationHelper, self).__init__(fig, ax)
        # Put the start and goal configurations in a numpy vector (and put the orientation in the interval [0, 2pi] rad)
        self.start = np.array([start_conf[0], start_conf[1], np.deg2rad(np.rad2deg(start_conf[2]) % 360)])
        self.goal = np.array([goal_conf[0], goal_conf[1], np.deg2rad(np.rad2deg(goal_conf[2]) % 360)])

        # Get the initial left foot position
        left_foot = np.array([
            self.start[0] - FOOT_DISTANCE * np.sin(self.start[2]),
            self.start[1] + FOOT_DISTANCE * np.cos(self.start[2])
        ])
        # Get the initial right foot position
        right_foot = np.array([
            self.start[0] + FOOT_DISTANCE * np.sin(self.start[2]),
            self.start[1] - FOOT_DISTANCE * np.cos(self.start[2])
        ])

        # Initialize the lists containing the evolution of the CoM and feet position
        self.com_pose_history = [self.start]
        self.left_foot_history = [left_foot]
        self.right_foot_history = [right_foot]

        # Compute the following CoM and feet position
        self.following_com_position = following_com_position
        self.following_left_foot = following_left_foot
        self.following_right_foot = following_right_foot
        # The number of the previous frame
        self.last_seen_frame = -1

    def update(self, frame: int):
        print("### FRAME", frame)

        # explanation of such control:
        # https://stackoverflow.com/questions/74252467/why-when-doing-animations-with-matplotlib-frame-0-appears-several-times
        if self.last_seen_frame != frame:
            self.last_seen_frame = frame
        else:
            return -1

        # Clear the canvas
        plt.cla()

        # Plot the goal position
        plt.scatter(self.goal[0], self.goal[1], marker="o", color="royalblue", label='goal', s=300)

        # Draw the last CoMs
        for idx, com in enumerate(
                reversed(self.com_pose_history[-min(len(self.com_pose_history), NUMBER_OF_SHADOWS):])):
            # Draw the point representing the CoM
            self._draw_circle(com, alpha=1.0 - idx / NUMBER_OF_SHADOWS)
            # Draw the line connecting this CoM to the previous one
            self._draw_tick(com, alpha=1.0 - idx / NUMBER_OF_SHADOWS)

        # Draw the last left footsteps
        for idx, left in enumerate(
                reversed(self.left_foot_history[-min(len(self.left_foot_history), NUMBER_OF_FOOTSTEPS_SHADOWS):])):
            # Plot the point corresponding to the left foot position (and give a label - to be used by the legend -
            # only to the first footstep).
            plt.scatter(left[0], left[1], marker="o", color="green", label='left foot' if idx == 0 else None,
                        s=20, alpha=1.0 - idx * 1 / NUMBER_OF_SHADOWS / 2)

        # Draw the last right footsteps
        for idx, right in enumerate(
                reversed(self.right_foot_history[-min(len(self.right_foot_history), NUMBER_OF_FOOTSTEPS_SHADOWS):])):
            # Plot the point corresponding to the right foot position (and give a label - to be used by the legend -
            # only to the first footstep).
            plt.scatter(right[0], right[1], marker="o", color="lightgreen", label='right foot' if idx == 0 else None,
                        s=20, alpha=1.0 - idx * 1 / NUMBER_OF_SHADOWS / 2)

        # Add a legend
        plt.subplots_adjust(right=0.75)
        plt.legend(loc='center right', bbox_to_anchor=(1.45, 0.5), ncol=1, fancybox=True, shadow=False, fontsize="13")

    def show_animation_with_autogeneration(self, path_to_gif: str, num_frames: int = 20, interval: int = 200):
        """
        Shows the animation regarding the humanoid and saves it at save_path. All the configurations
         following the start and goal configurations will be computed automatically after each frame.

        :param path_to_gif: The path to the GIF file where the animation will be saved.
        :param num_frames: The number of frames in the animation.
        :param interval: Delay between frames in milliseconds.
        """
        ani = FuncAnimation(self.fig, self.update_with_autogeneration, frames=num_frames, interval=interval)
        ani.save(path_to_gif, writer='ffmpeg')
        plt.show()

    def show_animation_with_offline_trajectory(self, path_to_gif: str, num_frames: int = 20, interval: int = 200):
        """
        Shows the animation regarding the humanoid and saves it at save_path. The configurations
        following the start and goal configurations are the ones stored in self.following_com_position,
        self.following_left_foot and self.following_right_foot.

        :param path_to_gif: The path to the GIF file where the animation will be saved.
        :param num_frames: The number of frames in the animation.
        :param interval: Delay between frames in milliseconds.
        """
        ani = FuncAnimation(self.fig, self.update_with_offline_trajectory, frames=num_frames, interval=interval)
        ani.save(path_to_gif, writer='ffmpeg')
        plt.show()

    def show_animation(self, path_to_gif: str, num_frames: int = 20, interval: int = 200):
        self.show_animation_with_offline_trajectory(path_to_gif, num_frames, interval)

    def _draw_circle(self, position, alpha=1.0, radius=2.0, color='tomato', fill=True, linewidth=2):
        robot = plt.Circle((position[0], position[1]), radius=radius, color=color,
                           fill=fill, linewidth=linewidth, alpha=alpha)
        self.ax.add_patch(robot)

    def _draw_tick(self, position, alpha=1.0, color='black', linewidth=2):
        tick_x = [position[0], position[0] + HumanoidAnimationHelper.TICK_LENGTH * np.cos(position[2])]
        tick_y = [position[1], position[1] + HumanoidAnimationHelper.TICK_LENGTH * np.sin(position[2])]
        plt.plot(tick_x, tick_y, color=color, linewidth=linewidth, alpha=alpha)

    def update_with_autogeneration(self, frame):
        """
        Updates the canvas to display the state corresponding to the given frame number. All the configurations
         following the start and goal configurations will be computed automatically after each frame.

        :param frame: The number of the frame whom state has to be represented.
        """
        res = self.update(frame)
        if res == -1:
            return

        # Set a lower step size for the first step
        step_size = STEP_SIZE / 2 if frame == 0 else STEP_SIZE

        # ===== COMPUTING NEXT VALUES =====
        last_conf = self.com_pose_history[-1]
        next_conf = np.array([
            last_conf[0] + step_size / 2 * np.cos(last_conf[2]),
            last_conf[1] + step_size / 2 * np.sin(last_conf[2]),
            last_conf[2]
        ])
        self.com_pose_history.append(next_conf)

        foot = 0 if frame % 2 == 0 else 1

        if foot == 0:
            print("LEFT")
            last_left_foot = self.left_foot_history[-1]
            left_foot = np.array([
                last_left_foot[0] + step_size * np.cos(next_conf[2]),
                last_left_foot[1] + step_size * np.sin(next_conf[2])
            ])
            self.left_foot_history.append(left_foot)
        else:
            print("RIGHT")
            last_right_foot = self.right_foot_history[-1]
            right_foot = np.array([
                last_right_foot[0] + step_size * np.cos(next_conf[2]),
                last_right_foot[1] + step_size * np.sin(next_conf[2])
            ])
            self.right_foot_history.append(right_foot)

        plt.xlim(HumanoidAnimationHelper.MIN_COORD, HumanoidAnimationHelper.MAX_COORD)
        plt.ylim(HumanoidAnimationHelper.MIN_COORD, HumanoidAnimationHelper.MAX_COORD)
        ax = plt.gca()
        ax.set_aspect('equal', adjustable='box')

    def update_with_offline_trajectory(self, frame):
        """
        Updates the canvas to display the state corresponding to the given frame number. The configurations
        following the start and goal configurations are the ones stored in self.following_left_foot,
        self.following_left_foot and self.following_right_foot.

        :param frame: The number of the frame whom state has to be represented.
        """
        res = self.update(frame)
        if res == -1:
            return

        # ===== COMPUTING NEXT VALUES =====
        self.com_pose_history.append(self.following_com_position.pop(0))
        foot = 0 if frame % 2 == 0 else 1
        if foot == 0:
            print("LEFT")
            self.left_foot_history.append(self.following_left_foot.pop(0))
        else:
            print("RIGHT")
            self.right_foot_history.append(self.following_right_foot.pop(0))

        plt.xlim(HumanoidAnimationHelper.MIN_COORD, HumanoidAnimationHelper.MAX_COORD)
        plt.ylim(HumanoidAnimationHelper.MIN_COORD, HumanoidAnimationHelper.MAX_COORD)
        ax = plt.gca()
        ax.set_aspect('equal', adjustable='box')


def generate_com_and_feet_evolution(start_com, start_left_foot, start_right_foot, num_frames):
    """
    Generates all the CoM and feet positions of the animation (starting from the configuration after the start
     configuration).
    """
    com_pose_history = []
    left_foot_history = []
    right_foot_history = []

    last_conf = start_com
    last_left_foot = start_left_foot
    last_right_foot = start_right_foot
    for i in range(num_frames):
        # Set a lower step size for the first step
        step_size = STEP_SIZE / 2 if i == 0 else STEP_SIZE

        # Generate the new CoM configuration
        next_conf = np.array([
            last_conf[0] + step_size / 2 * np.cos(last_conf[2]),
            last_conf[1] + step_size / 2 * np.sin(last_conf[2]),
            last_conf[2]
        ])
        com_pose_history.append(next_conf)
        last_conf = next_conf

        foot = 0 if i % 2 == 0 else 1
        if foot == 0:
            # Generate the new left feet position
            new_left_foot = np.array([
                last_left_foot[0] + step_size * np.cos(next_conf[2]),
                last_left_foot[1] + step_size * np.sin(next_conf[2])
            ])
            left_foot_history.append(new_left_foot)
            last_left_foot = new_left_foot
        else:
            # Generate the new right feet position
            new_right_foot = np.array([
                last_right_foot[0] + step_size * np.cos(next_conf[2]),
                last_right_foot[1] + step_size * np.sin(next_conf[2])
            ])
            right_foot_history.append(new_right_foot)
            last_right_foot = new_right_foot

    return com_pose_history, left_foot_history, right_foot_history


if __name__ == "__main__":
    # Set a random goal
    goal = np.random.randint(-10, 10, (3, 1))
    # Set a random initial position
    start = np.random.randint(-10, 10, (3, 1))

    anim_helper = HumanoidAnimationHelper(goal_conf=goal, start_conf=start)
    # anim_helper.show_animation_with_autogeneration('../Assets/Animations/humanoid_2d_animation.gif')

    anim_helper.following_com_position, anim_helper.following_left_foot, anim_helper.following_right_foot = (
        generate_com_and_feet_evolution(
            anim_helper.start, anim_helper.left_foot_history[0],
            anim_helper.right_foot_history[0], num_frames=21))
    anim_helper.show_animation('../Assets/Animations/humanoid_2d_animation.gif')
