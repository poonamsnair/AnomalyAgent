#!/usr/bin/env python3
"""
🚀 AnomalyAgent - Easy Server Startup
=====================================

Simple script to start the AnomalyAgent API server with proper configuration.
Handles environment setup, dependency checking, and provides clear status updates.

Usage: python3 start.py [--port PORT] [--host HOST]
"""

import argparse
import subprocess
import sys
import time
import requests
import os
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("📦 Checking dependencies...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'openai', 'pydantic', 'requests',
        'inflection', 'jsonlines', 'crawl4ai', 'markitdown', 'fastmcp'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("💡 Install with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed")
    return True

def check_api_key():
    """Check if OpenAI API key is configured"""
    print("🔑 Checking API key configuration...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        print("⚠️  OpenAI API key not configured")
        print("💡 Set environment variable: export OPENAI_API_KEY='your-key-here'")
        print("💡 Or update supervisord.conf for production deployment")
        return False
    
    if api_key.startswith('sk-'):
        print("✅ API key configured")
        return True
    else:
        print("❌ Invalid API key format")
        return False

def start_with_supervisor(port=8081):
    """Start server using supervisor (production mode)"""
    print("🏭 Starting server with supervisor (production mode)...")
    
    # Check if supervisord.conf exists
    supervisor_conf = Path("supervisord.conf")
    if not supervisor_conf.exists():
        print("❌ supervisord.conf not found")
        return False
    
    try:
        # Start supervisor
        print("   Starting supervisord...")
        subprocess.run(["supervisord", "-c", "supervisord.conf"], check=True, capture_output=True)
        time.sleep(2)
        
        # Check status
        result = subprocess.run(["supervisorctl", "-c", "supervisord.conf", "status"], 
                              capture_output=True, text=True)
        
        if "RUNNING" in result.stdout:
            print("✅ Server started successfully with supervisor")
            return True
        else:
            print("❌ Server failed to start with supervisor")
            print(f"Status: {result.stdout}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Supervisor startup failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ Supervisor not installed (pip install supervisor)")
        return False

def start_direct(host="0.0.0.0", port=8081):
    """Start server directly (development mode)"""
    print("🛠️ Starting server in development mode...")
    
    try:
        # Start API server directly
        print(f"   Starting API server on {host}:{port}...")
        process = subprocess.Popen([
            sys.executable, "api_server.py"
        ], env=dict(os.environ, HOST=host, PORT=str(port)))
        
        # Wait a moment for startup
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Server started successfully in development mode")
            return True, process
        else:
            print("❌ Server failed to start")
            return False, None
            
    except Exception as e:
        print(f"❌ Direct startup failed: {e}")
        return False, None

def wait_for_api(host="localhost", port=8081, timeout=30):
    """Wait for API to become available"""
    print(f"⏳ Waiting for API to become available at http://{host}:{port}...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"http://{host}:{port}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                models = health_data.get('models_loaded', [])
                print(f"✅ API is ready! Models loaded: {len(models)}")
                return True
        except:
            pass
        
        time.sleep(1)
        print(".", end="", flush=True)
    
    print(f"\n❌ API not available after {timeout}s")
    return False

def show_usage_info(host, port):
    """Show usage information after successful startup"""
    print("\n🎉 ANOMALY AGENT SERVER READY!")
    print("=" * 40)
    print(f"📡 API Server: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print(f"🏥 Health Check: http://{host}:{port}/health")
    print()
    print("🎯 Quick Commands:")
    print("   python3 demo.py      # Run interactive demo")
    print("   python3 test.py      # Run comprehensive tests")
    print("   python3 test.py --quick  # Quick validation")
    print()
    print("🛑 To stop server:")
    print("   Ctrl+C (development mode)")
    print("   supervisorctl -c supervisord.conf stop anomaly_agent_api (production)")

def main():
    """Main startup function"""
    parser = argparse.ArgumentParser(description="Start AnomalyAgent API Server")
    parser.add_argument("--port", type=int, default=8081, help="Server port (default: 8081)")
    parser.add_argument("--host", default="0.0.0.0", help="Server host (default: 0.0.0.0)")
    parser.add_argument("--dev", action="store_true", help="Force development mode")
    parser.add_argument("--prod", action="store_true", help="Force production mode")
    
    args = parser.parse_args()
    
    print("🚀 ANOMALY AGENT - SERVER STARTUP")
    print("=" * 40)
    
    # Pre-flight checks
    if not check_dependencies():
        sys.exit(1)
    
    # API key check (warning only)
    api_key_ok = check_api_key()
    if not api_key_ok:
        print("⚠️  Continuing without API key - some features may not work")
        print()
    
    # Choose startup mode
    use_supervisor = False
    if args.prod:
        use_supervisor = True
    elif args.dev:
        use_supervisor = False
    else:
        # Auto-detect based on environment
        use_supervisor = Path("supervisord.conf").exists() and not args.dev
    
    # Start server
    success = False
    process = None
    
    if use_supervisor:
        success = start_with_supervisor(args.port)
    else:
        success, process = start_direct(args.host, args.port)
    
    if not success:
        print("❌ Failed to start server")
        sys.exit(1)
    
    # Wait for API to be ready
    if wait_for_api(args.host, args.port):
        show_usage_info(args.host, args.port)
        
        # If running in development mode, keep process alive
        if process:
            try:
                print("\n🔄 Server running... Press Ctrl+C to stop")
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping server...")
                process.terminate()
                process.wait()
                print("✅ Server stopped")
    else:
        print("❌ Server startup failed - check logs for details")
        if process:
            process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main()