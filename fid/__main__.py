import typer

from . import console
from .commands import (
    Dirs,
    FidPrompt,
    InteractiveMode,
    ListRoles,
    ResetConfig,
    Role,
    SelectModel,
    Settings,
    ShowVersion,
)

app = typer.Typer(
    name="Fid",
    help="AI for the command line. Built for pipelines.",
    add_completion=False,
    context_settings={
        "help_option_names": ["-h", "--help"],
    },
    pretty_exceptions_show_locals=False,
    rich_markup_mode="rich",
)


@app.command(
    help="AI for the command line. Built for pipelines.",
    epilog='\033[36mExample:\033[0m cat README.md | fid -p \033[95m"Fix the grammer"\033[0m',
)
def main(
    prompt: list[str] = typer.Argument(None, help="send a prompt", show_default=False),
    model: bool = typer.Option(False, "-m", "--model", help="Specify model"),
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
    version: bool = typer.Option(False, "-v", "--version", help="Show version"),
    dirs: bool = typer.Option(
        False,
        "--dirs",
        help="Print the directories in which fid store its data",
    ),
    settings: bool = typer.Option(
        False, "-s", "--settings", help="Open settings in $EDITOR"
    ),
    reset_settings: bool = typer.Option(
        False,
        "--reset-settings",
        help=" Backup your old settings file and reset everything to the defaults",
    ),
):
    try:
        if model:
            SelectModel().execute()
        if version:
            ShowVersion().execute()
        elif reset_settings:
            ResetConfig().execute()
        elif settings:
            Settings().execute()
        elif dirs:
            Dirs().execute()
        elif list_roles:
            ListRoles().execute()
        elif role:
            Role(role=role, prompt=prompt).execute()
        elif prompt:
            FidPrompt(prompt).execute()
        else:
            InteractiveMode().execute()
    except KeyboardInterrupt:
        console.print("\n[gray62]Operation cancelled by user.[/gray62]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"[red reverse]Error[/red reverse]: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
