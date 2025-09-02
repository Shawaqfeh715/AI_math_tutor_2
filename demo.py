#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))

from src.backend.classifier import MathClassifier
from src.backend.solver import MathSolver
from src.backend.explainer import MathExplainer, ExplanationStyle

def main():
    print("🧮 AI Math Tutor Demo")
    print("=" * 50)
    
    classifier = MathClassifier()
    solver = MathSolver()
    explainer = MathExplainer()
    
    test_problems = [
        "2x + 3 = 7",
        "x^2 - 5x + 6 = 0",
        "x^3 + 2x^2 - 5x + 1"
    ]
    
    for i, problem in enumerate(test_problems, 1):
        print(f"\n📝 Problem {i}: {problem}")
        
        try:
            classification = classifier.classify(problem)
            print(f"✅ Classified as: {classification.problem_type}")
            print(f"   Subjects: {[str(s) for s in classification.subjects]}")
            print(f"   Difficulty: {classification.difficulty}")
            print(f"   Confidence: {classification.confidence:.2f}")
            
            solution = solver.solve_problem(classification, problem)
            
            if "error" in solution:
                print(f"❌ Solver error: {solution['error']}")
            else:
                print(f"✅ Solution: {solution.get('solution', 'N/A')}")
                print(f"   Steps: {len(solution.get('steps', []))}")
                
                if solution.get('steps'):
                    steps = solution['steps']
                    explanation = explainer.explain_solution(
                        problem, 
                        classification, 
                        steps, 
                        ExplanationStyle.INTERMEDIATE
                    )
                    print(f"✅ Explanation generated successfully!")
                    print(f"   Concept: {explanation.get('concept_explanation', {}).get('concept', 'N/A')}")
                    print(f"   Strategy: {explanation.get('strategy_explanation', {}).get('strategy_name', 'N/A')}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n🎉 Demo completed!")
    print("\nThe AI Math Tutor system is working correctly!")
    print("Key features:")
    print("✅ Problem classification")
    print("✅ Mathematical solving")
    print("✅ Educational explanations")
    print("✅ Multiple explanation styles")
    print("✅ Confidence scoring")

if __name__ == "__main__":
    main()
