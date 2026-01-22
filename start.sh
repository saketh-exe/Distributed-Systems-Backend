#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Distributed Systems Backend Services...${NC}\n"

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Array to track PIDs
PIDS=()

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}Shutting down all services...${NC}"
    
    # Kill processes by port
    echo "Stopping services on ports..."
    lsof -ti:3000 | xargs -r kill -9 2>/dev/null  # Module 1
    lsof -ti:3001 | xargs -r kill -9 2>/dev/null  # Wrapper
    lsof -ti:3002 | xargs -r kill -9 2>/dev/null  # Module 2 HTTP
    lsof -ti:1099 | xargs -r kill -9 2>/dev/null  # RMI Registry
    lsof -ti:8765 | xargs -r kill -9 2>/dev/null  # Module 4
    
    # Kill Java processes (RMI Server, HTTP Gateway)
    pkill -f "java RMIServer" 2>/dev/null
    pkill -f "java HttpRmiGateway" 2>/dev/null
    pkill -f "rmiregistry" 2>/dev/null
    
    # Kill Python processes
    pkill -f "Module 1/main.py" 2>/dev/null
    pkill -f "Module 4/main.py" 2>/dev/null
    pkill -f "gunicorn.*wrapper:app" 2>/dev/null
    
    # Kill alacritty windows
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null
    done
    
    echo -e "${GREEN}All services stopped and ports released.${NC}"
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT SIGTERM

# Function to run commands in new terminal
run_in_terminal() {
    local title=$1
    local command=$2
    alacritty --title="$title" --hold -e bash -c "$command" &
    PIDS+=($!)
}

# Module 1: Complaint Management System (Socket Server)
echo -e "${YELLOW}Starting Module 1: Complaint Management System...${NC}"
run_in_terminal "Module 1 - Complaints" "cd '$SCRIPT_DIR/Module 1' && python3 main.py"
sleep 2

# Module 2: Hostel Room Management (RMI + HTTP Gateway)
echo -e "${YELLOW}Starting Module 2: Hostel Room Management...${NC}"

# Compile Java files
echo "Compiling Java files..."
cd "Module 2"
javac *.java
if [ $? -ne 0 ]; then
    echo "Java compilation failed!"
    exit 1
fi
cd ..

# Start RMI Registry
run_in_terminal "Module 2 - RMI Registry" "cd '$SCRIPT_DIR/Module 2' && rmiregistry 1099"
sleep 2

# Start RMI Server
run_in_terminal "Module 2 - RMI Server" "cd '$SCRIPT_DIR/Module 2' && java RMIServer"
sleep 2

# Start HTTP Gateway
run_in_terminal "Module 2 - HTTP Gateway" "cd '$SCRIPT_DIR/Module 2' && java HttpRmiGateway"
sleep 2

# Module 4: WebRTC Signaling Server (WebSocket)
echo -e "${YELLOW}Starting Module 4: WebRTC Signaling Server...${NC}"
run_in_terminal "Module 4 - WebRTC" "cd '$SCRIPT_DIR/Module 4' && python3 main.py"
sleep 2

# Wrapper: Main API Gateway (Flask + SocketIO)
echo -e "${YELLOW}Starting Wrapper: Main API Gateway...${NC}"
run_in_terminal "Wrapper - Main API" "cd '$SCRIPT_DIR' && gunicorn -k eventlet -w 1 wrapper:app --bind 0.0.0.0:3001"

echo -e "\n${GREEN}All services started!${NC}"
echo -e "${GREEN}Check the opened terminal tabs for each service.${NC}"
echo -e "\n${YELLOW}Service URLs:${NC}"
echo -e "  - Module 1 (Complaints):     tcp://localhost:3000"
echo -e "  - Module 2 (HTTP Gateway):   http://localhost:3002"
echo -e "  - Module 2 (RMI Registry):   rmi://localhost:1099"
echo -e "  - Module 4 (WebRTC):         ws://localhost:8765"
echo -e "  - Wrapper (Main API):        http://localhost:3001"
echo -e "\n${YELLOW}Press Ctrl+C to stop all services${NC}\n"

# Wait for Ctrl+C
wait
