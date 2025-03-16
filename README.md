# UdS_OP (Universal Desktop Software Operator)

## Overview
UdS_OP is a versatile AI assistant with a desktop interface, designed to help users complete various tasks using natural language instructions. The assistant integrates multiple tools including web browsing, Python code execution, file operations, and web search capabilities, making it a powerful productivity tool for developers, office workers, and general users.

## Features
- **Desktop GUI Interface**: User-friendly interface built with Tkinter
- **Command Line Interface**: Alternative terminal-based interface for power users
- **Web Browsing Capabilities**: Ability to interact with websites and automate web-based tasks
- **Python Code Execution**: Run Python code to solve problems or create applications
- **File Operations**: Save, modify, and manage files on your system
- **Web Search**: Search the web for information to assist with tasks
- **Terminal Commands**: Execute system commands to perform operations
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Architecture
The UdS_OP architecture consists of:
- **Agent System**: Core AI logic for understanding and processing user requests
- **Tool Collection**: Various tools that extend the agent's capabilities
- **Desktop Application**: GUI interface for interacting with the agent
- **Terminal Interface**: Command-line alternative to the GUI

## Requirements
- Python 3.8 or higher
- A compatible operating system (Windows, macOS, Linux)
- Appropriate API keys for LLM services (configured in the Uds_OP/config.toml file similar to config.example.toml)

## Installation

### Step 1: Clone the repository
```bash
git clone https://github.com/sigmabotech/UdS_Operator
cd UdS_Operator
```


### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure the application
Create a `config.toml` file in the UdS_OP directory with your API keys and configuration settings based on the provided example:

```toml
# LLM Configuration
[llm.anthropic]
model = "claude-3-opus-20240229"
base_url = "https://api.anthropic.com/v1"
api_key = "YOUR_ANTHROPIC_API_KEY"
api_type = "Anthropic"
api_version = ""

# Alternative LLM configurations
[llm.openai]
model = "gpt-4-turbo"
base_url = "https://api.openai.com/v1"
api_key = "YOUR_OPENAI_API_KEY"
api_type = "Openai"
api_version = ""

# Browser Configuration
[browser_config]
headless = false
disable_security = true
```

## Usage

### Running the Desktop Application
```bash
cd UdS_OP
python desktop_app.py
```

### Running the Command Line Interface
```bash
cd UdS_OP
python main.py
```

### Example Tasks
- "How many files are in my Downloads folder?"
- "Create a simple calculator webpage with HTML, CSS, and JavaScript"
- "Convert all JPG images in a folder to PNG format"
- "Go to amazon.de and then order the harry potter books"

## APIs, Frameworks, and Tools

### Large Language Models
- **Anthropic Claude**: Primary LLM used for reasoning and task processing
- **OpenAI GPT-4**: Alternative LLM option
- **Ollama**: Optional local LLM support

### Frontend Frameworks
- **Tkinter**: Python's standard GUI toolkit used to build the desktop interface
- **ScrolledText**: Extended text widget with scrolling capabilities
- **ttk**: Themed Tkinter widgets for improved UI

### Backend Libraries
- **asyncio**: Asynchronous I/O library for concurrent operations
- **Pydantic**: Data validation and settings management
- **browser-use**: Browser automation for web interactions
- **requests/httpx**: HTTP clients for web requests

### Development Tools
- **Python 3.8+**: Programming language
- **tomllib**: TOML configuration parser
- **logging**: Structured logging system
- **argparse**: Command-line argument parsing

## Technical Documentation

### Agent System
The UdS_OP agent is built around a flexible architecture that combines:

1. **Tool-Call Agent**: The core agent system that processes requests and calls appropriate tools
2. **Planning System**: A multi-step reasoning approach that breaks down complex tasks
3. **LLM Integration**: Leverages powerful LLMs for reasoning and task understanding

#### Agent Components:
- **udsop.py**: Main agent class that integrates all tools and capabilities
- **toolcall.py**: Handles the tool-calling logic and interaction with LLMs
- **planning.py**: Implements planning capabilities for complex tasks
- **base.py**: Provides the base agent architecture and common functionality

### Tool Collection
UdS_OP integrates multiple tools that extend its capabilities:

1. **PythonExecute**: Executes Python code in a controlled environment
2. **WebSearch**: Searches the web for information using various search engines
3. **BrowserUseTool**: Automates browser interactions for web-based tasks
4. **FileSaver**: Handles file operations like saving, reading, and manipulation
5. **Terminal**: Executes terminal commands with proper sandboxing

### Desktop Application
The desktop application provides a user-friendly interface for interacting with the agent:

1. **Main Window**: Input area, output display, and control buttons
2. **Progress Indicators**: Visual feedback during task processing
3. **History Management**: Conversation history with the agent
4. **Theme Support**: Customizable appearance



### Logs
Logs are stored in the `logs/` directory and can help diagnose issues.

## Development
To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

