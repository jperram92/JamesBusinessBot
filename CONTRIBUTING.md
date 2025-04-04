# Contributing to JamesBusinessBot

Thank you for your interest in contributing to JamesBusinessBot! This document provides guidelines and instructions for contributing to our project.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Code Style](#code-style)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and considerate of differing viewpoints and experiences.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/JamesBusinessBot.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`

## Development Setup

### Frontend (React/Vite)
1. Install Node.js dependencies:
   ```bash
   npm install
   ```
2. Start the development server:
   ```bash
   npm run dev
   ```

### Backend (Python)
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Making Changes

1. Make your changes in your feature branch
2. Write clear, descriptive commit messages
3. Follow the existing code style and conventions
4. Add tests for new features
5. Update documentation as needed

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the documentation if you're changing functionality
3. The PR will be merged once you have the sign-off of at least one maintainer
4. Make sure all tests pass before submitting a PR
5. All commits must be signed with GPG
6. Force pushing to protected branches is not allowed
7. Pull requests require at least one approval before merging

### GPG Signing Requirements
All commits must be signed with GPG. To set up GPG signing:

1. Generate a GPG key:
   ```bash
   gpg --full-generate-key
   ```
   - Choose RSA and RSA (default)
   - Choose 4096 bits
   - Choose 0 = key does not expire
   - Enter your name and email (use the same email as your GitHub account)

2. List your GPG keys:
   ```bash
   gpg --list-secret-keys --keyid-format LONG
   ```

3. Export your GPG key:
   ```bash
   gpg --armor --export YOUR_KEY_ID
   ```

4. Add the key to your GitHub account:
   - Go to Settings -> SSH and GPG keys
   - Click "New GPG key"
   - Paste your exported key

5. Configure Git to use your GPG key:
   ```bash
   git config --global user.signingkey YOUR_KEY_ID
   git config --global commit.gpgsign true
   ```

6. For Windows users, you may need to set the GPG program:
   ```bash
   git config --global gpg.program "C:\Program Files\GnuPG\bin\gpg.exe"
   ```

### Branch Protection Rules
- The `main` and `master` branches are protected
- Direct pushes to protected branches are not allowed
- All changes must go through pull requests
- Pull requests require:
  - At least one approval from a maintainer
  - All status checks to pass
  - No merge conflicts
  - Signed commits
- Force pushing to protected branches is prohibited

## Code Style

### JavaScript/React
- Use ESLint and Prettier for code formatting
- Follow React best practices and hooks guidelines
- Use meaningful component and variable names
- Comment complex logic

### Python
- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for functions and classes

## Testing

### Frontend
- Write unit tests for components
- Test user interactions and state changes
- Ensure responsive design works across devices

### Backend
- Write unit tests using pytest
- Include integration tests where appropriate
- Maintain good test coverage

## Documentation

- Keep documentation up to date
- Use clear and concise language
- Include examples where helpful
- Document any new features or changes to existing features

## Questions?

If you have any questions, please open an issue in the GitHub repository.

Thank you for contributing to JamesBusinessBot! 