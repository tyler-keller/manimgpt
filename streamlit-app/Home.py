import streamlit as st
import subprocess
import ollama
import uuid
import ast
import re
import os
import anthropic
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv('../.ENV')

model_to_context = {
    'llama3': 8192,
    'deepseek-coder-v2': 16384,
}

def get_ollama_response(messages, model_id):
    try:
        response = ollama.chat(
            model=model_id,
            messages=messages,
            stream=False,
            options={
                'temperature': 0,
                'num_ctx': model_to_context[model_id],
            }
        )
        return response['message']['content']
    except Exception as e:
        print(f'Error getting Ollama response: {e}')
        exit(-1)

def get_anthropic_response(messages, model_id):
    try:
        client = anthropic.Anthropic(api_key=os.getenv(key='ANTHROPIC_API_KEY'))
        message = client.messages.create(
            model=model_id,
            max_tokens=1000,
            temperature=0,
            system=system_message,
            messages=messages
        )
        return message.content
    except Exception as e:
        print(f'Error getting Anthropic response: {e}')
        return e

def get_openai_response(messages, model_id):
    try:
        client = OpenAI(api_key=os.getenv(key=os.getenv(key='OPENAI_API_KEY')))
        completion = client.chat.completions.create(
        model=model_id,
        messages=messages
        )
        return completion.choices[0].message
    except Exception as e:
        print(f'Error getting OpenAI response: {e}')
        return e

def write_python_to_file(filename, python_content):
    try:
        with open(f'./test-scripts/{filename}.py', 'w+') as f:
            f.write(python_content)
    except Exception as e:
        print(f'Error writing to python file: {e}')
        exit(-1)

def parse_python(filename, model_response):
    os.makedirs('./test-scripts', exist_ok=True)
    print(model_response)
    python_match = re.search(r'```(?i:python)?([\s\S]*?)```', model_response)
    if python_match:
        python_code = python_match.group(1).strip()
        if not is_valid_python_code(python_code):
            print('Invalid Python code')
            return None
        write_python_to_file(filename, python_match.group(1).strip())
        return python_code
    else:
        return None

def run_python_file(filename):
    try:
        subprocess.check_output(
            ['manim', '-pql', f'./test-scripts/{filename}.py', filename],
            stderr=subprocess.STDOUT,
            text=True
        )
        return None
    except subprocess.CalledProcessError as e:
        return e.output

def is_valid_python_code(code):
    try:
        ast.parse(code)
        return True
    except SyntaxError as e:
        print(f"SyntaxError: {e}")
        return False

def create_message(role, content):
    return {
        'role': role,
        'content': content
    }

def parse_class_name(code):
    match = re.search(r'class\s+(\w+)\s*\(', code)
    if match:
        return match.group(1)
    return None

def extract_error_info(error_message: str) -> str:
    error_type_message = re.search(r'([A-Za-z]+Error: .+)', error_message)
    if error_type_message:
        error_type_message = error_type_message.group(1)
    else:
        error_type_message = "Error type and message not found."
    return error_type_message

def run_llm(model_id: str, model_type: str, messages: list, user_prompt: str, retry_count: int):
    progress = st.text('Starting runs...')
    filename = str(uuid.uuid4())

    for i in range(retry_count):
        progress.text(f'Run {i} of {retry_count}...')
        if model_type == 'ollama':
            model_response = get_ollama_response(messages, model_id)
        elif model_type == 'anthropic':
            model_response = get_anthropic_response(messages, model_id)
        elif model_type == 'openai':
            model_response = get_openai_response(messages, model_id)
        else:
            st.write('Invalid model type -- this shouldn\'t happen')
        messages.append(create_message('assistant', model_response))
        python_code = parse_python(filename, model_response)
        if not python_code:
            st.write('No code in response. Trying again.')
            messages.append(
                create_message(
                    'user', f'There was no Python code in your last response. Please provide manim code that can {user_prompt}.'
                )
            )
            continue
        class_name = parse_class_name(python_code)
        current_code = st.code(body=python_code, language='python')
        error = run_python_file(filename)
        if error:
            cleaned_error = extract_error_info(error)
            st.write(error)
            st.write(cleaned_error)
            current_code.empty()
            messages.append(
                create_message(
                    'user', f'Python code:\n```python\n{python_code}\n```\nError running python file:\n{cleaned_error}\nIterate and make manim code that can {user_prompt}.'
                )
            )
        else:
            st.video(f'./media/videos/{filename}/480p15/{class_name}.mp4', format='video/mp4')
            break

if __name__ == '__main__':
    system_message = '''You are an AI assistant that turns a user prompt into a visualization using manim.
manim is a Python math animation engine that allows you to create animations programmatically.
The user will ask you to create a specific type of animation and you will have to generate the code for it.

For example, you would generate code in the following format to create a simple "Hello world":
```python
from manim import *

class CreateCircle(Scene):
    def construct(self):
        circle = Circle()  # create a circle
        circle.set_fill(PINK, opacity=0.5)  # set the color and transparency
        self.play(Create(circle))  # show the circle on screen
```

You should only output the manim code for the animation requested by the user. 
It's important that your code run without errors and that it generates the correct animation.
Your response should have your encompassed by triple back ticks in the standard markdown format.

It's important to add self.wait() commands to let the content sit and allow the user to digest it.

You should do the following given a user prompt:
0. Parse the user prompt to understand what the user is asking you to visualize
1. Explain the concept in simple terms and outline a plan to visualize it
2. Execute on your plan and generate the manim code for the visualization

In the case that your code doesn't work, it will be sent back to you by the user along with the error and you will have to iterate so that it can work.
'''

    with st.form(key='form_1'):
        with st.expander(label='SYSTEM MESSAGE'):
            system_message = st.text_area(label='SYSTEM MESSAGE', value=system_message, height=500)
        
        model_id = st.selectbox(label='MODEL', options=['llama3', 'deepseek-coder-v2', 'claude-3-5-sonnet-20240620', 'gpt-3.5-turbo'])

        model_type = ''
        if 'claude' in model_id:
            model_type = 'anthropic'
        elif 'gpt' in model_id and model_id not in model_to_context.keys():
            model_type = 'openai'
        else:
            model_type = 'ollama'

        user_prompt = 'Explain backpropagation using math animation.'
        user_prompt = st.text_area(label='USER PROMPT', value=user_prompt)

        messages = [
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': user_prompt},
        ]

        retry_count = 5
        retry_count = st.number_input(label='RETRY COUNT', value=retry_count, min_value=1)

        st.form_submit_button(label='SUBMIT', on_click=run_llm, args=(model_id, model_type, messages, user_prompt, retry_count))
