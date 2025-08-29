# Fid

AI for the command line, built for pipelines.

Fid brings Large Language Models (LLMs) directly to your terminal. It can take command output, process it with AI, and return results in formats like Markdown, JSON, or plain text. Think of it as a lightweight way to make your command-line workflows smarter with just a touch of AI.

You can also use [OpenAI], [Cohere], [Groq], or [Azure OpenAI].

[OpenAI]: https://platform.openai.com/account/api-keys
[Cohere]: https://dashboard.cohere.com/api-keys
[Groq]: https://console.groq.com/keys
[Azure OpenAI]: https://azure.microsoft.com/en-us/products/cognitive-services/openai-service

### Installation

```bash
uv pip install fid
```

## What Can It Do?

Fid reads from standard input and pairs it with a prompt you provide via command-line arguments. That input is then sent to an LLM, which generates an answer, formatted in Markdown.

You can configure models in your settings file by running
`fid --settings`.

## Examples

### 1. Summarize logs

```bash
cat /var/log/syslog | fid summarize the key errors
```

### 2. Shell commands

```bash
fid explain "ls -lh /etc"
```

### 3. Get one-liner shell fixes (using a custom role)

```bash
fid --role shell find all .py files modified in the last 24 hours
```

## Usage

- `-m`, `--model`: Specify Large Language Model to use
- `--role`: Specify the role to use (See [custom roles](#custom-roles))
- `--list-roles`: List the roles defined in configuration
- `--settings`: Open settings
- `--dirs`: Print directories where config is stored
- `--reset-settings`: Restore settings to default
- `--version`: Show version

## Custom Roles

Roles allow you to set system prompts. Here is an example of a `shell` role:

```yaml
roles:
  shell:
    - you are a shell expert
    - you do not explain anything
    - you simply output one liners to solve the problems you're asked
    - you do not provide any explanation whatsoever, ONLY the command
```

Then, use the custom role in `fid`:

```sh
fid --role shell list files in the current directory
```

## Setup

### Gemini

Fid uses `gemini-2.0-flash` by default.

Set the `GOOGLE_API_KEY` enviroment variable. If you don't have one yet,
you can get it from the [Google AI Studio](https://aistudio.google.com/apikey).

### Open AI

Set the `OPENAI_API_KEY` environment variable. If you don't have one yet, you
can grab it the [OpenAI website](https://platform.openai.com/account/api-keys).

Alternatively, set the [`AZURE_OPENAI_KEY`] environment variable to use Azure
OpenAI. Grab a key from [Azure](https://azure.microsoft.com/en-us/products/cognitive-services/openai-service).

### Cohere

Cohere provides enterprise optimized models.

Set the `COHERE_API_KEY` environment variable. If you don't have one yet, you can
get it from the [Cohere dashboard](https://dashboard.cohere.com/api-keys).

### Groq

Groq provides models powered by their LPU inference engine.

Set the `GROQ_API_KEY` environment variable. If you don't have one yet, you can
get it from the [Groq console](https://console.groq.com/keys).

## License

[MIT](https://github.com/chamanbravo/fid/raw/main/LICENSE)
