import logging
import re
from typing import Dict, Any, List, Tuple
from functools import lru_cache
from sympy import (solve, diff, integrate, sympify, Symbol, pi, SympifyError,
                   evaluate, latex, expand, factor, simplify, Eq)
from src.backend.classifier import ClassificationResult, ProblemType, MathSubject

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class StepExplanation:
    def __init__(self, step_num: int, description: str, expression: str,
                 latex_expr: str = "", reasoning: str = ""):
        self.step_num = step_num
        self.description = description
        self.expression = expression
        self.latex_expr = latex_expr or latex(sympify(expression) if expression else "")
        self.reasoning = reasoning

    def to_dict(self):
        return {
            "step": self.step_num,
            "description": self.description,
            "expression": self.expression,
            "latex": self.latex_expr,
            "reasoning": self.reasoning
        }


class MathSolver:
    def __init__(self):
        self.variables = {'x', 'y', 'z', 't'}
        self.common_functions = {'sin', 'cos', 'tan', 'log', 'ln', 'exp', 'sqrt'}
        logger.info("MathSolver initialized")

    @lru_cache(maxsize=64)
    def solve_problem(self, classification: ClassificationResult,
                      parsed_expression: str) -> Dict[str, Any]:

        try:
            if not isinstance(classification, ClassificationResult):
                raise TypeError("Classification must be a ClassificationResult object")
            if not parsed_expression:
                raise ValueError("Parsed expression cannot be empty")

            problem_type = classification.problem_type
            subjects = classification.subjects

            logger.debug(f"Solving: {parsed_expression}, type: {problem_type}, subjects: {subjects}")

            if problem_type == ProblemType.EQUATION:
                return self._solve_equation_with_steps(parsed_expression, classification)
            elif problem_type == ProblemType.DERIVATIVE:
                return self._solve_derivative_with_steps(parsed_expression, classification)
            elif problem_type == ProblemType.WORD_PROBLEM:
                return self._solve_word_problem_with_steps(parsed_expression, classification)
            else:
                raise ValueError(f"Unsupported problem type: {problem_type}")

        except (TypeError, ValueError) as e:
            logger.error(f"Solver error: {str(e)}")
            return {"error": str(e), "solution": None, "steps": []}
        except Exception as e:
            logger.error(f"Unexpected solver error: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}", "solution": None, "steps": []}

    def _solve_equation_with_steps(self, expr: str,
                                   classification: ClassificationResult) -> Dict[str, Any]:

        steps = []
        try:
            expr_sym = sympify(expr, evaluate=False)
            steps.append(StepExplanation(
                1, "Parse the equation", str(expr_sym),
                reasoning="First, we identify the mathematical expression and parse it."
            ))

            variables = list(classification.variables) if classification.variables else ['x']
            var_symbols = [Symbol(var) for var in variables]
            steps.append(StepExplanation(
                2, f"Identify variable(s): {', '.join(variables)}",
                f"Variable(s) to solve for: {', '.join(variables)}",
                reasoning=f"We need to solve for the variable(s): {', '.join(variables)}"
            ))

            if '=' in expr:
                left, right = expr.split('=')
                left_sym = sympify(left.strip(), evaluate=False)
                right_sym = sympify(right.strip(), evaluate=False)
                equation = Eq(left_sym, right_sym)

                steps.append(StepExplanation(
                    3, "Set up the equation", str(equation),
                    reasoning="We have an equation with left and right sides."
                ))

                solutions = solve(equation, var_symbols[0] if len(var_symbols) == 1 else var_symbols, dict=True)
            else:
                equation = Eq(expr_sym, 0)
                steps.append(StepExplanation(
                    3, "Assume equation equals zero", f"{expr_sym} = 0",
                    reasoning="Since no equals sign is present, we assume the expression equals zero."
                ))
                solutions = solve(expr_sym, var_symbols[0] if len(var_symbols) == 1 else var_symbols, dict=True)

            if solutions:
                solution_text = self._format_solutions(solutions)
                steps.append(StepExplanation(
                    len(steps) + 1, "Solution(s) found", solution_text,
                    reasoning="These are the values that satisfy the equation."
                ))
            else:
                steps.append(StepExplanation(
                    len(steps) + 1, "No solution found", "No real solutions exist",
                    reasoning="The equation has no real solutions."
                ))

            logger.info(f'Equation solved: {expr} -> {solutions}')
            return {
                "solution": solutions,
                "solution_type": "equation",
                "variables": variables,
                "steps": [step.to_dict() for step in steps],
                "latex_steps": [step.latex_expr for step in steps]
            }

        except SympifyError as e:
            logger.error(f'Equation parsing failed: {str(e)}')
            return {"error": f'Invalid equation: {str(e)}', "solution": None, "steps": []}

    def _solve_derivative_with_steps(self, expr: str,
                                     classification: ClassificationResult) -> Dict[str, Any]:

        steps = []
        try:
            expr_sym = sympify(expr, evaluate=False)
            steps.append(StepExplanation(
                1, "Parse the function", str(expr_sym),
                reasoning="First, we identify the function to differentiate."
            ))

            variables = list(classification.variables) if classification.variables else ['x']
            var_symbol = Symbol(variables[0])
            steps.append(StepExplanation(
                2, f"Identify variable for differentiation: {variables[0]}",
                f"d/d{variables[0]}",
                reasoning=f"We will differentiate with respect to {variables[0]}."
            ))

            derivative = diff(expr_sym, var_symbol)
            steps.append(StepExplanation(
                3, "Apply differentiation rules", str(derivative),
                reasoning="Using standard differentiation rules (power rule, chain rule, etc.)."
            ))

            simplified = simplify(derivative)
            if simplified != derivative:
                steps.append(StepExplanation(
                    4, "Simplify the result", str(simplified),
                    reasoning="Simplify the derivative expression."
                ))
                final_result = simplified
            else:
                final_result = derivative

            logger.info(f"Derivative computed: {expr} -> {final_result}")
            return {
                "solution": str(final_result),
                "solution_type": "derivative",
                "variables": variables,
                "steps": [step.to_dict() for step in steps],
                "latex_steps": [step.latex_expr for step in steps]
            }

        except SympifyError as e:
            logger.error(f'Derivative parsing failed: {str(e)}')
            return {"error": f'Invalid expression: {str(e)}', "solution": None, "steps": []}

    def _solve_word_problem_with_steps(self, expr: str,
                                       classification: ClassificationResult) -> Dict[str, Any]:

        steps = []
        try:
            steps.append(StepExplanation(
                1, "Analyze the word problem", expr,
                reasoning="First, we read and understand what the problem is asking."
            ))

            if MathSubject.GEOMETRY in classification.subjects:
                return self._solve_geometry_word_problem(expr, steps)
            elif MathSubject.ALGEBRA in classification.subjects:
                return self._solve_algebra_word_problem(expr, steps)
            else:
                steps.append(StepExplanation(
                    2, "Problem type not recognized", "Unable to categorize this word problem",
                    reasoning="This word problem type is not yet supported."
                ))
                return {"error": "Unsupported word problem type", "solution": None,
                        "steps": [step.to_dict() for step in steps]}

        except Exception as e:
            logger.error(f"Word problem error: {str(e)}")
            return {"error": f"Invalid word problem: {str(e)}", "solution": None, "steps": []}

    def _solve_geometry_word_problem(self, expr: str, steps: List[StepExplanation]) -> Dict[str, Any]:
        expr_lower = expr.lower()

        if "circle" in expr_lower and "area" in expr_lower:
            numbers = [float(num) for num in re.findall(r'\d+\.?\d*', expr)]
            if numbers:
                radius = numbers[0]
                steps.append(StepExplanation(
                    2, f"Identify the radius", f"r = {radius}",
                    reasoning="Extract the radius value from the problem statement."
                ))

                steps.append(StepExplanation(
                    3, "Apply circle area formula", "A = πr²",
                    reasoning="The area of a circle is π times the radius squared."
                ))

                area = pi * radius ** 2
                steps.append(StepExplanation(
                    4, "Calculate the area", f"A = π × {radius}² = {area}",
                    reasoning="Substitute the radius value and calculate."
                ))

                return {
                    "solution": str(area),
                    "solution_type": "area",
                    "variables": set(),
                    "steps": [step.to_dict() for step in steps]
                }

        steps.append(StepExplanation(
            2, "Geometry problem not recognized", "This geometry problem type is not supported",
            reasoning="Only basic circle area problems are currently supported."
        ))
        return {"error": "Unsupported geometry problem", "solution": None, "steps": [step.to_dict() for step in steps]}

    def _solve_algebra_word_problem(self, expr: str, steps: List[StepExplanation]) -> Dict[str, Any]:
        steps.append(StepExplanation(
            2, "Algebra word problem analysis", "Analyzing for algebraic relationships",
            reasoning="Looking for equations and relationships in the problem."
        ))

        return {"error": "Algebra word problems not fully implemented", "solution": None,
                "steps": [step.to_dict() for step in steps]}

    def _format_solutions(self, solutions: List[Dict]) -> str:
        if not solutions:
            return "No solutions found"

        formatted = []
        for sol_dict in solutions:
            sol_parts = []
            for var, val in sol_dict.items():
                sol_parts.append(f"{var} = {val}")
            formatted.append(", ".join(sol_parts))

        return "; ".join(formatted)

    def get_solution_explanation(self, problem: str, classification: ClassificationResult) -> Dict[str, Any]:
        result = self.solve_problem(classification, problem)

        if "error" in result:
            return result

        # Add educational context
        result["educational_notes"] = self._get_educational_notes(classification)
        result["common_mistakes"] = self._get_common_mistakes(classification.problem_type)
        result["related_concepts"] = self._get_related_concepts(classification)

        return result

    def _get_educational_notes(self, classification: ClassificationResult) -> List[str]:
        """Provide educational context based on problem type"""
        notes = []

        if classification.problem_type == ProblemType.EQUATION:
            notes.append("Remember: What you do to one side of an equation, you must do to the other side.")
            notes.append("Always check your answer by substituting back into the original equation.")

        elif classification.problem_type == ProblemType.DERIVATIVE:
            notes.append("The derivative represents the rate of change or slope at any point.")
            notes.append("Common rules: d/dx(x^n) = nx^(n-1), d/dx(sin x) = cos x")

        return notes

    def _get_common_mistakes(self, problem_type: ProblemType) -> List[str]:
        mistakes = {
            ProblemType.EQUATION: [
                "Forgetting to distribute when multiplying",
                "Sign errors when moving terms across the equals sign",
                "Dividing by zero"
            ],
            ProblemType.DERIVATIVE: [
                "Forgetting the chain rule",
                "Confusing power rule exponents",
                "Not simplifying the final answer"
            ],
            ProblemType.WORD_PROBLEM: [
                "Misinterpreting what the question is asking",
                "Using wrong units",
                "Not checking if the answer makes sense in context"
            ]
        }
        return mistakes.get(problem_type, [])

    def _get_related_concepts(self, classification: ClassificationResult) -> List[str]:
        concepts = []

        for subject in classification.subjects:
            if subject == MathSubject.ALGEBRA:
                concepts.extend(["Linear equations", "Quadratic formula", "Factoring"])
            elif subject == MathSubject.CALCULUS:
                concepts.extend(["Limits", "Chain rule", "Integration"])
            elif subject == MathSubject.GEOMETRY:
                concepts.extend(["Area formulas", "Perimeter", "Volume"])

        return list(set(concepts))