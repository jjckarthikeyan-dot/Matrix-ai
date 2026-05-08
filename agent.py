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
Your task is to analyze user requests and write comprehensive bash or python scripts to fulfill them on a local Linux machine.
If the request involves multiple steps (e.g., creating a folder, writing code inside it, running a command), write a single script that accomplishes all the steps.
Output ONLY the code to run, enclosed in triple backticks like so:
```bash
mkdir -p myfolder
echo 'print("Hello")' > myfolder/hello.py
python3 myfolder/hello.py
```
or
```python
import os
os.makedirs("myfolder", exist_ok=True)
with open("myfolder/hello.py", "w") as f:
    f.write("print('Hello')")
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
            return False, f"Unsupported language: {lang}"

        output = result.stdout
        if result.returncode != 0 or result.stderr:
            output += f"\nErrors:\n{result.stderr}"
            return False, output
        return True, output
    except subprocess.TimeoutExpired:
        return False, "Command timed out."
    except Exception as e:
        return False, f"Execution error: {str(e)}"

def parse_and_execute(ollama_response):
    if "```bash" in ollama_response:
        cmd = ollama_response.split("```bash")[1].split("```")[0].strip()
        return execute_command(cmd, 'bash')
    elif "```python" in ollama_response:
        code = ollama_response.split("```python")[1].split("```")[0].strip()
        return execute_command(code, 'python')
    else:
         # Fallback if Ollama didn't format correctly
         return False, f"Ollama response formatting error (no valid code block found):\n{ollama_response}"

def poll_tasks():
    print("Agent started. Polling for tasks...")
    while True:
        task = Task.objects.filter(status='Pending').first()
        if task:
            print(f"Found pending task: {task.title}")
            task.status = 'In Progress'
            task.save()

            try:
                max_retries = 3
                current_prompt = task.description
                final_result_log = ""

                for attempt in range(max_retries):
                    print(f"Asking Ollama for task: {task.description} (Attempt {attempt + 1})")
                    ollama_response = ask_ollama(current_prompt)
                    final_result_log += f"--- Attempt {attempt + 1} ---\nOllama Suggested:\n{ollama_response}\n\n"

                    print(f"Executing based on Ollama response...")
                    success, execution_result = parse_and_execute(ollama_response)
                    final_result_log += f"Execution Result:\n{execution_result}\n\n"

                    if success:
                        task.status = 'Completed'
                        task.result = final_result_log
                        break
                    else:
                        print(f"Execution failed. Retrying... Error: {execution_result}")
                        current_prompt = f"Previous request: {task.description}\n\nYour previous code failed with the following error:\n{execution_result}\n\nPlease provide corrected code to accomplish the task."
                else:
                    # Executed all retries and failed
                    task.status = 'Failed'
                    task.result = final_result_log

            except Exception as e:
                task.status = 'Failed'
                task.result = f"Fatal Error: {str(e)}"
            finally:
                task.save()

        time.sleep(5)

if __name__ == "__main__":
    poll_tasks()
