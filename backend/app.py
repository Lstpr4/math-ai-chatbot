# Mathly - Math AI Assistant Backend
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS # type: ignore
import os
import json
import re
import base64
import io
import numpy as np # type: ignore
from PIL import Image # type: ignore
import cv2 # type: ignore
from pathlib import Path
from math_processor import MathProcessor
import pytesseract # type: ignore

# Try to import new AI model, fall back to old one if it doesn't exist
try:
    from ai_model_new import MathAIModel
    print("Using enhanced AI model with Claude Sonnet and Grok integration")
except ImportError:
    from ai_model import MathAIModel
    print("Using standard AI model")

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend')
# Enable CORS with explicit origins for better security
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5000", "http://localhost:5001", "http://127.0.0.1:5000", "http://127.0.0.1:5001"]}})  # Enable CORS for API routes

# Initialize our models
data_path = Path(__file__).parent.parent / 'data' / 'expanded_formulas.json'
math_processor = MathProcessor()
math_ai = MathAIModel(str(data_path))

# Serve frontend static files
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# API endpoint to calculate a math expression
@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.json
    expression = data.get('expression')
    
    if not expression:
        return jsonify({'error': 'No expression provided'}), 400
    
    try:
        result = math_processor.evaluate_expression(expression)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# API endpoint for the chat functionality
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('input')
    
    if not user_input:
        return jsonify({'error': 'No input provided'}), 400
    
    # Identify the problem type
    problem_type = math_processor.identify_problem_type(user_input)
    
    try:
        # Special case for quadratic equations, use AI model handler
        if 'quadratic' in user_input.lower() and 'equation' in user_input.lower():
            response = math_ai.process_query(user_input)
            
        elif problem_type == 'quadratic_equation' or problem_type == 'equation':
            # Extract the equation if wrapped in words like "solve"
            if 'solve' in user_input.lower():
                equation = re.sub(r'.*?(?:solve|find the solution to|solve for x in)\s+', '', user_input)
                equation = re.sub(r'\s+(?:for|where).*', '', equation)
            else:
                equation = user_input
                
            # Solve equation with steps
            solution = math_processor.solve_equation_with_steps(equation)
            response = solution
        elif problem_type == 'differentiation':
            # Get expression to differentiate
            if 'differentiate' in user_input.lower() or 'derivative' in user_input.lower():
                # Extract variable if specified
                var_match = re.search(r'with respect to ([a-z])', user_input.lower())
                variable = var_match.group(1) if var_match else 'x'
                
                # Extract expression
                expr = re.sub(r'.*?(?:differentiate|derivative of|find the derivative of)\s+', '', user_input)
                expr = re.sub(r'\s+with respect.*', '', expr)
                
                solution = math_processor.differentiate_with_steps(expr, variable=variable)
                response = solution
            else:
                response = math_processor.differentiate_with_steps(user_input)
        elif problem_type == 'integration':
            # Get expression to integrate
            if 'integrate' in user_input.lower() or 'integral' in user_input.lower():
                # Extract variable if specified
                var_match = re.search(r'with respect to ([a-z])', user_input.lower())
                variable = var_match.group(1) if var_match else 'x'
                
                # Extract expression
                expr = re.sub(r'.*?(?:integrate|integral of|find the integral of)\s+', '', user_input)
                expr = re.sub(r'\s+with respect.*', '', expr)
                
                solution = math_processor.integrate_with_steps(expr, variable=variable)
                response = solution
            else:
                response = math_processor.integrate_with_steps(user_input)
        elif problem_type == 'limit':
            # Get expression for limit
            if 'limit' in user_input.lower():
                # Extract variable and point
                var_match = re.search(r'(?:as|when)\s+([a-z])\s+(?:approaches|→|goes to|tends to)\s+([\w\-\+\.∞]+)', user_input.lower())
                if var_match:
                    variable = var_match.group(1)
                    point = var_match.group(2)
                else:
                    variable = 'x'
                    point = '0'
                
                # Extract expression
                expr = re.sub(r'.*?(?:limit of|find the limit of)\s+', '', user_input)
                expr = re.sub(r'\s+(?:as|when).*', '', expr)
                
                solution = math_processor.calculate_limit(expr, variable=variable, point=point)
                response = solution
            else:
                response = math_processor.calculate_limit(user_input)
        elif problem_type == 'factoring':
            expr = re.sub(r'.*?(?:factor|factorize|factorize)\s+', '', user_input)
            response = math_processor.factor_expression(expr)
        elif problem_type == 'expansion':
            expr = re.sub(r'.*?(?:expand|distribute)\s+', '', user_input)
            response = math_processor.expand_expression(expr)
        elif contains_math := re.search(r'\d[\+\-\*\/\^\(\)]\d', user_input):
            # Handle basic arithmetic
            result = math_processor.evaluate_expression(user_input)
            response = f"The result of {user_input} is {result}"
        else:
            # Use the AI model for general queries
            response = math_ai.process_query(user_input)
    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print(f"Error processing request: {traceback_str}")
        response = f"I had trouble processing that request. Please check your input and try again."
    
    return jsonify({'response': response})

# API endpoint to get a specific formula
@app.route('/api/formula/<category>', methods=['GET'])
def get_formula(category):
    formula = math_ai.get_formula(category)
    return jsonify({'formula': formula})
    
# API endpoint to get a specific formula with topic
@app.route('/api/formula/<category>/<topic>', methods=['GET'])
def get_formula_topic(category, topic):
    formula = math_ai.get_formula(category, topic)
    return jsonify({'formula': formula})
    
# API endpoint for advanced formula search
@app.route('/api/formula_search', methods=['POST'])
def search_formula():
    data = request.json
    category = data.get('category', '')
    topic = data.get('topic', None)
    search_term = data.get('term', '').lower()
    
    if not category and not search_term:
        return jsonify({'error': 'No category or search term provided'}), 400
    
    # If we have a search term, try to find matching formulas
    if search_term:
        # Search through all categories if none specified
        categories = [category] if category else ["algebra", "geometry", "trigonometry", "calculus", "statistics", "physics", "constants"]
        results = []
        
        for cat in categories:
            try:
                # Get all formulas in this category
                formulas = math_ai.formulas["formulas"].get(cat, {})
                
                # Search through formulas
                for name, formula in formulas.items():
                    if search_term in name.lower():
                        if isinstance(formula, dict):
                            # If it's a nested dictionary, search through sub-formulas
                            for sub_name, sub_formula in formula.items():
                                if search_term in sub_name.lower() or search_term in name.lower():
                                    if isinstance(sub_formula, dict):
                                        results.append(f"{cat} > {name} > {sub_name}: (complex formula)")
                                    else:
                                        results.append(f"{cat} > {name} > {sub_name}: {sub_formula}")
                        else:
                            results.append(f"{cat} > {name}: {formula}")
            except Exception as e:
                print(f"Error searching in category {cat}: {e}")
        
        if results:
            return jsonify({'results': results})
        else:
            return jsonify({'message': f"No formulas found matching '{search_term}'"}), 404
    
    # Otherwise use standard formula lookup
    formula_result = math_ai.get_formula(category, topic)
    return jsonify({'formula': formula_result})

# API endpoint to solve math questions
@app.route('/api/solve', methods=['POST'])
def solve_math():
    data = request.json
    question = data.get('question', '')
    
    result = math_processor.process_question(question)
    
    return jsonify({
        'question': question,
        'answer': result
    })

# API endpoint to process images of math problems
@app.route('/api/image', methods=['POST'])
def process_image():
    data = request.json
    image_data = data.get('image', '')
    
    if not image_data:
        return jsonify({'error': 'No image provided'}), 400
    
    try:
        # Extract base64 data
        image_data = image_data.split(',')[1]
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to OpenCV format
        open_cv_image = np.array(image)
        open_cv_image = open_cv_image[:, :, ::-1].copy()  # RGB to BGR
        
        # Preprocess the image
        gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        
        # OCR to extract text
        math_problem = pytesseract.image_to_string(gray)
        math_problem = math_problem.strip()
        
        if not math_problem:
            return jsonify({
                'response': "I couldn't read any text from the image. Please make sure the math problem is clearly visible."
            })
        
        # Process the extracted math problem
        response = f"I extracted this math problem: {math_problem}\n\n"
        
        # Identify the problem type and process accordingly
        problem_type = math_processor.identify_problem_type(math_problem)
        
        if problem_type == 'equation':
            solution = math_processor.solve_equation_with_steps(math_problem)
            response += solution
        elif problem_type == 'differentiation':
            solution = math_processor.differentiate_with_steps(math_problem)
            response += solution
        elif problem_type == 'integration':
            solution = math_processor.integrate_with_steps(math_problem)
            response += solution
        elif problem_type == 'limit':
            solution = math_processor.calculate_limit(math_problem)
            response += solution
        elif problem_type == 'factoring':
            solution = math_processor.factor_expression(math_problem)
            response += solution
        elif problem_type == 'expansion':
            solution = math_processor.expand_expression(math_problem)
            response += solution
        else:
            # Try to use the image text processor
            solution = math_processor.process_image_text(math_problem)
            response += solution
        
        return jsonify({'response': response})
    
    except Exception as e:
        return jsonify({'error': f"Error processing image: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)