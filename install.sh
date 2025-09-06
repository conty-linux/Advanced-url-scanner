#!/bin/bash

echo "🚀 Installing Advanced URL Scanner..."

# Check if running on Kali Linux
if ! grep -qi kali /etc/os-release; then
    echo "⚠️ This tool is optimized for Kali Linux"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv curl wget nmap dnsutils git

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# Make scripts executable
chmod +x backend/app.py
chmod +x run.sh
chmod +x scan_example.sh

# Create desktop shortcut
cat > ~/.local/share/applications/url-scanner.desktop << 'DESKTOP'
[Desktop Entry]
Version=1.0
Type=Application
Name=Advanced URL Scanner
Comment=Professional URL monitoring and vulnerability assessment tool
Exec=/bin/bash -c "cd $(dirname '%k') && ./run.sh"
Icon=utilities-system-monitor
Path=$PWD
Terminal=true
StartupNotify=false
Categories=Network;Security;
DESKTOP

echo "✅ Installation completed!"
echo "🚀 Run './run.sh' to start the application"
echo "📖 Check README.md for usage instructions"
