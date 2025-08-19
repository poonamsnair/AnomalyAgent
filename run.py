#!/usr/bin/env python3
"""
Simple run script for AnomalyAgent API server
"""

import subprocess
import sys
import time
from pathlib import Path

def main():
    """Main entry point for running AnomalyAgent"""
    
    print("🚀 AnomalyAgent Behavioral Risk Detection API")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("api_server.py").exists():
        print("❌ Error: api_server.py not found. Run this script from the AnomalyAgent root directory.")
        sys.exit(1)
    
    print("📋 Options:")
    print("1. Start API server (supervisor daemon)")
    print("2. Start API server (direct)")  
    print("3. Stop API server")
    print("4. Check status")
    print("5. View logs")
    print("6. Run tests")
    
    choice = input("\n🎯 Select option (1-6): ").strip()
    
    if choice == "1":
        print("🔄 Starting API server with supervisor...")
        result = subprocess.run(["supervisord", "-c", "supervisord.conf"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ API server started successfully!")
            print("🌐 API URL: https://8081-i6ebstkn8678no6p36fel-6532622b.e2b.dev")
            print("📖 Documentation: https://8081-i6ebstkn8678no6p36fel-6532622b.e2b.dev/docs")
        else:
            print(f"❌ Failed to start: {result.stderr}")
    
    elif choice == "2":
        print("🔄 Starting API server directly...")
        print("⚠️  Press Ctrl+C to stop")
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
            health = requests.get("https://8081-i6ebstkn8678no6p36fel-6532622b.e2b.dev/health", timeout=5)
            if health.status_code == 200:
                print("✅ API is responding and healthy")
            else:
                print("⚠️ API returned error code:", health.status_code)
        except:
            print("❌ API is not responding")
    
    elif choice == "5":
        print("📋 Recent logs:")
        subprocess.run(["supervisorctl", "-c", "supervisord.conf", "tail", "anomaly_agent_api"])
    
    elif choice == "6":
        print("🧪 Running tests...")
        subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])
        
    else:
        print("❌ Invalid option selected")

if __name__ == "__main__":
    main()