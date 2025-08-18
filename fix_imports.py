#!/usr/bin/env python3
"""
Script to fix import statements throughout the codebase.
Replace src. imports with src. imports.
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix imports in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Track if any changes were made
        original_content = content
        
        # Replace src. with src.
        content = re.sub(r'from AnomalyAgent\.src\.', 'from src.', content)
        content = re.sub(r'import AnomalyAgent\.src\.', 'import src.', content)
        
        # Replace absolute imports that might still exist
        content = re.sub(r'AnomalyAgent\.src\.', 'src.', content)
        
        # Write back if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed imports in: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to fix imports in all Python files"""
    root_dir = Path(__file__).parent
    
    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk(root_dir):
        # Skip .git and __pycache__ directories
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache']]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"Found {len(python_files)} Python files")
    
    fixed_count = 0
    for file_path in python_files:
        if fix_imports_in_file(file_path):
            fixed_count += 1
    
    print(f"Fixed imports in {fixed_count} files")

if __name__ == "__main__":
    main()