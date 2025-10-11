## Contributing to ALPR System

Thank you for your interest in contributing to the ALPR System! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing Guidelines](#testing-guidelines)
- [Code Style](#code-style)

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Prioritize the community's best interests

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Setup Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd lpr-1

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# Run tests to verify setup
pytest tests/
```

## Development Process

### Branching Strategy

We use GitHub Flow:

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: New features and enhancements
- `hotfix/*`: Emergency fixes

### Creating a Feature Branch

```bash
# Start from develop
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/your-feature-name
```

## Commit Guidelines

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks, dependencies

### Examples

```bash
feat(alpr): add license plate detection method
fix(ocr): handle empty text results gracefully
docs(readme): add troubleshooting section for CUDA
test(utils): add edge case tests for bbox cropping
chore(deps): update ultralytics to 8.1.0
```

## Pull Request Process

### Before Submitting

1. **Update from develop:**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout feature/your-feature
   git merge develop
   ```

2. **Run tests:**
   ```bash
   pytest tests/ -v
   pytest tests/ --cov=. --cov-report=term
   ```

3. **Check code quality:**
   ```bash
   black . --check
   flake8 .
   mypy *.py
   ```

4. **Update documentation:**
   - Add/update docstrings
   - Update README if needed
   - Add entry to CHANGELOG (if exists)

### Submitting Pull Request

1. Push your branch:
   ```bash
   git push origin feature/your-feature
   ```

2. Create Pull Request on GitHub with:
   - **Clear title** following commit convention
   - **Description** of what changed and why
   - **Related issues** (if applicable)
   - **Screenshots** (for UI changes)
   - **Testing done**

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Changes Made
- Change 1
- Change 2

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guide
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass (coverage > 80%)
- [ ] No new warnings
```

## Testing Guidelines

### Test Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for full pipeline
└── fixtures/       # Test data and mock objects
```

### Writing Tests

```python
import pytest
from unittest.mock import Mock, patch

def test_feature_behavior():
    """Test that feature behaves correctly."""
    # Arrange
    input_data = ...
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_value
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/unit/test_utils.py -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# Specific test
pytest tests/unit/test_utils.py::TestOCRUtilities::test_format_license_plate_removes_spaces
```

### Test Coverage

- Aim for > 80% coverage
- Cover edge cases and error conditions
- Mock external dependencies (YOLO, Roboflow, Supabase)

## Code Style

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with these tools:

- **Black**: Code formatting (line length: 100)
- **Flake8**: Linting
- **MyPy**: Type checking

### Formatting

```bash
# Format code
black .

# Check formatting
black . --check

# Lint code
flake8 .

# Type check
mypy *.py
```

### Best Practices

1. **Type hints**: Add type hints to all functions
   ```python
   def process_frame(frame: np.ndarray, frame_number: int) -> Tuple[np.ndarray, List[Dict]]:
       ...
   ```

2. **Docstrings**: Use Google-style docstrings
   ```python
   def detect_vehicles(self, frame: np.ndarray) -> np.ndarray:
       """Detect vehicles in frame using YOLO.
       
       Args:
           frame: Input frame (BGR format)
           
       Returns:
           numpy array: Detections as [[x1, y1, x2, y2, confidence], ...]
       """
   ```

3. **Error handling**: Use specific exceptions
   ```python
   if not config.ROBOFLOW_API_KEY:
       raise ValueError("Roboflow API key not set")
   ```

4. **Constants**: Use uppercase for constants
   ```python
   VEHICLE_CONFIDENCE_THRESHOLD = 0.5
   ```

## Areas for Contribution

### Good First Issues

- Documentation improvements
- Adding more test cases
- Fixing typos and formatting
- Improving error messages
- Adding configuration options

### Advanced Contributions

- Performance optimizations
- New detection models
- Additional tracking algorithms
- Database schema improvements
- CI/CD pipeline setup

### Feature Requests

- Multi-language OCR support
- Real-time video streaming
- Web interface
- Model training scripts
- Analytics dashboard

## Questions?

- Open an issue for bug reports or feature requests
- Start a discussion for questions
- Check existing issues and PRs first

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to the ALPR System! 🚗📷

