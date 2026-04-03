"""
Test script to verify installation
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test critical imports"""
    print("\n📦 Testing imports...")
    
    imports_to_test = [
        ("langgraph", "langgraph"),
        ("fastapi", "fastapi"),
        ("chromadb", "chromadb"),
        ("neo4j", "neo4j"),
        ("pydantic", "pydantic"),
        ("sentence_transformers", "sentence_transformers"),
        ("dotenv", "python-dotenv"),
        ("loguru", "loguru")
    ]
    
    failed = []
    for module_name, package_name in imports_to_test:
        try:
            __import__(module_name)
            print(f"  ✅ {package_name}")
        except ImportError as e:
            print(f"  ❌ {package_name}: {e}")
            failed.append(package_name)
    
    return failed

def test_environment():
    """Test environment setup"""
    print("\n🔧 Testing environment...")
    
    # Check if .env exists
    if Path(".env").exists():
        print("  ✅ .env file exists")
    else:
        print("  ⚠️ .env file missing")
    
    # Check if docker-compose exists
    if Path("docker-compose.yml").exists():
        print("  ✅ docker-compose.yml exists")
    else:
        print("  ❌ docker-compose.yml missing")
    
    # Check if directories exist
    dirs = ["src", "tests", "data", "logs", "config"]
    for d in dirs:
        if Path(d).exists():
            print(f"  ✅ {d}/ directory exists")
        else:
            print(f"  ❌ {d}/ directory missing")

if __name__ == "__main__":
    print("=" * 50)
    print("BA Agent - Setup Verification")
    print("=" * 50)
    
    failed_imports = test_imports()
    test_environment()
    
    print("\n" + "=" * 50)
    if not failed_imports:
        print("✅ All tests passed! Ready for Step 2.")
    else:
        print(f"⚠️ Failed imports: {', '.join(failed_imports)}")
        print("Some packages may need manual installation.")
    print("=" * 50)
