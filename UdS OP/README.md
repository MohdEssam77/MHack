# Udsop Desktop Assistant

A simple desktop application that provides a graphical interface to the powerful Udsop AI agent.

## Features

- Clean, modern user interface using Tkinter
- Ask questions or give instructions to the Udsop agent 
- Special display area for answers to questions
- Conversation history tracking
- Async processing to keep the UI responsive

## Requirements

- Python 3.7+
- Tkinter (included with most Python installations)
- All dependencies from the Udsop agent system

## Installation

1. Ensure you have all the dependencies for the Udsop agent installed
2. Clone this repository or download the files
3. Make sure the `desktop_app.py` file is in the root directory of your Udsop project

## Usage

1. Navigate to your Udsop project directory
2. Run the desktop application:

```bash
python desktop_app.py
```

3. The application window will open
4. Type your instructions or questions in the input box at the bottom
5. Press Enter or click Submit to send your query to the agent
6. View the agent's responses in the conversation area
7. If you asked a question, the answer will also appear in the dedicated answer area at the top

## Keyboard Shortcuts

- **Enter**: Submit your query
- **Ctrl+Enter**: Insert a newline in the input area

## How It Works

The desktop application integrates with the existing Udsop agent system. When you submit a query:

1. The application creates a separate thread to run the agent
2. The agent processes your query using its available tools
3. All output is captured and displayed in the UI
4. If the query is detected as a question, the answer is extracted and displayed in the dedicated answer area

## License

Same as the Udsop project 