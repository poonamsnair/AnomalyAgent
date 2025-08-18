#!/usr/bin/env python3
"""
Test script to use OpenAI directly without litellm
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
root = str(Path(__file__).resolve().parents[0])
sys.path.insert(0, root)

# Set environment variable
os.environ['OPENAI_API_KEY'] = "YOUR_OPENAI_API_KEY_HERE"

print("Testing direct OpenAI usage...")

try:
    print("1. Testing OpenAI import...")
    from openai import AsyncOpenAI
    print("✓ OpenAI imported successfully")
    
    print("2. Testing OpenAI client creation...")
    client = AsyncOpenAI(api_key=os.environ['OPENAI_API_KEY'])
    print("✓ OpenAI client created successfully")
    
    print("3. Testing OpenAI API call...")
    import asyncio
    
    async def test_openai_call():
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": "Say hello in one word"}
            ],
            max_tokens=10
        )
        return response.choices[0].message.content
    
    result = asyncio.run(test_openai_call())
    print(f"✓ OpenAI API call successful. Response: {result}")
    
    print("4. Testing simplified model structure...")
    from src.models.openaillm import OpenAIServerModel
    
    # Create a direct OpenAI model without litellm
    model = OpenAIServerModel(
        model_id="gpt-4o",
        client=client,
        custom_role_conversions={"tool-call": "assistant", "tool-response": "user"}
    )
    print("✓ Direct OpenAI model created successfully")
    
    print("All tests passed! OpenAI direct usage works fine.")
    
except Exception as e:
    print(f"✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()