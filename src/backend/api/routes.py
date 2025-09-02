from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from typing import Dict, Any

from ..classifier import MathClassifier
from ..solver import MathSolver
from ..explainer import MathExplainer, ExplanationStyle

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

classifier = MathClassifier()
solver = MathSolver()
explainer = MathExplainer()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "AI Math Tutor"})

@app.route('/classify', methods=['POST'])
def classify_problem():
    try:
        data = request.get_json()
        if not data or 'problem' not in data:
            return jsonify({"error": "Missing 'problem' field"}), 400
        
        problem = data['problem']
        if not isinstance(problem, str) or not problem.strip():
            return jsonify({"error": "Problem must be a non-empty string"}), 400
        
        result = classifier.classify(problem)
        return jsonify({
            "success": True,
            "classification": result.to_dict(),
            "explanation": classifier.get_classification_explanation(problem)
        })
    
    except Exception as e:
        logger.error(f"Classification error: {str(e)}")
        return jsonify({"error": f"Classification failed: {str(e)}"}), 500

@app.route('/solve', methods=['POST'])
def solve_problem():
    try:
        data = request.get_json()
        if not data or 'problem' not in data:
            return jsonify({"error": "Missing 'problem' field"}), 400
        
        problem = data['problem']
        if not isinstance(problem, str) or not problem.strip():
            return jsonify({"error": "Problem must be a non-empty string"}), 400
        
        classification = classifier.classify(problem)
        solution = solver.solve_problem(classification, problem)
        
        if "error" in solution:
            return jsonify({
                "success": False,
                "error": solution["error"],
                "classification": classification.to_dict()
            })
        
        return jsonify({
            "success": True,
            "classification": classification.to_dict(),
            "solution": solution
        })
    
    except Exception as e:
        logger.error(f"Solving error: {str(e)}")
        return jsonify({"error": f"Solving failed: {str(e)}"}), 500

@app.route('/explain', methods=['POST'])
def explain_problem():
    try:
        data = request.get_json()
        if not data or 'problem' not in data:
            return jsonify({"error": "Missing 'problem' field"}), 400
        
        problem = data['problem']
        style = data.get('style', 'intermediate')
        
        if not isinstance(problem, str) or not problem.strip():
            return jsonify({"error": "Problem must be a non-empty string"}), 400
        
        try:
            explanation_style = ExplanationStyle(style)
        except ValueError:
            explanation_style = ExplanationStyle.INTERMEDIATE
        
        classification = classifier.classify(problem)
        solution = solver.solve_problem(classification, problem)
        
        if "error" in solution:
            return jsonify({
                "success": False,
                "error": solution["error"],
                "classification": classification.to_dict()
            })
        
        steps = solution.get("steps", [])
        explanation = explainer.explain_solution(
            problem, 
            classification, 
            steps, 
            explanation_style
        )
        
        return jsonify({
            "success": True,
            "classification": classification.to_dict(),
            "solution": solution,
            "explanation": explanation
        })
    
    except Exception as e:
        logger.error(f"Explanation error: {str(e)}")
        return jsonify({"error": f"Explanation failed: {str(e)}"}), 500

@app.route('/full_analysis', methods=['POST'])
def full_analysis():
    try:
        data = request.get_json()
        if not data or 'problem' not in data:
            return jsonify({"error": "Missing 'problem' field"}), 400
        
        problem = data['problem']
        style = data.get('style', 'intermediate')
        
        if not isinstance(problem, str) or not problem.strip():
            return jsonify({"error": "Problem must be a non-empty string"}), 400
        
        try:
            explanation_style = ExplanationStyle(style)
        except ValueError:
            explanation_style = ExplanationStyle.INTERMEDIATE
        
        classification = classifier.classify(problem)
        solution = solver.solve_problem(classification, problem)
        
        if "error" in solution:
            return jsonify({
                "success": False,
                "error": solution["error"],
                "classification": classification.to_dict()
            })
        
        steps = solution.get("steps", [])
        explanation = explainer.explain_solution(
            problem, 
            classification, 
            steps, 
            explanation_style
        )
        
        return jsonify({
            "success": True,
            "problem": problem,
            "classification": classification.to_dict(),
            "solution": solution,
            "explanation": explanation,
            "metadata": {
                "confidence": classification.confidence,
                "difficulty": str(classification.difficulty),
                "subjects": [str(s) for s in classification.subjects],
                "problem_type": str(classification.problem_type)
            }
        })
    
    except Exception as e:
        logger.error(f"Full analysis error: {str(e)}")
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

@app.route('/batch_classify', methods=['POST'])
def batch_classify():
    try:
        data = request.get_json()
        if not data or 'problems' not in data:
            return jsonify({"error": "Missing 'problems' field"}), 400
        
        problems = data['problems']
        if not isinstance(problems, list):
            return jsonify({"error": "Problems must be a list"}), 400
        
        results = []
        for problem in problems:
            try:
                classification = classifier.classify(problem)
                results.append({
                    "problem": problem,
                    "classification": classification.to_dict(),
                    "success": True
                })
            except Exception as e:
                results.append({
                    "problem": problem,
                    "error": str(e),
                    "success": False
                })
        
        return jsonify({
            "success": True,
            "results": results,
            "total": len(problems),
            "successful": sum(1 for r in results if r["success"])
        })
    
    except Exception as e:
        logger.error(f"Batch classification error: {str(e)}")
        return jsonify({"error": f"Batch classification failed: {str(e)}"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
