import asyncio
import os
import subprocess
import sys

import typer
from rich.console import Console
from rich.prompt import Prompt

from . import __version__
from .config import Config
from .models import select_model
from .pal import Pal, run

console = Console()

config = Config()

app = typer.Typer(
    help="AI Pal on the command line. Built for pipelines.",
    add_completion=False,
    context_settings={
        "help_option_names": ["-h", "--help"],
    },
)


@app.command(
    help="AI Pal on the command line. Built for pipelines.",
    epilog='\033[36mExample:\033[0m cat README.md | pal -p \033[95m"Fix the grammer"\033[0m',
)
def main(
    prompt: list[str] = typer.Argument(None, help="send a prompt", show_default=False),
    model: bool = typer.Option(False, "-m", "--model", help="Specify model"),
    version: bool = typer.Option(False, "-v", "--version", help="Show version"),
    settings: bool = typer.Option(
        False, "-s", "--settings", help="Open settings in $EDITOR"
    ),
    reset_settings: bool = typer.Option(
        False,
        "--reset-settings",
        help=" Backup your old settings file and reset everything to the defaults",
    ),
    dirs: bool = typer.Option(
        False,
        "--dirs",
        help="Print the directories in which pal store its data",
    ),
    role: str = typer.Option(
        None,
        "-r",
        "--role",
        help="System role to use",
        show_default=False,
        metavar="",
    ),
    list_roles: bool = typer.Option(
        False, "--list-roles", help="List the roles defined in your configuration file"
    ),
):
    if model:
        select_model(config)
    elif version:
        console.print(f"Version: {__version__.__version__}")
    elif reset_settings:
        config.reset_settings()
        console.print("Config reset successfully.")
    elif settings:
        editor = os.environ.get("EDITOR", "vim")
        try:
            subprocess.run([editor, str(config.config_file)])
        except FileNotFoundError:
            console.print("[red reverse]ERROR:[/red reverse] Missing $EDITOR")
            console.print(
                f'[dim]exec: "{editor}": executable file not found in %PATH%[/dim]'
            )
            raise typer.Exit(1)
    elif dirs:
        console.print(f"[magenta]Configuration:[/magenta] {config.config_dir}")
    elif list_roles:
        roles = config.config.roles.keys()
        console.print("\n".join(roles))
    elif role:
        prompt_str = " ".join(prompt)
        stdin_data = None
        if not sys.stdin.isatty():
            stdin_data = sys.stdin.read().strip()

        if stdin_data:
            prompt_str = stdin_data + "\n" + prompt_str

        pal_config = config.config
        system_prompt = pal_config.roles.get(role, [])
        pal = Pal(model=pal_config.default_model, system_prompt=system_prompt)
        agent = pal.agent()
        asyncio.run(run(prompt_str, agent))
    elif prompt:
        prompt_str = " ".join(prompt)
        stdin_data = None
        if not sys.stdin.isatty():
            stdin_data = sys.stdin.read().strip()

        if stdin_data:
            prompt_str = stdin_data + "\n" + prompt_str

        pal_config = config.config
        pal = Pal(model=pal_config.default_model)
        agent = pal.agent()
        asyncio.run(run(prompt_str, agent))
    else:
        prompt_input = Prompt.ask("[magenta]Enter a prompt:[/magenta]\n")
        pal_config = config.config
        print()
        pal = Pal(model=pal_config.default_model)
        agent = pal.agent()
        asyncio.run(run(prompt_input, agent))


if __name__ == "__main__":
    app()
