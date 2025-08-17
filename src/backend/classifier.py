import re
from enum import Enum, auto
from typing import Set, Dict, List, Optional,Any
from dataclasses import dataclass
import logging
from sympy import parse_expr, Derivative, sympify, SympifyError, Symbol


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MathSubject(Enum):
    ALGEBRA = auto()
    CALCULUS = auto()
    GEOMETRY = auto()
    TRIGONOMETRY = auto()
    STATISTICS = auto()

    def __str__(self):
        return self.name.title()


class ProblemType(Enum):
    EQUATION = "Equation"
    DERIVATIVE = "Derivative"
    INTEGRAL = "Integral"
    WORD_PROBLEM = "Word Problem"
    INEQUALITY = "Inequality"
    SYSTEM_OF_EQUATIONS = "System of Equations"
    FACTORING = "Factoring"
    SIMPLIFICATION = "Simplification"

    def __str__(self):
        return self.value


class DifficultyLevel(Enum):
    ELEMENTARY = 1
    HIGH_SCHOOL = 2
    UNDERGRADUATE = 3
    ADVANCED = 4

    def __str__(self):
        return self.name.title().replace('_', ' ')


@dataclass
class ClassificationResult:
    subjects: Set[MathSubject]
    problem_type: ProblemType
    variables: Set[str]
    functions: Set[str]
    difficulty: DifficultyLevel
    metadata: Dict
    confidence: float = 0.0  # Confidence score for the classification

    def to_dict(self):
        return {
            "subjects": [str(s) for s in self.subjects],
            "problem_type": str(self.problem_type),
            "variables": list(self.variables),
            "functions": list(self.functions),
            "difficulty": str(self.difficulty),
            "confidence": self.confidence,
            "metadata": self.metadata
        }


class MathClassifier:
    def __init__(self):
        # self.nlp = MathNLPProcessor()  # Commented out since not provided
        self.setup_patterns()
        self.functions = {'sin', 'cos', 'tan', 'sec', 'csc', 'cot', 'arcsin', 'arccos', 'arctan',
                          'sinh', 'cosh', 'tanh', 'log', 'ln', 'exp', 'sqrt', 'abs'}
        self.variables = {'x', 'y', 'z', 't', 'u', 'v', 'w', 'a', 'b', 'c', 'd', 'n', 'm'}
        logger.info("Enhanced MathClassifier initialized")

    def setup_patterns(self):
        """Initialize comprehensive pattern matching for different math subjects and problem types"""
        self.subject_patterns = {
            MathSubject.ALGEBRA: [
                re.compile(r'\b[a-z]\s*=\s*[^=]', re.IGNORECASE),  # Variable assignments
                re.compile(r'\b(solve|equation|linear|quadratic)\b', re.IGNORECASE),
                re.compile(r'[a-z]\^?\d+|\d*[a-z]', re.IGNORECASE),  # Algebraic terms
                re.compile(r'\b(factor|expand|simplify)\b', re.IGNORECASE)
            ],
            MathSubject.CALCULUS: [
                re.compile(r'\b(derivative|differentiate|d/dx|d/dy)\b', re.IGNORECASE),
                re.compile(r'\b(integral|integrate|∫)\b', re.IGNORECASE),
                re.compile(r'\b(limit|lim)\b', re.IGNORECASE),
                re.compile(r"[f|g|h]'|f''", re.IGNORECASE),  # Function notation
                re.compile(r'\b(chain\s+rule|product\s+rule|quotient\s+rule)\b', re.IGNORECASE)
            ],
            MathSubject.GEOMETRY: [
                re.compile(r'\b(area|perimeter|volume|surface\s+area)\b', re.IGNORECASE),
                re.compile(r'\b(circle|triangle|square|rectangle|polygon|sphere|cylinder|cone)\b', re.IGNORECASE),
                re.compile(r'\b(radius|diameter|circumference|hypotenuse)\b', re.IGNORECASE),
                re.compile(r'\b(angle|degree|radian|π|pi)\b', re.IGNORECASE)
            ],
            MathSubject.TRIGONOMETRY: [
                re.compile(r'\b(sin|cos|tan|sec|csc|cot)\b', re.IGNORECASE),
                re.compile(r'\b(sine|cosine|tangent)\b', re.IGNORECASE),
                re.compile(r'\b(triangle|angle|degree|radian)\b', re.IGNORECASE)
            ],
            MathSubject.STATISTICS: [
                re.compile(r'\b(mean|median|mode|standard\s+deviation|variance)\b', re.IGNORECASE),
                re.compile(r'\b(probability|statistics|data|sample)\b', re.IGNORECASE),
                re.compile(r'\b(normal\s+distribution|bell\s+curve)\b', re.IGNORECASE)
            ]
        }

        self.problem_type_patterns = {
            ProblemType.EQUATION: [
                re.compile(r'.+=.+'),  # Contains equals sign
                re.compile(r'\b(solve\s+for|find\s+[a-z])\b', re.IGNORECASE)
            ],
            ProblemType.DERIVATIVE: [
                re.compile(r'\b(derivative|differentiate|d/dx|d/dy)\b', re.IGNORECASE),
                re.compile(r"[f|g|h]'", re.IGNORECASE)
            ],
            ProblemType.INTEGRAL: [
                re.compile(r'\b(integral|integrate|∫)\b', re.IGNORECASE),
                re.compile(r'\b(antiderivative)\b', re.IGNORECASE)
            ],
            ProblemType.INEQUALITY: [
                re.compile(r'[<>≤≥]'),
                re.compile(r'\b(greater\s+than|less\s+than|at\s+least|at\s+most)\b', re.IGNORECASE)
            ],
            ProblemType.SYSTEM_OF_EQUATIONS: [
                re.compile(r'(\n.*=|\r.*=.*\r.*=)', re.MULTILINE),  # Multiple equations
                re.compile(r'\b(system\s+of\s+equations)\b', re.IGNORECASE)
            ],
            ProblemType.FACTORING: [
                re.compile(r'\b(factor|factoring|factorize)\b', re.IGNORECASE)
            ],
            ProblemType.SIMPLIFICATION: [
                re.compile(r'\b(simplify|simplification|reduce)\b', re.IGNORECASE)
            ],
            ProblemType.WORD_PROBLEM: [
                re.compile(r'\b(find|calculate|determine|how\s+much|how\s+many)\b', re.IGNORECASE),
                re.compile(r'.{50,}')  # Longer text likely indicates word problem
            ]
        }

    def classify(self, text: str) -> ClassificationResult:
        """Enhanced classification with confidence scoring"""
        try:
            if not isinstance(text, str):
                raise TypeError("Input must be a string")
            if not text.strip():
                raise ValueError("Input cannot be empty")

            # Use fallback processing if NLP processor is not available
            processed_result = self._basic_text_processing(text)

            subjects = self._detect_subjects_enhanced(text)
            problem_type = self._detect_problem_type_enhanced(text)
            variables = self._extract_variables(text)
            functions = self._extract_functions(text)
            difficulty = self._estimate_difficulty_enhanced(text, variables, functions, subjects)
            confidence = self._calculate_confidence(text, subjects, problem_type)

            logger.info(f"Classified input: '{text[:50]}...' as {problem_type} with {confidence:.2f} confidence")

            return ClassificationResult(
                subjects=subjects,
                problem_type=problem_type,
                variables=variables,
                functions=functions,
                difficulty=difficulty,
                confidence=confidence,
                metadata={
                    "parsed_expression": processed_result.get("expression", text),
                    "word_count": len(text.split()),
                    "has_numbers": bool(re.search(r'\d', text)),
                    "has_equations": '=' in text,
                    "complexity_indicators": self._get_complexity_indicators(text)
                }
            )

        except (TypeError, ValueError) as e:
            logger.error(f"Classification error: {str(e)}")
            return self._fallback_classification(text)
        except Exception as e:
            logger.error(f"Unexpected classification error: {str(e)}")
            return self._fallback_classification(text)

    def _basic_text_processing(self, text: str) -> Dict:
        """Basic text processing when NLP processor is not available"""
        # Extract mathematical expressions
        math_expressions = re.findall(r'[a-zA-Z0-9+\-*/^()=<>≤≥√∫]+', text)

        return {
            "expression": " ".join(math_expressions) if math_expressions else text,
            "tokens": text.split(),
            "has_math": bool(math_expressions)
        }

    def _detect_subjects_enhanced(self, text: str) -> Set[MathSubject]:
        """Enhanced subject detection with weighted scoring"""
        subject_scores = {}

        for subject, patterns in self.subject_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(pattern.findall(text))
                score += matches
            subject_scores[subject] = score

        # Additional context-based detection
        if any(func in text.lower() for func in ['sin', 'cos', 'tan']):
            subject_scores[MathSubject.TRIGONOMETRY] = subject_scores.get(MathSubject.TRIGONOMETRY, 0) + 2

        # Select subjects with score > 0, or default to Algebra
        detected_subjects = {subject for subject, score in subject_scores.items() if score > 0}

        if not detected_subjects:
            detected_subjects.add(MathSubject.ALGEBRA)

        return detected_subjects

    def _detect_problem_type_enhanced(self, text: str) -> ProblemType:
        """Enhanced problem type detection with priority ordering"""
        type_scores = {}

        for prob_type, patterns in self.problem_type_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(pattern.findall(text))
                score += matches
            if score > 0:
                type_scores[prob_type] = score

        if not type_scores:
            # Default logic based on text characteristics
            if len(text.split()) > 10:
                return ProblemType.WORD_PROBLEM
            elif '=' in text:
                return ProblemType.EQUATION
            else:
                return ProblemType.SIMPLIFICATION

        # Return the problem type with the highest score
        return max(type_scores, key=type_scores.get)

    def _extract_variables(self, text: str) -> Set[str]:
        """Extract mathematical variables from text"""
        # Look for single letters that appear to be variables
        variable_pattern = re.compile(r'\b([a-z])\b(?!\s*[a-z])', re.IGNORECASE)
        potential_vars = set(variable_pattern.findall(text.lower()))

        # Filter out common English words that might be single letters
        common_words = {'a', 'i', 'o'}  # Articles and pronouns
        variables = potential_vars - common_words

        # Add variables from function notation like f(x), g(y)
        func_vars = re.findall(r'[fgh]\(([a-z])\)', text.lower())
        variables.update(func_vars)

        # If no variables found, default to 'x'
        if not variables:
            variables.add('x')

        return variables & self.variables  # Only return known variable names

    def _extract_functions(self, text: str) -> Set[str]:
        """Extract mathematical functions from text"""
        found_functions = set()
        text_lower = text.lower()

        for func in self.functions:
            if func in text_lower:
                found_functions.add(func)

        # Look for function notation f(x), g(x), etc.
        func_notation = re.findall(r'\b([fgh])\s*\(', text_lower)
        found_functions.update(func_notation)

        return found_functions

    def _estimate_difficulty_enhanced(self, text: str, variables: Set[str],
                                      functions: Set[str], subjects: Set[MathSubject]) -> DifficultyLevel:
        """Enhanced difficulty estimation"""
        difficulty_score = 0

        # Base complexity factors
        difficulty_score += len(variables)
        difficulty_score += len(functions) * 2
        difficulty_score += len(subjects)

        complexity_indicators = [
            ('partial', 2), ('integration by parts', 3), ('chain rule', 2),
            ('system', 2), ('matrix', 3), ('polynomial', 1),
            ('quadratic', 1), ('cubic', 2), ('exponential', 2),
            ('logarithm', 2), ('trigonometric', 2), ('inverse', 2)
        ]

        text_lower = text.lower()
        for indicator, weight in complexity_indicators:
            if indicator in text_lower:
                difficulty_score += weight

        if MathSubject.CALCULUS in subjects:
            difficulty_score += 2
        if MathSubject.STATISTICS in subjects:
            difficulty_score+=1

        if difficulty_score >= 8:
            return DifficultyLevel.ADVANCED
        elif difficulty_score >=5:
              return  DifficultyLevel.UNDERGRADUATE
        elif difficulty_score>=3:
              return DifficultyLevel.HIGH_SCHOOL
        else:
             return  DifficultyLevel.ELEMENTARY

    def _calculate_confidence(self,text:str, subjects: Set[MathSubject],
                              problem_type:ProblemType)->float:
        confidence=0.5

        if "=" in text:
            confidence+= 0.2

        text_lower=text.lower()

        math_function_count=sum(1 for func in self.functions if func in text_lower)
        confidence+=min(math_function_count*0.1,0.3)

        if any(var in text_lower for var in self.variables):
            confidence+=0.15

        subject_keyword_matches=0
        for subject, patterns in self.subject_patterns.items():
            if subject in subjects:
                for pattern in patterns:
                    subject_keyword_matches+=len(pattern.findall(text))

        confidence += min(subject_keyword_matches*0.05,0.2)

        type_indicators=0
        if problem_type in self.problem_type_patterns:
            for pattern in self.problem_type_patterns[problem_type]:
                type_indicators+=len(pattern.findall(text))

        confidence += min(type_indicators*0.1, 0.25)

        if len(text.strip()) < 5:
            confidence *= 0.7

        return min(confidence,1)

    def _get_complexity_indicators(self,text:str)->List[str]:
        indicators=[]
        text_lower=text.lower()

        complexity_keywords={
            'high':['derivative','integral','limit','matrix','system','partial'],
            'medium': ['quadratic','polynomial','trigonometric','lograthim','exponential'],
            'low': ['linear','addition','subtraction','multiplication','division']
        }

        for level, keywords in complexity_keywords:
            for keyword in keywords:
                if keyword in text_lower:
                    indicators.append(f"{level}_{keyword}")

        return indicators

    def _fallback_classification(self,text:str)->ClassificationResult:

        logger.debug(f'Fallback classification for: {text}')

        has_equation= '=' in text

        has_derivative_terms= any(term in text.lower() for term in ['derivative','differentiate','d/dx'])
        has_geometry_terms=any(term in text.lower() for term in ['area','circle','triangle','radius'])
        word_count=len(text.split())

        if has_derivative_terms:
           problem_type=ProblemType.DERIVATIVE
           subjects={MathSubject.CALCULUS}
        elif has_geometry_terms:
             problem_type=ProblemType.WORD_PROBLEM if word_count>8 else ProblemType.EQUATION
             subjects={MathSubject.GEOMETRY}
        elif has_equation:
             problem_type=ProblemType.EQUATION
             subjects={MathSubject.ALGEBRA}
        elif word_count>10:
             problem_type= ProblemType.WORD_PROBLEM
             subjects= {MathSubject.ALGEBRA}
        else:
             problem_type=ProblemType.EQUATION
             subjects={MathSubject.ALGEBRA}

        variables=self._extract_variables(text)
        functions=self._extract_functions(text)

        return ClassificationResult(
            subjects=subjects,
            problem_type=problem_type,
            variables= variables if variables else {'x'},
            difficulty=DifficultyLevel.HIGH_SCHOOL,
            confidence=0.3,
            metadata={
                'error':'Classification failed - using fallback',
                 'original_text':text,
                  'fallback_reasoning': {
                      'has_equation':has_equation,
                       'has_derivative':has_derivative_terms,
                       'has_geometry':has_geometry_terms,
                         'word count':word_count
                  }
            }
        )

    def get_classification_explanation(self,text:str)->Dict[str,Any]:

        result=self.classify(text)

        explanation={
            "classification":result.to_dict(),
             "reasoning": {
                   "subject_detection":self._explain_subject_detection(text),
                    "problem type detection":self._explain_problem_type_detection(text),
                     "difficulty assesment": self._explain_difficulty_assessment(text,result),
                     "difficulty factors": self._explain_confidence_factors(text,result)
             }
        }

        return explanation

    def _explain_subject_detection(self, text: str) -> Dict[str, Any]:
        explanations = {}

        for subject, patterns in self.subject_patterns.items():
            matches = []
            for pattern in patterns:
                found = pattern.findall(text)
                if found:
                    matches.extend(found)

            if matches:
                explanations[str(subject)] = {
                    "matches": matches,
                    "reason": f"Found {len(matches)} indicator(s) for {subject}"
                }

        return explanations

    def _explain_problem_type_detection(self, text: str) -> Dict[str, Any]:
        explanations = {}

        for prob_type, patterns in self.problem_type_patterns.items():
            matches = []
            for pattern in patterns:
                found = pattern.findall(text)
                if found:
                    matches.extend(found)

            if matches:
                explanations[str(prob_type)] = {
                    "matches": matches,
                    "score": len(matches)
                }

        return explanations

    def _explain_difficulty_assessment(self, text: str, result: ClassificationResult) -> Dict[str, Any]:
        factors = {
            "variable_count": len(result.variables),
            "function_count": len(result.functions),
            "subject_count": len(result.subjects),
            "complexity_indicators": result.metadata.get("complexity_indicators", []),
            "final_difficulty": str(result.difficulty)
        }

        return factors

    def _explain_confidence_factors(self, text: str, result: ClassificationResult) -> Dict[str, Any]:
        factors = {
            "has_clear_equation": '=' in text,
            "has_mathematical_functions": len(result.functions) > 0,
            "has_variables": len(result.variables) > 0,
            "text_length": len(text),
            "final_confidence": result.confidence
        }

        return factors




