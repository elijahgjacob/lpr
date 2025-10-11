"""Test to verify project structure is set up correctly."""
import os
import pytest


def test_required_directories_exist():
    """Verify all required directories exist."""
    required_dirs = [
        "models",
        "videos",
        "results",
        "tests",
        "tests/unit",
        "tests/integration",
        "tests/fixtures",
    ]
    
    for dir_path in required_dirs:
        assert os.path.exists(dir_path), f"Directory {dir_path} does not exist"
        assert os.path.isdir(dir_path), f"{dir_path} is not a directory"


def test_required_files_exist():
    """Verify all required configuration files exist."""
    required_files = [
        "requirements.txt",
        ".gitignore",
        ".env.example",
        "pytest.ini",
        ".coveragerc",
        "README.md",
    ]
    
    for file_path in required_files:
        assert os.path.exists(file_path), f"File {file_path} does not exist"
        assert os.path.isfile(file_path), f"{file_path} is not a file"


def test_gitignore_contains_env():
    """Verify .gitignore includes .env file."""
    with open(".gitignore", "r") as f:
        content = f.read()
    
    assert ".env" in content, ".env not found in .gitignore"
    assert "__pycache__" in content, "__pycache__ not found in .gitignore"


def test_env_example_has_required_keys():
    """Verify .env.example has all required configuration keys."""
    with open(".env.example", "r") as f:
        content = f.read()
    
    required_keys = [
        "ROBOFLOW_API_KEY",
        "ROBOFLOW_WORKSPACE",
        "ROBOFLOW_PROJECT",
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "ENABLE_SUPABASE",
    ]
    
    for key in required_keys:
        assert key in content, f"{key} not found in .env.example"


def test_requirements_has_core_dependencies():
    """Verify requirements.txt includes core dependencies."""
    with open("requirements.txt", "r") as f:
        content = f.read()
    
    core_deps = [
        "torch",
        "ultralytics",
        "opencv-python",
        "easyocr",
        "roboflow",
        "supabase",
        "pytest",
    ]
    
    for dep in core_deps:
        assert dep in content, f"{dep} not found in requirements.txt"

