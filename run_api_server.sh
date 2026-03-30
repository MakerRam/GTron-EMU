#!/bin/bash

# Start the API server for the firmware emulator
# Usage: ./run_api_server.sh
# The server will be available at http://localhost:5000

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Vision System Monitor - API Server ===${NC}"
echo ""

# Set up Python path
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"
export PATH="/home/ramkumar/.local/bin:$PATH"

cd "$SCRIPT_DIR"

# Check if port 5000 is already in use
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  Port 5000 is already in use${NC}"
    echo "Use: lsof -i :5000 to find the process"
    exit 1
fi

python3 << 'EOF'
import sys
sys.path.insert(0, '.')

from firmware_emulator.src.device_state import DeviceState
from firmware_emulator.src.state_export import StateExporter
from firmware_emulator.src.api_server import APIServer

print("\033[92m✓ Initializing API server...\033[0m")

# Create state and API server (no serial connection needed)
device_state = DeviceState()
state_exporter = StateExporter(device_state)
api_server = APIServer(state_exporter, port=5000)

print("\033[92m✓ API Server starting...\033[0m")
print("")
print("📊 Vision System Monitor API")
print("=" * 50)
print(f"\033[94mServer: http://localhost:5000\033[0m")
print("")
print("Endpoints:")
print(f"  \033[94m/health\033[0m              Health check")
print(f"  \033[94m/api/state\033[0m           Full device state (3-5 KB)")
print(f"  \033[94m/api/state/summary\033[0m   Compact state (150 bytes)")
print("")
print("Usage:")
print("  curl http://localhost:5000/health")
print("  curl http://localhost:5000/api/state | python3 -m json.tool")
print("")
print("\033[93mPress Ctrl+C to stop the server\033[0m")
print("=" * 50)
print("")

try:
    api_server.start()
except KeyboardInterrupt:
    print("\n\033[92m✓ Server stopped\033[0m")
    sys.exit(0)
EOF
