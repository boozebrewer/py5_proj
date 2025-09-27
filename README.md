# Maxwell's Demon Simulation

This project is a 2D simulation of Maxwell's Demon, a thought experiment that explores the second law of thermodynamics. The simulation is built using Python and the `py5` library, which is a Python version of the Processing creative coding framework.

In this simulation, a "demon" controls a gate between two chambers of a container filled with gas particles. The demon opens and closes the gate to allow faster-moving particles to move to one chamber and slower-moving particles to move to the other, thus creating a temperature difference between the two chambers and seemingly violating the second law of thermodynamics.

## Running the Simulation

To run the simulation, you need to have Python and the `py5` library installed.

1.  **Install dependencies:**

    ```bash
    pip install py5
    ```

2.  **Run the simulation:**

    ```bash
    python main.py
    ```

## Controls

*   **Spacebar:** Pause or resume the simulation.
*   **R:** Reset the simulation to its initial state.
*   **Left/Right Arrow Keys:** Decrease or increase the speed threshold for the demon.

## Features

*   Real-time simulation of gas particles in a 2D environment.
*   Interactive controls to pause, reset, and adjust the simulation parameters.
*   Visualization of the temperature difference between the two chambers.
*   A procedurally generated "demon" character.
*   Plots showing the temperature history and particle speed distribution.

## Files

*   `main.py`: The main entry point for the application.
*   `demon_sketch.py`: The core of the simulation, managing particles, the demon's gate, and the overall simulation state.
*   `particle.py`: Defines the `Particle` class.
*   `drawing.py`: Contains functions for drawing the different elements of the simulation.
*   `config.py`: Stores configuration constants for the simulation.
*   `utils.py`: Provides utility functions.
