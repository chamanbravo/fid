import readchar
from rich.console import Console
from rich.live import Live
from rich.table import Table

console = Console()
options = [
    "google-gla:gemini-2.0-flash",
    "google-gla:gemini-2.0-flash-lite",
    "google-gla:gemini-2.5-flash",
    "google-gla:gemini-2.5-flash-lite",
    "google-gla:gemini-2.5-pro",
]
current_index = 0


def get_menu_table():
    table = Table(box=None)
    for i, option in enumerate(options):
        if i == current_index:
            table.add_row(f"> [bold green]{option}[/bold green]")
        else:
            table.add_row(f"  {option}")
    return table


with Live(get_menu_table(), refresh_per_second=10, console=console) as live:
    while True:
        key = readchar.readkey()
        if key == readchar.key.UP:
            current_index = (current_index - 1) % len(options)
        elif key == readchar.key.DOWN:
            current_index = (current_index + 1) % len(options)
        elif key == readchar.key.ENTER:
            console.print(
                f"You selected: [bold yellow]{options[current_index]}[/bold yellow]"
            )
            break
        live.update(get_menu_table())
