# Networking_NLP
This Repo is dedicated for NLP based tasks in Networking




# Cisco Router AI Assistant

An intelligent CLI tool that allows you to interact with Cisco routers using natural language queries, powered by LangChain and Ollama LLM.

## Features

- 🤖 Natural Language Interface for Cisco Router Management
- 🔒 Secure SSH Connection Management
- 💡 Intelligent Command Processing
- 🧠 Conversation Memory
- 🛠️ Multiple Built-in Tools for Common Tasks

## Prerequisites

- Python 3.9+
- Ollama installed with llama3.1 model
- Access to a Cisco router
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cisco-router-ai-assistant.git
cd cisco-router-ai-assistant
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Edit the router configuration in `NLP.py`:

```python
router = {
    'hostname': '10.10.20.48',  # Change to your router IP
    'username': 'developer',    # Your username
    'password': 'C1sco12345',  # Your password
    'port': 22,                # SSH port
}
```

## Available Commands

The AI assistant can help with:
- Interface status and details
- Routing information
- System resources (CPU, memory)
- Configuration sections
- General show commands
- Interface counting
- Loopback IP information
- Hostname information
- Uptime information

## Usage

1. Start the program:
```bash
python NLP.py
```

2. Ask questions in plain English:
```
Ask the router: What is the current CPU usage?
Ask the router: Show me all interface statuses
Ask the router: What is the router's hostname?
```

3. Type 'exit' or 'quit' to end the session

## Features in Detail

### 1. Natural Language Processing
- Uses LangChain with Ollama LLM for processing natural language queries
- Maintains conversation context using ConversationBufferMemory

### 2. Network Operations
- Secure SSH connections using Paramiko
- Error handling and timeout management
- JSON-formatted output for structured data

### 3. Built-in Tools
- Show command execution
- Interface management
- Routing information
- System resource monitoring
- Configuration section retrieval

## Security Notes

- Always change default credentials
- Use environment variables for sensitive information
- Restrict show commands only for security
- Implement proper access controls on your network


## Acknowledgments

- LangChain for the AI framework
- Ollama for the LLM support
- Paramiko for SSH functionality
