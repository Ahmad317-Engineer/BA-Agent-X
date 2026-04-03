"""
BA Agent - Core Test (Without Docker)
Tests only Python components, not Docker services
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def test_core_imports():
    """Test core Python imports"""
    print("\n📦 Testing Core Imports...")
    
    imports = [
        ("fastapi", "FastAPI"),
        ("pydantic", "Pydantic"),
        ("loguru", "Loguru"),
        ("chromadb", "ChromaDB"),
        ("sentence_transformers", "Sentence Transformers"),
        ("slack_sdk", "Slack SDK"),
        ("github", "PyGithub"),
        ("langgraph", "LangGraph"),
        ("langchain", "LangChain"),
        ("neo4j", "Neo4j (Python driver)")
    ]
    
    results = []
    for module, name in imports:
        try:
            __import__(module)
            print(f"  ✅ {name}")
            results.append(True)
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
            results.append(False)
    
    return all(results)

def test_local_services():
    """Test services that would run locally"""
    print("\n🔧 Testing Local Services...")
    
    # Check if files exist
    files = [".env", "docker-compose.yml", "main.py", "test_setup.py"]
    for f in files:
        if Path(f).exists():
            print(f"  ✅ {f} exists")
        else:
            print(f"  ❌ {f} missing")
    
    # Check directories
    dirs = ["src", "tests", "data", "logs", "config"]
    for d in dirs:
        if Path(d).exists():
            print(f"  ✅ {d}/ exists")
        else:
            print(f"  ❌ {d}/ missing")

def test_environment():
    """Test environment variables"""
    print("\n🌍 Environment Variables:")
    env_vars = ["NEO4J_URI", "NEO4J_USER", "CHROMA_HOST", "OLLAMA_URL"]
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var} = {value}")
        else:
            print(f"  ⚠️  {var} not set (will use defaults)")

if __name__ == "__main__":
    print("=" * 60)
    print("BA AGENT - SETUP VERIFICATION (Without Docker)")
    print("=" * 60)
    
    core_ok = test_core_imports()
    test_local_services()
    test_environment()
    
    print("\n" + "=" * 60)
    if core_ok:
        print("✅ All Python packages installed successfully!")
    else:
        print("⚠️  Some packages missing. Run: pip install slack_sdk langgraph langchain")
    
    print("\n📌 NOTE: Docker not detected. To run Neo4j, PostgreSQL, and Ollama:")
    print("   1. Install Docker Desktop from: https://www.docker.com/products/docker-desktop/")
    print("   2. Run: docker-compose up -d")
    print("   3. Or use cloud versions of these services")
    print("=" * 60)
