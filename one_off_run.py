import ollama
import re
import os
import subprocess
import uuid
import ast


system_message = '''
You are an AI assistant that turns a user prompt into a visualization using manim.
manim is a Python math animation engine that allows you to create animations programmatically.
The user will ask you to create a specific type of animation and you will have to generate the code for it.

For example, if the user asks you to create a simple square animation, you should generate the following code:
```python
from manim import *

class HelloWorld(Scene):
    def construct(self):
        helloWorld = TextMobject("Hello world!")
        self.play(Write(helloWorld))
        self.wait()
```

You should only output the manim code for the animation requested by the user. 
The code should be encompassed by triple back ticks in the standard markdown format.
You should assume that user requests may require more complex animations.
In that case, you should think step-by-step about how to create the animation and generate the corresponding manim code.

It's important to add sleep() commands to let the content sit and allow the user to digest it.

You're chain of thought should do the following:
1. Identify what the user is asking you to visualize (ie. "the gradient of a function")
2. Identify a plan of action to best visualize the mathematical concept 
'''

model_id = 'llama3'
num_ctx = 8192

def get_response(user_prompt):
    try:
        response = ollama.chat(
            model=model_id,
            messages=[
                {'role': 'system', 'content': system_message},
                {'role': 'user', 'content': f'{user_prompt}'
                },
            ],
            stream=False,
            options={
                'temperature': 0,
                'num_ctx': num_ctx,
            }
        )
        return response['message']['content']
    except Exception as e:
        print(f'Error getting Ollama response: {e}')
        exit(-1)

def parse_python_and_run(model_response):
    try:
        os.makedirs('./test-scripts', exist_ok=True)
        print(model_response)
        python_match = re.search(r'```(?:python)?([\s\S]*?)```', model_response)
        if python_match:
            python_code = python_match.group(1).strip()
            if not is_valid_python_code(python_code):
                print('Invalid Python code')
                return None
            filename = write_python_to_file(python_match.group(1).strip())
            run_python_file(f'./test-scripts/{filename}.py')
        else:
            print('NO PYTHON MATCH!')
            exit(-1)
    except Exception as e:
        print(f'Error running python file: {e}')
        exit(-1)

def write_python_to_file(python_content):
    try:
        filename = str(uuid.uuid4())
        with open(f'./test-scripts/{filename}.py', 'w+') as f:
            f.write(python_content)
        return filename
    except Exception as e:
        print(f'Error writing to python file: {e}')
        exit(-1)

def run_python_file(filename):
    try:
        subprocess.call(['manim', '-pql', filename, 'CreateCircle'])
    except Exception as e:
        print(f'Error running python file: {e}')
        exit(-1)

def is_valid_python_code(code):
    try:
        ast.parse(code)
        return True
    except SyntaxError as e:
        print(f"SyntaxError: {e}")
        return False


if __name__ == '__main__':
    user_prompt = 'explain a gradient'
    valid = False
    while True:
        try:
            model_response = get_response(user_prompt)
            parse_python_and_run(model_response)
            continue
        except Exception as e:
            print(f'Error: {e}')
            continue