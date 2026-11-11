""" Chapter V
Visual representation
Your program must provide a way to display the maze visually, using either:
• Terminal ASCII rendering, or
• A graphical display using the MiniLibX (MLX) library.


The visual should clearly show walls, entry, exit, and the solution path.

User interactions must be available, at least for the following tasks:
• Re-generate a new maze and display it -> OPCIONES 1 Y 2.
• Show/Hide a valid shortest path from the entrance to the exit -> OPCIONES 8 Y 9.
• Change maze wall colours -> OPCION 4
• Optional: set specific colours to display the “42” pattern -> OPCION 7


You can add extra user interactions -> OPCIONES 5 Y 6
"""
import curses
from typing import Callable

from core import Maze
from themes import MAZE_THEMES


class MazeMenu:
    def __init__(self, amazeing_maze: Maze):
        self.maze_menu_options: dict[str, tuple[str, Callable[[], None]]] = {
            "1": ("Re-generate a new maze", self.regenerate_maze),
            "2": ("Display Maze", self.display_maze),
            # creo que esto es inutil, ya que el laberinto se muestra siempre resuelto, resolver el mazo entra dentro de las acciones a realizar en bulce en el programa
            "3": ("Solve Maze", self.solve_maze),
            "4": ("Select Maze Theme", self.select_maze_theme),
            "5": ("Entry Point", self.set_entry_point),
            "6": ("Exit Point", self.set_exit_point),
            "7": ("Display 42 Pattern Colour", self.display_42_pattern_colour),
            "8": ("Show Shortest Path", self.show_shortest_path),
            "9": ("Hide Shortest Path", self.hide_shortest_path),
            "10": ("Exit Program", self.exit_program),
        }
        self.maze: Maze = amazeing_maze

    def display_menu(self) -> None:
        print("Maze Menu:")
        for key, value in self.maze_menu_options.items():
            print(f"{key}. {value[0]}")

    def handle_choice(self) -> Callable[[], None]:
        user_choice = input("Elige una opcion: ").strip()
        while user_choice not in self.maze_menu_options:
            print("Opcion invalida, por favor intentelo de nuevo.")
            user_choice = input("Elige una opcion: ").strip()
        return self.maze_menu_options[user_choice][1]()

    def regenerate_maze(self) -> None:
        print("Regenerating a new maze...")
        # Implement the logic to regenerate a new maze. Creo que hay que ejecutar el mazegenerator

    def display_maze(self) -> None:
        print("Displaying the maze...")
        # Implement the logic to display the maze visually

    def solve_maze(self) -> None:
        print("Solving the maze...")
        # Implement the logic to solve the maze and display the solution path
        maze_solver = "";

    def select_maze_theme(self) -> None:
        maze_themes: list[str] = MAZE_THEMES.keys()
        print(f"Selecting the maze theme ...")
        print(f"Selected theme: {self.maze.get_theme_name()}")
        print("Available Maze Themes:")
        for index, theme in enumerate(maze_themes):
            print(f"{index}: {theme}")
        choice = input("Select a maze theme: ").strip()
        while not choice.isdigit() or not 0 <= int(choice) < len(maze_themes):
            print("Invalid choice. Please try again.")
            choice = input("Select a maze theme: ").strip()
        self.maze.set_maze_theme(maze_themes[int(choice)])
        print(f"Selected theme: {self.maze.get_theme_name()}")
        # CUIDADO, CADA VEZ QUE SE CAMBIA EL THEME HAY QUE EJECUTAR display_maze() con el nuevo tema y visualizarlo creo(con la opcion display-maze).

    def set_entry_point(self) -> None:
        print("Setting entry point...")
        x, y = input(
            "Set the coordinates for the entry point(x,y): "
        ).strip().split(",", 2)
        while not self.maze.is_inside(x, y):
            print("Invalid coordinates. Please try again.")
            x, y = input(
                "Set the coordinates for the entry point(x,y): "
            ).strip().split(",", 2)
        #self.maze.get_maze_config().set_maze_entry_point((x, y))
        self.maze.get_maze_config().maze_entry = (x, y)
        """ CUIDADO:
        HAY QUE VER SI SE HAN DE ABRIR O CERRAR CELDAS CUANDO SE ESTABLECE UN PUNTO DE ENTRADA EN WALLS CERRADOS
        NUNCA PODRA SER EL 42(LA SEED) O EL OTRO PUNTO(EL DE SALIDA)
        """

    def set_exit_point(self) -> None:
        print("Setting exit point...")
        x, y = input(
            "Set the coordinates for the exit point(x,y): "
        ).strip().split(",", 2)
        while not self.maze.is_inside(x, y):
            print("Invalid coordinates. Please try again.")
            x, y = input(
                "Set the coordinates for the exit point(x,y): "
            ).strip().split(",", 2)
        """ CUIDADO:
        HAY QUE VER SI SE HAN DE ABRIR O CERRAR CELDAS CUANDO SE ESTABLECE UN PUNTO DE SALIDA EN WALLS CERRADOS
        NUNCA PODRA SER EL 42(LA SEED) O EL OTRO PUNTO(EL DE ENTRADA)
        """
        self.maze.get_maze_config().maze_exit = (x, y)

    def display_42_pattern_colour(self) -> None:
        print("Displaying 42 pattern colour...")
        # Implement the logic to display the 42 pattern colour

    def show_shortest_path(self) -> None:
        print("Showing the shortest path ...")
        # Implement the logic to show the shortest path from entry to exit

    def hide_shortest_path(self) -> None:
        print("Hiding the shortest path ...")
        # Implement the logic to hide the shortest path from entry to exit

    def exit_program(self) -> None:
        print("Exiting program ...")
        exit()

    def run(self) -> None:
        """Start the interactive terminal menu."""
        curses.wrapper(self._run_menu)

    def _run_menu(self, stdscr: curses.window) -> None:
        """Handle keyboard navigation and menu rendering."""
        curses.curs_set(0)
        stdscr.keypad(True)
        options = list(self.maze_menu_options.values())
        selected = 0
        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()
            title = "A-MAZE-ING"
            stdscr.addstr(1, max(0, (width - len(title)) // 2), title)
            for index, (label, _) in enumerate(options):
                y = 3 + index
                if y >= height - 2:
                    break
                x = 4
                text = f"> {label}" if index == selected else f"  {label}"
                if index == selected:
                    stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(y, x, text[:max(0, width - x - 1)])
                if index == selected:
                    stdscr.attroff(curses.A_REVERSE)
            footer = "UP/DOWN: Navigate | ENTER: Select | ESC: Exit"
            stdscr.addstr(
                height - 1,
                0,
                footer[:max(0, width - 1)]
            )
            stdscr.refresh()
            key = stdscr.getch()
            if key == curses.KEY_UP:
                selected = (selected - 1) % len(options)
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % len(options)
            elif key in (curses.KEY_ENTER, 10, 13):
                # Temporarily leave curses before running normal input/print methods.
                curses.endwin()
                options[selected][1]()
                stdscr.clear()
                #stdscr.refresh() - vibecoding
            elif key == 27:
                break

"""
Una consideración importante: tus métodos actuales utilizan print() e input().
curses controla la terminal y puede interferir con esas operaciones.
En el ejemplo he añadido curses.endwin() antes de ejecutar la opción, para que puedas probarlas con la terminal normal.
Si quieres que, después de ejecutar una opción, el menú siga funcionando de forma fiable,
    conviene restaurar el modo curses tras cada acción y gestionar los mensajes de resultado dentro de la interfaz.

Con esto ya tienes la base de navegación por flechas.
No necesitas implementar todavía el generador ni el solver para probarla:
    puedes seleccionar las opciones que ya tienes y comprobar que se ejecutan cuando pulsas Enter.
"""


"""Compatibility exports for the terminal menu."""

from app.menu import MENU_OPTIONS, Menu, render_menu

__all__ = ["MENU_OPTIONS", "Menu", "render_menu"]