from langchain_community.chat_models import ChatOllama
from langchain.agents import AgentType
from langchain.agents.initialize import initialize_agent
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
import paramiko
import re
import json
from typing import Optional

# Router credentials
router = {
    'hostname': '10.10.20.48',  # Change to your router IP
    'username': 'developer',  # Your username
    'password': 'C1sco12345',  # Your password
    'port': 22,    # SSH port
}

def send_command(command):
    """Helper function to send commands via SSH"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            router['hostname'],
            username=router['username'],
            password=router['password'],
            port=router['port'],
            timeout=20
        )
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        ssh.close()
        if error:
            return f"Error: {error}"
        return output
    except Exception as e:
        return f"Error: {str(e)}"

# Tool: Execute any show command
def execute_show_command(command: str) -> str:
    """Execute any show command on the router"""
    if not command.startswith("show "):
        return "Error: Only show commands are allowed for security reasons."
    try:
        output = send_command(command)
        return f"Command output:\n{output}"
    except Exception as e:
        return f"Error executing command: {str(e)}"

# Tool: Get interface details
def get_interface_details(interface_name: Optional[str] = None) -> str:
    try:
        if interface_name:
            output = send_command(f"show interfaces {interface_name}")
            return f"Interface details:\n{output}"
        else:
            output = send_command("show ip interface brief")
            return f"All interfaces:\n{output}"
    except Exception as e:
        return f"Error: {str(e)}"

# Tool: Get routing information
def get_routing_info(_) -> str:
    try:
        output = send_command("show ip route")
        return f"Routing table:\n{output}"
    except Exception as e:
        return f"Error: {str(e)}"

# Tool: Get interface status
def get_interface_status(_) -> str:
    try:
        output = send_command("show ip interface brief")
        interfaces = []
        for line in output.splitlines()[1:]:  # Skip header
            parts = line.split()
            if len(parts) >= 6:
                interface = {
                    "name": parts[0],
                    "ip": parts[1] if parts[1] != "unassigned" else None,
                    "status": parts[4],
                    "protocol": parts[5]
                }
                interfaces.append(interface)
        return json.dumps({"interfaces": interfaces}, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"

# Tool: Get system resources
def get_system_resources(_) -> str:
    try:
        cpu = send_command("show processes cpu | include CPU")
        memory = send_command("show processes memory | include Processor")
        return f"System Resources:\nCPU Usage:\n{cpu}\nMemory Usage:\n{memory}"
    except Exception as e:
        return f"Error: {str(e)}"

# Tool: Get configuration section
def get_config_section(section: str) -> str:
    try:
        output = send_command(f"show running-config | section {section}")
        return f"Configuration section '{section}':\n{output}"
    except Exception as e:
        return f"Error: {str(e)}"

# Tool: Count interfaces
def count_interfaces(_):
    try:
        output = send_command("show ip interface brief")
        interfaces = re.findall(r'^\S+', output, re.MULTILINE)
        return f"There are {len(interfaces)} interfaces configured."
    except Exception as e:
        return f"Error: {str(e)}"

# Tool: Get loopback IP
def get_loopback_ip(_):
    try:
        output = send_command("show ip interface brief")
        for line in output.splitlines():
            if "Loopback" in line:
                match = re.search(r'\d+\.\d+\.\d+\.\d+', line)
                if match:
                    return f"The loopback IP address is {match.group(0)}"
        return "No loopback interface found."
    except Exception as e:
        return f"Error: {str(e)}"

# Tool: Get hostname
def get_hostname(_):
    try:
        output = send_command("show running-config | include hostname")
        match = re.search(r'hostname\s+(\S+)', output)
        if match:
            return f"The hostname of the router is {match.group(1)}"
        return "Hostname not found."
    except Exception as e:
        return f"Error: {str(e)}"

# Tool: Get uptime
def get_uptime(_):
    try:
        output = send_command("show version")
        for line in output.splitlines():
            if "uptime is" in line:
                return f"Router {line.strip()}"
        return "Uptime not found."
    except Exception as e:
        return f"Error: {str(e)}"

# Define tools for LangChain agent
tools = [
    Tool(
        name="ExecuteShowCommand",
        func=execute_show_command,
        description="Use this to execute any show command on the router. The command must start with 'show'."
    ),
    Tool(
        name="GetInterfaceDetails",
        func=get_interface_details,
        description="Get detailed information about a specific interface or all interfaces. Provide interface name as argument or leave empty for all interfaces."
    ),
    Tool(
        name="GetRoutingInfo",
        func=get_routing_info,
        description="Get the routing table information from the router."
    ),
    Tool(
        name="GetInterfaceStatus",
        func=get_interface_status,
        description="Get a summary of all interface statuses including IP, status, and protocol state."
    ),
    Tool(
        name="GetSystemResources",
        func=get_system_resources,
        description="Get information about CPU and memory usage on the router."
    ),
    Tool(
        name="GetConfigSection",
        func=get_config_section,
        description="Get a specific section of the running configuration. Provide the section name as argument."
    ),
    Tool(
        name="CountInterfaces",
        func=count_interfaces,
        description="Use when asked how many interfaces are on the router."
    ),
    Tool(
        name="GetLoopbackIP",
        func=get_loopback_ip,
        description="Use when asked about the loopback IP address."
    ),
    Tool(
        name="GetHostname",
        func=get_hostname,
        description="Use when asked about the router hostname."
    ),
    Tool(
        name="GetUptime",
        func=get_uptime,
        description="Use when asked about how long the router has been running."
    ),
]

# Set up local LLM (Ollama)
llm = ChatOllama(model="llama3.1")  # Using llama2 which is more stable

# Create memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Create agent with memory
agent_executor = initialize_agent(
    tools,
    llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,  # Changed to conversational agent
    memory=memory,
    verbose=True,
    handle_parsing_errors=True,  # Added error handling
    max_iterations=3  # Limit iterations to prevent infinite loops
)

print("Router Assistant ready! You can ask questions about:")
print("- Interface status and details")
print("- Routing information")
print("- System resources (CPU, memory)")
print("- Configuration sections")
print("- General show commands")
print("Type 'exit' or 'quit' to end the session")

# Ask your router in plain English
while True:
    try:
        query = input("\nAsk the router: ")
        if query.lower() in ['exit', 'quit']:
            break
        answer = agent_executor.invoke({"input": query})["output"]
        print("\nAnswer:", answer)
    except KeyboardInterrupt:
        print("\nExiting...")
        break
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Please try rephrasing your question.")