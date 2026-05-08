import os
import sys
import time
import django
import subprocess
import requests

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_agent.settings')
django.setup()

from dashboard.models import Task

OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "llama3" # You can change this to whatever model you have pulled in Ollama

def ask_ollama(prompt):
    system_prompt = """You are a highly capable AI agent acting as a company employee.
Your task is to analyze user requests and determine the exact bash/terminal command or python code needed to fulfill them on a local Linux machine.
If the request requires executing a command, output ONLY the command to run, enclosed in triple backticks like so:
```bash
ls -la
```
or
```python
print("Hello")
```
Do not provide any other explanations or conversational text, just the code block.
"""
    full_prompt = f"{system_prompt}\n\nUser Request: {prompt}"

    try:
        response = requests.post(OLLAMA_API_URL, json={
            "model": MODEL_NAME,
            "prompt": full_prompt,
            "stream": False
        })
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Ollama: {e}"

def execute_command(command_str, lang):
    try:
        if lang == 'bash':
            result = subprocess.run(command_str, shell=True, capture_output=True, text=True, timeout=60)
        elif lang == 'python':
            result = subprocess.run(["python3", "-c", command_str], capture_output=True, text=True, timeout=60)
        else:
            return f"Unsupported language: {lang}"

        output = result.stdout
        if result.stderr:
            output += f"\nErrors:\n{result.stderr}"
        return output
    except subprocess.TimeoutExpired:
        return "Command timed out."
    except Exception as e:
        return f"Execution error: {str(e)}"

def parse_and_execute(ollama_response):
    if "```bash" in ollama_response:
        cmd = ollama_response.split("```bash")[1].split("```")[0].strip()
        return execute_command(cmd, 'bash')
    elif "```python" in ollama_response:
        code = ollama_response.split("```python")[1].split("```")[0].strip()
        return execute_command(code, 'python')
    else:
         # Fallback if Ollama didn't format correctly
         return f"Ollama response (no command executed):\n{ollama_response}"

def poll_tasks():
    print("Agent started. Polling for tasks...")
    while True:
        task = Task.objects.filter(status='Pending').first()
        if task:
            print(f"Found pending task: {task.title}")
            task.status = 'In Progress'
            task.save()

            try:
                print(f"Asking Ollama for task: {task.description}")
                ollama_response = ask_ollama(task.description)

                print(f"Executing based on Ollama response...")
                execution_result = parse_and_execute(ollama_response)

                task.status = 'Completed'
                task.result = f"Ollama suggested:\n{ollama_response}\n\nExecution Result:\n{execution_result}"
            except Exception as e:
                task.status = 'Failed'
                task.result = f"Error: {str(e)}"
            finally:
                task.save()

        time.sleep(5)

if __name__ == "__main__":
    poll_tasks()
