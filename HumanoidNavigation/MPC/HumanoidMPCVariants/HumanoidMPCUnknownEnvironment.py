from typing import Union

import numpy as np
from scipy.spatial import ConvexHull

from HumanoidNavigation.MPC.HumanoidMpc import HumanoidMPC, conf, ASSETS_PATH
from HumanoidNavigation.RangeFinder.range_finder_wth_polygons_dbscan import range_finder
from HumanoidNavigation.Utils.ObstaclesUtils import ObstaclesUtils
from HumanoidNavigation.Utils.obstacles import set_seed
from HumanoidNavigation.report_simulations.Scenario import Scenario


class HumanoidMPCUnknownEnvironment(HumanoidMPC):
    """
    A subclass of HumanoidMPC, where the robot is not aware of the full map, but it can only perceive the environment
     through a LiDAR system.
    """

    def __init__(self, goal, obstacles, N_horizon=3, N_mpc_timesteps=100, sampling_time=1e-3,
                 init_state: Union[np.ndarray, tuple[float, float, float, float, float]] = None,
                 start_with_right_foot: bool = True, verbosity: int = 1,
                 lidar_range: float = 3.0, lidar_resolution: int = 360):

        self.lidar_range=lidar_range
        self.lidar_resolution = lidar_resolution

        super().__init__(goal, obstacles, N_horizon=N_horizon, N_mpc_timesteps=N_mpc_timesteps, sampling_time=sampling_time,
                 init_state=init_state, start_with_right_foot=start_with_right_foot, verbosity=verbosity)

    def _get_list_c_and_eta(self, loc_x_k: float, loc_y_k: float, glob_theta_k: float, glob_x_km1: float,
                            glob_y_km1: float):
        """
        It computes the list of the points C and the normal vectors Eta, which are defined for each obstacle as the
        point on the obstacle's edge that is closest to the robot's position, and the vector from the robot's position
        to C.

        :param loc_x_k: The CoM X-coordinate of the humanoid w.r.t the local RF at time step k in the simulation.
        :param loc_y_k: The CoM Y-coordinate of the humanoid w.r.t the local RF at time step k in the simulation.
        :param glob_theta_k: The orientation of the humanoid w.r.t the inertial RF at time step k in the simulation.
        :param glob_x_km1: The CoM X-coordinate of the humanoid w.r.t the inertial RF at time step k-1 in the simulation
        :param glob_y_km1: The CoM Y-coordinate of the humanoid w.r.t the inertial RF at time step k-1 in the simulation
        """
        list_c, list_norm_vec = [], []
        # Get the vector of the CoM position from the current state
        pos_from_state = np.array([loc_x_k, loc_y_k])
        # pos_from_state = [loc_x_k, loc_y_k]

        # Add one constraint for each obstacle in the map
        local_obstacles = []
        for obstacle in self.obstacles:
            #  Convert the obstacle's points in the local RF (i.e. the one of the state)
            local_obstacle = ObstaclesUtils.transform_obstacle_coords(
                obstacle=obstacle, transformation_matrix=self._get_glob_to_loc_rf_trans_mat(
                    glob_theta_k, glob_x_km1, glob_y_km1
                )
            )
            local_obstacles.append(local_obstacle)

        # perform range finder search
        lidar_readings, _, inferred_obstacles = range_finder(
            lidar_position=pos_from_state,
            obstacles=[ch.points for ch in local_obstacles],
            # obstacles = [ch.points for ch in self.obstacles],
            lidar_range=self.lidar_range,
            resolution=self.lidar_resolution
        )

        current_inferred_obstacles = []

        for obstacle in inferred_obstacles:
            local_obstacle = ConvexHull(obstacle)
            current_inferred_obstacles.append(local_obstacle)
            # Find c, i.e. the point on the obstacle's edge closest to (com_x, com_y) and compute
            # the normal vector from (com_x, com_y) to c
            c, normal_vector = ObstaclesUtils.get_closest_point_and_normal_vector_from_obs(
                x=pos_from_state, polygon=local_obstacle, unitary_normal_vector=True,
            )
            list_c.append(c)
            list_norm_vec.append(normal_vector)

        self.list_inferred_obstacles.append(current_inferred_obstacles)
        self.list_lidar_readings.append(lidar_readings)

        return list_c, list_norm_vec


if __name__ == "__main__":
    seed = 10
    ObstaclesUtils.set_random_seed(seed)
    set_seed(seed)

    start, goal = (0, 0), (4, 3.5)

    start, goal, obstacles = Scenario.load_scenario(
        Scenario.CROWDED,
        start,
        goal,
        20,
        range_x=(-1, 6),
        range_y=(-1, 6)
    )

    # initial_state = (start[0], 0, start[1], 0, 0)
    # initial_state = (start[0], 0, start[1], 0, np.pi * 3 / 2)
    initial_state = (start[0], 0, start[1], 0, np.pi/4)

    # mpc = HumanoidMPC(
    mpc = HumanoidMPCUnknownEnvironment(
        N_horizon=3,
        N_mpc_timesteps=300,
        sampling_time=conf["DELTA_T"],
        goal=goal,
        init_state=initial_state,
        obstacles=obstacles,
        verbosity=0,
        lidar_range=1.5
    )

    mpc.run_simulation(path_to_gif=ASSETS_PATH, make_fast_plot=True, plot_animation=False)
