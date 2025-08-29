import asyncio

import readchar
from rich.console import Console
from rich.live import Live
from rich.prompt import Prompt
from rich.table import Table

from .config import Config
from .fid import Fid, run


def select_model(config: Config):
    console = Console()
    options = [
        "google-gla:gemini-2.0-flash",
        "google-gla:gemini-2.0-flash-lite",
        "google-gla:gemini-2.5-flash",
        "google-gla:gemini-2.5-flash-lite",
        "google-gla:gemini-2.5-pro",
    ]
    current_index = 0
    selected_model = None

    def get_menu_table():
        table = Table(box=None, show_header=False)
        for i, option in enumerate(options):
            if i == current_index:
                table.add_row(f"> [bold green]{option}[/bold green]")
            else:
                table.add_row(f"  {option}")
        return table

    console.print("[magenta]Choose the model:[magenta]")
    with Live(get_menu_table(), refresh_per_second=10, console=console) as live:
        while True:
            key = readchar.readkey()
            if key == readchar.key.UP:
                current_index = (current_index - 1) % len(options)
            elif key == readchar.key.DOWN:
                current_index = (current_index + 1) % len(options)
            elif key == readchar.key.ENTER:
                selected_model = options[current_index]
                break
            live.update(get_menu_table())

    if selected_model:
        config.config.default_model = selected_model

        prompt_input = Prompt.ask("\n[magenta]Enter a prompt:[/magenta]\n")
        fid_config = config.config
        fid = Fid(model=fid_config.default_model)
        agent = fid.agent()
        print()
        asyncio.run(run(prompt_input, agent))
