import re
import spacy
from functools import lru_cache
from typing import Dict, List, Tuple, Any
from src.backend.classifier import MathClassifier
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    nlp = spacy.load("en_core_web_sm", disable=['ner'])  # Keep parser for better analysis
except OSError:
    logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
    nlp = None


def tokenize(text: str) -> List[str]:
    if nlp:
        doc = nlp(text)
        tokens = [token.text for token in doc if token.text.strip()]
    else:
        tokens = re.findall(r'\w+|[^\w\s]', text)

    logger.debug(f'Tokens: {tokens}')
    return tokens


class MathNLPProcessor:
    def __init__(self):
        self.classifier = MathClassifier()

        self.math_symbols = {
            '×': '*',
            '·': '*',
            '÷': '/',
            '²': '**2',
            '³': '**3',
            '⁴': '**4',
            'π': 'pi',
            '√': 'sqrt',
            '∫': 'integrate',
            '∞': 'oo',
            '≤': '<=',
            '≥': '>=',
            '≠': '!=',
            '±': '+/-',
            '∑': 'Sum',
            '∆': 'Delta',
            '∂': 'diff',
        }

        self.context = []
        self.max_context = 5

        self.equation_pattern = re.compile(r'(.+?)\s*=\s*(.+)')
        self.function_pattern = re.compile(r'([fgh])\s*\(\s*([a-z])\s*\)')
        self.derivative_pattern = re.compile(r'd/d([a-z])\s*\((.+?)\)|d/d([a-z])\s+(.+)')

        logger.info("Enhanced MathNLPProcessor initialized")

    @lru_cache(maxsize=128)
    def normalize_text(self, text: str) -> str:
        if not text or not isinstance(text, str):
            return ""

        normalized = text.strip()

        for symbol, replacement in self.math_symbols.items():
            normalized = normalized.replace(symbol, f' {replacement} ')

        text_to_math = {
            r'\btimes\b': '*',
            r'\bover\b': '/',
            r'\bdivided by\b': '/',
            r'\bplus\b': '+',
            r'\bminus\b': '-',
            r'\bsquared\b': '**2',
            r'\bcubed\b': '**3',
            r'\bto the power of\b': '**',
            r'\bequals\b': '=',
        }

        for pattern, replacement in text_to_math.items():
            normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)

        normalized = re.sub(r'\s+', ' ', normalized).strip()

        logger.debug(f'Normalized: "{text}" -> "{normalized}"')
        return normalized

    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        math_relevant = {
            'x', 'y', 'z', 't', 'u', 'v', 'w', 'a', 'b', 'c', 'd', 'n', 'm',
            '=', '+', '-', '*', '/', '**', '^', '<', '>', '<=', '>=', '!=',
            'sin', 'cos', 'tan', 'sec', 'csc', 'cot',
            'arcsin', 'arccos', 'arctan', 'sinh', 'cosh', 'tanh',
            'log', 'ln', 'exp', 'sqrt', 'abs',
            'pi', 'e', 'i', 'oo',
            'derivative', 'integral', 'limit', 'diff', 'integrate',
            'area', 'volume', 'perimeter', 'circumference', 'radius', 'diameter',
            'circle', 'triangle', 'square', 'rectangle', 'polygon',
            'solve', 'factor', 'expand', 'simplify', 'equation', 'inequality',
        }

        filtered_tokens = []
        for token in tokens:
            if (token.lower() in math_relevant or
                    token.isdigit() or
                    re.match(r'\d*\.\d+', token) or
                    re.match(r'\d+/\d+', token) or
                    len(token) == 1):
                filtered_tokens.append(token)

        logger.debug(f'Filtered tokens: {filtered_tokens}')
        return filtered_tokens

    def pos_tag(self, text: str) -> List[Tuple[str, str]]:
        if not nlp:
            return self._fallback_pos_tag(text)

        doc = nlp(text)
        enhanced_tags = []

        for token in doc:
            pos = token.pos_
            text_lower = token.text.lower()

            if text_lower in {'x', 'y', 'z', 't', 'u', 'v', 'w'}:
                pos = 'VAR'
            elif text_lower in {'sin', 'cos', 'tan', 'log', 'exp', 'sqrt'}:
                pos = 'FUNC'
            elif token.text in {'=', '+', '-', '*', '/', '**', '^', '<', '>'}:
                pos = 'OP'
            elif text_lower in {'pi', 'e'}:
                pos = 'CONST'
            elif token.pos_ in ['NUM', 'NOUN', 'SYM'] or pos in ['VAR', 'FUNC', 'OP', 'CONST']:
                pass
            else:
                continue

            enhanced_tags.append((token.text, pos))

        logger.debug(f'POS tags: {enhanced_tags}')
        return enhanced_tags

    def _fallback_pos_tag(self, text: str) -> List[Tuple[str, str]]:
        patterns = [
            (r'\d+\.?\d*', 'NUM'),
            (r'[xyz]', 'VAR'),
            (r'sin|cos|tan|log|exp|sqrt', 'FUNC'),
            (r'[+\-*/=<>]', 'OP'),
            (r'pi|e', 'CONST'),
        ]

        tags = []
        tokens = tokenize(text)

        for token in tokens:
            tag = 'UNKNOWN'
            for pattern, pos in patterns:
                if re.match(pattern, token.lower()):
                    tag = pos
                    break
            tags.append((token, tag))

        return tags

    def lexical_analysis(self, text: str) -> Dict[str, Any]:
        normalized = self.normalize_text(text)
        tokens = tokenize(normalized)
        tokens_no_stopwords = self.remove_stopwords(tokens)
        pos_tags = self.pos_tag(normalized)

        variables = {token for token, pos in pos_tags if pos == 'VAR'}
        functions = {token for token, pos in pos_tags if pos == 'FUNC'}
        operators = {token for token, pos in pos_tags if pos == 'OP'}
        numbers = {token for token, pos in pos_tags if pos == 'NUM'}

        return {
            "original": text,
            "normalized": normalized,
            "tokens": tokens,
            "tokens_no_stopwords": tokens_no_stopwords,
            "pos_tags": pos_tags,
            "variables": list(variables),
            "functions": list(functions),
            "operators": list(operators),
            "numbers": list(numbers)
        }

    def syntactic_analysis(self, text: str) -> Dict[str, Any]:
        if not nlp:
            return self._fallback_syntactic_analysis(text)

        doc = nlp(text)

        math_components = []
        dependencies = []

        for token in doc:
            if (token.pos_ in ['NOUN', 'NUM', 'SYM'] or
                    token.text.lower() in {'x', 'y', 'z', '=', '+', '-', '*', '/', 'pi', 'sin', 'cos', 'tan'}):
                math_components.append(token.text)

                if token.dep_ != 'ROOT':
                    dependencies.append((token.text, token.dep_, token.head.text))

        patterns = self._detect_math_patterns(text)

        logger.debug(f'Math components: {math_components}')
        logger.debug(f'Patterns detected: {patterns}')

        return {
            "math_components": math_components,
            "dependencies": dependencies,
            "patterns": patterns,
            "complexity_score": len(math_components) + len(patterns)
        }

    def _fallback_syntactic_analysis(self, text: str) -> Dict[str, Any]:
        tokens = tokenize(text)
        math_components = [token for token in tokens if
                           re.match(r'[a-zA-Z0-9+\-*/^()=<>√∫π]', token)]

        patterns = self._detect_math_patterns(text)

        return {
            "math_components": math_components,
            "dependencies": [],
            "patterns": patterns,
            "complexity_score": len(math_components) + len(patterns)
        }

    def _detect_math_patterns(self, text: str) -> Dict[str, bool]:
        patterns = {
            "has_equation": bool(self.equation_pattern.search(text)),
            "has_function": bool(self.function_pattern.search(text)),
            "has_derivative": bool(self.derivative_pattern.search(text)),
            "has_inequality": bool(re.search(r'[<>≤≥]', text)),
            "has_fraction": bool(re.search(r'\d+/\d+', text)),
            "has_exponent": bool(re.search(r'\^|\*\*|²|³', text)),
            "has_trig": bool(re.search(r'\b(sin|cos|tan)\b', text, re.IGNORECASE)),
            "has_log": bool(re.search(r'\b(log|ln)\b', text, re.IGNORECASE)),
            "has_sqrt": bool(re.search(r'sqrt|√', text, re.IGNORECASE)),
            "is_word_problem": len(text.split()) > 8 and any(word in text.lower()
                                                             for word in
                                                             ['find', 'calculate', 'determine', 'solve for'])
        }
        return patterns

    def semantic_analysis(self, text: str, syntactic_result: Dict[str, Any]) -> Dict[str, Any]:
        try:
            classification = self.classifier.classify(text)
            math_expr = " ".join(syntactic_result["math_components"])

            parsed_expr = None
            is_valid = False
            error_msg = None

            try:
                from sympy import parse_expr, sympify

                parsing_strategies = [
                    lambda x: parse_expr(x, transformations='all', evaluate=False),
                    lambda x: sympify(x, evaluate=False),
                    lambda x: parse_expr(x, evaluate=False),  # Without transformations
                ]

                for strategy in parsing_strategies:
                    try:
                        parsed_expr = strategy(math_expr)
                        is_valid = True
                        break
                    except:
                        continue

                if parsed_expr:
                    logger.info(f"Successfully parsed expression: {parsed_expr}")
                else:
                    logger.warning(f"Could not parse expression: {math_expr}")

            except Exception as e:
                error_msg = str(e)
                logger.error(f'Expression parsing failed: {error_msg}')

            return {
                "classification": classification.to_dict(),
                "parsed_expression": str(parsed_expr) if parsed_expr else math_expr,
                "original_expression": math_expr,
                "is_valid": is_valid,
                "patterns": syntactic_result.get("patterns", {}),
                "complexity_score": syntactic_result.get("complexity_score", 0),
                **({"error": error_msg} if error_msg else {})
            }

        except Exception as e:
            logger.error(f'Semantic analysis error: {str(e)}')
            return {
                "classification": self.classifier._fallback_classification(text).to_dict(),
                "parsed_expression": text,
                "original_expression": text,
                "is_valid": False,
                "error": str(e)
            }

    def pragmatic_analysis(self, text: str, classification: Dict[str, Any]) -> Dict[str, Any]:
        text_lower = text.lower()

        intent_patterns = {
            "solve": [r'\bsolve\b', r'\bfind\b', r'\bcalculate\b', r'\bdetermine\b'],
            "explain": [r'\bexplain\b', r'\bshow\s+me\b', r'\bhow\s+to\b', r'\bwhy\b', r'\bwhat\s+is\b'],
            "simplify": [r'\bsimplify\b', r'\breduce\b', r'\bminimize\b'],
            "factor": [r'\bfactor\b', r'\bfactorize\b'],
            "expand": [r'\bexpand\b', r'\bmultiply\s+out\b'],
            "derive": [r'\bderivative\b', r'\bdifferentiate\b', r'\bd/dx\b'],
            "integrate": [r'\bintegral\b', r'\bintegrate\b', r'\bantiderivative\b'],
            "plot": [r'\bplot\b', r'\bgraph\b', r'\bdraw\b', r'\bsketch\b'],
            "check": [r'\bcheck\b', r'\bverify\b', r'\bis\s+this\s+correct\b']
        }

        intent_scores = {}
        for intent, patterns in intent_patterns.items():
            score = sum(len(re.findall(pattern, text_lower)) for pattern in patterns)
            if score > 0:
                intent_scores[intent] = score

        primary_intent = max(intent_scores, key=intent_scores.get) if intent_scores else "solve"
        confidence = intent_scores.get(primary_intent, 0) / max(1, len(text.split()) // 3)

        learning_level = self._detect_learning_level(text_lower)

        logger.debug(f'Intent detected: {primary_intent} (confidence: {confidence:.2f})')

        return {
            'primary_intent': primary_intent,
            'intent_confidence': min(confidence, 1.0),
            'all_intents': intent_scores,
            'learning_level': learning_level,
            'problem_type': classification.get('problem_type', 'Unknown'),
            'requires_explanation': any(word in text_lower for word in ['explain', 'show', 'how', 'why', 'what']),
            'requires_steps': any(word in text_lower for word in ['step', 'show work', 'explain how'])
        }

    def _detect_learning_level(self, text: str) -> str:
        beginner_indicators = ['basic', 'simple', 'easy', 'help me understand', 'i don\'t get']
        intermediate_indicators = ['solve', 'find', 'calculate']
        advanced_indicators = ['prove', 'derive', 'analyze', 'optimize']

        if any(indicator in text for indicator in advanced_indicators):
            return 'advanced'
        elif any(indicator in text for indicator in beginner_indicators):
            return 'beginner'
        else:
            return 'intermediate'

    def discourse_integration(self, text: str, semantic_result: Dict[str, Any]) -> Dict[str, Any]:

        context_entry = {
            "text": text,
            "semantic_result": semantic_result,
            "timestamp": None,
            "problem_type": semantic_result.get("classification", {}).get("problem_type"),
            "difficulty": semantic_result.get("classification", {}).get("difficulty")
        }

        self.context.append(context_entry)

        if len(self.context) > self.max_context:
            self.context.pop(0)

        conversation_patterns = self._analyze_conversation_flow()

        logger.debug(f'Context updated: {len(self.context)} entries')

        return {
            "context": [item["text"] for item in self.context],
            "current_expression": semantic_result.get("parsed_expression", ""),
            "conversation_patterns": conversation_patterns,
            "context_similarity": self._calculate_context_similarity(),
            "suggested_next_steps": self._suggest_next_steps(semantic_result)
        }

    def _analyze_conversation_flow(self) -> Dict[str, Any]:
        """Analyze patterns in the conversation flow"""
        if len(self.context) < 2:
            return {"pattern": "single_interaction"}

        problem_types = [item.get("problem_type") for item in self.context[-3:]]
        difficulties = [item.get("difficulty") for item in self.context[-3:]]

        return {
            "pattern": "progressive" if len(set(problem_types)) > 1 else "focused",
            "difficulty_trend": "increasing" if len(set(difficulties)) > 1 else "consistent",
            "topic_consistency": len(set(problem_types)) == 1
        }

    def _calculate_context_similarity(self) -> float:
        if len(self.context) < 2:
            return 0.0

        current = self.context[-1]
        previous = self.context[-2]

        current_words = set(current["text"].lower().split())
        previous_words = set(previous["text"].lower().split())

        if not current_words or not previous_words:
            return 0.0

        intersection = current_words & previous_words
        union = current_words | previous_words

        return len(intersection) / len(union) if union else 0.0

    def _suggest_next_steps(self, semantic_result: Dict[str, Any]) -> List[str]:
        suggestions = []
        classification = semantic_result.get("classification", {})
        problem_type = classification.get("problem_type", "")

        if problem_type == "Equation":
            suggestions.extend([
                "Try a similar equation with different coefficients",
                "Practice factoring if this was a quadratic equation",
                "Learn about graphing this equation"
            ])
        elif problem_type == "Derivative":
            suggestions.extend([
                "Try finding the second derivative",
                "Practice with the chain rule",
                "Learn about applications of derivatives"
            ])
        elif problem_type == "Word Problem":
            suggestions.extend([
                "Try solving a similar problem with different numbers",
                "Practice identifying key information in word problems",
                "Learn about problem-solving strategies"
            ])

        return suggestions[:3]

    def process(self, text: str) -> Dict[str, Any]:
        if not text or not isinstance(text, str):
            return {"error": "Invalid input: text must be a non-empty string"}

        try:
            logger.info(f"Processing input: {text[:100]}{'...' if len(text) > 100 else ''}")

            lexical_result = self.lexical_analysis(text)
            syntactic_result = self.syntactic_analysis(lexical_result['normalized'])
            semantic_result = self.semantic_analysis(lexical_result["normalized"], syntactic_result)
            pragmatic_result = self.pragmatic_analysis(text, semantic_result['classification'])
            discourse_result = self.discourse_integration(lexical_result['normalized'], semantic_result)

            logger.info(f"Successfully processed input with intent: {pragmatic_result['primary_intent']}")

            return {
                'success': True,
                'lexical': lexical_result,
                'syntactic': syntactic_result,
                'semantic': semantic_result,
                'pragmatic': pragmatic_result,
                'discourse': discourse_result,
                'processing_metadata': {
                    'input_length': len(text),
                    'processing_time': None,
                    'confidence': semantic_result.get('classification', {}).get('confidence', 0.0)
                }
            }

        except Exception as e:
            logger.error(f'NLP processing failed: {str(e)}')
            return {
                'success': False,
                'error': str(e),
                'fallback_classification': self.classifier._fallback_classification(text).to_dict()
            }