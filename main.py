"""
BA Agent - Main Entry Point
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    print("=" * 50)
    print("BA Agent - Business Analyst Autonomous Agent")
    print("=" * 50)
    print(f"Python Version: {sys.version}")
    print(f"Working Directory: {Path.cwd()}")
    print("\n✅ Agent framework initialized successfully!")
    print("\nNext steps:")
    print("1. Run: docker-compose up -d")
    print("2. Run: python test_setup.py")
    print("3. Proceed to Step 2")

if __name__ == "__main__":
    main()
