#!/usr/bin/env python3
"""
Windows setup script for screen-vision skill.
Run: python3 setup-win.py
Or in PowerShell: python setup-win.py
"""

import subprocess
import sys
import os

print("=" * 40)
print("  Screen-Vision Windows Setup")
print("=" * 40)
print()

# Check Python
print("[1/3] Checking Python...")
print(f"  Found: {sys.executable}")
print("  ✅ Python")
print()

# Install Python dependencies
print("[2/3] Installing Python dependencies...")
subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", 
                "pyautogui", "Pillow", "numpy"], check=False)

try:
    import pyautogui
    print("  ✅ pyautogui")
except ImportError:
    print("  ❌ pyautogui install failed")

try:
    from PIL import Image
    print("  ✅ Pillow")
except ImportError:
    print("  ❌ Pillow install failed")

print()

# Verify
print("[3/3] Verifying...")
try:
    import pyautogui
    size = pyautogui.size()
    print(f"  Screen: {size.width}x{size.height}")
    print("  ✅ All ready!")
except Exception as e:
    print(f"  ❌ Error: {e}")

print()
print("=" * 40)
print("  ✅ Setup Complete!")
print("=" * 40)
print()
print("No special permissions needed on Windows.")
print("Ready to use! Tell your AI: '帮我操作电脑'")
