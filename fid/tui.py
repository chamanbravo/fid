import asyncio
import os

from textual.app import App, ComposeResult
from textual.containers import Center, Container, Horizontal, Right
from textual.reactive import reactive
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

    chat = reactive([])
    initialized = False

    def __init__(self, config: Configs):
        super().__init__()
        self.config = config
        self.system_prompt = self.config.roles.get(self.config.role, [])
        self.agent = Fid(model=config.default_model, system_prompt=self.system_prompt)

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
                        f"Role [snow on mediumslateblue] {self.config.role} [/]",
                        id="role",
                    )
                    with Right():
                        yield Label(
                            f"[dim]{self.config.default_model}[/dim]", id="model"
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

        self.chat = [*self.chat, {"type": "user", "text": message.value}]

        input_widget = self.query_one("#input", Input)
        input_widget.value = ""

        loading_label = {"type": "loading", "text": "Firing neurons..."}
        self.chat = [*self.chat, loading_label]

        asyncio.create_task(self.update_chat(message.value))

    async def update_chat(self, message: str):
        async with self.agent.agent.run_stream(message) as result:
            async for res_message in result.stream():
                if self.chat and self.chat[-1]["type"] in ("loading", "ai"):
                    self.chat = [*self.chat[:-1], {"type": "ai", "text": res_message}]

    def watch_chat(self, chat: list[dict[str, str]]):
        chat_container = self.query_one("#chat", Container)
        msg = chat[-1] if len(chat) else {}
        node = chat_container.children[-1] if chat_container.children else None
        if msg:
            msg_type = msg.get("type")
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
