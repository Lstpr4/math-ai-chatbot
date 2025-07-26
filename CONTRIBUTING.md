# Contributing to Mathly

Thank you for considering contributing to Mathly! This document provides guidelines and instructions for contributing to the project.

## Ways to Contribute

- **Bug Reports**: If you find a bug, please create an issue with a clear description and steps to reproduce it.
- **Feature Requests**: Have ideas for new features? Feel free to create an issue describing your suggestion.
- **Code Contributions**: Want to fix bugs or add features yourself? Follow the steps below to submit a pull request.

## Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```
   git clone https://github.com/YOUR-USERNAME/math-ai-chatbot.git
   cd math-ai-chatbot
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a branch for your changes:
   ```
   git checkout -b feature/your-feature-name
   ```

5. Make your changes and test thoroughly

6. Commit your changes:
   ```
   git commit -am "Add a brief description of your changes"
   ```

7. Push to your fork:
   ```
   git push origin feature/your-feature-name
   ```

8. Create a pull request from your fork to the main repository

## Code Style

- Follow PEP 8 style guidelines for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Write docstrings for functions and classes

## Testing

Before submitting a pull request, make sure your changes:
- Don't break existing functionality
- Handle edge cases appropriately
- Are well-documented

## Adding New Formulas

If you want to add new formulas to the database:
1. Locate the appropriate category in `data/expanded_formulas.json`
2. Add your formula following the existing format and structure
3. Ensure your JSON is valid

## License

By contributing to Mathly, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

Thank you for helping improve Mathly!
