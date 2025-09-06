# 🔍 Advanced URL Scanner

Professional URL monitoring and vulnerability assessment tool designed for Kali Linux penetration testing environments.

## 🌟 Features

- **File Upload Support**: Upload URL.txt files with bulk URL lists
- **Real-time Scanning**: Live progress tracking and terminal output
- **Multiple Scan Modes**: Fast, detailed, and stealth scanning options
- **Professional Dashboard**: Dark theme, terminal-style interface
- **Categorized Results**: Automatic categorization by HTTP status codes
- **Export Capabilities**: JSON, CSV export formats
- **Copy Functions**: Easy URL copying and bulk operations
- **Responsive Design**: Works on desktop and mobile devices
- **CLI & Web Interface**: Both command-line and web-based operation

## 📦 Installation

### Quick Install (Recommended)
```bash
git clone https://github.com/conty-linux/Advanced-url-scanner.git
cd advanced-url-scanner
chmod +x install.sh
./install.sh
```

### Manual Install
```bash
# Install system dependencies (Kali Linux)
sudo apt update && sudo apt install -y python3 python3-pip python3-venv

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r backend/requirements.txt
```

### Docker Install
```bash
# Build and run with Docker
docker-compose up --build

# Or run specific container
docker build -t url-scanner .
docker run -p 5000:5000 -v $(pwd)/data:/app/data url-scanner
```

## 🚀 Usage

### Web Interface (Recommended)
```bash
./run.sh server
# Open http://localhost:5000 in your browser
```

### Command Line Interface
```bash
# Scan from file
./run.sh cli --file data/urls.txt

# Scan single URL
./run.sh cli --url https://example.com

# Advanced options
./run.sh cli --file data/urls.txt --stealth --detailed --output results.json

# Export results
./run.sh cli --file data/urls.txt --format csv --output scan_results.csv
```

### Example Scans
```bash
# Run example scanning scenarios
./scan_example.sh
```

## 📁 Project Structure
```
advanced-url-scanner/
├── backend/
│   ├── app.py              # Main Python backend
│   ├── requirements.txt    # Python dependencies
│   └── setup.py           # Package setup
├── frontend/
│   └── index.html         # Web dashboard
├── data/
│   └── sample_urls.txt    # Example URL list
├── logs/
│   └── url_scanner.log    # Application logs
├── exports/
│   └── (generated files) # Scan results
├── docs/
├── docker-compose.yml     # Docker configuration
├── Dockerfile            # Docker image
├── install.sh           # Installation script
├── run.sh              # Main launcher
├── scan_example.sh     # Example scenarios
└── README.md          # This file
```

## 🔧 Configuration Options

### Scan Modes
- **Fast**: Basic HTTP status checking
- **Detailed**: Full header analysis and response inspection
- **Stealth**: Slower scanning with delays to avoid detection

### CLI Parameters
```bash
Options:
  --file, -f TEXT          File containing URLs to scan
  --url, -u TEXT           Single URL to scan
  --output, -o TEXT        Output file for results
  --format [json|csv]      Output format (default: json)
  --timeout FLOAT          Request timeout in seconds (default: 10.0)
  --stealth                Enable stealth mode with delays
  --no-ssl-verify          Disable SSL certificate verification
  --detailed               Include detailed header analysis
  --server                 Start web server mode
  --port INTEGER           Web server port (default: 5000)
  --host TEXT              Web server host (default: 127.0.0.1)
```

## 📊 Output Formats

### JSON Output
```json
{
  "scan_info": {
    "timestamp": "2024-01-01T12:00:00",
    "total_urls": 100
  },
  "statistics": {
    "success": 75,
    "redirects": 10,
    "client_errors": 10,
    "server_errors": 3,
    "network_errors": 2
  },
  "categories": {
    "2xx": [...],
    "3xx": [...],
    "4xx": [...],
    "5xx": [...],
    "network": [...]
  }
}
```

### CSV Output
```csv
URL,Status Code,Status Text,Response Time (ms),Server,Content Length,Error,Timestamp
https://example.com,200,OK,234.5,nginx/1.18.0,12345,,2024-01-01T12:00:00
```

## 🌐 Web Dashboard Features

- **File Upload**: Drag & drop URL.txt files
- **Real-time Progress**: Live scanning progress with terminal output
- **Category Views**: Results organized by status code ranges
- **Popup Details**: Detailed information for each URL
- **Copy Functions**: Individual and bulk URL copying
- **Export Options**: Download results in multiple formats
- **Statistics**: Real-time scanning statistics
- **Dark Theme**: Professional terminal-inspired design

## 🔒 Security Features

- **SSL Verification**: Optional SSL certificate validation
- **User-Agent Rotation**: Configurable user-agent strings
- **Rate Limiting**: Built-in request rate limiting
- **Stealth Mode**: Delayed requests to avoid detection
- **Error Handling**: Robust error handling and logging

## 🛠️ Development

### Setting up Development Environment
```bash
# Clone repository
git clone <repository-url>
cd advanced-url-scanner

# Install development dependencies
pip install -r backend/requirements.txt
pip install -r backend/requirements-dev.txt

# Run in development mode
export FLASK_ENV=development
python backend/app.py --server --host 127.0.0.1 --port 5000
```

### Contributing
1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## 📝 Examples

### Sample URL File Format
```
# Comments start with #
https://google.com
https://github.com
https://stackoverflow.com
https://example.com
https://httpstat.us/404
https://httpstat.us/500
```

### API Usage
```bash
# Start server
curl -X POST http://localhost:5000/scan \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com"], "config": {"stealth_mode": true}}'

# Check status
curl http://localhost:5000/status

# Get results
curl http://localhost:5000/results
```

## 🐛 Troubleshooting

### Common Issues

**Port already in use**:
```bash
# Find and kill process using port 5000
sudo lsof -ti:5000 | xargs sudo kill -9
```

**Permission denied**:
```bash
# Make scripts executable
chmod +x install.sh run.sh scan_example.sh
```

**Virtual environment issues**:
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For support, please:
1. Check the troubleshooting section
2. Review the logs in `logs/url_scanner.log`
3. Open an issue on GitHub
4. Contact the development team

## 🔄 Updates

Keep the tool updated:
```bash
git pull origin main
pip install -r backend/requirements.txt --upgrade
```

---

**⚠️ Disclaimer**: This tool is for educational and authorized security testing purposes only. Users are responsible for ensuring they have permission to scan target URLs.
