"""
NIVARAN — API Key Diagnostic Script
Run this to verify your Gemini API key is correctly configured.

Usage:
    cd nivaran-backend
    python test_key.py
"""

import os
import sys

# ─── Step 1: Load .env ────────────────────────────────
print("=" * 50)
print("NIVARAN — Gemini API Key Diagnostic")
print("=" * 50)

try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    print(f"\n[1] Looking for .env at: {os.path.abspath(env_path)}")
    
    if not os.path.exists(env_path):
        print("    ❌ .env file NOT FOUND!")
        print("    → Create it: cp .env.example .env")
        print("    → Then add your key: GEMINI_API_KEY=your_key_here")
        sys.exit(1)
    
    print("    ✅ .env file exists")
    
    # Load it
    load_dotenv(env_path, override=True)
    
except ImportError:
    print("    ❌ python-dotenv not installed! Run: pip install python-dotenv")
    sys.exit(1)

# ─── Step 2: Check the key ────────────────────────────
key = os.getenv('GEMINI_API_KEY')

print(f"\n[2] Checking GEMINI_API_KEY environment variable...")

if not key:
    print("    ❌ GEMINI_API_KEY is empty/missing in .env!")
    print("    → Open .env and set: GEMINI_API_KEY=your_actual_key")
    sys.exit(1)

if key == 'your_gemini_api_key_here':
    print("    ❌ GEMINI_API_KEY still has the PLACEHOLDER value!")
    print("    → Open .env and replace 'your_gemini_api_key_here' with your real key")
    print(f"    → Get a key at: https://aistudio.google.com/app/apikey")
    sys.exit(1)

# Show first/last few chars to confirm correct key is loaded
masked = key[:5] + "..." + key[-4:] if len(key) > 12 else key[:5] + "..."
print(f"    ✅ Key loaded: {masked} (length: {len(key)} chars)")

# ─── Step 3: Test the API ─────────────────────────────
print(f"\n[3] Testing Gemini API connection...")

try:
    import google.generativeai as genai
    
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    response = model.generate_content("Say 'NIVARAN test successful' in exactly those words.")
    
    if response and response.text:
        print(f"    ✅ API WORKS! Response: {response.text.strip()[:80]}")
        print("\n" + "=" * 50)
        print("✅ ALL CHECKS PASSED — Your key is valid!")
        print("   Restart your Flask server: python app.py")
        print("=" * 50)
    else:
        print("    ⚠️  API returned empty response (key may be valid but quota exhausted)")
        
except Exception as e:
    error_msg = str(e)
    print(f"    ❌ API call FAILED: {error_msg[:200]}")
    
    if 'API_KEY_INVALID' in error_msg:
        print("\n    → Your API key is INVALID. Generate a new one at:")
        print("      https://aistudio.google.com/app/apikey")
    elif 'PERMISSION_DENIED' in error_msg:
        print("\n    → Your key doesn't have Gemini API access enabled.")
        print("      Go to https://aistudio.google.com and enable the API.")
    elif 'QUOTA' in error_msg.upper():
        print("\n    → Your API quota is exhausted. Wait or check billing.")
    else:
        print("\n    → Check your internet connection and try again.")
    
    sys.exit(1)
