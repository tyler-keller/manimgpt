# manimgpt

### problem:

there is no good visualization tool for mathematical concepts.

### solution: 

natural language prompts to make manim generated scenes.

### example usage:

USER:

"explain transformers"

GPT:

\```python

\# TODO: manim code that explains transformers

\```

### installation:

there's a requirements.txt that should install all required dependencies:
```bash
pip install -r requirements.txt
```

if you want to run the streamlit-app:
```bash
cd streamlit-app
streamlit run Home.py
```

there are options to run both anthropic and openai models. the app should grab API keys from user environment if they exist. you can also create a .ENV in the root directory w/ valid API keys:
```bash
ANTHROPIC_API_KEY=todo
OPENAI_API_KEY=todo
```

there's a one_off_run.py script (not as up to date -- mostly contains testing):
```bash
python one_off_run.py
```

### TODO:

<!-- - test manim generation w/ default ollama llama 3b -->
<!-- - refine natural language to manim pipeline -->
- learn how to write manim
<!-- - finetune LLMs on manim instruct datasets [following this format](https://huggingface.co/datasets/nickrosh/Evol-Instruct-Code-80k-v1):
    - [most found here...](https://huggingface.co/datasets?search=manim)
    - https://huggingface.co/datasets/mediciresearch/manimation
    - https://huggingface.co/datasets/Edoh/manim_python
    - https://huggingface.co/datasets/generaleoley/manim-codegen
NOT POSSIBLE w/ CURRENT SETUP and KNOWLEDGE -->
