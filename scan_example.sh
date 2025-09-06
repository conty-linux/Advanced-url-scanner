#!/bin/bash

# Example scanning script with common use cases

echo "🔍 Advanced URL Scanner - Example Scans"
echo "======================================="

# Ensure we're in the right directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate 2>/dev/null || {
    echo "❌ Virtual environment not found. Run ./install.sh first"
    exit 1
}

# Create sample URLs file if it doesn't exist
if [ ! -f "data/sample_urls.txt" ]; then
    mkdir -p data
    cat > data/sample_urls.txt << 'URLS'
https://google.com
https://github.com
https://stackoverflow.com
https://example.com
https://httpstat.us/200
https://httpstat.us/404
https://httpstat.us/500
https://httpstat.us/301
https://nonexistent-domain-12345.com
https://expired.badssl.com
URLS
    echo "📄 Created sample URLs file: data/sample_urls.txt"
fi

echo ""
echo "Select scan type:"
echo "1) Quick scan (basic)"
echo "2) Detailed scan (full headers)"
echo "3) Stealth scan (slow & careful)"
echo "4) Custom scan"
echo "5) Start web interface"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo "🚀 Starting quick scan..."
        python3 backend/app.py --file data/sample_urls.txt --format json
        ;;
    2)
        echo "🔍 Starting detailed scan..."
        python3 backend/app.py --file data/sample_urls.txt --detailed --format json
        ;;
    3)
        echo "🥷 Starting stealth scan..."
        python3 backend/app.py --file data/sample_urls.txt --stealth --timeout 15 --format json
        ;;
    4)
        echo "⚙️ Custom scan options:"
        read -p "Enter URL file path [data/sample_urls.txt]: " urlfile
        urlfile=${urlfile:-data/sample_urls.txt}
        
        read -p "Enable stealth mode? (y/N): " stealth
        read -p "Detailed headers? (y/N): " detailed
        read -p "Timeout in seconds [10]: " timeout
        timeout=${timeout:-10}
        
        cmd="python3 backend/app.py --file $urlfile --timeout $timeout"
        
        if [[ $stealth =~ ^[Yy]$ ]]; then
            cmd="$cmd --stealth"
        fi
        
        if [[ $detailed =~ ^[Yy]$ ]]; then
            cmd="$cmd --detailed"
        fi
        
        echo "🚀 Running: $cmd"
        eval $cmd
        ;;
    5)
        echo "🌐 Starting web interface..."
        echo "Open http://localhost:5000 in your browser"
        python3 backend/app.py --server
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Scan completed!"
echo "📁 Check the exports/ directory for output files"
