import re
from enum import Enum, auto
from typing import Set, Dict
from dataclasses import dataclass
import logging
from sympy import parse_expr, Derivative, sympify, SympifyError
from src.utils.nlp_utils import MathNLPProcessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MathSubject(Enum):
    ALGEBRA = auto()
    CALCULUS = auto()
    GEOMETRY = auto()

    def __str__(self):
        return self.name.title()

class ProblemType(Enum):
    EQUATION = "Equation"
    DERIVATIVE = "Derivative"
    WORD_PROBLEM = "Word Problem"

    def __str__(self):
        return self.value

class DifficultyLevel(Enum):
    HIGH_SCHOOL = 1
    UNDERGRADUATE = 2

    def __str__(self):
        return self.name.title()

@dataclass
class ClassificationResult:
    subjects: Set[MathSubject]
    problem_type: ProblemType
    variables: Set[str]
    functions: Set[str]
    difficulty: DifficultyLevel
    metadata: Dict

    def to_dict(self):
        return {
            "subjects": [str(s) for s in self.subjects],
            "problem_type": str(self.problem_type),
            "variables": list(self.variables),
            "functions": list(self.functions),
            "difficulty": str(self.difficulty),
            "metadata": self.metadata
        }

class MathClassifier:
    def __init__(self):
        self.nlp = MathNLPProcessor()
        self.patterns = {
            MathSubject.ALGEBRA: [re.compile(r'[a-z]=[^=]')],  # Matches equations like x=5
            MathSubject.CALCULUS: [re.compile(r'd/d|derivative\b', re.IGNORECASE)],
            MathSubject.GEOMETRY: [re.compile(r'\b(area|circle|triangle)\b', re.IGNORECASE)]
        }
        self.functions = {'sin', 'cos', 'tan', 'sqrt'}
        self.variables = {'x', 'y', 'z'}
        logger.info("MathClassifier initialized")

    def classify(self, text: str) -> ClassificationResult:
        try:
            if not isinstance(text, str):
                raise TypeError("Input must be a string")
            if not text.strip():
                raise ValueError("Input cannot be empty")
            nlp_result = self.nlp.process(text)
            if "error" in nlp_result:
                logger.error(f"Classification failed: {nlp_result['error']}")
                return self._fallback_classification(text)

            lexical = nlp_result["lexical"]
            syntactic = nlp_result["syntactic"]
            semantic = nlp_result["semantic"]
            pragmatic = nlp_result["pragmatic"]

            subjects = self._detect_subjects(text, lexical["tokens"], semantic)
            problem_type = self._detect_problem_type(text, semantic, pragmatic)
            variables = set(token for token, pos in lexical["pos_tags"] if token in self.variables)
            functions = set(token for token in lexical["tokens"] if token in self.functions)
            difficulty = self._estimate_difficulty(variables, functions, subjects)

            logger.info(f"Classified input: {text} as {problem_type}")
            return ClassificationResult(
                subjects=subjects,
                problem_type=problem_type,
                variables=variables,
                functions=functions,
                difficulty=difficulty,
                metadata={
                    "parsed_expression": semantic["parsed_expression"],
                    "intent": pragmatic["intent"]
                }
            )
        except (TypeError, ValueError) as e:
            logger.error(f"Classification error: {str(e)}")
            return self._fallback_classification(text)
        except Exception as e:
            logger.error(f"Unexpected classification error: {str(e)}")
            return self._fallback_classification(text)

    def _detect_subjects(self, text: str, tokens: list, semantic: dict) -> Set[MathSubject]:
        subjects = set()
        for subject, patterns in self.patterns.items():
            if any(pattern.search(text.lower()) for pattern in patterns):
                subjects.add(subject)
        if semantic["is_valid"]:
            try:
                expr = sympify(semantic["parsed_expression"], evaluate=False)
                if expr.has(Derivative) or any(func in str(expr) for func in self.functions):
                    subjects.add(MathSubject.CALCULUS)
            except SympifyError as e:
                logger.debug(f"SymPy validation skipped: {str(e)}")
        return subjects or {MathSubject.ALGEBRA}  # Default to Algebra

    def _detect_problem_type(self, text: str, semantic: dict, pragmatic: dict) -> ProblemType:
        text_lower = text.lower()
        if pragmatic["intent"] == "explain" or len(text.split()) > 5:
            return ProblemType.WORD_PROBLEM
        if '=' in text_lower:
            return ProblemType.EQUATION
        if 'derivative' in text_lower or 'd/dx' in text_lower:
            return ProblemType.DERIVATIVE
        return ProblemType.EQUATION

    def _estimate_difficulty(self, variables: Set[str], functions: Set[str], subjects: Set[MathSubject]) -> DifficultyLevel:
        score = len(variables) + len(functions) * 2 + len(subjects)
        return DifficultyLevel.UNDERGRADUATE if score > 2 else DifficultyLevel.HIGH_SCHOOL

    def _fallback_classification(self, text: str) -> ClassificationResult:
        logger.debug(f"Fallback classification for: {text}")
        return ClassificationResult(
            subjects={MathSubject.ALGEBRA},
            problem_type=ProblemType.EQUATION,
            variables={'x'},
            functions=set(),
            difficulty=DifficultyLevel.HIGH_SCHOOL,
            metadata={"error": "Classification failed", "original_text": text}
        )