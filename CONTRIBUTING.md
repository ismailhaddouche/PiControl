# Contributing to PiControl

Thank you for your interest in contributing to PiControl! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

### Our Standards

- **Be respectful** - Different viewpoints and experiences are valuable
- **Be constructive** - Focus on what is best for the project and community
- **Be collaborative** - Work together towards common goals
- **Be professional** - Maintain professionalism in all interactions

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Set up development environment** (see below)
4. **Create a branch** for your changes
5. **Make your changes**
6. **Test your changes**
7. **Submit a pull request**

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- Virtual environment tool (venv, virtualenv, or conda)

### Setup Steps

1. Clone your fork:
   ```bash
   git clone https://github.com/YOUR-USERNAME/PiControl.git
   cd PiControl
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   make install-dev
   # or manually:
   pip install -e ".[dev]"
   ```

4. Install pre-commit hooks:
   ```bash
   make pre-commit-install
   # or manually:
   pre-commit install
   ```

5. Create `.env` file from example:
   ```bash
   cp .env.example .env
   # Edit .env and set SECRET_KEY
   ```

6. Initialize test database:
   ```bash
   make db-init
   ```

### Verify Setup

Run tests to verify everything is working:

```bash
make test
```

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

- **Bug fixes** - Fix issues reported in GitHub Issues
- **New features** - Add new functionality (discuss first in an issue)
- **Documentation** - Improve README, guides, docstrings
- **Tests** - Add or improve test coverage
- **Code quality** - Refactoring, performance improvements
- **Security** - Security enhancements and fixes

### Workflow

1. **Check existing issues** - See if your idea/bug is already reported
2. **Create an issue** - For significant changes, discuss first
3. **Create a branch** - Use descriptive branch names
4. **Make changes** - Follow coding standards
5. **Test thoroughly** - Add tests for new functionality
6. **Commit changes** - Use semantic commit messages
7. **Push to your fork** - Keep your fork up to date
8. **Submit PR** - Reference related issues

### Branch Naming

Use descriptive branch names with prefixes:

- `feature/` - New features (`feature/add-employee-export`)
- `fix/` - Bug fixes (`fix/rfid-timeout-issue`)
- `docs/` - Documentation (`docs/update-installation-guide`)
- `refactor/` - Code refactoring (`refactor/simplify-auth-logic`)
- `test/` - Adding tests (`test/add-employee-crud-tests`)

## Coding Standards

### Python Style Guide

We follow **PEP 8** with some modifications:

- **Line length**: 120 characters (not 79)
- **Formatter**: Black
- **Linter**: Ruff
- **Import sorting**: isort
- **Type hints**: Encouraged but not required

### Code Formatting

All code must be formatted with Black:

```bash
make format
```

### Linting

Code must pass Ruff checks:

```bash
make lint
```

### Type Hints

While not required, type hints are encouraged:

```python
def create_employee(session: Session, document_id: str, name: str) -> Employee:
    """Create a new employee."""
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def process_checkin(employee_id: str, timestamp: datetime) -> bool:
    """
    Process employee check-in.

    Args:
        employee_id: Employee document ID
        timestamp: Check-in timestamp

    Returns:
        True if check-in successful, False otherwise

    Raises:
        ValueError: If employee_id is invalid
    """
    ...
```

### Commit Messages

Use semantic commit messages:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(rfid): add support for MIFARE DESFire cards

fix(auth): prevent session fixation vulnerability

docs(readme): update installation instructions for Raspberry Pi 5

test(employee): add tests for employee archival
```

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest tests/test_admin_flow.py -v

# Run specific test
pytest tests/test_admin_flow.py::test_admin_setup_login_and_employee_creation -v
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names
- Test both success and failure cases
- Aim for >80% code coverage

Example test:

```python
def test_employee_creation():
    """Test creating a new employee."""
    # Arrange
    session = get_test_session()
    
    # Act
    employee = create_employee(session, "T001", "John Doe")
    
    # Assert
    assert employee.document_id == "T001"
    assert employee.name == "John Doe"
    assert employee.rfid_uid is None
```

### Test Categories

Mark tests with appropriate markers:

```python
@pytest.mark.slow
def test_large_data_import():
    ...

@pytest.mark.hardware
def test_rfid_reader():
    ...

@pytest.mark.integration
def test_full_checkin_flow():
    ...
```

## Pull Request Process

### Before Submitting

1. **Update documentation** - If you changed functionality
2. **Add tests** - For new features or bug fixes
3. **Run all checks**:
   ```bash
   make check-all  # Runs lint, format-check, type-check
   make test       # Runs tests
   ```
4. **Update CHANGELOG** - Add entry describing your changes (if applicable)
5. **Rebase on main** - Ensure your branch is up to date

### PR Checklist

- [ ] Code follows style guidelines (Black, Ruff)
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] Commit messages are semantic
- [ ] Branch is up to date with main
- [ ] No merge conflicts
- [ ] CI checks passing

### PR Description

Provide a clear description:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Related Issues
Fixes #123

## Testing
Describe testing performed

## Screenshots (if applicable)

## Checklist
- [x] Tests pass
- [x] Code formatted
- [x] Documentation updated
```

### Review Process

1. **Automated checks** - CI must pass
2. **Code review** - At least one approval required
3. **Testing** - Verify changes work as expected
4. **Merge** - Squash and merge or rebase

## Reporting Bugs

### Before Reporting

- **Search existing issues** - Bug may already be reported
- **Verify it's a bug** - Not a configuration issue
- **Test on latest version** - Bug may already be fixed

### Bug Report Template

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Raspberry Pi OS Bullseye]
- Python version: [e.g., 3.11.2]
- PiControl version: [e.g., 1.0.0]
- Hardware: [e.g., Raspberry Pi 4B, RC522 RFID reader]

## Additional Context
Screenshots, logs, etc.
```

## Suggesting Enhancements

### Before Suggesting

- **Check existing issues** - May already be suggested
- **Check documentation** - Feature may already exist
- **Consider scope** - Is it appropriate for this project?

### Enhancement Request Template

```markdown
## Feature Description
Clear description of the proposed feature

## Problem It Solves
What problem does this address?

## Proposed Solution
How would it work?

## Alternatives Considered
Other approaches you've considered

## Additional Context
Mockups, examples, etc.
```

## Development Tools

### Useful Commands

```bash
# Development
make run-dev          # Run with auto-reload
make format           # Format code
make lint             # Check code style
make test-cov         # Run tests with coverage

# Database
make db-init          # Initialize database
make db-backup        # Backup database

# Cleanup
make clean            # Clean temporary files
make clean-all        # Clean everything including venv

# Help
make help             # Show all available commands
```

### Pre-commit Hooks

Pre-commit hooks run automatically before each commit:

- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON/TOML validation
- Black formatting
- Isort import sorting
- Ruff linting
- Bandit security checks
- Secret detection

Bypass hooks (not recommended):
```bash
git commit --no-verify
```

## Questions?

If you have questions about contributing:

1. Check existing issues and discussions
2. Open a new discussion on GitHub
3. Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to PiControl!** 🎉
