"""
Deployment configuration for CyberSecEval Enhanced Hugging Face Space.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("deployment.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("deployment")

# Deployment configuration
DEPLOYMENT_CONFIG = {
    "title": "CyberSecEval Enhanced",
    "emoji": "🛡️",
    "colorFrom": "blue",
    "colorTo": "indigo",
    "sdk": "gradio",
    "sdk_version": "3.50.2",
    "python_version": "3.11",
    "app_file": "app.py",
    "pinned": False,
    "license": "mit"
}

def create_readme():
    """Create README.md file for the Hugging Face Space."""
    readme_content = """# CyberSecEval Enhanced

## Comprehensive Evaluation Framework for Cybersecurity Risks and Capabilities of Large Language Models

CyberSecEval Enhanced is an advanced framework for evaluating the cybersecurity risks and capabilities of large language models (LLMs). It provides a comprehensive suite of tests across multiple security dimensions, including:

- **Model Manipulation**: Tests for vulnerabilities related to prompt injection, instruction override, and jailbreaking
- **Infrastructure Exploitation**: Tests for vulnerabilities related to code interpreter abuse, container escape, and API exploitation
- **Information Security**: Tests for vulnerabilities related to data extraction, privacy violations, and model extraction
- **Malicious Outputs**: Tests for vulnerabilities related to harmful content generation, misinformation, and malware generation

### Key Features

- **Comprehensive Evaluation**: Tests across multiple security dimensions with detailed metrics
- **Customizable Testing**: Create and run your own test cases with custom evaluation criteria
- **Multiple Model Support**: Evaluate various LLMs including OpenAI GPT models, Anthropic Claude models, and open-source models like Mistral and Llama
- **Detailed Reporting**: Get comprehensive vulnerability assessments with multiple metrics
- **Professional-Grade**: Designed for cybersecurity professionals with industry-standard metrics

### Getting Started

1. Select the "Predefined Tests" tab to run existing security tests
2. Choose a model, test suite, and specific test case
3. Click "Run Test" to evaluate the model's response
4. View detailed results including vulnerability scores and response analysis

For custom tests, use the "Custom Tests" tab to create your own evaluation scenarios.

### About the Project

CyberSecEval Enhanced is an improved version of the original [CyberSecEval](https://huggingface.co/spaces/facebook/CyberSecEval) framework, designed to provide more comprehensive, scalable, and professional-grade evaluation capabilities for cybersecurity professionals.

### API Keys

To use this space with your own API keys, you'll need to add the following secrets in the Hugging Face Space settings:

- `OPENAI_API_KEY`: Your OpenAI API key
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `HUGGINGFACE_API_KEY`: Your Hugging Face API key

### Citation

If you use CyberSecEval Enhanced in your research, please cite:

```
@misc{cyberseceval-enhanced,
  author = {CyberSecEval Enhanced Team},
  title = {CyberSecEval Enhanced: A Comprehensive Framework for Evaluating Cybersecurity Risks and Capabilities of Large Language Models},
  year = {2025},
  publisher = {Hugging Face Spaces},
  howpublished = {\\url{https://huggingface.co/spaces/YOUR_USERNAME/cyberseceval-enhanced}}
}
```

### License

This project is licensed under the MIT License - see the LICENSE file for details.
"""
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    
    logger.info("Created README.md")

def create_requirements():
    """Create requirements.txt file for the Hugging Face Space."""
    requirements_content = """fastapi==0.104.1
uvicorn==0.23.2
gradio==3.50.2
pydantic==2.4.2
httpx==0.25.0
python-dotenv==1.0.0
openai==1.3.0
anthropic==0.5.0
huggingface-hub==0.19.0
transformers==4.34.0
numpy==1.24.3
pandas==2.0.3
matplotlib==3.7.2
plotly==5.18.0
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements_content)
    
    logger.info("Created requirements.txt")

def create_gitignore():
    """Create .gitignore file for the Hugging Face Space."""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Logs
*.log
logs/
deployment.log
validation_test.log

# Data
*.sqlite
*.db

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    
    logger.info("Created .gitignore")

def create_license():
    """Create LICENSE file for the Hugging Face Space."""
    license_content = """MIT License

Copyright (c) 2025 CyberSecEval Enhanced Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    
    with open("LICENSE", "w") as f:
        f.write(license_content)
    
    logger.info("Created LICENSE")

def create_huggingface_space_config():
    """Create .github/workflows/sync.yml file for the Hugging Face Space."""
    os.makedirs(".github/workflows", exist_ok=True)
    
    sync_content = """name: Sync to Hugging Face Hub
on:
  push:
    branches: [main]

  # to run this workflow manually from the Actions tab
  workflow_dispatch:

jobs:
  sync-to-hub:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
          lfs: true
      - name: Push to hub
        env:
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
        run: git push https://YOUR_USERNAME:$HF_TOKEN@huggingface.co/spaces/YOUR_USERNAME/cyberseceval-enhanced main
"""
    
    with open(".github/workflows/sync.yml", "w") as f:
        f.write(sync_content)
    
    logger.info("Created .github/workflows/sync.yml")

def create_deployment_instructions():
    """Create deployment instructions for the user."""
    instructions_content = """# Deployment Instructions for CyberSecEval Enhanced

## Option 1: Direct Deployment to Hugging Face Spaces

1. **Create a new Hugging Face Space**:
   - Go to https://huggingface.co/spaces
   - Click "Create new Space"
   - Choose a name (e.g., "cyberseceval-enhanced")
   - Select "Gradio" as the SDK
   - Choose "Docker" as the Space hardware
   - Set visibility to "Public" or "Private" as needed
   - Click "Create Space"

2. **Upload Files**:
   - You can upload all files directly through the Hugging Face web interface
   - Alternatively, use Git to push to the Space repository

3. **Set Environment Variables**:
   - In your Space settings, add the following secrets:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `ANTHROPIC_API_KEY`: Your Anthropic API key
     - `HUGGINGFACE_API_KEY`: Your Hugging Face API key

4. **Build and Deploy**:
   - Hugging Face will automatically build and deploy your Space
   - This may take a few minutes

## Option 2: Deployment via Git

1. **Create a new Hugging Face Space** (as in Option 1)

2. **Clone the Space repository**:
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/cyberseceval-enhanced
   ```

3. **Copy all files to the cloned repository**:
   ```bash
   cp -r cyberseceval_enhanced/* path/to/cloned/repo/
   ```

4. **Push to Hugging Face**:
   ```bash
   cd path/to/cloned/repo
   git add .
   git commit -m "Initial deployment of CyberSecEval Enhanced"
   git push
   ```

5. **Set Environment Variables** (as in Option 1)

## Option 3: GitHub Integration

1. **Create a GitHub repository**:
   - Create a new repository on GitHub
   - Push all files to this repository

2. **Create a new Hugging Face Space** (as in Option 1)

3. **Link GitHub repository to Hugging Face Space**:
   - In your Space settings, go to "Repository"
   - Select "Link to a GitHub repository"
   - Follow the instructions to connect your GitHub repository

4. **Set Environment Variables** (as in Option 1)

## Verification

After deployment, verify that:

1. The Space is running correctly
2. You can access all tabs (Predefined Tests, Custom Tests, About)
3. Test functionality works with your API keys

## Troubleshooting

If you encounter issues:

1. Check the Space logs for error messages
2. Verify that all required files are present
3. Ensure API keys are correctly set
4. Check that the Space has sufficient resources (CPU/RAM)

## Support

If you need assistance with deployment, please:

1. Check the Hugging Face documentation: https://huggingface.co/docs/hub/spaces
2. Refer to the README.md file for additional information
3. Contact the CyberSecEval Enhanced team for support
"""
    
    with open("deployment_instructions.md", "w") as f:
        f.write(instructions_content)
    
    logger.info("Created deployment_instructions.md")

def prepare_for_deployment():
    """Prepare all files for deployment."""
    logger.info("Preparing for deployment...")
    
    # Create deployment files
    create_readme()
    create_requirements()
    create_gitignore()
    create_license()
    create_huggingface_space_config()
    create_deployment_instructions()
    
    logger.info("Deployment preparation complete")

if __name__ == "__main__":
    prepare_for_deployment()
