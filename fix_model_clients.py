#!/usr/bin/env python3
"""
Script to fix OpenAI model client configurations
"""

import re
from pathlib import Path

def fix_model_file():
    file_path = Path("src/models/models.py")
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern to match OpenAIServerModel initialization with client=client
    # We need to replace this with proper api_base and api_key parameters
    
    # Find all instances where we have:
    # client = AsyncOpenAI(...) followed by OpenAIServerModel(...client=client...)
    
    pattern = r'''client = AsyncOpenAI\(\s*
                 api_key=api_key,\s*
                 base_url=([^,\)]+),\s*
                 http_client=([^,\)]+),\s*
                 \)\s*
                 model = OpenAIServerModel\(\s*
                 ([^}]*?)
                 client=client,\s*
                 ([^}]*?)
                 \)'''
    
    def replacement(match):
        api_base_line = match.group(1).strip()
        http_client_line = match.group(2).strip()
        before_client = match.group(3).strip()
        after_client = match.group(4).strip()
        
        # Extract api_base variable if it's a function call
        if 'self._check_local_api_base' in api_base_line:
            api_base_var = f"api_base = {api_base_line}"
        else:
            api_base_var = f"api_base = {api_base_line}"
        
        return f'''{api_base_var}
            model = OpenAIServerModel(
                {before_client}
                api_base=api_base,
                api_key=api_key,
                http_client={http_client_line},
                {after_client}
            )'''
    
    # This is complex, so let's just manually fix the patterns we know about
    # Replace the pattern: client=client, with proper parameters
    
    # First, let's just replace client=client with the proper parameters for OpenAIServerModel
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Look for client = AsyncOpenAI( pattern
        if 'client = AsyncOpenAI(' in line:
            # Find the corresponding OpenAIServerModel usage
            j = i + 1
            client_lines = [line]
            
            # Collect all lines until we find the closing parenthesis of AsyncOpenAI
            paren_count = line.count('(') - line.count(')')
            while j < len(lines) and paren_count > 0:
                client_lines.append(lines[j])
                paren_count += lines[j].count('(') - lines[j].count(')')
                j += 1
            
            # Now look for the OpenAIServerModel initialization
            k = j
            while k < len(lines) and 'OpenAIServerModel(' not in lines[k]:
                new_lines.append(lines[k])
                k += 1
            
            if k < len(lines) and 'OpenAIServerModel(' in lines[k]:
                # Found the model initialization, now fix it
                model_lines = [lines[k]]
                paren_count = lines[k].count('(') - lines[k].count(')')
                k += 1
                
                while k < len(lines) and paren_count > 0:
                    model_lines.append(lines[k])
                    paren_count += lines[k].count('(') - lines[k].count(')')
                    k += 1
                
                # Extract api_base from client creation
                client_content = '\n'.join(client_lines)
                api_base_match = re.search(r'base_url=([^,\)]+)', client_content)
                api_base_expr = api_base_match.group(1).strip() if api_base_match else 'None'
                
                # Fix the model initialization
                model_content = '\n'.join(model_lines)
                if 'client=client,' in model_content:
                    # Replace client=client with proper parameters
                    model_content = model_content.replace('client=client,', 
                        f'api_base={api_base_expr},\n                api_key=api_key,\n                http_client=ASYNC_HTTP_CLIENT,')
                
                # Add the fixed model lines
                new_lines.extend(model_content.split('\n'))
                i = k
            else:
                # No OpenAIServerModel found, just add the client lines as-is
                new_lines.extend(client_lines)
                i = j
        else:
            new_lines.append(line)
            i += 1
    
    # Write back
    with open(file_path, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print("Fixed OpenAI model client configurations")

if __name__ == "__main__":
    fix_model_file()