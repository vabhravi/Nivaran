"""
NIVARAN — API Key Setup Script
Interactive script to configure your Gemini API key.

Usage:
    cd nivaran-backend
    python setup_key.py
"""

import os
import sys

ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')

print("=" * 55)
print("  NIVARAN — Gemini API Key Setup")
print("=" * 55)
print()
print("  Get a FREE API key at:")
print("  👉 https://aistudio.google.com/app/apikey")
print()

# Get the key from user
api_key = input("  Paste your Gemini API key here: ").strip()

if not api_key:
    print("\n  ❌ No key entered. Exiting.")
    sys.exit(1)

if api_key.startswith('your_') or len(api_key) < 10:
    print("\n  ❌ That doesn't look like a valid API key. Exiting.")
    sys.exit(1)

# Write the .env file
with open(ENV_PATH, 'w') as f:
    f.write(f"GEMINI_API_KEY={api_key}\n")
    f.write("SECRET_KEY=nivaran-secret-key-2024\n")

print(f"\n  ✅ API key saved to {ENV_PATH}")
masked = api_key[:8] + "..." + api_key[-4:]
print(f"  ✅ Key: {masked}")

# Test the key
print("\n  Testing API connection...")
try:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Reply with exactly: OK")
    if response and response.text:
        print(f"  ✅ API WORKS! Response: {response.text.strip()[:50]}")
        print("\n" + "=" * 55)
        print("  ALL SET! Now restart your Flask server:")
        print("  python app.py")
        print("=" * 55)
    else:
        print("  ⚠️  API returned empty response. Key may be valid but try again.")
except Exception as e:
    err = str(e)
    if 'API_KEY_INVALID' in err:
        print(f"  ❌ Key is INVALID. Please generate a new one.")
        print(f"     https://aistudio.google.com/app/apikey")
    else:
        print(f"  ❌ API test failed: {err[:150]}")
    sys.exit(1)
