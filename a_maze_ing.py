"""
IV.2 Usage
    Your program must be run with the following command:
        python3 a_maze_ing.py config.txt
    •a_maze_ing.py is your main program file. You must use this name.
    •config.txt is the only argument.
        It is a plain text file that defines the maze generation options.
        You can use a different filename.

    Your program must handle all errors gracefully:
        invalid configuration, file not found, bad
        syntax, impossible maze parameters, etc.
    It must never crash unexpectedly, and must
        always provide a clear error message to the user.
"""

import sys
from core.Maze import Maze
from utils.MazeMenu import MazeMenu
from themes.MazeThemes import MazeThemes
from config.MazeConfig import MazeConfig
from config.MazeConfigParser import MazeConfigParser


def check_a_maze_ing_config(config_file: str):
    """Check the configuration file for the maze generator application.

    Raises:
        ValueError: If the configuration file is invalid.
    """
    config_parser = MazeConfigParser(config_file)
    valid_config, config_message = config_parser.check_file_config_syntax()
    if not valid_config:
        raise ValueError(
            f"Bad syntax in file: {config_parser.config_file}"
            f"Message: {config_message}"
        )
    valid_params, params_message = config_parser.check_maze_parameters()
    if not valid_params:
        raise ValueError(
            f"Impossible maze parameters in file: {config_parser.config_file}"
            f"{config_parser.config_file}: {params_message}"
        )
    """maze_configuration_valid = config_parser.check_maze_configuration()
    if not maze_configuration_valid:
        raise ValueError(
            f"Invalid maze configuration in file {config_parser.config_file}"
        )"""


def a_maze_ing():
    """Run the maze generator application.

    Returns:
        Exit status of the application.
    """
    pass


def main() -> int:
    """Run the maze generator application.

    Returns:
        Exit status of the application.
    """
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return 1
    config_file = sys.argv[1]
    try:
        """maze_menu = MazeMenu(amazeing_maze)
        maze_menu.run()"""
        print(f"Loading configuration from {config_file}")
        # 1. Comprobamos el fichero de configuracion.
        check_a_maze_ing_config(config_file)
        # 2. Una vez se haya validado el fichero de configuracion obtenemos la configuracion.
        maze_config = MazeConfig.from_file(config_file)
        # 3. # Creamos el laberinto con la configuracion obtenida.
        amazeing_maze = Maze(
            maze_config, MazeThemes.MIDNIGHT_CYBER_PALETTE
        )
        # 4. Create MazeGenerator(BFS)
        # 5. Find solution(HUNT-KILL)
        # 6. Write output
        # 7. Display maze -> esto se hara practicamente igual que en el menu.
        # 8. Show menu and repeat
        maze_menu = MazeMenu(amazeing_maze)
        maze_menu.run()
    except (OSError, ValueError, Exception) as error:
        print(f"Error: {error}")
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting...")
    except SystemExit as sys_exit:
        print(f"\nProgram exited with status {sys_exit.code}.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    except BaseException as base_exception:
        print(
            f"\nAn unexpected error of {base_exception.__class__.__name__} has occurred: {base_exception}"
        )
