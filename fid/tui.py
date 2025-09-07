import asyncio
import os
from typing import Any

from pydantic_ai.messages import ModelMessagesTypeAdapter
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.command import DiscoveryHit, Hit, Hits, Provider
from textual.containers import Center, Container, Horizontal, Right
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Input, Label, Markdown

from . import __version__
from .config import Configs
from .fid import Fid

logo = f"""
    ███    ███
    ███    ███

████          ████
████          ████
    ██████████
    ██████████

               [dim]v{__version__}[/dim]
"""


class FidCommands(Provider):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._fid_app: "FidTui" = self.app  # pyright: ignore[reportAttributeAccessIssue]
        self.commands: list[dict[str, Any]] = [
            {
                "title": "New",
                "help": "Start new session (crtl + n)",
                "binding": "ctrl+n",
                "command": self._fid_app.action_new_session,
            },
            {
                "title": "Exit",
                "help": "Exit (ctrl + q)",
                "binding": "ctrl+q",
                "command": self.app.exit,
            },
        ]

    async def discover(self) -> Hits:
        for command in self.commands:
            yield DiscoveryHit(
                display=command["title"],
                command=command["command"],
                text=command["title"],
                help=command["help"],
            )

    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)
        app = self.app
        assert isinstance(app, FidTui)

        for command in self.commands:
            command_text = command["title"]
            score = matcher.match(command_text)

            if score > 0:
                yield Hit(
                    score,
                    matcher.highlight(command_text),
                    command["command"],
                    help=command["help"],
                )


class FidScreen(Screen[str]):
    chat = reactive([])
    initialized = False
    history = []

    def __init__(self, app: "FidTui"):
        super().__init__()
        self.app_ref = app

    def compose(self) -> ComposeResult:
        with Container(id="header"):
            yield Label("", id="title")

        with Container(id="chat"):
            ...

        with Container(id="logo-container"):
            with Center():
                yield Label(logo, id="logo")
            with Center():
                yield Label(f"[bold]Hey there, {os.getlogin()}[/bold]", id="greet")

        with Container(id="input-container"):
            with Container(id="input-content"):
                with Center():
                    yield Input(placeholder="type and press enter...", id="input")
                with Horizontal(id="config-info"):
                    yield Label(
                        f"Role [snow on mediumslateblue] {self.app_ref.config.role} [/]",
                        id="role",
                    )
                    with Right():
                        yield Label(
                            f"[dim]{self.app_ref.config.default_model}[/dim]",
                            id="model",
                        )

    async def on_input_submitted(self, message: Input.Submitted):
        if not message.value:
            return

        chat_container = self.query_one("#chat", Container)

        if not self.initialized:
            self.query_one("#title", Label).update(
                f"[mediumslateblue]#[/mediumslateblue] {message.value[:10]}"
            )

            header = self.query_one("#header", Container)
            header.styles.dock = "top"
            header.styles.display = "block"

            chat_container.styles.display = "block"

            input_container = self.query_one("#input-container", Container)
            input_container.styles.dock = "bottom"

            input_content = self.query_one("#input-content", Container)
            input_content.styles.width = "100%"
            input_content.styles.max_width = "100%"

            logo_container = self.query_one("#logo-container", Container)
            logo_container.styles.display = "none"

            self.initialized = True

        self.chat = [
            *self.chat,
            {"role": "user", "text": message.value},
        ]

        input_widget = self.query_one("#input", Input)
        input_widget.value = ""

        loading_label = {"role": "loading", "text": "Firing neurons..."}
        self.chat = [*self.chat, loading_label]

        asyncio.create_task(self.update_chat(message.value))

    async def update_chat(self, message: str):
        async with self.app_ref.agent.agent.run_stream(
            message, message_history=self.history
        ) as result:
            async for res_message in result.stream():
                if self.chat and self.chat[-1]["role"] in (
                    "loading",
                    "ai",
                ):
                    self.chat = [
                        *self.chat[:-1],
                        {"role": "ai", "text": res_message},
                    ]

            prev_messages = result.all_messages()
            self.history = ModelMessagesTypeAdapter.validate_python(prev_messages)

    def watch_chat(self, chat: list[dict[str, str]]):
        chat_container = self.query_one("#chat", Container)
        msg = chat[-1] if len(chat) else {}
        node = chat_container.children[-1] if chat_container.children else None
        if msg:
            msg_type = msg.get("role")
            msg_text: str = msg.get("text") or ""
            if msg_type == "user":
                chat_container.mount(Label(msg_text, classes="message"))
            elif msg_type == "ai":
                if isinstance(node, Markdown) and node:
                    node.update(msg_text)
                elif node:
                    node.remove()
                    chat_container.mount(Markdown(msg_text, classes="ai-message"))
            elif msg_type == "loading":
                chat_container.mount(Label(msg_text, classes="ai-message"))

            self.call_after_refresh(lambda: chat_container.scroll_end(animate=False))


class FidTui(App[str]):
    CSS = """
    Screen {
        align: center middle;
        width: 100%;
    }

    #header {
        border-left: heavy #1E1E1E;
        margin: 1 1;
    }

    #title {
        padding-left: 1;
    }

    #logo-container {
        align: center middle;
        height: auto;
        margin-bottom: 1;
    }

    #input-container {
        align: center middle;
        height: auto;
    }

    #input-content {
        width: 80%;
        max-width: 60;
        height: auto;
    }

    #config-info {
        height: auto;
        padding-top: 1;
    }

    #role {
        padding-left: 1;
    }

    #model {
        padding-right: 1;
    }

    #header {
        height: auto;
        display: none;
    }

    #chat {
        display: none;
        height: 1fr;
        overflow-y: auto;

        scrollbar-size-vertical: 1;
        scrollbar-color: #888 #222;
        scrollbar-color-hover: #ccc #222;
        scrollbar-corner-color: #222;
    }

    .message {
        border-left: heavy steelblue;
        margin: 0 1;
        padding: 1;
        background: #1e1e1e;
        width: 100%;
        margin-bottom: 1;
    }

    .ai-message {
        margin: 0 1;
        padding: 1;
        background: #111111;
        width: 100%;
        margin-bottom: 1;
    }
    """

    COMMANDS = {FidCommands}

    BINDINGS = [
        Binding("ctrl+n", "new_session", "Start new session"),
    ]

    def action_new_session(self) -> None:
        self.pop_screen()
        self.push_screen(FidScreen(self))

    def __init__(self, config: Configs):
        super().__init__()
        self.config = config
        self.system_prompt = self.config.roles.get(self.config.role, [])
        self.agent = Fid(model=config.default_model, system_prompt=self.system_prompt)

    def on_mount(self):
        self.push_screen(FidScreen(self))
