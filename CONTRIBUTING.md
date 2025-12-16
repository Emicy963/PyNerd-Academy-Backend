# Contributing to PyNerd

First off, thanks for taking the time to contribute! 🎉

The following is a set of guidelines for contributing to PyNerd. These are just guidelines, not rules. Use your best judgment and feel free to propose changes to this document in a pull request.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for PyNerd. Following these guidelines helps maintainers and the community understand your report, reproduce the behavior, and find related reports.

- **Use a clear and descriptive title** for the issue to identify the problem.
- **Describe the exact steps which reproduce the problem** in as many details as possible.
- **Describe the behavior you observed** after following the steps.

### Pull Requests

- Two approvals are required for merging changes into the master branch.
- Ensure all tests pass before submitting your PR.
- Follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for Python code.
- Add unit tests for any new functionality.

## Styleguides

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature").
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...").
- Limit the first line to 72 characters or less.
- Reference issues and pull requests liberally after the first line.
- **Format**: `type(scope): subject`
  - Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.

### Python Styleguide

- All code must run on Python 3.12+.
- Use `black` and `flake8` for linting and formatting.
- Add docstrings to all modules, classes, and public methods.

## Setting Up Development Environment

1. **Clone the repo**:
   ```bash
   git clone https://github.com/yourusername/pynerd.git
   ```
2. **Setup with Docker**:
   ```bash
   docker-compose up --build
   ```
3. **Run Tests**:
   ```bash
   docker-compose exec backend pytest
   ```

Happy coding!
