# Mathly - AI Model for Math Assistance
import json
import random
import re
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MathAIModel:
    def __init__(self, formulas_file):
        """Initialize the AI model with math knowledge"""
        self.formulas = self.load_formulas(formulas_file)
        self.math_topics = {
            'algebra': ['equation', 'solve', 'variable', 'expression', 'simplify', 'factor', 'expand'],
            'geometry': ['area', 'perimeter', 'volume', 'circle', 'triangle', 'square', 'rectangle'],
            'trigonometry': ['sin', 'cos', 'tan', 'angle', 'degree', 'radian', 'pythagorean'],
            'calculus': ['derivative', 'integral', 'limit', 'differentiate', 'integrate', 'rate of change'],
            'statistics': ['mean', 'median', 'mode', 'standard deviation', 'probability', 'distribution']
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
                return self.formulas["formulas"][category].get(topic, "Formula not found.")
            else:
                # Return all formulas in the category
                formulas = self.formulas["formulas"].get(category, {})
                if not formulas:
                    return f"No formulas found for {category}."
                
                result = []
                for name, formula in formulas.items():
                    result.append(f"{name}: {formula}")
                
                return "\n".join(result)
        except Exception:
            return "Formula not found."

    def detect_math_expression(self, text):
        """Detect if the input contains a math expression to evaluate"""
        # Check for basic arithmetic
        if re.search(r'\d[\+\-\*\/\^\(\)]\d', text):
            return True
        
        # Check for equation
        if '=' in text and re.search(r'[a-zA-Z]', text):
            return True
            
        return False

    def identify_topic(self, user_input):
        """Identify which math topic the query relates to"""
        user_input = user_input.lower()
        
        # Check each topic's keywords
        topic_scores = {}
        for topic, keywords in self.math_topics.items():
            score = 0
            for keyword in keywords:
                if keyword in user_input:
                    score += 1
            if score > 0:
                topic_scores[topic] = score
        
        if topic_scores:
            # Return the topic with the highest score
            return max(topic_scores, key=topic_scores.get)
        else:
            return None

    def process_query(self, user_input):
        """Process the user's query and generate a response"""
        user_input = user_input.lower()
        
        # Check if it's a greeting
        if any(greeting in user_input for greeting in ['hi', 'hello', 'hey']):
            return random.choice(self.greetings)
        
        # Identify the math topic
        topic = self.identify_topic(user_input)
        
        # Check if it's asking for a formula
        if 'formula' in user_input or 'equation' in user_input:
            if topic:
                # Try to extract specific formula name
                formula_name = None
                for keyword in self.math_topics[topic]:
                    if keyword in user_input:
                        formula_name = keyword
                        break
                        
                formulas = self.get_formula(topic, formula_name)
                template = random.choice(self.response_templates['provide_formula'])
                return template.format(topic, formulas)
            else:
                return "I need more information about which formula you're looking for. Could you specify the topic?"
        
        # Check if it's asking to solve an equation
        if 'solve' in user_input or 'find' in user_input or 'calculate' in user_input:
            # Extract the equation (this is very simplified)
            equation_match = re.search(r'(?:solve|find|calculate)\s+(?:for)?\s*(.+)', user_input)
            
            if equation_match:
                equation = equation_match.group(1).strip()
                return f"To solve '{equation}', I would need to use techniques from {topic if topic else 'mathematics'}. Let me know if you'd like me to explain the steps."
            else:
                return "Could you provide the equation or expression you want me to solve?"
        
        # Default response with topic if identified
        if topic:
            return f"I see you're asking about {topic}. Could you specify what you'd like to know or what problem you need help with?"
        else:
            return "I'm here to help with math! What specific question or problem do you have?"

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

# Example usage
if __name__ == "__main__":
    model = MathAIModel('data/math_formulas.json')
    print(model.process_query("Can you give me the formula for area of a circle?"))