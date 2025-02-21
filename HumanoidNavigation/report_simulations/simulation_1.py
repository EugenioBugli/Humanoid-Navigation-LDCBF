import os

import numpy as np

from HumanoidNavigation.MPC.HumanoidMpc import conf, HumanoidMPC
from HumanoidNavigation.Utils.PlotsUtils import PlotUtils
from HumanoidNavigation.report_simulations.Scenario import Scenario

PLOTS_PATH_BASE = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) + "/Assets/ReportResults/Simulation1"
PLOTS_PATH_CIRCLES = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) + "/Assets/ReportResults/Simulation1Circles"


def run_simulation_1():
    """
    It runs the simulation described in paragraph 1 of the Simulation chapter, and generates all the associated plots.
    """
    initial_state = (0, 0, 0, 0, 0)
    goal_pos = (5, 5)

    sampling_time = conf['DELTA_T']  # 1e-1
    num_steps_per_second = 1 / sampling_time

    _, _, obstacles = Scenario.load_scenario(Scenario.BASE, start=(initial_state[0], initial_state[2]),
                                             goal=goal_pos, seed=7)

    mpc = HumanoidMPC(
        N_horizon=3,
        N_mpc_timesteps=300,
        sampling_time=sampling_time,
        goal=goal_pos,
        init_state=initial_state,
        obstacles=obstacles,
        verbosity=0
    )

    X_pred_glob, U_pred_glob, anim = mpc.run_simulation(path_to_gif=f'{PLOTS_PATH_BASE}/animation.gif',
                                                        make_fast_plot=True,
                                                        plot_animation=False, fill_animator=True)

    PlotUtils.plot_signals([
        (X_pred_glob[[0, 2], :] - np.array([[goal_pos[0]], [goal_pos[1]]]), "Position error", ['X error', 'Y error']),
        (X_pred_glob[[1, 3], :], "Translational velocity", ['X velocity', 'Y velocity']),
        (np.expand_dims(X_pred_glob[4, :], axis=0), "Orientation $\\theta$"),
        (np.expand_dims(U_pred_glob[2, :], axis=0), "Turning rate $\\omega$")
    ], path_to_pdf=f"{PLOTS_PATH_BASE}/evolutions", samples_per_second=num_steps_per_second)

    # anim.plot_animation(path_to_gif=f'{PLOTS_PATH}/animation.gif')
    anim.plot_animation(path_to_gif=f'{PLOTS_PATH_BASE}/animation.gif',
                        path_to_frames_folder=f'{PLOTS_PATH_BASE}/grid_frames')


def run_simulation_circles():
    """
    It runs the circles simulation described in paragraph 1 of the Simulation chapter, and generates all the
     associated plots.
    """
    initial_state = (0, 0, 3, 0, 0)
    goal_pos = (6, -3)

    sampling_time = conf['DELTA_T']  # 1e-1
    num_steps_per_second = 1 / sampling_time

    _, _, obstacles = Scenario.load_scenario(Scenario.CIRCLE_OBSTACLES, start=(initial_state[0], initial_state[2]),
                                             goal=goal_pos)

    mpc = HumanoidMPC(
        N_horizon=3,
        N_mpc_timesteps=300,
        sampling_time=sampling_time,
        goal=goal_pos,
        init_state=initial_state,
        obstacles=obstacles,
        verbosity=0
    )

    X_pred_glob, U_pred_glob, anim = mpc.run_simulation(path_to_gif=f'{PLOTS_PATH_CIRCLES}/animation.gif',
                                                        make_fast_plot=True,
                                                        plot_animation=False, fill_animator=True)

    PlotUtils.plot_signals([
        (X_pred_glob[[0, 2], :] - np.array([[goal_pos[0]], [goal_pos[1]]]), "Position error", ['X error', 'Y error']),
        (X_pred_glob[[1, 3], :], "Translational velocity", ['X velocity', 'Y velocity']),
        (np.expand_dims(X_pred_glob[4, :], axis=0), "Orientation $\\theta$"),
        (np.expand_dims(U_pred_glob[2, :], axis=0), "Turning rate $\\omega$")
    ], path_to_pdf=f"{PLOTS_PATH_CIRCLES}/evolutions", samples_per_second=num_steps_per_second)

    # anim.plot_animation(path_to_gif=f'{PLOTS_PATH_CIRCLES}/animation.gif')
    anim.plot_animation(path_to_gif=f'{PLOTS_PATH_CIRCLES}/animation.gif',
                        path_to_frames_folder=f'{PLOTS_PATH_CIRCLES}/grid_frames')


if __name__ == "__main__":
    run_simulation_1()
    run_simulation_circles()
