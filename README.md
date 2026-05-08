# Company AI Agent

This project sets up a local, free AI agent acting as a company employee. It utilizes Django for a dashboard to assign tasks and view results, and a Python script (`agent.py`) that polls the database and uses an existing local Ollama installation to execute tasks on the host machine.

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.com/) installed and running locally
- The `llama3` model pulled in Ollama.

## Setup Instructions

1. **Start Ollama and Pull Model**
   Ensure Ollama is running. Pull the required model if you haven't already:
   ```bash
   ollama pull llama3
   ```
   *(Note: You can change the model used by editing the `MODEL_NAME` variable in `agent.py`)*

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup**
   Run the initial migrations to set up the SQLite database:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

## Running the Application

You need two terminal windows to run both the dashboard and the background agent.

1. **Start the Django Dashboard**
   In the first terminal, run:
   ```bash
   python manage.py runserver
   ```
   Access the dashboard at `http://127.0.0.1:8000/`. You can create new tasks here.

2. **Start the AI Agent**
   In the second terminal, start the background polling agent:
   ```bash
   python agent.py
   ```
   The agent will continuously look for tasks in the "Pending" state, ask Ollama for the appropriate command, execute it locally, and save the result back to the database.
