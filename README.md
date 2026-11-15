# Matrix AI — Local Task Agent Prototype

**Python · Django · Ollama · Local AI**

Matrix AI is a prototype that connects a Django task dashboard to a Python worker backed by a locally running Ollama model. The dashboard records work requests; the worker polls for pending tasks, sends prompts to the model, and records results.

> **Security warning:** The documented worker can execute model-generated commands on the host computer. Treat this as experimental software. Do not run it with elevated privileges, untrusted tasks, or access to sensitive files. Review command execution and add sandboxing, allowlists, and approval checks before wider use.

## Architecture

\`\`\`text
Django dashboard
      |
      v
Task database (SQLite)
      |
      v
Python agent worker
      |
      v
Local Ollama model
      |
      v
Host command execution*
      |
      v
Task result stored in database

* Experimental and potentially unsafe without isolation.
\`\`\`

## Requirements

- Python 3.8 or newer, subject to dependency compatibility
- A local Ollama installation
- The \`llama3\` model, unless the worker's model setting is changed
- Python dependencies from \`requirements.txt\`

## Local setup

\`\`\`bash
git clone https://github.com/jjckarthikeyan-dot/Matrix-ai.git
cd Matrix-ai
ollama pull llama3
python -m venv .venv
\`\`\`

Activate the environment:

- macOS/Linux: \`source .venv/bin/activate\`
- Windows PowerShell: \`.venv\Scripts\Activate.ps1\`

\`\`\`bash
pip install -r requirements.txt
python manage.py migrate
\`\`\`

Start the dashboard in one terminal:

\`\`\`bash
python manage.py runserver
\`\`\`

Open http://127.0.0.1:8000/ to inspect the dashboard.

The existing prototype also documents a separate worker process:

\`\`\`bash
python agent.py
\`\`\`

**Only start the worker in an isolated test environment after inspecting its command-execution behavior.** The dashboard alone is the safer first step for exploring the interface.

## Current scope

- Task entry through a Django dashboard
- Polling for pending work
- Local language-model integration through Ollama
- Persisting task results in the application database

## Before production use

1. Require human approval for consequential tool actions.
2. Execute commands within a restricted sandbox rather than the host.
3. Add access controls, secret management, audit logging, and rate limits.
4. Add automated tests, error handling, and deployment documentation.
5. Record measured task reliability and latency rather than assuming production readiness.

## Project status

Experimental prototype. Not described as autonomous, production-ready, or security-hardened.

## Author

[Karthikeyan Jammalamadaka](https://github.com/jjckarthikeyan-dot)
