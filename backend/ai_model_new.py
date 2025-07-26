# Mathly - AI Model for Math Assistance
import json
import random
import re
import os
import math
import requests
from pathlib import Path

# Try to import dotenv, but don't fail if not available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("dotenv not installed, skipping environment loading")

class MathAIModel:
    def __init__(self, formulas_file):
        """Initialize the AI model with math knowledge"""
        self.formulas = self.load_formulas(formulas_file)
        self.math_topics = {
            'algebra': ['equation', 'solve', 'variable', 'expression', 'simplify', 'factor', 'expand', 'sequence', 'arithmetic', 'geometric', 'matrices', 'determinant', 'multiply', 'times', 'division', 'divide', 'fractions', 'exponent', 'power', 'roots', 'logarithm', 'factoring'],
            'geometry': ['area', 'perimeter', 'volume', 'circle', 'triangle', 'square', 'rectangle', 'sphere', 'cylinder', 'cone', 'prism', 'pyramid', 'shape', 'angle', 'degree', 'parallelogram', 'trapezoid', 'polygon', 'rhombus', 'cube', 'surface area', 'diameter', 'radius', 'height', 'width', 'length', 'diagonal', 'circumference'],
            'trigonometry': ['sin', 'cos', 'tan', 'sine', 'cosine', 'tangent', 'angle', 'degree', 'radian', 'pythagorean', 'identity', 'law of sines', 'law of cosines', 'soh', 'cah', 'toa', 'soh-cah-toa', 'cotangent', 'cot', 'secant', 'sec', 'cosecant', 'csc', 'triangle'],
            'calculus': ['derivative', 'integral', 'antiderivative', 'limit', 'differentiate', 'integrate', 'rate of change', 'series', 'sequence', 'taylor', 'maclaurin', 'definite integral', 'indefinite integral', 'dx', 'differential', 'partial derivative', 'chain rule', 'product rule', 'quotient rule', 'power rule', 'substitution', 'integration by parts'],
            'statistics': ['mean', 'median', 'mode', 'standard deviation', 'probability', 'distribution', 'variance', 'correlation', 'regression', 'average', 'normal distribution', 'bell curve', 'percentile', 'quartile', 'histogram', 'frequency', 'sample', 'population', 'hypothesis testing', 'confidence interval'],
            'physics': ['mechanics', 'force', 'motion', 'energy', 'momentum', 'work', 'power', 'thermodynamics', 'heat', 'electromagnetism', 'voltage', 'current', 'resistance', 'waves', 'optics', 'quantum', 'relativity', 'gravity', 'acceleration', 'velocity', 'displacement', 'newton', 'joule', 'watt', 'ampere', 'volt', 'ohm', 'temperature', 'pressure', 'density', 'sound', 'light', 'refraction', 'reflection'],
            'constants': ['pi', 'e', 'avogadro', 'boltzmann', 'planck', 'speed of light', 'gravitational constant', 'golden ratio', 'phi', 'euler number']
        }
        
        # AI Model Configuration
        self.use_advanced_ai = True
        self.primary_model = "claude_sonnet"  # "claude_sonnet" or "grok"
        self.fallback_to_basic = True  # If API calls fail, use basic model
        
        # API Keys (would be loaded from environment variables in production)
        self.claude_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.grok_api_key = os.getenv("GROK_API_KEY", "")
        
        # Greeting templates
        self.greetings = [
            "Hello! How can I help with math today?",
            "Hi there! Need help with a math problem?",
            "Welcome to Mathly! What math question do you have?"
        ]
        
        # Response templates
        self.response_templates = {
            'cannot_solve': [
                "I'm not able to solve this specific problem right now. Could you try rephrasing it?",
                "This problem is a bit complex for me. Can you break it down into simpler steps?",
                "I'm still learning how to solve this type of problem. Let me try a simpler approach."
            ],
            'provide_formula': [
                "Here's the formula you need: {}",
                "The formula for {} is: {}",
                "In mathematics, {} is calculated using: {}"
            ],
            'solution': [
                "I've solved it! The answer is: {}",
                "After calculating, I get: {}",
                "The solution is: {}"
            ]
        }

    def load_formulas(self, formulas_file):
        """Load math formulas from JSON file"""
        try:
            with open(formulas_file, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading formulas: {e}")
            return {"formulas": {}}

    def get_formula(self, category, topic=None):
        """Get a formula from a specific category"""
        try:
            if topic:
                formula_data = self.formulas["formulas"][category].get(topic, None)
                if formula_data:
                    if isinstance(formula_data, dict):
                        # If it's a nested dictionary (like circle with area, circumference)
                        result = []
                        for sub_name, sub_formula in formula_data.items():
                            # Handle potentially deeper nesting
                            if isinstance(sub_formula, dict):
                                result.append(f"{topic} {sub_name}:")
                                for sub_sub_name, sub_sub_formula in sub_formula.items():
                                    result.append(f"  • {sub_sub_name}: {sub_sub_formula}")
                            else:
                                result.append(f"{topic} {sub_name}: {sub_formula}")
                        return "\n".join(result)
                    else:
                        return f"{topic}: {formula_data}"
                else:
                    return f"Formula for {topic} not found in {category}."
            else:
                # Return all formulas in the category
                formulas = self.formulas["formulas"].get(category, {})
                if not formulas:
                    return f"No formulas found for {category}."
                
                result = []
                # For large formula collections, limit to a reasonable number
                max_formulas = 15
                formula_count = 0
                
                for name, formula in formulas.items():
                    if formula_count >= max_formulas:
                        result.append(f"... and more {category} formulas (ask for specific topics for more details)")
                        break
                        
                    if isinstance(formula, dict):
                        # If it's a nested dictionary
                        result.append(f"{name}:")
                        sub_count = 0
                        for sub_name, sub_formula in formula.items():
                            if sub_count < 3:  # Limit to 3 subformulas per topic
                                if isinstance(sub_formula, dict):
                                    result.append(f"  • {sub_name}: (complex formula - ask specifically for details)")
                                else:
                                    result.append(f"  • {sub_name}: {sub_formula}")
                                sub_count += 1
                            formula_count += 1
                            if formula_count >= max_formulas:
                                break
                        if sub_count >= 3:
                            result.append(f"  • ... and more formulas for {name}")
                    else:
                        result.append(f"{name}: {formula}")
                        formula_count += 1
                
                return "\n".join(result)
        except Exception as e:
            print(f"Error getting formula: {e}")
            return "Formula not found."

    def detect_math_expression(self, text):
        """Detect if the input contains a math expression to evaluate"""
        # Skip detection if this is asking about a formula or explanation
        if any(word in text.lower() for word in ['formula', 'explain', 'what is', 'definition']):
            return False
            
        # Skip detection if this is a question about solving quadratic equation
        if 'quadratic' in text.lower() and 'equation' in text.lower() and any(word in text.lower() for word in ['solve', 'how']):
            return False
            
        # Skip if asking about trigonometric functions
        if any(trig in text.lower() for trig in ['sin', 'cos', 'tan', 'soh', 'cah', 'toa']):
            return False
            
        # Skip if asking about integration or differentiation
        if any(calc in text.lower() for calc in ['integrate', 'derivative', 'differentiate']):
            return False
            
        # Check for basic arithmetic with symbols
        if re.search(r'\d[\+\-\*\/\^\(\)]\d', text):
            return True
            
        # Check for arithmetic with words
        if re.search(r'\d+\s*(plus|minus|times|multiplied by|divided by|over)\s*\d+', text.lower()):
            return True
        
        # Check for equation
        if '=' in text and re.search(r'[a-zA-Z]', text):
            return True
            
        return False

    def identify_topic(self, user_input):
        """Identify which math topic the query relates to"""
        user_input = user_input.lower()
        
        # Direct topic mentions take precedence
        direct_mentions = {
            'algebra': ['algebra', 'algebraic', 'equation', 'polynomial', 'quadratic', 'linear'],
            'geometry': ['geometry', 'geometric', 'shape', 'angle', 'circle', 'triangle', 'square'],
            'trigonometry': ['trigonometry', 'trigonometric', 'sin', 'cos', 'tan', 'angle', 'soh', 'cah', 'toa'],
            'calculus': ['calculus', 'derivative', 'integral', 'differentiate', 'integrate'],
            'statistics': ['statistics', 'statistical', 'probability', 'mean', 'median', 'mode'],
            'physics': ['physics', 'physical', 'force', 'motion', 'energy', 'mechanics'],
            'constants': ['constant', 'pi', 'e', 'euler', 'avogadro', 'planck']
        }
        
        # First check for direct mentions of topics
        for topic, mentions in direct_mentions.items():
            if any(mention in user_input for mention in mentions):
                return topic
        
        # Then check using the expanded keyword list with scoring
        topic_scores = {}
        for topic, keywords in self.math_topics.items():
            score = 0
            matched_keywords = []
            
            for keyword in keywords:
                if keyword in user_input:
                    # Give higher score to longer keyword matches
                    score += len(keyword)
                    matched_keywords.append(keyword)
            
            if score > 0:
                topic_scores[topic] = score
        
        if topic_scores:
            # Return the topic with the highest score
            return max(topic_scores, key=topic_scores.get)
        
        # Handle specific operations that might not be captured by keywords
        if any(op in user_input for op in ['times', 'multiply', 'multiplied', 'multiplication', 'divided', 'division', 'plus', 'add', 'minus', 'subtract']):
            return 'algebra'
            
        if any(shape in user_input for shape in ['circle', 'square', 'triangle', 'rectangle', 'sphere', 'cube', 'cone', 'cylinder']):
            return 'geometry'
            
        if 'angle' in user_input or 'degree' in user_input or 'radian' in user_input:
            return 'trigonometry'
            
        # Default return if no topic identified
        return None
            
    def call_claude_api(self, query):
        """Call Claude Sonnet 3.5 API to solve math problems"""
        try:
            # Claude API requires a specific format
            if not self.claude_api_key:
                return None
                
            headers = {
                "x-api-key": self.claude_api_key,
                "content-type": "application/json"
            }
            
            payload = {
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 2048,
                "messages": [
                    {"role": "user", "content": f"Solve this math problem and explain step by step: {query}"}
                ]
            }
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'content' in result and len(result['content']) > 0:
                    # Extract the text content from Claude's response
                    return result['content'][0]['text']
            
            print(f"Claude API error: {response.status_code}")
            return None
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            return None
    
    def call_grok_api(self, query):
        """Call Grok's advanced AI API to solve math problems"""
        try:
            if not self.grok_api_key:
                return None
                
            headers = {
                "Authorization": f"Bearer {self.grok_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [
                    {"role": "user", "content": f"Solve this math problem step by step: {query}"}
                ],
                "model": "grok-advanced-math",
                "temperature": 0.2,
                "max_tokens": 2048
            }
            
            response = requests.post(
                "https://api.grok.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
            
            print(f"Grok API error: {response.status_code}")
            return None
        except Exception as e:
            print(f"Error calling Grok API: {e}")
            return None
            
    def get_advanced_solution(self, query):
        """Get solution from advanced AI models (Claude or Grok)"""
        if not self.use_advanced_ai:
            return None
            
        # Try primary model first
        if self.primary_model == "claude_sonnet":
            solution = self.call_claude_api(query)
            if solution:
                return solution
            elif self.fallback_to_basic:
                # Try Grok as fallback
                solution = self.call_grok_api(query)
                if solution:
                    return solution
        else:  # Grok is primary
            solution = self.call_grok_api(query)
            if solution:
                return solution
            elif self.fallback_to_basic:
                # Try Claude as fallback
                solution = self.call_claude_api(query)
                if solution:
                    return solution
                    
        return None

    def process_query(self, user_input):
        """Process the user's query and generate a response"""
        original_input = user_input
        user_input = user_input.lower()
        
        # Check if it's a greeting
        if any(greeting in user_input for greeting in ['hi', 'hello', 'hey']):
            return random.choice(self.greetings)
        
        # First, try to get solution from advanced AI
        if self.use_advanced_ai:
            advanced_solution = self.get_advanced_solution(original_input)
            if advanced_solution:
                return advanced_solution
                
        # If advanced AI didn't provide a solution, fall back to basic processing
        # Identify the math topic
        topic = self.identify_topic(user_input)
        
        # Detect if this is a math expression to evaluate (like "2+2")
        if self.detect_math_expression(user_input):
            return f"I detected a math expression. To calculate {original_input}, please use the main input field or type 'calculate' followed by your expression."
        
        # Special case for basic operations
        if ('what is' in user_input or 'how do' in user_input or 'explain' in user_input) and any(op in user_input for op in ['times', 'multiply', 'division', 'divide']):
            if 'times' in user_input or 'multiply' in user_input:
                return """Multiplication (often called "times") is a mathematical operation where numbers are added to themselves a specified number of times.
                
For example:
- 3 × 4 means add 3 to itself 4 times: 3 + 3 + 3 + 3 = 12
- The multiplication symbol is '×' or '*'
- The formula for multiplying numbers is: a × b = c

Common multiplication properties:
- Commutative: a × b = b × a
- Associative: (a × b) × c = a × (b × c)
- Distributive: a × (b + c) = (a × b) + (a × c)"""
            else:
                return """Division is a mathematical operation that represents splitting a quantity into equal parts.
                
For example:
- 12 ÷ 4 = 3 means 12 split into 4 equal parts is 3 per part
- The division symbol is '÷', '/' or a fraction line
- The formula for division is: a ÷ b = c, where a is the dividend, b is the divisor, and c is the quotient

Important properties:
- Division by zero is undefined
- Division is not commutative: a ÷ b ≠ b ÷ a
- Division is not associative: (a ÷ b) ÷ c ≠ a ÷ (b ÷ c)"""
                
        # Special case for trigonometry (SOH-CAH-TOA)
        if any(trig in user_input for trig in ['soh cah toa', 'soh-cah-toa', 'sohcahtoa']):
            return """SOH-CAH-TOA is a mnemonic used to remember the three basic trigonometric functions:

SOH = Sine equals Opposite over Hypotenuse
      sin(θ) = opposite / hypotenuse
      
CAH = Cosine equals Adjacent over Hypotenuse
      cos(θ) = adjacent / hypotenuse
      
TOA = Tangent equals Opposite over Adjacent
      tan(θ) = opposite / adjacent = sin(θ) / cos(θ)
      
In a right triangle:
- The hypotenuse is the longest side, opposite to the right angle
- The opposite side is across from the angle you're focusing on
- The adjacent side is next to the angle you're focusing on"""
            
        # Special case for angles and degrees
        if ('angle' in user_input or 'degree' in user_input) and ('what' in user_input or 'explain' in user_input or 'measure' in user_input):
            return """Angles measure the amount of rotation between two lines that meet at a common point (vertex).

Angles are commonly measured in:
- Degrees (°): A full circle is 360°
- Radians (rad): A full circle is 2π radians
- Grads: A full circle is 400 grads

Common angle types:
- Acute angle: Less than 90° (π/2 radians)
- Right angle: Exactly 90° (π/2 radians)
- Obtuse angle: Between 90° and 180° (π/2 to π radians)
- Straight angle: Exactly 180° (π radians)
- Reflex angle: Between 180° and 360° (π to 2π radians)

The formula to convert between degrees and radians is:
- Radians = Degrees × (π/180)
- Degrees = Radians × (180/π)"""
            
        # Special case for integral formulas
        if ('integral' in user_input or 'integration' in user_input) and 'formula' in user_input:
            return """Integration (finding integrals) is a fundamental concept in calculus.

Basic integral formulas:
- Indefinite integral: ∫ f(x) dx = F(x) + C, where F'(x) = f(x) and C is a constant
- Definite integral: ∫(a→b) f(x) dx = F(b) - F(a)

Common integration rules:
1. Power Rule: ∫ xⁿ dx = x^(n+1)/(n+1) + C (for n ≠ -1)
2. Exponential: ∫ eˣ dx = eˣ + C
3. Natural Log: ∫ 1/x dx = ln|x| + C
4. Trigonometric:
   - ∫ sin(x) dx = -cos(x) + C
   - ∫ cos(x) dx = sin(x) + C
   - ∫ tan(x) dx = ln|sec(x)| + C

Integration techniques:
- Substitution: ∫ f(g(x)) · g'(x) dx = ∫ f(u) du (where u = g(x))
- Integration by Parts: ∫ u(x)v'(x) dx = u(x)v(x) - ∫ v(x)u'(x) dx"""
            
        # Special case for circle area formula
        if 'circle' in user_input and 'area' in user_input and 'formula' in user_input:
            return "The formula for the area of a circle is: A = πr², where r is the radius of the circle."
            
        # Special case for quadratic equations
        if 'quadratic' in user_input and 'equation' in user_input:
            # Extract the actual equation if possible
            equation_match = re.search(r'x\^2\s*[\+\-]\s*\d+x\s*[\+\-]\s*\d+\s*=\s*0', user_input)
            if not equation_match:
                equation_match = re.search(r'x²\s*[\+\-]\s*\d+x\s*[\+\-]\s*\d+\s*=\s*0', user_input)
            
            if equation_match:
                equation = equation_match.group(0).strip()
                
                # Parse the coefficients
                equation = equation.replace('²', '^2')
                
                # Extract a, b, c from the equation ax^2 + bx + c = 0
                a = 1  # Default for x^2
                
                # Extract b (coefficient of x)
                b_match = re.search(r'[+-]\s*(\d+)\s*x', equation)
                b = 0
                if b_match:
                    b_sign = '+' if b_match.group(0)[0] == '+' else '-'
                    b_val = int(b_match.group(1))
                    b = b_val if b_sign == '+' else -b_val
                
                # Extract c (constant term)
                c_match = re.search(r'[+-]\s*(\d+)\s*=', equation)
                c = 0
                if c_match:
                    c_sign = '+' if c_match.group(0)[0] == '+' else '-'
                    c_val = int(c_match.group(1))
                    c = c_val if c_sign == '+' else -c_val
                
                # Calculate the discriminant
                discriminant = b**2 - 4*a*c
                
                # Calculate the solutions
                if discriminant < 0:
                    return f"""For the quadratic equation {equation}:

The discriminant b² - 4ac = {b}² - 4({a})({c}) = {discriminant}

Since the discriminant is negative, this equation has no real solutions."""
                elif discriminant == 0:
                    x = -b / (2*a)
                    return f"""For the quadratic equation {equation}:

1. Identify the coefficients: a={a}, b={b}, c={c}
2. Calculate the discriminant: b² - 4ac = {b}² - 4({a})({c}) = {discriminant}
3. Since the discriminant equals zero, there is exactly one solution:
   x = -b/(2a) = -({b})/(2({a})) = {x}

The solution is x = {x}"""
                else:
                    x1 = (-b + math.sqrt(discriminant)) / (2*a)
                    x2 = (-b - math.sqrt(discriminant)) / (2*a)
                    return f"""For the quadratic equation {equation}:

1. Identify the coefficients: a={a}, b={b}, c={c}
2. Calculate the discriminant: b² - 4ac = {b}² - 4({a})({c}) = {discriminant}
3. Apply the quadratic formula: x = (-b ± √(b² - 4ac)) / 2a
   x = (-({b}) ± √{discriminant}) / (2({a}))
4. Solve for both roots:
   x₁ = (-({b}) + √{discriminant}) / {2*a} = {x1}
   x₂ = (-({b}) - √{discriminant}) / {2*a} = {x2}

The solutions are x = {x1} or x = {x2}"""
            
            # If we can't extract the equation, provide a general solution
            return """To solve a quadratic equation in the form ax² + bx + c = 0:

1. Identify the values of a, b, and c
2. Apply the quadratic formula: x = (-b ± √(b² - 4ac)) / 2a
3. Calculate the discriminant: b² - 4ac
4. Find the two solutions by using both + and - in the formula

For example, with x² + 5x + 6 = 0:
- First, make sure it's in the form ax² + bx + c = 0
- We have a=1, b=5, c=6
- Using the quadratic formula: x = (-5 ± √(25 - 24)) / 2
- x = (-5 ± √1) / 2
- x = (-5 ± 1) / 2
- So x = -2 or x = -3"""
            
        # Special case for geometry formulas
        if 'formula' in user_input and 'geometry' in user_input:
            shape = None
            for shape_name in ['circle', 'triangle', 'square', 'rectangle', 'sphere', 'cylinder', 'cone', 'prism', 'pyramid']:
                if shape_name in user_input:
                    shape = shape_name
                    break
            
            if shape:
                formulas = self.get_formula('geometry', shape)
                return f"Here are the formulas for {shape}:\n{formulas}"
            else:
                formulas = self.get_formula('geometry')
                return f"Here are some geometry formulas:\n{formulas}"
        
        # Special case for physics formulas
        if 'formula' in user_input and 'physics' in user_input:
            branch = None
            for branch_name in ['mechanics', 'thermodynamics', 'electromagnetism', 'waves', 'optics', 'quantum', 'relativity']:
                if branch_name in user_input:
                    branch = branch_name
                    break
            
            if branch:
                formulas = self.get_formula('physics', branch)
                return f"Here are the formulas for {branch}:\n{formulas}"
            else:
                formulas = self.get_formula('physics')
                return f"Here are some physics formulas:\n{formulas}"
        
        # Special case for physical constants
        if ('constant' in user_input or 'value' in user_input) and any(const in user_input for const in ['physics', 'physical', 'fundamental']):
            constant = None
            for const_name in ['pi', 'speed of light', 'planck', 'gravitational', 'boltzmann', 'avogadro', 'elementary charge']:
                if const_name in user_input:
                    constant = const_name
                    break
            
            if constant:
                const_value = self.get_formula('constants', constant)
                return f"Here's the value for {constant}:\n{const_value}"
            else:
                constants = self.get_formula('constants')
                return f"Here are some fundamental physical constants:\n{constants}"
        
        # Check if it's asking for a formula
        if 'formula' in user_input or 'equation' in user_input or any(q in user_input for q in ['what is', 'how to calculate', 'how to find']):
            # Direct formula mappings for common requests
            formula_mappings = {
                'area circle': ('geometry', 'circle', 'The formula for the area of a circle is: A = πr²'),
                'circumference circle': ('geometry', 'circle', 'The formula for the circumference of a circle is: C = 2πr'),
                'area triangle': ('geometry', 'triangle', 'The formula for the area of a triangle is: A = (1/2) × b × h'),
                'area rectangle': ('geometry', 'rectangle', 'The formula for the area of a rectangle is: A = length × width'),
                'area square': ('geometry', 'square', 'The formula for the area of a square is: A = s²'),
                'pythagorean theorem': ('geometry', 'triangle', 'The Pythagorean theorem is: a² + b² = c²'),
                'sine': ('trigonometry', 'basic_ratios', 'Sine (sin): sin(θ) = opposite / hypotenuse'),
                'cosine': ('trigonometry', 'basic_ratios', 'Cosine (cos): cos(θ) = adjacent / hypotenuse'),
                'tangent': ('trigonometry', 'basic_ratios', 'Tangent (tan): tan(θ) = opposite / adjacent = sin(θ) / cos(θ)'),
                'quadratic formula': ('algebra', None, 'The quadratic formula is: x = (-b ± √(b² - 4ac)) / 2a'),
                'derivative': ('calculus', 'derivatives', 'The definition of a derivative is: f\'(x) = lim(h→0) [f(x+h) - f(x)] / h'),
                'integral': ('calculus', 'integrals', 'The indefinite integral is: ∫f(x)dx = F(x) + C, where F\'(x) = f(x)'),
                'mean': ('statistics', 'central_tendency', 'The formula for the arithmetic mean is: μ = (x₁ + x₂ + ... + xₙ) / n')
            }
            
            # Check for direct formula matches
            for key_phrase, (category, subtopic, direct_answer) in formula_mappings.items():
                if all(word in user_input for word in key_phrase.split()):
                    if direct_answer:
                        return direct_answer
                    elif subtopic:
                        return self.get_formula(category, subtopic)
                    else:
                        return self.get_formula(category)
            
            if topic:
                # Try to extract specific formula name by matching keywords
                formula_name = None
                matched_keywords = []
                
                for keyword in self.math_topics[topic]:
                    if keyword in user_input:
                        matched_keywords.append(keyword)
                
                # Choose the longest keyword match
                if matched_keywords:
                    formula_name = max(matched_keywords, key=len)
                
                # Special handling for specific topic areas
                if topic == 'physics':
                    # Check for specific physics branches
                    for branch in ['mechanics', 'thermodynamics', 'electromagnetism', 'waves', 'optics', 'quantum', 'relativity']:
                        if branch in user_input:
                            formula_name = branch
                            break
                    
                    # Check for specific mechanics terms
                    if 'mechanics' in user_input or any(term in user_input for term in ['force', 'motion', 'energy', 'power', 'work']):
                        # Handle mechanics subtopics
                        if 'kinematic' in user_input or any(term in user_input for term in ['velocity', 'acceleration', 'displacement']):
                            return self.get_formula('physics', 'mechanics')
                        if 'energy' in user_input or 'potential' in user_input or 'kinetic' in user_input:
                            return self.get_formula('physics', 'mechanics')
                            
                elif topic == 'calculus':
                    # Check for specific calculus topics
                    for calc_topic in ['derivative', 'integral', 'limit', 'series']:
                        if calc_topic in user_input:
                            formula_name = calc_topic
                            break
                            
                elif topic == 'trigonometry':
                    # Handle specific trig formulas
                    if any(trig in user_input for trig in ['sin', 'sine']):
                        return "Sine (sin): sin(θ) = opposite / hypotenuse"
                    elif any(trig in user_input for trig in ['cos', 'cosine']):
                        return "Cosine (cos): cos(θ) = adjacent / hypotenuse"
                    elif any(trig in user_input for trig in ['tan', 'tangent']):
                        return "Tangent (tan): tan(θ) = opposite / adjacent = sin(θ) / cos(θ)"
                    elif 'identity' in user_input:
                        return self.get_formula('trigonometry', 'identities')
                    elif any(law in user_input for law in ['law of sines', 'sine law']):
                        return "Law of Sines: a/sin(A) = b/sin(B) = c/sin(C)"
                    elif any(law in user_input for law in ['law of cosines', 'cosine law']):
                        return "Law of Cosines: c² = a² + b² - 2ab·cos(C)"
                        
                # Get the formula based on the identified name
                if formula_name:
                    formulas = self.get_formula(topic, formula_name)
                    return f"Here's what you need to know about {formula_name} in {topic}:\n{formulas}"
                else:
                    formulas = self.get_formula(topic)
                    return f"Here are some {topic} formulas that might help:\n{formulas}"
            else:
                # Topic wasn't identified, try to guess from keywords
                if any(word in user_input for word in ['area', 'volume', 'perimeter', 'circle', 'triangle', 'square', 'rectangle', 'angle']):
                    if 'circle' in user_input:
                        formulas = self.get_formula('geometry', 'circle')
                    elif 'triangle' in user_input:
                        formulas = self.get_formula('geometry', 'triangle')
                    elif 'square' in user_input:
                        formulas = self.get_formula('geometry', 'square')
                    elif 'rectangle' in user_input:
                        formulas = self.get_formula('geometry', 'rectangle')
                    else:
                        formulas = self.get_formula('geometry')
                    return f"Here are geometry formulas that might help:\n{formulas}"
                    
                elif any(word in user_input for word in ['force', 'energy', 'power', 'work', 'motion', 'velocity', 'acceleration']):
                    formulas = self.get_formula('physics', 'mechanics')
                    return f"Here are some physics mechanics formulas that might help:\n{formulas}"
                    
                elif any(word in user_input for word in ['sin', 'cos', 'tan', 'angle', 'degree', 'radian', 'soh', 'cah', 'toa']):
                    if 'identity' in user_input:
                        formulas = self.get_formula('trigonometry', 'identities')
                    else:
                        formulas = self.get_formula('trigonometry', 'basic_ratios')
                    return f"Here are trigonometry formulas that might help:\n{formulas}"
                    
                elif any(word in user_input for word in ['derivative', 'integral', 'differentiate', 'integrate', 'calculus']):
                    if 'derivative' in user_input or 'differentiate' in user_input:
                        formulas = self.get_formula('calculus', 'derivatives')
                    elif 'integral' in user_input or 'integrate' in user_input:
                        formulas = self.get_formula('calculus', 'integrals')
                    else:
                        formulas = self.get_formula('calculus')
                    return f"Here are calculus formulas that might help:\n{formulas}"
                    
                elif any(word in user_input for word in ['mean', 'average', 'median', 'mode', 'standard deviation', 'variance', 'probability']):
                    formulas = self.get_formula('statistics')
                    return f"Here are statistics formulas that might help:\n{formulas}"
                    
                else:
                    return """I need more information about which formula you're looking for. You can ask about:
- Algebra: quadratic formula, factoring, exponents, logarithms, etc.
- Geometry: area, perimeter, volume, shapes, angles
- Trigonometry: sine, cosine, tangent, SOH-CAH-TOA, identities
- Calculus: derivatives, integrals, limits
- Statistics: mean, median, mode, standard deviation, probability
- Physics: mechanics, thermodynamics, electricity, etc.
- Mathematical constants

What specific formula or topic are you interested in?"""
        
        # Check if it's asking to solve an equation
        if 'solve' in user_input or 'find' in user_input or 'calculate' in user_input:
            # Extract the equation (this is very simplified)
            equation_match = re.search(r'(?:solve|find|calculate)\s+(?:for)?\s*(.+)', user_input)
            if equation_match:
                equation = equation_match.group(1).strip()
                return f"To solve '{equation}', I would need to use techniques from {topic if topic else 'mathematics'}. Let me know if you'd like me to explain the steps."
            else:
                return "Could you provide the equation or expression you want me to solve?"
        
        # Try to handle specific math questions
        if self.is_specific_math_question(user_input):
            return self.handle_specific_math_question(user_input)
            
        # Default response with topic if identified
        if topic:
            response = f"I see you're asking about {topic}. "
            if 'formula' in user_input:
                response += f"I have many {topic} formulas available. Could you specify which formula you're looking for? "
                
                # Suggest some specific formulas based on topic
                if topic == 'algebra':
                    response += "For example: quadratic formula, exponential functions, logarithms, etc."
                elif topic == 'geometry':
                    response += "For example: area of shapes, perimeter, volume, angles, etc."
                elif topic == 'trigonometry':
                    response += "For example: sine, cosine, tangent, identities, etc."
                elif topic == 'calculus':
                    response += "For example: derivatives, integrals, limits, etc."
                elif topic == 'statistics':
                    response += "For example: mean, median, mode, standard deviation, probability, etc."
                elif topic == 'physics':
                    response += "For example: Newton's laws, energy, work, power, thermodynamics, etc."
            else:
                response += "Could you specify what you'd like to know or what problem you need help with?"
            return response
        else:
            return """I'm here to help with math! I can help with:

1. Algebra: equations, expressions, factoring, etc.
2. Geometry: shapes, areas, volumes, angles, etc.
3. Trigonometry: sine, cosine, tangent, SOH-CAH-TOA, etc.
4. Calculus: derivatives, integrals, limits, etc.
5. Statistics: mean, median, mode, probability, etc.
6. Physics formulas and constants

What specific question or problem do you have?"""
    
    def is_specific_math_question(self, user_input):
        """Check if the input is a specific math question"""
        # List of patterns for specific math questions
        patterns = [
            # Times tables questions
            r'what is (\d+) times (\d+)',
            r'what is (\d+) multiplied by (\d+)',
            # Division questions
            r'what is (\d+) divided by (\d+)',
            r'what is (\d+) over (\d+)',
            # Trigonometry questions
            r'what is (sin|cos|tan) of (\d+) degrees',
            r'what is (sin|cos|tan) (\d+)',
            # Area/perimeter questions
            r'area of (a|an)? (circle|square|triangle|rectangle) with (radius|side|base|height|width|length) (\d+)',
            r'perimeter of (a|an)? (circle|square|triangle|rectangle) with (radius|side|base|height|width|length) (\d+)',
            # Angle questions
            r'(supplement|complement) of (\d+) degrees',
            r'convert (\d+) (degrees|radians) to (degrees|radians)'
        ]
        
        # Check if any pattern matches
        for pattern in patterns:
            if re.search(pattern, user_input.lower()):
                return True
                
        # Check for specific keywords in combination
        if ('value' in user_input or 'equal' in user_input) and any(op in user_input for op in ['sin', 'cos', 'tan', 'angle', 'π', 'pi']):
            return True
            
        if ('find' in user_input or 'calculate' in user_input or 'determine' in user_input) and \
           any(term in user_input for term in ['area', 'volume', 'perimeter', 'derivative', 'integral']):
            return True
            
        return False

    def handle_specific_math_question(self, user_input):
        """Handle specific math questions with direct answers"""
        user_input = user_input.lower()
        
        # Handle multiplication (times tables)
        mult_match = re.search(r'what is (\d+) times (\d+)', user_input)
        if not mult_match:
            mult_match = re.search(r'what is (\d+) multiplied by (\d+)', user_input)
        
        if mult_match:
            a = int(mult_match.group(1))
            b = int(mult_match.group(2))
            return f"{a} × {b} = {a * b}"
        
        # Handle division
        div_match = re.search(r'what is (\d+) divided by (\d+)', user_input)
        if not div_match:
            div_match = re.search(r'what is (\d+) over (\d+)', user_input)
        
        if div_match:
            a = int(div_match.group(1))
            b = int(div_match.group(2))
            if b == 0:
                return "Division by zero is undefined."
            return f"{a} ÷ {b} = {a / b}"
        
        # Handle trig functions
        trig_match = re.search(r'what is (sin|cos|tan) of (\d+) degrees', user_input)
        if not trig_match:
            trig_match = re.search(r'what is (sin|cos|tan) (\d+)', user_input)
        
        if trig_match:
            func = trig_match.group(1)
            angle = int(trig_match.group(2))
            
            # Convert to radians for math functions
            angle_rad = math.radians(angle)
            
            if func == 'sin':
                value = math.sin(angle_rad)
                return f"sin({angle}°) = {value:.4f}"
            elif func == 'cos':
                value = math.cos(angle_rad)
                return f"cos({angle}°) = {value:.4f}"
            elif func == 'tan':
                # Check for undefined values (90°, 270°, etc.)
                if angle % 180 == 90:
                    return f"tan({angle}°) is undefined"
                value = math.tan(angle_rad)
                return f"tan({angle}°) = {value:.4f}"
        
        # Handle angle conversions
        angle_conv_match = re.search(r'convert (\d+) (degrees|radians) to (radians|degrees)', user_input)
        if angle_conv_match:
            value = float(angle_conv_match.group(1))
            from_unit = angle_conv_match.group(2)
            to_unit = angle_conv_match.group(3)
            
            if from_unit == 'degrees' and to_unit == 'radians':
                result = math.radians(value)
                return f"{value}° = {result:.6f} radians"
            elif from_unit == 'radians' and to_unit == 'degrees':
                result = math.degrees(value)
                return f"{value} radians = {result:.2f}°"
        
        # Handle area calculations
        area_match = re.search(r'area of (a|an)? (circle|square|triangle|rectangle) with (radius|side|base|height|width|length) (\d+)', user_input)
        if area_match:
            shape = area_match.group(2)
            dimension_type = area_match.group(3)
            dimension = int(area_match.group(4))
            
            if shape == 'circle' and dimension_type == 'radius':
                area = math.pi * dimension**2
                return f"The area of a circle with radius {dimension} is {area:.4f} square units (π × {dimension}²)"
            
            elif shape == 'square' and dimension_type == 'side':
                area = dimension**2
                return f"The area of a square with side length {dimension} is {area} square units ({dimension}²)"
                
            elif shape == 'rectangle':
                # We'd need more info for a rectangle, but let's handle special cases
                if 'width' in user_input and 'length' in user_input:
                    width_match = re.search(r'width (\d+)', user_input)
                    length_match = re.search(r'length (\d+)', user_input)
                    if width_match and length_match:
                        width = int(width_match.group(1))
                        length = int(length_match.group(1))
                        area = width * length
                        return f"The area of a rectangle with width {width} and length {length} is {area} square units"
                
            elif shape == 'triangle':
                # We'd need more info for a triangle, but let's handle special cases
                if 'base' in user_input and 'height' in user_input:
                    base_match = re.search(r'base (\d+)', user_input)
                    height_match = re.search(r'height (\d+)', user_input)
                    if base_match and height_match:
                        base = int(base_match.group(1))
                        height = int(height_match.group(1))
                        area = 0.5 * base * height
                        return f"The area of a triangle with base {base} and height {height} is {area} square units"
        
        # If we get here, it's a specific question but we couldn't handle it directly
        return "I recognize that's a specific math question, but I need more details to solve it correctly. Could you provide more information?"
