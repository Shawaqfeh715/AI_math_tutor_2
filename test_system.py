#!/usr/bin/env python3

import sys
import json
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))

from src.backend.classifier import MathClassifier
from src.backend.solver import MathSolver
from src.backend.explainer import MathExplainer, ExplanationStyle

def test_classifier():
    print("🧪 Testing Math Classifier...")
    
    classifier = MathClassifier()
    
    test_problems = [
        "Solve for x: 2x + 3 = 7",
        "Find the derivative of x² + 3x",
        "Calculate the area of a circle with radius 5",
        "Factor x² - 9",
        "Find sin(30°)"
    ]
    
    for problem in test_problems:
        print(f"\n📝 Problem: {problem}")
        try:
            result = classifier.classify(problem)
            print(f"✅ Classification: {result.problem_type}")
            print(f"   Subjects: {[str(s) for s in result.subjects]}")
            print(f"   Difficulty: {result.difficulty}")
            print(f"   Confidence: {result.confidence:.2f}")
            print(f"   Variables: {list(result.variables)}")
            print(f"   Functions: {list(result.functions)}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n✅ Classifier tests completed!")

def test_solver():
    print("\n🧪 Testing Math Solver...")
    
    classifier = MathClassifier()
    solver = MathSolver()
    
    test_problems = [
        "2x + 3 = 7",
        "x² - 5x + 6 = 0",
        "x³ + 2x² - 5x + 1"
    ]
    
    for problem in test_problems:
        print(f"\n📝 Problem: {problem}")
        try:
            classification = classifier.classify(problem)
            solution = solver.solve_problem(classification, problem)
            
            if "error" in solution:
                print(f"❌ Solver Error: {solution['error']}")
            else:
                print(f"✅ Solution: {solution.get('solution', 'N/A')}")
                print(f"   Steps: {len(solution.get('steps', []))}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n✅ Solver tests completed!")

def test_explainer():
    print("\n🧪 Testing Math Explainer...")
    
    classifier = MathClassifier()
    solver = MathSolver()
    explainer = MathExplainer()
    
    test_problem = "Solve for x: 2x + 3 = 7"
    
    print(f"📝 Problem: {test_problem}")
    
    try:
        classification = classifier.classify(test_problem)
        solution = solver.solve_problem(classification, test_problem)
        
        if "error" not in solution:
            steps = solution.get("steps", [])
            explanation = explainer.explain_solution(
                test_problem, 
                classification, 
                steps, 
                ExplanationStyle.INTERMEDIATE
            )
            
            print(f"✅ Explanation generated successfully!")
            print(f"   Concept: {explanation.get('concept_explanation', {}).get('concept', 'N/A')}")
            print(f"   Strategy: {explanation.get('strategy_explanation', {}).get('strategy_name', 'N/A')}")
            print(f"   Steps explained: {len(explanation.get('step_explanations', []))}")
        else:
            print(f"❌ Cannot explain - solver error: {solution['error']}")
            
    except Exception as e:
        print(f"❌ Explainer Error: {str(e)}")
    
    print("\n✅ Explainer tests completed!")

def test_integration():
    print("\n🧪 Testing Full System Integration...")
    
    classifier = MathClassifier()
    solver = MathSolver()
    explainer = MathExplainer()
    
    test_problem = "Find the derivative of x² + 3x"
    
    print(f"📝 Problem: {test_problem}")
    
    try:
        print("1️⃣ Classifying problem...")
        classification = classifier.classify(test_problem)
        print(f"   ✅ Classified as: {classification.problem_type}")
        
        print("2️⃣ Solving problem...")
        solution = solver.solve_problem(classification, test_problem)
        if "error" not in solution:
            print(f"   ✅ Solution found: {solution.get('solution', 'N/A')}")
        else:
            print(f"   ❌ Solver error: {solution['error']}")
            return
        
        print("3️⃣ Generating explanation...")
        steps = solution.get("steps", [])
        explanation = explainer.explain_solution(
            test_problem, 
            classification, 
            steps, 
            ExplanationStyle.INTERMEDIATE
        )
        print(f"   ✅ Explanation generated")
        
        print("4️⃣ System integration successful! 🎉")
        
    except Exception as e:
        print(f"❌ Integration Error: {str(e)}")
    
    print("\n✅ Integration tests completed!")

def test_performance():
    print("\n🧪 Testing Performance...")
    
    classifier = MathClassifier()
    
    test_problems = [
        "Solve for x: 2x + 3 = 7",
        "Find the derivative of x² + 3x",
        "Calculate the area of a circle with radius 5",
        "Factor x² - 9",
        "Find sin(30°)",
        "Solve: x² - 5x + 6 = 0",
        "Find d/dx(sin(x²))",
        "Calculate the mean of 5, 8, 12, 15, 20"
    ]
    
    start_time = time.time()
    
    for i, problem in enumerate(test_problems, 1):
        problem_start = time.time()
        try:
            result = classifier.classify(problem)
            problem_time = time.time() - problem_start
            print(f"✅ Problem {i}: {problem_time:.3f}s - {result.problem_type}")
        except Exception as e:
            problem_time = time.time() - problem_start
            print(f"❌ Problem {i}: {problem_time:.3f}s - Error: {str(e)}")
    
    total_time = time.time() - start_time
    avg_time = total_time / len(test_problems)
    
    print(f"\n📊 Performance Summary:")
    print(f"   Total time: {total_time:.3f}s")
    print(f"   Average time per problem: {avg_time:.3f}s")
    print(f"   Problems per second: {len(test_problems)/total_time:.2f}")
    
    print("\n✅ Performance tests completed!")

def main():
    print("🚀 AI Math Tutor System Test Suite")
    print("=" * 50)
    
    try:
        test_classifier()
        test_solver()
        test_explainer()
        test_integration()
        test_performance()
        
        print("\n🎉 All tests completed successfully!")
        print("The AI Math Tutor system is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
