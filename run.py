#!/usr/bin/env python3
"""
Simple run script for AnomalyAgent API server
"""

import subprocess
import sys
import time
from pathlib import Path

def get_api_url():
    """Get the API URL dynamically or use localhost"""
    try:
        # Try to get the public URL from environment or service
        import os
        
        # Check for E2B or cloud environment variables
        if "E2B_SANDBOX_ID" in os.environ:
            sandbox_id = os.environ["E2B_SANDBOX_ID"] 
            return f"https://8081-{sandbox_id}.e2b.dev"
        
        # Default to localhost for local development
        return "http://localhost:8081"
    except:
        return "http://localhost:8081"

def main():
    """Main entry point for running AnomalyAgent"""
    
    print("🚀 AnomalyAgent Behavioral Risk Detection API")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("api_server.py").exists():
        print("❌ Error: api_server.py not found. Run this script from the AnomalyAgent root directory.")
        sys.exit(1)
    
    # Get the API URL
    api_url = get_api_url()
    
    print("📋 Options:")
    print("1. Start API server (supervisor daemon)")
    print("2. Start API server (direct)")  
    print("3. Stop API server")
    print("4. Check status")
    print("5. View logs")
    print("6. Run tests")
    print("7. Show URLs")
    
    choice = input("\n🎯 Select option (1-7): ").strip()
    
    if choice == "1":
        print("🔄 Starting API server with supervisor...")
        result = subprocess.run(["supervisord", "-c", "supervisord.conf"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ API server started successfully!")
            print(f"🌐 API URL: {api_url}")
            print(f"📖 Documentation: {api_url}/docs")
            print(f"🧪 Interactive API: {api_url}/redoc")
        else:
            print(f"❌ Failed to start: {result.stderr}")
    
    elif choice == "2":
        print("🔄 Starting API server directly...")
        print("⚠️  Press Ctrl+C to stop")
        print(f"🌐 API will be available at: {api_url}")
        try:
            subprocess.run([sys.executable, "api_server.py"])
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
    
    elif choice == "3":
        print("🛑 Stopping API server...")
        subprocess.run(["supervisorctl", "-c", "supervisord.conf", "stop", "anomaly_agent_api"])
        print("✅ API server stopped")
    
    elif choice == "4":
        print("📊 Checking status...")
        subprocess.run(["supervisorctl", "-c", "supervisord.conf", "status"])
        
        # Also check API health
        try:
            import requests
            health = requests.get(f"{api_url}/health", timeout=5)
            if health.status_code == 200:
                print("✅ API is responding and healthy")
                print(f"🌐 Available at: {api_url}")
            else:
                print("⚠️ API returned error code:", health.status_code)
        except Exception as e:
            print(f"❌ API is not responding: {e}")
    
    elif choice == "5":
        print("📋 Recent logs:")
        subprocess.run(["supervisorctl", "-c", "supervisord.conf", "tail", "anomaly_agent_api"])
    
    elif choice == "6":
        print("🧪 Running tests...")
        subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])
    
    elif choice == "7":
        print("🔗 API URLs:")
        print(f"   🌐 Main API: {api_url}")
        print(f"   📖 Documentation: {api_url}/docs")
        print(f"   🧪 Interactive API: {api_url}/redoc")
        print(f"   💓 Health Check: {api_url}/health")
        
    else:
        print("❌ Invalid option selected")

if __name__ == "__main__":
    main()