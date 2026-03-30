#!/bin/bash

# Start the HTTP server for the visualizer
# Usage: ./run_visualizer_server.sh
# Then open http://localhost:8000/index.html in your browser

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VISUALIZER_DIR="$SCRIPT_DIR/visualizer"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Vision System Monitor - Visualizer Server ===${NC}"
echo ""
echo "Starting HTTP server for visualizer..."
echo "Files served from: $VISUALIZER_DIR"
echo ""

cd "$VISUALIZER_DIR"

# Check if port 8000 is already in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Port 8000 is already in use. Trying port 8001..."
    python3 -m http.server 8001
    echo -e "${GREEN}✓ Visualizer available at: http://localhost:8001/index.html${NC}"
else
    echo -e "${GREEN}✓ Starting HTTP server on port 8000${NC}"
    echo ""
    echo "Open your browser and go to:"
    echo -e "${BLUE}  http://localhost:8000/index.html${NC}"
    echo ""
    echo "Features:"
    echo "  • MOCK mode: Offline state simulation (no emulator needed)"
    echo "  • LIVE mode: Real-time device state from API"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    python3 -m http.server 8000
fi
