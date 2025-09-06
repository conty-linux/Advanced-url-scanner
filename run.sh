#!/bin/bash

# Advanced URL Scanner Launcher

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "🐍 Virtual environment activated"
else
    echo "⚠️ Virtual environment not found. Run ./install.sh first"
    exit 1
fi

# Parse command line arguments
case "$1" in
    "server"|"web")
        echo "🌐 Starting web server mode..."
        python3 backend/app.py --server --host 127.0.0.1 --port 5000
        ;;
    "cli")
        shift
        echo "💻 Starting CLI mode..."
        python3 backend/app.py "$@"
        ;;
    "docker")
        echo "🐳 Starting with Docker..."
        docker-compose up --build
        ;;
    "help"|"-h"|"--help"|"")
        echo "Advanced URL Scanner - Usage:"
        echo ""
        echo "  ./run.sh server    - Start web server (default: localhost:5000)"
        echo "  ./run.sh cli       - Run in CLI mode"
        echo "  ./run.sh docker    - Run with Docker"
        echo ""
        echo "CLI Examples:"
        echo "  ./run.sh cli --file data/urls.txt"
        echo "  ./run.sh cli --url https://example.com"
        echo "  ./run.sh cli --file data/urls.txt --output results.json"
        echo "  ./run.sh cli --file data/urls.txt --stealth --detailed"
        echo ""
        ;;
    *)
        echo "❌ Unknown option: $1"
        echo "Run './run.sh help' for usage information"
        exit 1
        ;;
esac
