#!/usr/bin/env python3
"""
Startup script for AnomalyAgent API server with proper path configuration
"""

import sys
import os
from pathlib import Path

# Add the current directory and parent directory to Python path
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(parent_dir))

# Set PYTHONPATH environment variable
os.environ['PYTHONPATH'] = f"{current_dir}:{parent_dir}:{os.environ.get('PYTHONPATH', '')}"

# Now import and run the API server
if __name__ == "__main__":
    try:
        from api_server import app
        import uvicorn
        
        print("Starting AnomalyAgent API Server...")
        print(f"Current directory: {current_dir}")
        print(f"Python path: {sys.path[:3]}")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8080,
            reload=False,  # Disable reload to avoid path issues
            log_level="info"
        )
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please ensure all dependencies are installed")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)