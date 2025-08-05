import logging
import re
from typing import Dict,Any
from functools import lru_cache
from sympy import solve, diff, sympify, Symbol, pi, SympifyError, evaluate
from src.backend.classifier import ClassificationResult, ProblemType, MathSubject

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %'
                           '(levelname)s -%(message)s')
logger=logging.getLogger(__name__)

class MathSolver:
     def __init__(self):
         self.variables={'x','y','z'}
         logger.info("MathSolver initialized")
     @lru_cache(maxsize=64)
     def solve_problem(self,
                       classification: ClassificationResult,
                       parsed_expression:str)->Dict[str,Any]:
         try:
             if not isinstance(classification,ClassificationResult):
                 raise TypeError("Classification must be "
                                 "a classificationResult object")
             if not parsed_expression:
                 raise ValueError("Parsed Expression cannot be empty")

             problem_type=classification.problem_type
             subjects=classification.subjects
             logger.debug(f"Solving:"
                          f"{parsed_expression},type:"
                          f"{problem_type},subjects:"
                          f"{subjects}")
             if problem_type ==ProblemType.EQUATION:
                 return self._solve_equation(parsed_expression,classification)
             elif problem_type == ProblemType.DERIVATIVE:
                 return self._solve_derivative(parsed_expression,classification)
             elif problem_type==ProblemType.WORD_PROBLEM:
                  return self._solve_word_problem(parsed_expression,classification)
             else:
                 raise ValueError(f"Unsupported problem type: {problem_type}")
         except (TypeError,ValueError) as e:
             logger.error(f"Solver error: {str(e)}")
             return  {"error":str(e),"solution":None}
         except Exception as e:
                logger.error(f"Unexpected solver error: {str(e)}")
                return {'error':f'Unexpected error: {str(e)}',
                                f'"solution:':None}
     @staticmethod
     def _solve_equation(expr:str, classification: ClassificationResult)->Dict[str,Any]:
         try:
             expr_sym=sympify(expr,evaluate=False)
             variables=[Symbol(var) for var in classification.variables]
             if not variables:
                 variables=[Symbol('x')]
             solutions= solve(expr_sym, variables[0] if len(variables)==1 else variables, dict=True)
             logger.info(f'Equation solved:{expr} -> {solutions}')
             return {
                  "solution":solutions,
                  "solution type":"equation",
                  "variables":classification.variables}
         except SympifyError as e:
             logger.error(f'Equation parsing failed: {str(e)}')
             return  {"error":f'Invalid equation:{str(e)}',
                      "solution":None}
     @staticmethod
     def _solve_derivative(expr:str, classification:ClassificationResult)->Dict[str,Any]:
         try:
             expr_sym= sympify(expr,evaluate=False)
             variables=[Symbol(var) for var in classification.variables]
             if not variables:
                 variables=[Symbol('x')]
             derivative=diff(expr_sym,variables[0])
             logger.info(f"Derivative computed: {expr}-> {derivative}")
             return {
                  "solution":str(derivative),
                  "solution_type":"derivative",
                  "variables":classification.variables
             }
         except SympifyError as e:
                logger.error(f'Derivative parsing failed: {str(e)}')
                return {"error":f'Invalid expression: {str(e)}',"solution":None}

     @staticmethod
     def _solve_word_problem(expr:str, classification:ClassificationResult)-> Dict[str,Any]:
         try:
             if MathSubject.GEOMETRY in classification.subjects:
                 if "circle" in expr.lower() and "radius" in expr.lower():
                     numbers=[float(num) for num in re.findall(f'\d+\.?\d*',expr)]
                     if numbers:
                         radius=numbers[0]
                         area=pi* radius**2
                         logger.info(f'Word Problem solved: {expr}->{area}')
                         return {
                             "solution":str(area),
                             "solution type": "area",
                              "variables":set()
                         }
                     logger.debug(f'Unsupported word problem: {expr}')
                     return {"error":"Unsupported word problem",
                             "solution":None}
         except Exception as e:
                logger.error(f"Word problem error: {str(e)}")
                return {'error':f'Invalid word problem: {str(e)}',
                        "solution":None}
