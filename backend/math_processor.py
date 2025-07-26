# MathProcessor - Handle mathematical operations and expressions
import math
import re
import numpy as np # type: ignore
from sympy import symbols, solve, simplify, expand, factor, sympify, Eq, diff, integrate, limit, Symbol # type: ignore
from sympy.parsing.sympy_parser import parse_expr # type: ignore
from pathlib import Path
import json

class MathProcessor:
    def __init__(self):
        # Create a dictionary of safe functions that can be used with eval
        self.safe_functions = {
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
            'sum': sum,
            'pow': pow,
            'math': math
        }
        
        # Add all math module functions
        for func_name in dir(math):
            if not func_name.startswith('_'):
                self.safe_functions[func_name] = getattr(math, func_name)
        
        # Load formulas
        formulas_path = Path(__file__).parent.parent / 'data' / 'math_formulas.json'
        with open(formulas_path) as f:
            self.formulas = json.load(f)

    def evaluate_expression(self, expression):
        """Safely evaluate a mathematical expression"""
        try:
            # Clean and secure the expression
            cleaned_expr = self._clean_expression(expression)
            return eval(cleaned_expr, {"__builtins__": {}}, self.safe_functions)
        except Exception as e:
            return f"Error: {str(e)}"

    def _clean_expression(self, expression):
        """Clean and secure the expression for evaluation"""
        # Remove any potentially dangerous code
        if any(keyword in expression for keyword in ['import', 'exec', 'eval', 'compile', 'open', '__']):
            raise ValueError("Potentially unsafe expression")
        return expression
    
    def solve_basic_equation(self, equation):
        """Solve a simple linear equation using basic algebra"""
        try:
            # Handle equations like "2x + 3 = 7"
            if '=' in equation:
                left, right = equation.split('=')
                # Very basic solver for ax + b = c format
                # This is a simplification; real implementation would need more parsing
                if 'x' in left:
                    # Move all non-x terms to the right side
                    terms = left.split('+')
                    x_term = None
                    constant = 0
                    
                    for term in terms:
                        term = term.strip()
                        if 'x' in term:
                            x_term = term
                        else:
                            try:
                                constant += float(term)
                            except:
                                return "Sorry, I can only solve simple linear equations right now."
                    
                    # Get coefficient of x
                    coef = 1.0
                    if x_term != 'x':
                        coef_str = x_term.replace('x', '')
                        if coef_str in ['+', '-', '*', '/']:
                            coef = 1.0 if coef_str == '+' else -1.0
                        else:
                            try:
                                coef = float(coef_str)
                            except:
                                return "Sorry, I can only solve simple linear equations right now."
                    
                    # Solve for x
                    right_val = float(right) - constant
                    result = right_val / coef
                    return f"x = {result}"
                else:
                    return "Sorry, I can only solve simple linear equations right now."
            else:
                return "Please provide an equation with an equals sign (=)."
        except Exception as e:
            return f"Error solving equation: {str(e)}"
    
    def solve_equation_with_steps(self, equation):
        """Solve an equation with step-by-step explanation"""
        try:
            # Extract just the equation if there's text around it
            equation_pattern = r'([^=]*=\s*[^=]*)'
            equation_match = re.search(equation_pattern, equation)
            if equation_match:
                equation = equation_match.group(1).strip()
            
            # Check for common equation patterns in text
            if 'x^2' in equation or 'x²' in equation:
                equation = re.sub(r'x²', 'x**2', equation)
                equation = re.sub(r'x\^2', 'x**2', equation)
            
            # Parse the equation
            if '=' not in equation:
                equation = equation + " = 0"  # Convert expressions to equations

            # Split the equation into left and right parts
            left_str, right_str = equation.split('=')
            left_str = left_str.strip()
            right_str = right_str.strip()

            # Clean the expressions (replace ^ with **)
            left_str = left_str.replace('^', '**')
            right_str = right_str.replace('^', '**')
            
            # Add multiplication operators where needed (e.g., 2x -> 2*x)
            left_str = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', left_str)
            right_str = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', right_str)
            
            print(f"Parsing equation: Left: '{left_str}', Right: '{right_str}'")
            
            # Convert to SymPy expressions
            x = symbols('x')
            
            # Special handling for simple cases
            if re.match(r'^x\*\*2\s*[\+\-]\s*\d+\s*\*\s*x\s*[\+\-]\s*\d+$', left_str) and right_str == '0':
                # Directly extract coefficients for quadratic equation ax^2 + bx + c = 0
                print("Detected standard form quadratic equation")
                return self._solve_quadratic_with_steps(left_str)
                
            left_expr = parse_expr(left_str)
            right_expr = parse_expr(right_str)
            
            # Create the equation
            eq = Eq(left_expr, right_expr)
            
            # Solve the equation
            solution = solve(eq, x)
            
            # Generate step-by-step explanation
            steps = []
            display_left = left_str.replace('**', '^').replace('*', '·')
            display_right = right_str.replace('**', '^').replace('*', '·')
            steps.append(f"Step 1: Start with the equation {display_left} = {display_right}")
            
            # Move all terms to left side
            steps.append(f"Step 2: Subtract {display_right} from both sides")
            steps.append(f"         {display_left} - {display_right} = 0")
            
            # Simplify
            simplified = simplify(left_expr - right_expr)
            simplified_str = str(simplified).replace('**', '^').replace('*', '·')
            steps.append(f"Step 3: Simplify the equation")
            steps.append(f"         {simplified_str} = 0")
            
            # Solve for x
            if solution:
                steps.append(f"Step 4: Solve for x")
                solution_str = str(solution).replace('**', '^').replace('*', '·')
                steps.append(f"         x = {solution_str}")
                steps.append(f"\nAnswer: x = {solution_str}")
            else:
                steps.append("\nNo solution found.")
                
            return "\n".join(steps)
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            return f"Error solving equation: {str(e)}\n{traceback_str}"
    
    def differentiate_with_steps(self, expression, variable='x'):
        """Differentiate an expression with step-by-step explanation"""
        try:
            # Clean the expression (replace ^ with ** and add * where needed)
            clean_expr = expression.replace('^', '**')
            
            # Add multiplication operators where needed (e.g., 2x -> 2*x)
            clean_expr = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', clean_expr)
            
            # Parse the expression
            x = symbols(variable)
            expr = parse_expr(clean_expr)
            
            # Compute the derivative
            derivative = diff(expr, x)
            
            # Generate step-by-step explanation
            steps = []
            steps.append(f"Step 1: Start with the expression f({variable}) = {expression}")
            steps.append(f"Step 2: Apply differentiation rules")
            
            # If expression is a sum/difference, show term-by-term differentiation
            terms = clean_expr.split('+')
            if len(terms) > 1:
                steps.append(f"         We can differentiate each term separately:")
                for i, term in enumerate(terms):
                    term = term.strip()
                    if '-' in term and term[0] != '-':
                        # Handle subtraction within terms
                        sub_terms = term.split('-')
                        for j, sub_term in enumerate(sub_terms):
                            if j == 0:
                                result = diff(parse_expr(sub_term), x)
                                display_term = sub_term.replace('**', '^').replace('*', '·')
                                steps.append(f"         d/d{variable}({display_term}) = {str(result).replace('**', '^').replace('*', '·')}")
                            else:
                                result = diff(-parse_expr(sub_term), x)
                                display_term = sub_term.replace('**', '^').replace('*', '·')
                                steps.append(f"         d/d{variable}(-{display_term}) = {str(result).replace('**', '^').replace('*', '·')}")
                    else:
                        result = diff(parse_expr(term), x)
                        display_term = term.replace('**', '^').replace('*', '·')
                        steps.append(f"         d/d{variable}({display_term}) = {str(result).replace('**', '^').replace('*', '·')}")
            
            # Show product rule, quotient rule, chain rule application if relevant
            if '*' in clean_expr and '/' not in clean_expr:
                steps.append(f"         Using the product rule: d/d{variable}(f·g) = f·(dg/d{variable}) + g·(df/d{variable})")
            elif '/' in clean_expr:
                steps.append(f"         Using the quotient rule: d/d{variable}(f/g) = (g·(df/d{variable}) - f·(dg/d{variable}))/g²")
            
            steps.append(f"Step 3: Simplify the result")
            formatted_derivative = str(derivative).replace('**', '^').replace('*', '·')
            steps.append(f"         d/d{variable}({expression}) = {formatted_derivative}")
            steps.append(f"\nAnswer: d/d{variable}({expression}) = {formatted_derivative}")
                
            return "\n".join(steps)
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            return f"Error differentiating expression: {str(e)}\n{traceback_str}"
    
    def integrate_with_steps(self, expression, variable='x'):
        """Integrate an expression with step-by-step explanation"""
        try:
            # Clean the expression (replace ^ with **)
            clean_expr = expression.replace('^', '**')
            
            # Add multiplication operators where needed (e.g., 2x -> 2*x)
            clean_expr = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', clean_expr)
            
            # Parse the expression
            x = symbols(variable)
            expr = parse_expr(clean_expr)
            
            # Compute the integral
            integral = integrate(expr, x)
            
            # Generate step-by-step explanation
            steps = []
            steps.append(f"Step 1: Start with the expression {expression}")
            steps.append(f"Step 2: Apply integration rules")
            
            # If expression is a sum/difference, show term-by-term integration
            terms = clean_expr.split('+')
            if len(terms) > 1:
                steps.append(f"         We can integrate each term separately:")
                for i, term in enumerate(terms):
                    term = term.strip()
                    if '-' in term and term[0] != '-':
                        # Handle subtraction within terms
                        sub_terms = term.split('-')
                        for j, sub_term in enumerate(sub_terms):
                            if j == 0:
                                result = integrate(parse_expr(sub_term), x)
                                display_term = sub_term.replace('**', '^').replace('*', '·')
                                steps.append(f"         ∫{display_term} d{variable} = {str(result).replace('**', '^').replace('*', '·')}")
                            else:
                                result = integrate(-parse_expr(sub_term), x)
                                display_term = sub_term.replace('**', '^').replace('*', '·')
                                steps.append(f"         ∫-{display_term} d{variable} = {str(result).replace('**', '^').replace('*', '·')}")
                    else:
                        result = integrate(parse_expr(term), x)
                        display_term = term.replace('**', '^').replace('*', '·')
                        steps.append(f"         ∫{display_term} d{variable} = {str(result).replace('**', '^').replace('*', '·')}")
            
            # Show specific integration rules applied
            if f"{variable}**" in clean_expr or f"{variable}^" in expression:
                steps.append(f"         Using power rule: ∫{variable}^n d{variable} = {variable}^(n+1)/(n+1) + C")
            elif f"sin({variable})" in clean_expr:
                steps.append(f"         Using sin rule: ∫sin({variable}) d{variable} = -cos({variable}) + C")
            elif f"cos({variable})" in clean_expr:
                steps.append(f"         Using cos rule: ∫cos({variable}) d{variable} = sin({variable}) + C")
            elif f"e**{variable}" in clean_expr or f"exp({variable})" in clean_expr:
                steps.append(f"         Using exponential rule: ∫e^{variable} d{variable} = e^{variable} + C")
            
            steps.append(f"Step 3: Add the constant of integration")
            formatted_integral = str(integral).replace('**', '^').replace('*', '·')
            steps.append(f"         ∫{expression} d{variable} = {formatted_integral} + C")
            steps.append(f"\nAnswer: ∫{expression} d{variable} = {formatted_integral} + C")
                
            return "\n".join(steps)
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            return f"Error integrating expression: {str(e)}\n{traceback_str}"
    
    def calculate_limit(self, expression, variable='x', point='0'):
        """Calculate the limit of an expression as variable approaches point"""
        try:
            # Clean the expression (replace ^ with **)
            clean_expr = expression.replace('^', '**')
            
            # Add multiplication operators where needed (e.g., 2x -> 2*x)
            clean_expr = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', clean_expr)
            
            # Parse the expression and point
            x = symbols(variable)
            expr = parse_expr(clean_expr)
            
            # Handle infinity
            if str(point).lower() in ['inf', 'infinity', '∞']:
                point_eval = float('inf')
            elif str(point).lower() in ['-inf', '-infinity', '-∞']:
                point_eval = float('-inf')
            else:
                point_eval = float(point)
            
            # Calculate the limit
            result = limit(expr, x, point_eval)
            
            # Generate explanation
            explanation = [
                f"Calculating limit of {expression} as {variable} approaches {point}:",
                f"lim_{{{variable}→{point}}} {expression} = {str(result).replace('**', '^').replace('*', '·')}"
            ]
            
            # Check for special cases
            if result == float('inf') or result == float('-inf'):
                explanation.append(f"The limit is {'positive' if result > 0 else 'negative'} infinity.")
            
            # Check for indeterminate forms
            if str(result) == 'nan':
                explanation.append("This appears to be an indeterminate form.")
                
                # Try using L'Hôpital's rule for 0/0 or ∞/∞ forms
                if '/' in clean_expr:
                    explanation.append("We can try using L'Hôpital's rule.")
                    num, denom = clean_expr.split('/')
                    num_expr = parse_expr(num)
                    denom_expr = parse_expr(denom)
                    
                    # Check limits of numerator and denominator separately
                    num_limit = limit(num_expr, x, point_eval)
                    denom_limit = limit(denom_expr, x, point_eval)
                    
                    if (num_limit == 0 and denom_limit == 0) or \
                       (abs(num_limit) == float('inf') and abs(denom_limit) == float('inf')):
                        # Apply L'Hôpital's rule
                        num_diff = diff(num_expr, x)
                        denom_diff = diff(denom_expr, x)
                        new_expr = num_diff / denom_diff
                        new_result = limit(new_expr, x, point_eval)
                        
                        num_diff_str = str(num_diff).replace('**', '^').replace('*', '·')
                        denom_diff_str = str(denom_diff).replace('**', '^').replace('*', '·')
                        new_result_str = str(new_result).replace('**', '^').replace('*', '·')
                        explanation.append(f"Applying L'Hôpital's rule:")
                        explanation.append(f"lim_{{{variable}→{point}}} {num_diff_str}/{denom_diff_str} = {new_result_str}")
                        result = new_result
            
            result_str = str(result).replace('**', '^').replace('*', '·')
            explanation.append(f"\nAnswer: The limit equals {result_str}")
            return "\n".join(explanation)
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            return f"Error calculating limit: {str(e)}\n{traceback_str}"
    
    def factor_expression(self, expression):
        """Factor an algebraic expression with explanation"""
        try:
            # Clean the expression (replace ^ with **)
            clean_expr = expression.replace('^', '**')
            
            # Add multiplication operators where needed (e.g., 2x -> 2*x)
            clean_expr = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', clean_expr)
            
            # Parse the expression
            expr = parse_expr(clean_expr)
            
            # Factor the expression
            factored = factor(expr)
            
            # Generate explanation
            explanation = [
                f"Factoring the expression {expression}:",
                f"Step 1: Identify common factors and factorizable patterns"
            ]
            
            # Check if it's a quadratic and show the steps
            if expr.is_polynomial() and expr.as_poly().degree() == 2:
                explanation.append(f"Step 2: This is a quadratic expression. We can factor it using the quadratic formula or grouping.")
            elif '*' in str(factored) and str(factored) != str(expr):
                explanation.append(f"Step 2: Extract common factors and identify factorizable patterns")
            else:
                explanation.append(f"Step 2: Apply algebraic factoring techniques")
                
            explanation.append(f"Step 3: The factored form is:")
            formatted_factored = str(factored).replace('**', '^').replace('*', '·')
            explanation.append(f"{formatted_factored}")
            
            # If no factorization was possible
            if str(factored) == str(expr):
                explanation.append("\nThis expression is already in its simplest factored form.")
            
            explanation.append(f"\nAnswer: {expression} = {formatted_factored}")
            return "\n".join(explanation)
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            return f"Error factoring expression: {str(e)}\n{traceback_str}"
    
    def expand_expression(self, expression):
        """Expand an algebraic expression with explanation"""
        try:
            # Clean the expression (replace ^ with **)
            clean_expr = expression.replace('^', '**')
            
            # Add multiplication operators where needed (e.g., 2x -> 2*x)
            clean_expr = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', clean_expr)
            
            # Parse the expression
            expr = parse_expr(clean_expr)
            
            # Expand the expression
            expanded = expand(expr)
            
            # Generate explanation
            explanation = [
                f"Expanding the expression {expression}:",
                f"Step 1: Apply the distributive property to remove parentheses"
            ]
            
            if '**2' in str(expr) or '^2' in expression:
                explanation.append(f"Step 2: Use the formula (a + b)² = a² + 2ab + b² or similar patterns")
            elif '*' in str(expr):
                explanation.append(f"Step 2: Multiply each term in the first parenthesis by each term in the second")
            
            explanation.append(f"Step 3: Combine like terms")
            explanation.append(f"The expanded form is:")
            formatted_expanded = str(expanded).replace('**', '^').replace('*', '·')
            explanation.append(f"{formatted_expanded}")
            
            # If no expansion was possible
            if str(expanded) == str(expr):
                explanation.append("\nThis expression is already in its expanded form.")
            
            explanation.append(f"\nAnswer: {expression} = {formatted_expanded}")
            return "\n".join(explanation)
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            return f"Error expanding expression: {str(e)}\n{traceback_str}"
    
    def get_formula(self, category, formula_name):
        """Get a specific formula from the loaded formulas"""
        try:
            return self.formulas["formulas"][category][formula_name]
        except KeyError:
            return "Formula not found."
    
    def get_all_formulas_in_category(self, category):
        """Get all formulas in a category"""
        try:
            category_formulas = self.formulas["formulas"][category]
            result = []
            for name, formula in category_formulas.items():
                result.append(f"{name}: {formula}")
            return "\n".join(result)
        except KeyError:
            return f"Category '{category}' not found in formulas."
    
    def identify_problem_type(self, problem_text):
        """Try to determine the type of math problem"""
        problem_text = problem_text.lower()
        
        # Check for equations with explicit patterns first
        quadratic_patterns = [
            r'x\^2', r'x²', r'\dx\^2', r'\dx²',  # Finds x^2, x², 2x^2, etc.
            r'quadratic equation', r'quadratic formula'
        ]
        
        # Check for quadratic equation patterns
        for pattern in quadratic_patterns:
            if re.search(pattern, problem_text):
                return 'quadratic_equation'
        
        # Check for other types of equations
        if 'solve' in problem_text and ('equation' in problem_text or '=' in problem_text):
            return 'equation'
        elif 'derivative' in problem_text or 'differentiate' in problem_text:
            return 'differentiation'
        elif 'integrate' in problem_text or 'integral' in problem_text:
            return 'integration'
        elif 'limit' in problem_text:
            return 'limit'
        elif 'factor' in problem_text:
            return 'factoring'
        elif 'expand' in problem_text:
            return 'expansion'
        elif 'formula' in problem_text or 'formulas' in problem_text:
            for category in self.formulas["formulas"]:
                if category in problem_text:
                    return f'formula_{category}'
            return 'formula_general'
        elif any(kw in problem_text for kw in ['calculate', 'compute', 'evaluate']):
            return 'calculation'
        # Check if the text contains an equation with x² or x^2
        elif re.search(r'x\^2|x²', problem_text) and ('=' in problem_text):
            return 'quadratic_equation'
        else:
            return 'general'
    
    def process_image_text(self, text):
        """Process extracted text from an image to identify and solve math problems"""
        try:
            # Clean up the extracted text
            cleaned_text = text.strip().replace('\n', ' ')
            
            # Identify the problem type
            problem_type = self.identify_problem_type(cleaned_text)
            
            # Extract the actual math expression or equation
            expression = self._extract_math_expression(cleaned_text)
            
            # Solve based on problem type
            if problem_type == 'equation':
                return self.solve_equation_with_steps(expression)
            elif problem_type == 'differentiation':
                # Extract variable if specified
                var_match = re.search(r'with respect to ([a-z])', cleaned_text.lower())
                variable = var_match.group(1) if var_match else 'x'
                return self.differentiate_with_steps(expression, variable=variable)
            elif problem_type == 'integration':
                # Extract variable if specified
                var_match = re.search(r'with respect to ([a-z])', cleaned_text.lower())
                variable = var_match.group(1) if var_match else 'x'
                return self.integrate_with_steps(expression, variable=variable)
            elif problem_type == 'limit':
                # Extract limit point and variable if specified
                var_match = re.search(r'(?:as|when)\s+([a-z])\s+(?:approaches|→|goes to|tends to)\s+([\w\-\+\.∞]+)', cleaned_text.lower())
                if var_match:
                    variable = var_match.group(1)
                    point = var_match.group(2)
                else:
                    variable = 'x'
                    point_match = re.search(r'as\s+\w+\s+approaches\s+([\w\-\+\.∞]+)', cleaned_text.lower())
                    point = point_match.group(1) if point_match else '0'
                
                return self.calculate_limit(expression, variable=variable, point=point)
            elif problem_type == 'factoring':
                return self.factor_expression(expression)
            elif problem_type == 'expansion':
                return self.expand_expression(expression)
            else:
                # Try to evaluate as a general expression
                return self.evaluate_expression(expression)
        except Exception as e:
            return f"Error processing image text: {str(e)}"
    
    def _extract_math_expression(self, text):
        """Extract the mathematical expression from text"""
        # Look for common patterns in math problems
        equation_patterns = [
            r'(?:solve|find)?\s*(?:the)?\s*(?:equation)?\s*(.+?=.+?)(?:$|\.|\?)',  # Equations with =
            r'(?:evaluate|calculate|compute|find|determine)\s*(?:the)?\s*(?:value of)?\s*(.+?)(?:$|\.|\?)',  # Expressions to evaluate
            r'(?:differentiate|derivative of|integrate|integral of|limit of|factor|expand)\s*(.+?)(?:$|with respect to|\.|when|\?)',  # Calculus problems
        ]
        
        for pattern in equation_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no pattern matches, return the cleaned text
        return text.strip()

    def process_question(self, question):
        """Process a math question and return the result"""
        try:
            # Identify the type of problem
            problem_type = self.identify_problem_type(question)
            
            # Extract the mathematical expression
            expression = self._extract_math_expression(question)
            
            # Process based on problem type
            if problem_type == 'equation':
                return self.solve_equation_with_steps(expression)
            elif problem_type == 'differentiation':
                return self.differentiate_with_steps(expression)
            elif problem_type == 'integration':
                return self.integrate_with_steps(expression)
            elif problem_type == 'limit':
                # Extract limit point if specified
                match = re.search(r'as\s+\w+\s+approaches\s+([\w\-\+\.]+)', question.lower())
                point = match.group(1) if match else '0'
                return self.calculate_limit(expression, point=point)
            elif problem_type == 'factoring':
                return self.factor_expression(expression)
            elif problem_type == 'expansion':
                return self.expand_expression(expression)
            elif problem_type.startswith('formula_'):
                category = problem_type.split('_')[1]
                return self.get_all_formulas_in_category(category)
            elif problem_type == 'calculation':
                return self.evaluate_expression(expression)
            else:
                return "I'm not sure how to solve this problem. Could you please rephrase it?"
        except Exception as e:
            return f"Error processing question: {str(e)}"
    
    def _solve_quadratic_with_steps(self, equation):
        """Solve a quadratic equation with step-by-step explanation"""
        try:
            # Try to extract coefficients a, b, c from ax^2 + bx + c = 0
            a, b, c = 0, 0, 0
            
            # Extract a (coefficient of x^2)
            a_match = re.search(r'^([+-]?\s*\d*)\s*\*?\s*x\*\*2', equation)
            if a_match:
                a_str = a_match.group(1).strip()
                if a_str == '' or a_str == '+':
                    a = 1
                elif a_str == '-':
                    a = -1
                else:
                    a = float(a_str.replace('*', '').strip())
            
            # Extract b (coefficient of x)
            b_match = re.search(r'[+-]\s*(\d*)\s*\*?\s*x(?!\*)', equation)
            if b_match:
                b_str = b_match.group(0).strip()  # Include the sign
                if b_str == '+x' or b_str == '+ x':
                    b = 1
                elif b_str == '-x' or b_str == '- x':
                    b = -1
                else:
                    # Extract just the number and sign
                    b_val = re.search(r'[+-]\s*(\d*)', b_str)
                    if b_val:
                        if b_val.group(1) == '':  # Just + or -
                            b = 1 if b_str.strip()[0] == '+' else -1
                        else:
                            b = float(b_val.group(0).replace('*', '').strip())
            
            # Extract c (constant term)
            c_match = re.search(r'[+-]\s*(\d+)(?!\s*\*?\s*x)', equation)
            if c_match:
                c_str = c_match.group(0).strip()  # Include the sign
                c = float(c_str.replace('*', '').strip())
            
            print(f"Quadratic equation coefficients: a={a}, b={b}, c={c}")
            
            # Calculate discriminant
            discriminant = b**2 - 4*a*c
            
            # Generate step-by-step explanation
            steps = []
            steps.append(f"Step 1: Identify that this is a quadratic equation in the form ax² + bx + c = 0")
            steps.append(f"Step 2: Identify the coefficients: a={a}, b={b}, c={c}")
            steps.append(f"Step 3: Calculate the discriminant: b² - 4ac = {b}² - 4({a})({c}) = {discriminant}")
            
            if discriminant < 0:
                steps.append(f"Step 4: Since the discriminant is negative, there are no real solutions")
                steps.append("\nThis equation has no real solutions.")
            elif discriminant == 0:
                x = -b / (2*a)
                steps.append(f"Step 4: Since the discriminant is zero, there is exactly one solution")
                steps.append(f"Step 5: x = -b / (2a) = -({b}) / (2({a})) = {x}")
                steps.append(f"\nAnswer: x = {x}")
            else:
                x1 = (-b + math.sqrt(discriminant)) / (2*a)
                x2 = (-b - math.sqrt(discriminant)) / (2*a)
                steps.append(f"Step 4: Use the quadratic formula: x = (-b ± √(b² - 4ac)) / 2a")
                steps.append(f"Step 5: x = (-({b}) ± √{discriminant}) / (2({a}))")
                steps.append(f"Step 6: Solve for both roots:")
                steps.append(f"        x₁ = (-({b}) + √{discriminant}) / {2*a} = {x1}")
                steps.append(f"        x₂ = (-({b}) - √{discriminant}) / {2*a} = {x2}")
                steps.append(f"\nAnswer: x = {x1} or x = {x2}")
            
            return "\n".join(steps)
            
        except Exception as e:
            print(f"Error in _solve_quadratic_with_steps: {e}")
            return f"Error solving quadratic equation: {str(e)}"
