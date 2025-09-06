#!/usr/bin/env python3
"""
Advanced URL Scanner Backend
Professional URL monitoring and vulnerability assessment tool for Kali Linux
"""

import asyncio
import aiohttp
import time
import json
import sys
import os
from urllib.parse import urlparse
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import argparse
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import threading
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('url_scanner.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

@dataclass
class ScanResult:
    url: str
    status_code: Optional[int]
    status_text: str
    response_time: float
    headers: Dict[str, str]
    content_length: int
    server: str
    timestamp: str
    error: Optional[str] = None
    redirect_url: Optional[str] = None
    ssl_info: Optional[Dict] = None

@dataclass
class ScanConfig:
    timeout: float = 10.0
    max_redirects: int = 5
    user_agent: str = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    verify_ssl: bool = True
    stealth_mode: bool = False
    detailed_headers: bool = False

class URLScanner:
    def __init__(self, config: ScanConfig):
        self.config = config
        self.session = None
        self.results = []
        self.stats = {
            'total': 0,
            'completed': 0,
            'success': 0,
            'redirects': 0,
            'client_errors': 0,
            'server_errors': 0,
            'network_errors': 0
        }

    async def init_session(self):
        """Initialize aiohttp session with custom configuration"""
        connector = aiohttp.TCPConnector(
            ssl=self.config.verify_ssl,
            limit=100,
            limit_per_host=10,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=30
        )
        
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        
        headers = {
            'User-Agent': self.config.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers
        )

    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()

    async def scan_url(self, url: str) -> ScanResult:
        """Scan a single URL and return detailed results"""
        start_time = time.time()
        
        try:
            # Validate URL
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"Invalid URL format: {url}")
            
            # Make request with stealth delay
            if self.config.stealth_mode:
                await asyncio.sleep(0.5)
            
            async with self.session.get(
                url,
                max_redirects=self.config.max_redirects,
                allow_redirects=True
            ) as response:
                
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                
                # Extract headers
                headers = {}
                if self.config.detailed_headers:
                    headers = dict(response.headers)
                else:
                    # Extract important headers only
                    important_headers = [
                        'server', 'content-type', 'content-length',
                        'cache-control', 'set-cookie', 'x-powered-by'
                    ]
                    headers = {
                        key: response.headers.get(key, '')
                        for key in important_headers
                        if response.headers.get(key)
                    }
                
                # Get content length
                content_length = int(response.headers.get('content-length', 0))
                
                # Get server info
                server = response.headers.get('server', 'Unknown')
                
                # Handle redirects
                redirect_url = None
                if response.status in [301, 302, 303, 307, 308]:
                    redirect_url = response.headers.get('location')
                
                # SSL information (basic)
                ssl_info = None
                if parsed.scheme == 'https':
                    ssl_info = {
                        'secure': True,
                        'version': 'TLS'  # Simplified for demo
                    }
                
                result = ScanResult(
                    url=url,
                    status_code=response.status,
                    status_text=response.reason,
                    response_time=round(response_time, 2),
                    headers=headers,
                    content_length=content_length,
                    server=server,
                    timestamp=datetime.now().isoformat(),
                    redirect_url=redirect_url,
                    ssl_info=ssl_info
                )
                
                # Update stats
                self.update_stats(response.status)
                
                logging.info(f"✅ {url} -> {response.status} ({response_time:.2f}ms)")
                return result
                
        except asyncio.TimeoutError:
            error_msg = "Request timeout"
            logging.warning(f"⏱️ {url} -> Timeout")
        except aiohttp.ClientError as e:
            error_msg = f"Client error: {str(e)}"
            logging.warning(f"❌ {url} -> {error_msg}")
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logging.error(f"💥 {url} -> {error_msg}")
        
        # Return error result
        response_time = (time.time() - start_time) * 1000
        self.stats['network_errors'] += 1
        
        return ScanResult(
            url=url,
            status_code=None,
            status_text="Network Error",
            response_time=round(response_time, 2),
            headers={},
            content_length=0,
            server="Unknown",
            timestamp=datetime.now().isoformat(),
            error=error_msg
        )

    def update_stats(self, status_code: int):
        """Update scanning statistics"""
        self.stats['completed'] += 1
        
        if 200 <= status_code < 300:
            self.stats['success'] += 1
        elif 300 <= status_code < 400:
            self.stats['redirects'] += 1
        elif 400 <= status_code < 500:
            self.stats['client_errors'] += 1
        elif 500 <= status_code < 600:
            self.stats['server_errors'] += 1

    async def scan_urls(self, urls: List[str], callback=None) -> List[ScanResult]:
        """Scan multiple URLs concurrently"""
        self.stats['total'] = len(urls)
        self.stats['completed'] = 0
        
        await self.init_session()
        
        try:
            # Create semaphore to limit concurrent requests
            semaphore = asyncio.Semaphore(20)
            
            async def scan_with_semaphore(url):
                async with semaphore:
                    result = await self.scan_url(url)
                    if callback:
                        await callback(result, self.stats)
                    return result
            
            # Run scans concurrently
            tasks = [scan_with_semaphore(url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and convert to results
            self.results = [
                result for result in results 
                if isinstance(result, ScanResult)
            ]
            
            return self.results
            
        finally:
            await self.close_session()

    def categorize_results(self) -> Dict[str, List[ScanResult]]:
        """Categorize scan results by status code ranges"""
        categories = {
            '2xx': [],  # Success
            '3xx': [],  # Redirects
            '4xx': [],  # Client errors
            '5xx': [],  # Server errors
            'network': []  # Network errors
        }
        
        for result in self.results:
            if result.status_code is None:
                categories['network'].append(result)
            elif 200 <= result.status_code < 300:
                categories['2xx'].append(result)
            elif 300 <= result.status_code < 400:
                categories['3xx'].append(result)
            elif 400 <= result.status_code < 500:
                categories['4xx'].append(result)
            elif 500 <= result.status_code < 600:
                categories['5xx'].append(result)
            else:
                categories['network'].append(result)
        
        return categories

    def export_results(self, filename: str, format: str = 'json'):
        """Export scan results to file"""
        categories = self.categorize_results()
        
        export_data = {
            'scan_info': {
                'timestamp': datetime.now().isoformat(),
                'total_urls': len(self.results),
                'config': asdict(self.config)
            },
            'statistics': self.stats,
            'categories': {
                category: [asdict(result) for result in results]
                for category, results in categories.items()
            }
        }
        
        if format.lower() == 'json':
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
        elif format.lower() == 'csv':
            import csv
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'URL', 'Status Code', 'Status Text', 'Response Time (ms)',
                    'Server', 'Content Length', 'Error', 'Timestamp'
                ])
                for result in self.results:
                    writer.writerow([
                        result.url, result.status_code, result.status_text,
                        result.response_time, result.server, result.content_length,
                        result.error or '', result.timestamp
                    ])
        
        logging.info(f"📄 Results exported to {filename}")

def load_urls_from_file(filepath: str) -> List[str]:
    """Load URLs from text file"""
    urls = []
    try:
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                url = line.strip()
                if url and not url.startswith('#'):
                    # Basic URL validation
                    if url.startswith(('http://', 'https://')):
                        urls.append(url)
                    else:
                        logging.warning(f"⚠️ Invalid URL at line {line_num}: {url}")
        
        logging.info(f"📁 Loaded {len(urls)} URLs from {filepath}")
        return urls
        
    except FileNotFoundError:
        logging.error(f"❌ File not found: {filepath}")
        return []
    except Exception as e:
        logging.error(f"💥 Error reading file {filepath}: {e}")
        return []

# Flask Web Server
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Global scanner instance
scanner = None
scan_task = None
scan_results = []

@app.route('/')
def index():
    """Serve the main dashboard"""
    # In production, serve the HTML file separately
    return "URL Scanner API Server is running. Use /scan endpoint to start scanning."

@app.route('/scan', methods=['POST'])
def start_scan():
    """Start URL scanning"""
    global scanner, scan_task
    
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        config_data = data.get('config', {})
        
        if not urls:
            return jsonify({'error': 'No URLs provided'}), 400
        
        # Create scan configuration
        config = ScanConfig(
            timeout=config_data.get('timeout', 10.0),
            max_redirects=config_data.get('max_redirects', 5),
            user_agent=config_data.get('user_agent', 'URL-Scanner/1.0'),
            verify_ssl=config_data.get('verify_ssl', True),
            stealth_mode=config_data.get('stealth_mode', False),
            detailed_headers=config_data.get('detailed_headers', False)
        )
        
        scanner = URLScanner(config)
        
        # Start scanning in background
        def run_scan():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            global scan_results
            scan_results = loop.run_until_complete(scanner.scan_urls(urls))
        
        scan_task = threading.Thread(target=run_scan)
        scan_task.start()
        
        return jsonify({
            'message': 'Scan started',
            'total_urls': len(urls),
            'scan_id': int(time.time())
        })
        
    except Exception as e:
        logging.error(f"Error starting scan: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status')
def scan_status():
    """Get current scan status"""
    global scanner
    
    if not scanner:
        return jsonify({'status': 'idle'})
    
    return jsonify({
        'status': 'running' if scan_task and scan_task.is_alive() else 'completed',
        'stats': scanner.stats,
        'progress': scanner.stats['completed'] / max(scanner.stats['total'], 1) * 100
    })

@app.route('/results')
def get_results():
    """Get scan results"""
    global scanner, scan_results
    
    if not scanner or not scan_results:
        return jsonify({'results': [], 'categories': {}})
    
    categories = scanner.categorize_results()
    
    return jsonify({
        'results': [asdict(result) for result in scan_results],
        'categories': {
            category: [asdict(result) for result in results]
            for category, results in categories.items()
        },
        'stats': scanner.stats
    })

@app.route('/export/<format>')
def export_results(format):
    """Export results in specified format"""
    global scanner
    
    if not scanner or not scan_results:
        return jsonify({'error': 'No results to export'}), 400
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'scan_results_{timestamp}.{format}'
    
    try:
        scanner.export_results(filename, format)
        return jsonify({
            'message': f'Results exported to {filename}',
            'filename': filename
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

async def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description='Advanced URL Scanner')
    parser.add_argument('--file', '-f', help='File containing URLs to scan')
    parser.add_argument('--url', '-u', help='Single URL to scan')
    parser.add_argument('--output', '-o', help='Output file for results')
    parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Output format')
    parser.add_argument('--timeout', type=float, default=10.0, help='Request timeout in seconds')
    parser.add_argument('--stealth', action='store_true', help='Enable stealth mode')
    parser.add_argument('--no-ssl-verify', action='store_true', help='Disable SSL verification')
    parser.add_argument('--detailed', action='store_true', help='Detailed headers analysis')
    parser.add_argument('--server', action='store_true', help='Start web server mode')
    parser.add_argument('--port', type=int, default=5000, help='Web server port')
    parser.add_argument('--host', default='127.0.0.1', help='Web server host')
    
    args = parser.parse_args()
    
    if args.server:
        # Start Flask web server
        logging.info(f"🚀 Starting URL Scanner Web Server on {args.host}:{args.port}")
        app.run(host=args.host, port=args.port, debug=False, threaded=True)
        return
    
    # CLI Mode
    urls = []
    
    if args.file:
        urls.extend(load_urls_from_file(args.file))
    
    if args.url:
        urls.append(args.url)
    
    if not urls:
        logging.error("❌ No URLs to scan. Use --file or --url")
        return
    
    # Create scanner configuration
    config = ScanConfig(
        timeout=args.timeout,
        verify_ssl=not args.no_ssl_verify,
        stealth_mode=args.stealth,
        detailed_headers=args.detailed
    )
    
    scanner = URLScanner(config)
    
    logging.info(f"🔍 Starting scan of {len(urls)} URLs")
    
    async def progress_callback(result: ScanResult, stats: dict):
        """Progress callback for real-time updates"""
        progress = stats['completed'] / stats['total'] * 100
        print(f"\rProgress: {progress:.1f}% ({stats['completed']}/{stats['total']})", end='')
    
    # Start scanning
    results = await scanner.scan_urls(urls, progress_callback)
    print()  # New line after progress
    
    # Display results summary
    categories = scanner.categorize_results()
    
    print("\n" + "="*60)
    print("📊 SCAN RESULTS SUMMARY")
    print("="*60)
    print(f"Total URLs scanned: {len(results)}")
    print(f"✅ Success (2xx): {len(categories['2xx'])}")
    print(f"🔄 Redirects (3xx): {len(categories['3xx'])}")
    print(f"⚠️ Client Errors (4xx): {len(categories['4xx'])}")
    print(f"💥 Server Errors (5xx): {len(categories['5xx'])}")
    print(f"🔌 Network Errors: {len(categories['network'])}")
    print("="*60)
    
    # Display top findings
    for category, results_list in categories.items():
        if results_list:
            print(f"\n{category.upper()} Results:")
            for result in results_list[:5]:  # Show first 5
                status = result.status_code if result.status_code else "ERROR"
                print(f"  {status} | {result.response_time:>6.2f}ms | {result.url}")
            if len(results_list) > 5:
                print(f"  ... and {len(results_list) - 5} more")
    
    # Export results
    if args.output:
        scanner.export_results(args.output, args.format)
    else:
        # Auto-generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'scan_results_{timestamp}.{args.format}'
        scanner.export_results(filename, args.format)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("\n⏹️ Scan interrupted by user")
    except Exception as e:
        logging.error(f"💥 Fatal error: {e}")
        sys.exit(1)
