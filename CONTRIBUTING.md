# Contributing to LDPlayer Management System

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Foster a harassment-free environment
- Welcome diverse perspectives
- Focus on constructive feedback

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+
- Git
- Docker (optional)

### Development Setup

1. Fork the repository
2. Clone your fork locally
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
4. Install development dependencies:
   ```bash
   cd Server
   pip install -r requirements.txt
   pip install pytest pytest-cov black flake8 mypy
   ```
5. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Code Style

#### Python
- Follow PEP 8
- Use type hints for all functions
- Maximum line length: 100 characters
- Format with `black`
- Lint with `flake8`
- Type check with `mypy`

```python
# Good example
def process_emulator(emulator_id: str, action: str) -> Dict[str, Any]:
    """Process emulator action.
    
    Args:
        emulator_id: Unique emulator identifier
        action: Action to perform (start, stop, restart)
    
    Returns:
        Operation result dictionary
    
    Raises:
        EmulatorNotFoundError: If emulator doesn't exist
    """
    # Implementation
```

#### JavaScript/React
- Follow ESLint rules
- Use functional components
- Add PropTypes or TypeScript types
- Maximum line length: 100 characters

### Git Commit Messages

Format: `type(scope): description`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting, missing semicolons, etc)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Adding/updating tests
- `chore`: Build process, dependencies, etc

Examples:
```
feat(emulator): add batch restart operation
fix(auth): resolve JWT token validation issue
docs(api): update endpoint documentation
test(workstation): add connection timeout tests
```

### Testing

#### Running Tests
```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific test file
pytest tests/test_auth.py -v

# Quick test (quiet mode)
pytest tests/ -q
```

#### Writing Tests

- Test file naming: `test_*.py`
- Test function naming: `test_*`
- One test per assertion (preferred)
- Use fixtures for setup/teardown
- Mock external dependencies

Example:
```python
import pytest
from unittest.mock import Mock, patch
from src.services.emulator_service import EmulatorService

@pytest.fixture
def emulator_service():
    return EmulatorService()

def test_start_emulator_success(emulator_service):
    """Test successful emulator start"""
    result = emulator_service.start("emulator-1")
    assert result["status"] == "success"
    assert result["emulator_id"] == "emulator-1"

def test_start_emulator_not_found(emulator_service):
    """Test starting non-existent emulator"""
    with pytest.raises(EmulatorNotFoundError):
        emulator_service.start("non-existent")
```

### Code Review Checklist

Before submitting a PR, ensure:
- [ ] Code follows style guide
- [ ] Tests pass (`pytest tests/ -v`)
- [ ] Coverage maintained (>90%)
- [ ] Documentation updated
- [ ] No debug statements (`print()`, `console.log()`)
- [ ] No sensitive data committed
- [ ] Commit messages are clear
- [ ] Branch updated with `main`

## Submitting Changes

### Pull Request Process

1. **Update your branch:**
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request:**
   - Use clear title and description
   - Reference related issues (#123)
   - Include test results
   - Add screenshot if UI changes

### PR Description Template
```markdown
## Description
Brief description of changes

## Motivation and Context
Why is this change needed?

## Types of Changes
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Added tests
- [ ] Tests pass
- [ ] Coverage maintained

## Screenshots (if applicable)

## Related Issues
Closes #123
```

## File Organization

### Adding New Modules

```
# Backend service
src/services/new_service.py
tests/test_new_service.py

# API routes
src/api/new_routes.py

# Utility
src/utils/new_util.py
tests/test_new_util.py
```

### Documentation Files

- Module docstrings (required)
- Function docstrings (required)
- Complex logic comments (as needed)
- Type hints (required)

## Common Tasks

### Adding a New API Endpoint

1. Create route in `src/api/routes.py` or new file
2. Add Pydantic model in `src/core/models.py`
3. Create service method in `src/services/`
4. Add tests in `tests/`
5. Update API documentation

Example:
```python
# src/api/emulators.py
@router.post("/emulators/{emulator_id}/custom-action")
async def custom_action(
    emulator_id: str,
    request: CustomActionRequest,
    service: EmulatorService = Depends(get_emulator_service)
) -> CustomActionResponse:
    """Custom emulator action"""
    result = await service.custom_action(emulator_id, request)
    return CustomActionResponse(**result)

# tests/test_emulators.py
@pytest.mark.asyncio
async def test_custom_action():
    response = client.post("/api/emulators/1/custom-action", json={...})
    assert response.status_code == 200
```

### Fixing a Bug

1. Create issue describing the bug
2. Create branch: `fix/issue-description`
3. Add failing test first (TDD approach)
4. Fix the bug
5. Verify test passes
6. Submit PR with `Fixes #123`

### Adding Documentation

1. Update relevant MD files
2. Keep formatting consistent
3. Add examples where applicable
4. Update table of contents if needed
5. Verify links work

## Release Process

Maintainers only:

1. Update version in `setup.py`
2. Update `CHANGELOG.md`
3. Create git tag: `git tag -a v1.0.0 -m "Release 1.0.0"`
4. Push tag: `git push origin v1.0.0`
5. Create GitHub release with notes

## Getting Help

- **Questions:** Open a discussion in Discussions tab
- **Bugs:** Create an issue with reproduction steps
- **Features:** Discuss in Discussions first
- **Documentation:** Submit improved docs via PR

## Code Review Comments

When reviewing, focus on:
- Correctness and logic
- Performance implications
- Security concerns
- Test coverage
- Code clarity
- Consistency with project style

Be kind and constructive. All reviewers started as beginners!

## Additional Resources

- [Project Architecture](docs/ARCHITECTURE.md)
- [API Documentation](docs/API_DOCUMENTATION.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Python Style Guide (PEP 8)](https://pep8.org/)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/deployment/)
- [React Best Practices](https://react.dev/learn)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to make this project better!** 🙏
