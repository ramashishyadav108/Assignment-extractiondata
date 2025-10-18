#!/usr/bin/env python3
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API
api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key found: {api_key[:20]}..." if api_key else "No API key found")

genai.configure(api_key=api_key)

# List all available models
print("\nAvailable Gemini Models:")
print("-" * 80)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✓ {model.name}")
        print(f"  Display Name: {model.display_name}")
        print(f"  Description: {model.description}")
        print(f"  Methods: {model.supported_generation_methods}")
        print()
