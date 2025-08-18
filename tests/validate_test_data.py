#!/usr/bin/env python3
"""
Simple test data validation script that doesn't require complex dependencies.
"""

import json
import os
from pathlib import Path

def validate_json_file(file_path):
    """Validate that a file contains valid JSON."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return True, data
    except json.JSONDecodeError as e:
        return False, f"JSON decode error: {e}"
    except Exception as e:
        return False, f"Error reading file: {e}"

def validate_jsonl_file(file_path):
    """Validate that a file contains valid JSONL."""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            if line.strip():  # Skip empty lines
                json.loads(line)
        
        return True, f"Valid JSONL with {len([l for l in lines if l.strip()])} records"
    except json.JSONDecodeError as e:
        return False, f"JSONL decode error on line {i+1}: {e}"
    except Exception as e:
        return False, f"Error reading file: {e}"

def main():
    """Main validation function."""
    test_data_dir = Path(__file__).parent / "test_data"
    
    print("Validating AnomalyAgent Test Data")
    print("=" * 50)
    
    if not test_data_dir.exists():
        print(f"✗ Test data directory not found: {test_data_dir}")
        return False
    
    # Expected test files
    test_files = [
        ("goal_misalignment_trajectory.json", "json"),
        ("goal_misalignment_trajectory.jsonl", "jsonl"),
        ("purpose_deviation_trajectory.json", "json"),
        ("deception_trajectory.json", "json"),
        ("experience_failure_trajectory.json", "json"),
        ("safe_behavior_trajectory.json", "json"),
        ("skywork_format_trajectory.json", "json")
    ]
    
    all_valid = True
    
    for filename, file_type in test_files:
        file_path = test_data_dir / filename
        
        if not file_path.exists():
            print(f"✗ Missing file: {filename}")
            all_valid = False
            continue
        
        if file_type == "json":
            valid, result = validate_json_file(file_path)
        elif file_type == "jsonl":
            valid, result = validate_jsonl_file(file_path)
        else:
            valid, result = False, "Unknown file type"
        
        if valid:
            print(f"✓ {filename}")
            
            # Additional validation for JSON files
            if file_type == "json" and isinstance(result, dict):
                # Check required fields
                required_fields = ["trajectory_id", "agent_name", "behavioral_risk_category"]
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    print(f"  ⚠ Missing fields: {missing_fields}")
                else:
                    print(f"  ✓ Required fields present")
                    print(f"  ✓ Category: {result.get('behavioral_risk_category')}")
                    print(f"  ✓ Risk expected: {result.get('expected_risk_detected')}")
                    
                    if "steps" in result:
                        print(f"  ✓ Steps: {len(result['steps'])}")
        else:
            print(f"✗ {filename}: {result}")
            all_valid = False
    
    print("\n" + "=" * 50)
    if all_valid:
        print("🎉 All test data files are valid!")
        
        # Summary statistics
        print("\nTest Data Summary:")
        risk_categories = set()
        total_steps = 0
        
        for filename, file_type in test_files:
            if file_type == "json":
                file_path = test_data_dir / filename
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    category = data.get('behavioral_risk_category')
                    if category:
                        risk_categories.add(category)
                    
                    steps = data.get('steps', [])
                    total_steps += len(steps)
                except:
                    pass
        
        print(f"- Risk categories covered: {len(risk_categories)}")
        print(f"- Categories: {', '.join(sorted(risk_categories))}")
        print(f"- Total trajectory steps: {total_steps}")
        
        return True
    else:
        print("❌ Some test data files have issues.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)