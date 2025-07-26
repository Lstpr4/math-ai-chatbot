# Mathly - AI Math Assistant

Mathly is an intelligent math assistant chatbot that helps users solve math problems, provides formulas, explains concepts, and offers step-by-step solutions.

## Project Overview

This project uses HTML/CSS and JavaScript for the frontend user interface, with a Python Flask backend that handles the math processing and AI response generation. The enhanced version integrates Claude Sonnet 3.5 and Grok AI for advanced math problem solving.

## Project Structure

```
math-ai-chatbot
├── frontend
│   ├── index.html        # User interface with chat window
│   ├── styles
│   │   └── main.css      # Modern and responsive UI styling
│   └── scripts
│       └── app.js        # Client-side chat interaction logic
├── backend
│   ├── app.py            # Flask server and API endpoints
│   ├── math_processor.py # Mathematical expression processing
│   ├── ai_model.py       # AI response generation system
│   └── requirements.txt  # Python dependencies
├── data
│   └── math_formulas.json # Comprehensive math formula database
└── README.md             # Project documentation
```

## Features

- 🧠 **Advanced AI**: Powered by Claude Sonnet 3.5 and Grok for solving complex math problems
- 💬 **Interactive Chat Interface**: Modern, responsive design with real-time feedback
- 🧮 **Math Expression Evaluation**: Safely evaluates mathematical expressions and equations
- 📚 **Comprehensive Formula Database**: Contains formulas across algebra, geometry, trigonometry, calculus, statistics, and physics
- 🔍 **Topic Detection**: Identifies the area of mathematics the user is asking about
- ➗ **Smart Equation Solving**: Handles quadratic equations and provides detailed solutions
- ✨ **Beautiful UI**: Animated backgrounds and visual effects for a premium experience
- 📹 **Camera Input**: Experimental support for solving written math problems
- 📊 **Beautiful Math Rendering**: Uses MathJax to display mathematical notation properly

## Setup Instructions

1. Install Python dependencies:
   ```bash
   cd math-ai-chatbot/backend
   pip install -r requirements.txt
   ```

2. Start the backend server:
   ```bash
   python app.py
   ```

3. Access the chatbot:
   - Option 1: Open `frontend/index.html` directly in your browser
   - Option 2: Navigate to `http://localhost:5000` in your browser (Flask will serve the frontend)

## Usage Examples

- "What's the formula for the area of a circle?"
- "Can you help me solve 2x + 3 = 7?"
- "What's the derivative of x²?"
- "Calculate 5 * (3 + 2) / 4"
- "What formulas do I need for trigonometry?"
- "What's the Pythagorean theorem?"

## How It Works

1. The frontend sends user questions to the backend API
2. The backend analyzes the question to identify the mathematical topic
3. Based on the topic and intent, it:
   - Looks up relevant formulas
   - Evaluates mathematical expressions
   - Solves basic equations
   - Generates appropriate explanations
4. The response is sent back to the frontend and displayed with proper formatting

## Extending the Project

- Add support for more complex equation solving using symbolic math libraries
- Implement image recognition for handwritten math problems
- Add step-by-step solution walkthroughs for common problem types
- Create a user account system to track learning progress

## License

MIT License - Feel free to use, modify, and distribute this project for educational purposes.