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

For example, you should generate code in the following format to create a simple "Hello world":
```python
from manim import *

class HelloWorld(Scene):
    def construct(self):
        helloWorld = TextMobject("Hello world!")
        self.play(Write(helloWorld))
        self.wait()
```

You should only output the manim code for the animation requested by the user. 
It's important that your code run without errors and that it generates the correct animation.
Your response should have your encompassed by triple back ticks in the standard markdown format.

It's important to add self.wait() commands to let the content sit and allow the user to digest it.

You should do the following given a user prompt:
0. Parse the user prompt to understand what the user is asking you to visualize
1. Explain the concept in simple terms and outline a plan to visualize it
2. Execute on your plan and generate the manim code for the visualization

'''
# ---

# Text below is from the manim quickstart guide:

# This quickstart guide will lead you through creating a sample project using Manim: an animation engine for precise programmatic animations.

# from manim import *

# class CreateCircle(Scene):
#     def construct(self):
#         circle = Circle()  # create a circle
#         circle.set_fill(PINK, opacity=0.5)  # set the color and transparency
#         self.play(Create(circle))  # show the circle on screen

# If you see an animation of a pink circle being drawn, congratulations! You just wrote your first Manim scene from scratch.

# If you get an error message instead, you do not see a video, or if the video output does not look like the preceding animation, it is likely that Manim has not been installed correctly. Please refer to our FAQ section for help with the most common issues.

# Let's go over the script you just executed line by line to see how Manim was able to draw the circle.

# The first line imports all of the contents of the library:

# from manim import *
# This is the recommended way of using Manim, as a single script often uses multiple names from the Manim namespace. In your script, you imported and used Scene, Circle, PINK and Create.

# Now let's look at the next two lines:

# class CreateCircle(Scene):
#     def construct(self):
#         [...]
# Most of the time, the code for scripting an animation is entirely contained within the construct() method of a Scene class. Inside construct(), you can create objects, display them on screen, and animate them.

# The next two lines create a circle and set its color and opacity:

# circle = Circle()  # create a circle
# circle.set_fill(PINK, opacity=0.5)  # set the color and transparency
# Finally, the last line uses the animation Create to display the circle on your screen:

# self.play(Create(circle))  # show the circle on screen
# Tip

# All animations must reside within the construct() method of a class derived from Scene. Other code, such as auxiliary or mathematical functions, may reside outside the class.

# Transforming a square into a circle¶
# With our circle animation complete, let's move on to something a little more complicated.

# Open scene.py, and add the following code snippet below the CreateCircle class:

# class SquareToCircle(Scene):
#     def construct(self):
#         circle = Circle()  # create a circle
#         circle.set_fill(PINK, opacity=0.5)  # set color and transparency

#         square = Square()  # create a square
#         square.rotate(PI / 4)  # rotate a certain amount

#         self.play(Create(square))  # animate the creation of the square
#         self.play(Transform(square, circle))  # interpolate the square into the circle
#         self.play(FadeOut(square))  # fade out animation
# Render SquareToCircle by running the following command in the command line:

# manim -pql scene.py SquareToCircle
# The following animation will render:

# This example shows one of the primary features of Manim: the ability to implement complicated and mathematically intensive animations (such as cleanly interpolating between two geometric shapes) with just a few lines of code.

# Positioning Mobjects¶
# Next, let's go over some basic techniques for positioning Mobjects.

# Open scene.py, and add the following code snippet below the SquareToCircle method:

# class SquareAndCircle(Scene):
#     def construct(self):
#         circle = Circle()  # create a circle
#         circle.set_fill(PINK, opacity=0.5)  # set the color and transparency

#         square = Square()  # create a square
#         square.set_fill(BLUE, opacity=0.5)  # set the color and transparency

#         square.next_to(circle, RIGHT, buff=0.5)  # set the position
#         self.play(Create(circle), Create(square))  # show the shapes on screen
# Render SquareAndCircle by running the following command in the command line:

# manim -pql scene.py SquareAndCircle
# The following animation will render:

# next_to is a Mobject method for positioning Mobjects.

# We first specified the pink circle as the square's reference point by passing circle as the method's first argument. The second argument is used to specify the direction the Mobject is placed relative to the reference point. In this case, we set the direction to RIGHT, telling Manim to position the square to the right of the circle. Finally, buff=0.5 applied a small distance buffer between the two objects.

# Try changing RIGHT to LEFT, UP, or DOWN instead, and see how that changes the position of the square.

# Using positioning methods, you can render a scene with multiple Mobjects, setting their locations in the scene using coordinates or positioning them relative to each other.

# For more information on next_to and other positioning methods, check out the list of Mobject methods in our reference manual.

# Using .animate syntax to animate methods¶
# The final lesson in this tutorial is using .animate, a Mobject method which animates changes you make to a Mobject. When you prepend .animate to any method call that modifies a Mobject, the method becomes an animation which can be played using self.play. Let's return to SquareToCircle to see the differences between using methods when creating a Mobject, and animating those method calls with .animate.

# Open scene.py, and add the following code snippet below the SquareAndCircle class:

# class AnimatedSquareToCircle(Scene):
#     def construct(self):
#         circle = Circle()  # create a circle
#         square = Square()  # create a square

#         self.play(Create(square))  # show the square on screen
#         self.play(square.animate.rotate(PI / 4))  # rotate the square
#         self.play(Transform(square, circle))  # transform the square into a circle
#         self.play(
#             square.animate.set_fill(PINK, opacity=0.5)
#         )  # color the circle on screen
        
# The following animation will render:

# The first self.play creates the square. The second animates rotating it 45 degrees. The third transforms the square into a circle, and the last colors the circle pink. Although the end result is the same as that of SquareToCircle, .animate shows rotate and set_fill being applied to the Mobject dynamically, instead of creating them with the changes already applied.

# Try other methods, like flip or shift, and see what happens.

# Open scene.py, and add the following code snippet below the AnimatedSquareToCircle class:

# class DifferentRotations(Scene):
#     def construct(self):
#         left_square = Square(color=BLUE, fill_opacity=0.7).shift(2 * LEFT)
#         right_square = Square(color=GREEN, fill_opacity=0.7).shift(2 * RIGHT)
#         self.play(
#             left_square.animate.rotate(PI), Rotate(right_square, angle=PI), run_time=2
#         )
#         self.wait()
# Render DifferentRotations by running the following command in the command line:

# manim -pql scene.py DifferentRotations
# The following animation will render:

# This Scene illustrates the quirks of .animate. When using .animate, Manim actually takes a Mobject's starting state and its ending state and interpolates the two. In the AnimatedSquareToCircle class, you can observe this when the square rotates: the corners of the square appear to contract slightly as they move into the positions required for the first square to transform into the second one.

# In DifferentRotations, the difference between .animate's interpretation of rotation and the Rotate method is far more apparent. The starting and ending states of a Mobject rotated 180 degrees are the same, so .animate tries to interpolate two identical objects and the result is the left square. If you find that your own usage of .animate is causing similar unwanted behavior, consider using conventional animation methods like the right square, which uses Rotate.

# Transform vs ReplacementTransform¶
# The difference between Transform and ReplacementTransform is that Transform(mob1, mob2) transforms the points (as well as other attributes like color) of mob1 into the points/attributes of mob2.

# ReplacementTransform(mob1, mob2) on the other hand literally replaces mob1 on the scene with mob2.

# The use of ReplacementTransform or Transform is mostly up to personal preference. They can be used to accomplish the same effect, as shown below.

# class TwoTransforms(Scene):
#     def transform(self):
#         a = Circle()
#         b = Square()
#         c = Triangle()
#         self.play(Transform(a, b))
#         self.play(Transform(a, c))
#         self.play(FadeOut(a))

#     def replacement_transform(self):
#         a = Circle()
#         b = Square()
#         c = Triangle()
#         self.play(ReplacementTransform(a, b))
#         self.play(ReplacementTransform(b, c))
#         self.play(FadeOut(c))

#     def construct(self):
#         self.transform()
#         self.wait(0.5)  # wait for 0.5 seconds
#         self.replacement_transform()
# However, in some cases it is more beneficial to use Transform, like when you are transforming several mobjects one after the other. The code below avoids having to keep a reference to the last mobject that was transformed.

# Example: TransformCycle ¶

# from manim import *

# class TransformCycle(Scene):
#     def construct(self):
#         a = Circle()
#         t1 = Square()
#         t2 = Triangle()
#         self.add(a)
#         self.wait()
#         for t in [t1,t2]:
#             self.play(Transform(a,t))
# class TransformCycle(Scene):
#     def construct(self):
#         a = Circle()
#         t1 = Square()
#         t2 = Triangle()
#         self.add(a)
#         self.wait()
#         for t in [t1,t2]:
#             self.play(Transform(a,t))

model_id = 'llama3'
num_ctx = 8192
# model_id = 'deepseek-coder-v2'
# num_ctx = 16384

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
                'temperature': 0.05,
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
        subprocess.call(['conda', 'env', 'list'])
        subprocess.call(['manim', '-pql', filename, filename])
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
            python = parse_python(model_response)
            error = run_python_file(python)
            if error:
                user_prompt = error
                print(f'Error: {error}')
                continue
            continue
        except Exception as e:
            print(f'Error: {e}')
            continue