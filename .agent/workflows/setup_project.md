---
description: Setup Webnovel Architect project after cloning
---

# Webnovel Architect Setup Workflow

Follow these steps to quickly set up the project environment and get the application running at top speed.
Since the environment is Windows, we use Windows-specific activation commands.

// turbo-all

1. Create a Python virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
.\venv\Scripts\activate
```

3. Install the required Python dependencies:
```bash
pip install -r requirements.txt
```

4. Download the required spaCy NLP model:
```bash
python -m spacy download en_core_web_sm
```

5. Run the verification script to ensure the core pipeline is operational:
```bash
python verify_modular.py
```

6. Launch the interactive Streamlit UI:
```bash
streamlit run app_ui.py
```
