"""
🚀 A2A System Launcher - Start everything you need
=================================================
"""

import subprocess
import sys
import time
import requests
import os
from pathlib import Path

def find_venv_path():
    """Find the virtual environment activation script"""
    venv_paths = [
        Path(".venv/Scripts/activate.bat"),
        Path("venv/Scripts/activate.bat"),
        Path(".venv/Scripts/Activate.ps1"),
        Path("venv/Scripts/Activate.ps1")
    ]
    
    for path in venv_paths:
        if path.exists():
            return str(path)
    return None

def get_python_executable():
    """Get the Python executable from virtual environment"""
    venv_pythons = [
        Path(".venv/Scripts/python.exe"),
        Path("venv/Scripts/python.exe")
    ]
    
    for python_path in venv_pythons:
        if python_path.exists():
            return str(python_path)
    
    # Fallback to system Python
    return sys.executable

def check_port(port):
    """Check if a port is in use"""
    try:
        response = requests.get(f"http://localhost:{port}", timeout=2)
        return True
    except:
        return False

def start_agent(agent_name, port):
    """Start an individual agent"""
    print(f"🤖 Starting {agent_name} Agent on port {port}...")
    
    # Get the appropriate Python executable
    python_exe = get_python_executable()
    cmd = [python_exe, "-m", f"src.agents.{agent_name.lower()}_agent"]
    
    # Start in new terminal window
    if os.name == 'nt':  # Windows
        venv_path = find_venv_path()
        if venv_path and venv_path.endswith('.bat'):
            # Use batch activation
            full_cmd = f'cd "{os.getcwd()}" && "{venv_path}" && {" ".join(cmd)}'
        elif venv_path and venv_path.endswith('.ps1'):
            # Use PowerShell activation
            full_cmd = f'cd "{os.getcwd()}"; & "{venv_path}"; {" ".join(cmd)}'
        else:
            # No virtual environment found, use system Python
            full_cmd = f'cd "{os.getcwd()}" && {" ".join(cmd)}'
            print(f"⚠️  No virtual environment found, using system Python")
        
        subprocess.Popen([
            "powershell.exe", 
            "-Command", 
            f"Start-Process powershell -ArgumentList '-NoExit', '-Command', '{full_cmd}' -WindowStyle Normal"
        ])
    else:  # Unix/Linux/Mac
        subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"cd {os.getcwd()} && {' '.join(cmd)} && bash"])

def start_web_ui():
    """Start the web UI server"""
    print("🌐 Starting Web UI Server on port 8080...")
    
    # Get the appropriate Python executable
    python_exe = get_python_executable()
    
    if os.name == 'nt':  # Windows
        venv_path = find_venv_path()
        if venv_path and venv_path.endswith('.bat'):
            # Use batch activation
            full_cmd = f'cd "{os.getcwd()}" && "{venv_path}" && {python_exe} web_ui_server.py'
        elif venv_path and venv_path.endswith('.ps1'):
            # Use PowerShell activation
            full_cmd = f'cd "{os.getcwd()}"; & "{venv_path}"; {python_exe} web_ui_server.py'
        else:
            # No virtual environment found, use system Python
            full_cmd = f'cd "{os.getcwd()}" && {python_exe} web_ui_server.py'
            print(f"⚠️  No virtual environment found, using system Python")
        
        subprocess.Popen([
            "powershell.exe",
            "-Command", 
            f"Start-Process powershell -ArgumentList '-NoExit', '-Command', '{full_cmd}' -WindowStyle Normal"
        ])
    else:  # Unix/Linux/Mac
        subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"cd {os.getcwd()} && {python_exe} web_ui_server.py && bash"])

def main():
    print("🚀 A2A SYSTEM LAUNCHER")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("src/agents").exists():
        print("❌ Error: Please run this script from the A2A project root directory")
        print("   Expected directory structure: src/agents/")
        return
    
    # Check virtual environment
    venv_path = find_venv_path()
    python_exe = get_python_executable()
    
    if venv_path:
        print(f"✅ Virtual environment detected: {venv_path}")
    else:
        print("⚠️  No virtual environment found - using system Python")
        print("💡 Recommended: Create virtual environment with 'python -m venv .venv'")
    
    print(f"🐍 Using Python: {python_exe}")
    print()
    
    print("📋 Choose what to start:")
    print("1. 🤖 Start All A2A Agents (ports 9001-9004)")
    print("2. 🌐 Start Web UI Server (port 8080)")
    print("3. 🚀 Start Everything (Agents + Web UI)")
    print("4. 🔍 Check Status")
    print("5. ❌ Exit")
    
    choice = input("\\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        # Start all agents
        agents = [
            ("supervisor", 9001),
            ("milestone", 9002), 
            ("task", 9003),
            ("resource", 9004)
        ]
        
        print("\\n🤖 Starting all A2A agents...")
        for agent_name, port in agents:
            if check_port(port):
                print(f"⚠️  Port {port} is already in use (Agent might be running)")
            else:
                start_agent(agent_name, port)
                time.sleep(1)  # Small delay between starts
        
        print("\\n✅ All agents started!")
        print("💡 Wait 10-15 seconds for all agents to fully initialize")
        print("🧪 Test with: python main.py")
        
    elif choice == "2":
        # Start web UI only
        if check_port(8080):
            print("⚠️  Port 8080 is already in use (Web UI might be running)")
        else:
            start_web_ui()
            print("\\n✅ Web UI Server started!")
            print("🌐 Access at: http://localhost:8080")
        
    elif choice == "3":
        # Start everything
        print("\\n🚀 Starting complete A2A system...")
        
        # Start agents first
        agents = [
            ("supervisor", 9001),
            ("milestone", 9002),
            ("task", 9003), 
            ("resource", 9004)
        ]
        
        for agent_name, port in agents:
            if not check_port(port):
                start_agent(agent_name, port)
                time.sleep(1)
        
        # Wait a bit for agents to start
        print("⏳ Waiting for agents to initialize...")
        time.sleep(5)
        
        # Start web UI
        if not check_port(8080):
            start_web_ui()
        
        print("\\n✅ Complete A2A system started!")
        print("🌐 Web UI: http://localhost:8080")
        print("🤖 Agents running on ports 9001-9004")
        print("💡 Wait 10-15 seconds for full initialization")
        
    elif choice == "4":
        # Check status
        print("\\n🔍 Checking A2A system status...")
        
        services = [
            ("Supervisor Agent", 9001),
            ("Milestone Agent", 9002),
            ("Task Agent", 9003),
            ("Resource Agent", 9004),
            ("Web UI Server", 8080)
        ]
        
        for service_name, port in services:
            if check_port(port):
                print(f"✅ {service_name} - Running on port {port}")
            else:
                print(f"❌ {service_name} - Not running on port {port}")
        
        print("\\n💡 Tips:")
        print("   - Use option 3 to start everything")
        print("   - Check terminal windows for agent logs")
        print("   - Test with Web UI at http://localhost:8080")
        
    elif choice == "5":
        print("👋 Goodbye!")
        return
        
    else:
        print("❌ Invalid choice. Please enter 1-5.")
        return
    
    print("\\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("   1. Wait for all services to fully start (10-15 seconds)")
    print("   2. Open Web UI: http://localhost:8080")
    print("   3. Or test via CLI: python main.py")
    print("   4. Choose a demo scenario and test!")

if __name__ == "__main__":
    main()
