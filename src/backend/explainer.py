from __future__ import annotations

import logging
import re
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum, auto
import random

try:
    from .solver import StepExplanation
except ImportError:
    @dataclass
    class StepExplanation:
        step_num: int
        expression: str
        description: str
        reasoning: str
        latex_expr: Optional[str] = None

from .classifier import ClassificationResult, ProblemType, MathSubject, DifficultyLevel

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ExplanationStyle(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    CONVERSATIONAL = "conversational"


@dataclass
class ConceptExplanation:
    concept: str
    definition: str
    examples: List[str]
    common_mistakes: List[str]
    prerequisites: List[str]
    related_concepts: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "concept": self.concept,
            "definition": self.definition,
            "examples": self.examples,
            "common_mistakes": self.common_mistakes,
            "prerequisites": self.prerequisites,
            "related_concepts": self.related_concepts
        }


@dataclass
class VoiceExplanation:
    text: str
    phonetic_math: str
    pace_markers: List[int]
    emphasis_words: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "phonetic_math": self.phonetic_math,
            "pace_markers": self.pace_markers,
            "emphasis_words": self.emphasis_words
        }


class MathExplainer:
    def __init__(self):
        self.concept_database = self._build_concept_database()
        self.explanation_templates = self._build_explanation_templates()
        self.voice_patterns = self._build_voice_patterns()
        self.difficulty_adjustments = self._build_difficulty_adjustments()
        logger.info("MathExplainer initialized successfully")

    def explain_solution(self,
                         problem: str,
                         classification: ClassificationResult,
                         solution_steps: List[StepExplanation],
                         style: ExplanationStyle = ExplanationStyle.INTERMEDIATE,
                         include_voice: bool = True) -> Dict[str, Any]:

        try:
            logger.info(f"Generating explanation for {classification.problem_type} problem")

            step_explanations = self._explain_solution_steps(solution_steps, classification, style)
            concept_explanation = self._explain_underlying_concepts(classification, style)
            strategy_explanation = self._explain_problem_solving_strategy(classification, solution_steps, style)

            educational_content = self._generate_educational_content(classification, style)
            learning_objectives = self._identify_learning_objectives(classification)

            next_steps = self._suggest_next_steps(classification, solution_steps)
            practice_problems = self._generate_practice_problems(classification)

            voice_explanation = None
            if include_voice:
                voice_explanation = self._generate_voice_explanation(problem, solution_steps, style)

            result = {
                "problem": problem,
                "classification": classification.to_dict(),
                "step_explanations": step_explanations,
                "concept_explanation": concept_explanation.to_dict(),
                "strategy_explanation": strategy_explanation,
                "educational_content": educational_content,
                "learning_objectives": learning_objectives,
                "next_steps": next_steps,
                "practice_problems": practice_problems,
                "explanation_metadata": {
                    "style": style.value,
                    "difficulty_level": str(classification.difficulty),
                    "subjects": [str(s) for s in classification.subjects],
                    "confidence": classification.confidence
                }
            }

            if voice_explanation:
                result["voice_explanation"] = voice_explanation.to_dict()

            logger.info("Explanation generated successfully")
            return result

        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}", exc_info=True)
            return self._generate_fallback_explanation(problem, classification)

    def _explain_solution_steps(self,
                                steps: List[StepExplanation],
                                classification: ClassificationResult,
                                style: ExplanationStyle) -> List[Dict[str, Any]]:
        explained_steps = []

        for i, step in enumerate(steps):
            explanation = {
                "step_number": step.step_num,
                "original_expression": step.expression,
                "description": step.description,
                "reasoning": step.reasoning or "Mathematical operation",
                "enhanced_explanation": self._enhance_step_explanation(step, classification, style),
                "mathematical_justification": self._explain_mathematical_reasoning(step, classification),
                "alternative_approaches": self._suggest_alternative_approaches(step, classification),
                "common_errors": self._identify_common_errors_for_step(step, classification),
                "visualization_hints": self._generate_visualization_hints(step, classification),
                "difficulty_notes": self._get_step_difficulty_notes(step, classification, style)
            }

            if hasattr(step, 'latex_expr') and step.latex_expr:
                explanation["latex_expression"] = step.latex_expr

            if i > 0:
                explanation["connection_to_previous"] = self._explain_step_connection(
                    steps[i - 1], step, classification
                )

            explanation["voice_friendly"] = self._make_voice_friendly(step, style)

            explained_steps.append(explanation)

        return explained_steps

    def _enhance_step_explanation(self,
                                  step: StepExplanation,
                                  classification: ClassificationResult,
                                  style: ExplanationStyle) -> str:
        base_explanation = step.reasoning or step.description

        enhancers = {
            ExplanationStyle.BEGINNER: self._beginner_enhancement,
            ExplanationStyle.CONVERSATIONAL: self._conversational_enhancement,
            ExplanationStyle.ADVANCED: self._advanced_enhancement,
            ExplanationStyle.INTERMEDIATE: self._intermediate_enhancement
        }

        enhancer = enhancers.get(style, self._intermediate_enhancement)
        return enhancer(base_explanation, step, classification)

    def _beginner_enhancement(self, explanation: str, step: StepExplanation,
                              classification: ClassificationResult) -> str:
        enhanced = f"Let's work through this step carefully. {explanation}"

        if step.step_num == 1:
            enhanced = f"Great! Let's start solving this problem together. {enhanced}"

        if "=" in step.expression:
            enhanced += " Remember, whatever we do to one side of an equation, we must do to the other side to keep it balanced - like a seesaw!"

        if any(op in step.expression for op in ['+', '-', '*', '/']):
            enhanced += " We follow the order of operations (PEMDAS/BODMAS) to make sure we get the right answer."

        if "factor" in explanation.lower():
            enhanced += " Factoring means we're looking for numbers that multiply together to give us our original expression."

        return enhanced

    def _conversational_enhancement(self, explanation: str, step: StepExplanation,
                                    classification: ClassificationResult) -> str:
        starters = [
            "Now here's what we're going to do: ",
            "The next logical step is to ",
            "Here's where it gets interesting - ",
            "Let's tackle this by ",
            "Notice how we can "
        ]

        starter = starters[step.step_num % len(starters)]
        enhanced = f"{starter}{explanation.lower()}"

        if classification.problem_type == ProblemType.EQUATION:
            enhanced += " Can you see how this gets us closer to isolating our variable?"
        elif classification.problem_type == ProblemType.DERIVATIVE:
            enhanced += " Notice how the derivative rules make this straightforward?"
        elif "solve" in explanation.lower():
            enhanced += " We're making great progress toward our final answer!"

        return enhanced

    def _advanced_enhancement(self, explanation: str, step: StepExplanation,
                              classification: ClassificationResult) -> str:
        enhanced = explanation

        if classification.problem_type == ProblemType.DERIVATIVE:
            enhanced += " This application demonstrates the fundamental theorem connecting instantaneous rates of change to function behavior."
        elif classification.problem_type == ProblemType.EQUATION:
            enhanced += " This transformation preserves the solution set while simplifying the algebraic structure."
        elif "integral" in explanation.lower():
            enhanced += " This integration technique leverages the fundamental theorem of calculus."

        if MathSubject.CALCULUS in classification.subjects:
            enhanced += " This step exemplifies the systematic approach characteristic of rigorous mathematical analysis."

        return enhanced

    def _intermediate_enhancement(self, explanation: str, step: StepExplanation,
                                  classification: ClassificationResult) -> str:
        enhanced = explanation

        if "factor" in explanation.lower():
            enhanced += " This factoring technique helps us break down complex expressions into simpler parts."
        elif "substitute" in explanation.lower():
            enhanced += " Substitution is a powerful technique that simplifies our work."
        elif "solve" in explanation.lower():
            enhanced += " We're using algebraic manipulation to isolate the variable."

        return enhanced

    def _explain_mathematical_reasoning(self, step: StepExplanation,
                                        classification: ClassificationResult) -> str:
        reasoning_database = {
            ProblemType.EQUATION: {
                "solve": "We use the properties of equality: adding, subtracting, multiplying, or dividing both sides by the same non-zero value maintains the equation's validity.",
                "factor": "Factoring utilizes the zero product property: if ab = 0, then either a = 0 or b = 0 (or both).",
                "substitute": "Substitution allows us to replace variables with equivalent expressions, maintaining mathematical equivalence.",
                "simplify": "Algebraic simplification combines like terms and reduces expressions to their most compact form.",
                "expand": "Expansion uses the distributive property: a(b + c) = ab + ac."
            },
            ProblemType.DERIVATIVE: {
                "power rule": "The power rule states: d/dx(xⁿ) = n·xⁿ⁻¹, derived from the limit definition of derivatives.",
                "chain rule": "The chain rule handles composite functions: d/dx[f(g(x))] = f'(g(x))·g'(x).",
                "product rule": "For products: d/dx[f(x)g(x)] = f'(x)g(x) + f(x)g'(x).",
                "quotient rule": "For quotients: d/dx[f(x)/g(x)] = [f'(x)g(x) - f(x)g'(x)]/[g(x)]²."
            },
            ProblemType.INTEGRAL: {
                "antiderivative": "Integration finds the antiderivative - the function whose derivative gives our integrand.",
                "substitution": "u-substitution simplifies integrals by changing variables to a more manageable form.",
                "parts": "Integration by parts uses: ∫u dv = uv - ∫v du."
            },
            ProblemType.WORD_PROBLEM: {
                "identify": "Problem analysis begins with identifying known quantities, unknown variables, and relationships.",
                "translate": "Mathematical modeling translates word descriptions into equations or expressions.",
                "interpret": "Solution interpretation requires understanding the mathematical result in the original context."
            }
        }

        problem_type = classification.problem_type
        step_content = step.description.lower()

        if problem_type in reasoning_database:
            for keyword, reasoning in reasoning_database[problem_type].items():
                if keyword in step_content:
                    return reasoning

        return "This step follows standard mathematical procedures to progress systematically toward the solution."

    def _suggest_alternative_approaches(self, step: StepExplanation,
                                        classification: ClassificationResult) -> List[str]:
        alternatives = []
        step_desc = step.description.lower()

        if classification.problem_type == ProblemType.EQUATION:
            if "factor" in step_desc:
                alternatives.extend([
                    "Use the quadratic formula instead of factoring",
                    "Complete the square method",
                    "Graphical solution by finding x-intercepts"
                ])
            elif "solve" in step_desc and "quadratic" in step_desc:
                alternatives.extend([
                    "Factoring method (if expression factors nicely)",
                    "Completing the square",
                    "Graphical method"
                ])

        elif classification.problem_type == ProblemType.DERIVATIVE:
            if "chain rule" in step_desc:
                alternatives.append("Break into intermediate steps for clarity")
            elif "product rule" in step_desc:
                alternatives.append("Expand first, then differentiate term by term")

        elif classification.problem_type == ProblemType.INTEGRAL:
            if "substitution" in step_desc:
                alternatives.extend([
                    "Integration by parts",
                    "Partial fractions (if applicable)"
                ])

        return alternatives[:3]

    def _identify_common_errors_for_step(self, step: StepExplanation,
                                         classification: ClassificationResult) -> List[str]:
        errors = []
        step_desc = step.description.lower()
        expression = step.expression

        if "=" in expression:
            errors.append("Forgetting to perform the same operation on both sides of the equation")

        if any(op in expression for op in ["^", "**"]):
            errors.append("Incorrectly applying exponent rules (e.g., (x²)³ ≠ x⁵)")

        if "factor" in step_desc:
            errors.extend([
                "Not checking if the factorization is correct by expanding",
                "Missing the greatest common factor",
                "Sign errors when factoring"
            ])

        if classification.problem_type == ProblemType.DERIVATIVE:
            errors.extend([
                "Forgetting to apply the chain rule to composite functions",
                "Incorrectly differentiating constants",
                "Sign errors with trigonometric derivatives"
            ])

        elif classification.problem_type == ProblemType.INTEGRAL:
            errors.extend([
                "Forgetting the constant of integration (+C)",
                "Incorrect u-substitution",
                "Sign errors in integration by parts"
            ])

        return errors[:4]

    def _generate_visualization_hints(self, step: StepExplanation,
                                      classification: ClassificationResult) -> List[str]:
        hints = []

        if classification.problem_type == ProblemType.EQUATION:
            hints.extend([
                "Think of an equation as a balance scale - what you do to one side, do to the other",
                "Visualize 'undoing' operations in reverse order"
            ])

        elif classification.problem_type == ProblemType.DERIVATIVE:
            hints.extend([
                "Picture the slope of the tangent line at any point on the curve",
                "Think about how the function is changing at that instant"
            ])

        elif classification.problem_type == ProblemType.INTEGRAL:
            hints.extend([
                "Visualize the area under the curve",
                "Think of integration as 'accumulating' small pieces"
            ])

        if MathSubject.GEOMETRY in classification.subjects:
            hints.append("Draw a diagram to visualize the geometric relationships")

        return hints[:3]

    def _get_step_difficulty_notes(self, step: StepExplanation,
                                   classification: ClassificationResult,
                                   style: ExplanationStyle) -> List[str]:
        notes = []

        if classification.difficulty == DifficultyLevel.ELEMENTARY:
            notes.extend([
                "Take your time with this step",
                "Double-check your arithmetic",
                "It's okay to use a calculator for complex numbers"
            ])
        elif classification.difficulty == DifficultyLevel.UNDERGRADUATE:
            notes.extend([
                "This step requires careful attention to mathematical rigor",
                "Consider the theoretical implications",
                "Multiple solution paths may exist"
            ])

        return notes

    def _make_voice_friendly(self, step: StepExplanation, style: ExplanationStyle) -> str:
        voice_text = step.description

        replacements = {
            '^2': ' squared',
            '^3': ' cubed',
            '^': ' to the power of ',
            '*': ' times ',
            '/': ' divided by ',
            '=': ' equals ',
            '+': ' plus ',
            '-': ' minus ',
            'sqrt': ' square root of ',
            'sin': ' sine of ',
            'cos': ' cosine of ',
            'tan': ' tangent of ',
            'log': ' logarithm of ',
            'ln': ' natural logarithm of ',
            'pi': ' pi ',
            'e': ' e ',
            '(': ' open parenthesis ',
            ')': ' close parenthesis ',
            '[': ' open bracket ',
            ']': ' close bracket '
        }

        for symbol, spoken in replacements.items():
            voice_text = voice_text.replace(symbol, spoken)

        voice_text = re.sub(r'\s+', ' ', voice_text).strip()

        if len(voice_text) > 50:
            voice_text = voice_text.replace(',', ', pause,')

        return voice_text

    def _explain_step_connection(self, prev_step: StepExplanation,
                                 current_step: StepExplanation,
                                 classification: ClassificationResult) -> str:
        connection_templates = [
            "Building on our previous result where we {prev_action}, we now {current_action}",
            "Since we {prev_action}, our next logical step is to {current_action}",
            "The previous step gave us {prev_result}, so now we can {current_action}",
            "Having {prev_action}, we proceed by {current_action}"
        ]

        prev_action = self._extract_key_action(prev_step.description)
        current_action = self._extract_key_action(current_step.description)

        template = connection_templates[0]
        return template.format(prev_action=prev_action, current_action=current_action)

    def _extract_key_action(self, description: str) -> str:
        description = description.lower()

        if "solve" in description:
            return "solved for the variable"
        elif "factor" in description:
            return "factored the expression"
        elif "expand" in description:
            return "expanded the expression"
        elif "simplify" in description:
            return "simplified the expression"
        elif "substitute" in description:
            return "made a substitution"
        elif "differentiate" in description:
            return "found the derivative"
        elif "integrate" in description:
            return "evaluated the integral"
        else:
            return "performed the operation"

    def _explain_underlying_concepts(self, classification: ClassificationResult,
                                     style: ExplanationStyle) -> ConceptExplanation:
        primary_subject = list(classification.subjects)[0] if classification.subjects else MathSubject.ALGEBRA
        problem_type = classification.problem_type

        concept_key = f"{primary_subject.name}_{problem_type.value.replace(' ', '_')}"

        if concept_key in self.concept_database:
            concept = self.concept_database[concept_key]
        else:
            concept = self._generate_dynamic_concept_explanation(classification)

        if style == ExplanationStyle.BEGINNER:
            concept.definition = self._simplify_definition(concept.definition)
            concept.examples = concept.examples[:2]

        return concept

    def _explain_problem_solving_strategy(self, classification: ClassificationResult,
                                          steps: List[StepExplanation],
                                          style: ExplanationStyle) -> Dict[str, Any]:

        strategy_database = {
            ProblemType.EQUATION: {
                "strategy_name": "Algebraic Equation Solving",
                "overview": "Systematically isolate the variable using inverse operations while maintaining equation balance.",
                "key_principles": [
                    "Maintain equation balance (what you do to one side, do to the other)",
                    "Use inverse operations to 'undo' what's been done to the variable",
                    "Work in reverse order of operations (PEMDAS backwards)",
                    "Simplify at each step to avoid errors"
                ],
                "when_to_use": "When you have an equation with one or more unknowns that need to be solved.",
                "success_indicators": [
                    "Variable is isolated on one side",
                    "Solution can be verified by substitution",
                    "All algebraic steps are valid"
                ]
            },
            ProblemType.DERIVATIVE: {
                "strategy_name": "Systematic Differentiation",
                "overview": "Apply differentiation rules in the correct order to find the rate of change function.",
                "key_principles": [
                    "Identify the type of function (polynomial, trigonometric, exponential, etc.)",
                    "Apply basic rules (power rule, product rule, quotient rule, chain rule)",
                    "Work from outside to inside for composite functions",
                    "Simplify the final result"
                ],
                "when_to_use": "When finding slopes, rates of change, or critical points of functions.",
                "success_indicators": [
                    "All terms are properly differentiated",
                    "Result is simplified",
                    "Units make sense (if applicable)"
                ]
            },
            ProblemType.INTEGRAL: {
                "strategy_name": "Integration Strategy",
                "overview": "Find the antiderivative using appropriate integration techniques.",
                "key_principles": [
                    "Identify the type of integrand",
                    "Choose appropriate technique (substitution, parts, partial fractions)",
                    "Don't forget the constant of integration (+C)",
                    "Verify by differentiating the result"
                ],
                "when_to_use": "When finding areas, accumulated quantities, or antiderivatives.",
                "success_indicators": [
                    "Integration technique is correctly applied",
                    "Constant of integration is included",
                    "Result can be verified by differentiation"
                ]
            },
            ProblemType.WORD_PROBLEM: {
                "strategy_name": "Mathematical Modeling",
                "overview": "Translate real-world problems into mathematical language, solve, and interpret results.",
                "key_principles": [
                    "Identify what you're looking for (the unknown)",
                    "Define variables for unknown quantities",
                    "Translate relationships into mathematical expressions",
                    "Solve the mathematical problem",
                    "Interpret the result in the original context"
                ],
                "when_to_use": "When mathematical concepts need to be applied to real-world situations.",
                "success_indicators": [
                    "All relevant information is used",
                    "Mathematical model accurately represents the situation",
                    "Solution makes sense in context"
                ]
            }
        }

        base_strategy = strategy_database.get(classification.problem_type, {
            "strategy_name": "General Problem Solving",
            "overview": "Apply mathematical reasoning systematically to reach a solution.",
            "key_principles": [
                "Understand what the problem is asking",
                "Plan your approach before starting",
                "Work step by step",
                "Check your answer"
            ],
            "when_to_use": "For any mathematical problem requiring systematic solution.",
            "success_indicators": [
                "Solution addresses the original question",
                "All steps are mathematically valid",
                "Answer is reasonable"
            ]
        })

        base_strategy.update({
            "step_breakdown": self._analyze_solution_pattern(steps),
            "difficulty_adaptations": self._get_difficulty_adaptations(classification),
            "estimated_time": self._estimate_solution_time(classification, len(steps)),
            "required_tools": self._identify_required_tools(classification)
        })

        return base_strategy

    def _analyze_solution_pattern(self, steps: List[StepExplanation]) -> List[Dict[str, str]]:
        patterns = []

        for i, step in enumerate(steps):
            step_desc = step.description.lower()

            if "identify" in step_desc or i == 0:
                patterns.append({
                    "phase": "Problem Analysis",
                    "description": "Understanding what we're given and what we need to find"
                })
            elif "substitute" in step_desc:
                patterns.append({
                    "phase": "Substitution",
                    "description": "Replacing variables or expressions with known values"
                })
            elif "solve" in step_desc:
                patterns.append({
                    "phase": "Solution Finding",
                    "description": "Applying mathematical operations to isolate the unknown"
                })
            elif "simplify" in step_desc:
                patterns.append({
                    "phase": "Simplification",
                    "description": "Reducing the expression to its simplest form"
                })
            elif "verify" in step_desc or "check" in step_desc:
                patterns.append({
                    "phase": "Verification",
                    "description": "Confirming our solution is correct"
                })
            else:
                patterns.append({
                    "phase": "Mathematical Operation",
                    "description": "Applying mathematical rules and procedures"
                })

        return patterns

    def _get_difficulty_adaptations(self, classification: ClassificationResult) -> List[str]:
        difficulty_map = {
            DifficultyLevel.ELEMENTARY: [
                "Use more visual aids and diagrams",
                "Break down each step into smaller sub-steps",
                "Provide more examples and practice problems",
                "Use concrete numbers before introducing variables"
            ],
            DifficultyLevel.HIGH_SCHOOL: [
                "Connect to previously learned concepts",
                "Show alternative solution methods",
                "Explain why each step is necessary"
            ],
            DifficultyLevel.UNDERGRADUATE: [
                "Include theoretical background",
                "Discuss when the method does/doesn't apply",
                "Connect to broader mathematical themes"
            ],
            DifficultyLevel.ADVANCED: [
                "Emphasize rigor and proof techniques",
                "Discuss generalizations and extensions",
                "Consider edge cases and assumptions"
            ]
        }

        return difficulty_map.get(classification.difficulty, [])

    def _estimate_solution_time(self, classification: ClassificationResult, num_steps: int) -> str:
        base_time = num_steps * 2

        difficulty_multipliers = {
            DifficultyLevel.ELEMENTARY: 1.5,
            DifficultyLevel.HIGH_SCHOOL: 1.0,
            DifficultyLevel.UNDERGRADUATE: 1.2,
            DifficultyLevel.ADVANCED: 1.8
        }

        multiplier = difficulty_multipliers.get(classification.difficulty, 1.0)
        estimated_minutes = int(base_time * multiplier)

        if estimated_minutes < 5:
            return "2-5 minutes"
        elif estimated_minutes < 15:
            return "5-15 minutes"
        elif estimated_minutes < 30:
            return "15-30 minutes"
        else:
            return "30+ minutes"

    def _identify_required_tools(self, classification: ClassificationResult) -> List[str]:
        tools = ["Paper and pencil"]

        if classification.difficulty in [DifficultyLevel.UNDERGRADUATE, DifficultyLevel.ADVANCED]:
            tools.append("Scientific calculator")

        if MathSubject.CALCULUS in classification.subjects:
            tools.append("Graphing capability (optional)")

        if classification.problem_type == ProblemType.WORD_PROBLEM:
            tools.append("Unit conversion references (if needed)")

        if MathSubject.STATISTICS in classification.subjects:
            tools.append("Statistical tables or calculator")

        return tools

    def _generate_voice_explanation(self, problem: str, steps: List[StepExplanation],
                                    style: ExplanationStyle) -> VoiceExplanation:

        voice_parts = [
            f"Let's solve this problem step by step. The problem is: {self._make_math_speakable(problem)}"
        ]

        for step in steps:
            step_text = f"Step {step.step_num}: {step.description}. "
            step_text += f"We get: {self._make_math_speakable(step.expression)}. "
            if step.reasoning:
                step_text += f"This works because {step.reasoning.lower()}. "
            voice_parts.append(step_text)

        voice_parts.append("And that gives us our final answer!")

        full_text = " ".join(voice_parts)
        phonetic_math = self._make_math_speakable(problem)
        pace_markers = [len(part) for part in voice_parts]
        emphasis_words = self._extract_emphasis_words(problem, steps)

        return VoiceExplanation(
            text=full_text,
            phonetic_math=phonetic_math,
            pace_markers=pace_markers,
            emphasis_words=emphasis_words
        )

    def _make_math_speakable(self, text: str) -> str:
        replacements = {
            '^2': ' squared',
            '^3': ' cubed',
            '^': ' to the power of ',
            '*': ' times ',
            '/': ' divided by ',
            '=': ' equals ',
            '+': ' plus ',
            '-': ' minus ',
            'sqrt': ' square root of ',
            'sin': ' sine of ',
            'cos': ' cosine of ',
            'tan': ' tangent of ',
            'log': ' logarithm of ',
            'ln': ' natural logarithm of ',
            'pi': ' pi ',
            'e': ' e ',
            '(': ' open parenthesis ',
            ')': ' close parenthesis '
        }

        for symbol, spoken in replacements.items():
            text = text.replace(symbol, spoken)

        return re.sub(r'\s+', ' ', text).strip()

    def _extract_emphasis_words(self, problem: str, steps: List[StepExplanation]) -> List[str]:
        emphasis_words = []
        
        math_terms = ['solve', 'find', 'calculate', 'determine', 'derivative', 'integral', 'equation']
        for term in math_terms:
            if term in problem.lower():
                emphasis_words.append(term)

        for step in steps:
            if '=' in step.expression:
                emphasis_words.append('equals')
            if any(op in step.expression for op in ['+', '-', '*', '/']):
                emphasis_words.append('operation')

        return list(set(emphasis_words))

    def _generate_educational_content(self, classification: ClassificationResult, style: ExplanationStyle) -> Dict[str, Any]:
        content = {
            "key_concepts": self._get_key_concepts(classification),
            "formulas": self._get_relevant_formulas(classification),
            "examples": self._get_examples(classification),
            "practice_tips": self._get_practice_tips(classification)
        }

        if style == ExplanationStyle.BEGINNER:
            content["key_concepts"] = content["key_concepts"][:3]
            content["examples"] = content["examples"][:2]

        return content

    def _get_key_concepts(self, classification: ClassificationResult) -> List[str]:
        concepts = []
        
        if MathSubject.ALGEBRA in classification.subjects:
            concepts.extend(["Variables", "Equations", "Algebraic manipulation"])
        if MathSubject.CALCULUS in classification.subjects:
            concepts.extend(["Derivatives", "Rates of change", "Limits"])
        if MathSubject.GEOMETRY in classification.subjects:
            concepts.extend(["Shapes", "Area", "Perimeter", "Volume"])
        if MathSubject.TRIGONOMETRY in classification.subjects:
            concepts.extend(["Trigonometric functions", "Angles", "Triangles"])
        if MathSubject.STATISTICS in classification.subjects:
            concepts.extend(["Data analysis", "Probability", "Distributions"])

        return concepts

    def _get_relevant_formulas(self, classification: ClassificationResult) -> List[str]:
        formulas = []
        
        if classification.problem_type == ProblemType.EQUATION:
            formulas.append("ax + b = c → x = (c - b)/a")
        if classification.problem_type == ProblemType.DERIVATIVE:
            formulas.append("d/dx(x^n) = nx^(n-1)")
        if MathSubject.GEOMETRY in classification.subjects:
            formulas.append("Area of circle: A = πr²")
            formulas.append("Area of triangle: A = ½bh")

        return formulas

    def _get_examples(self, classification: ClassificationResult) -> List[str]:
        examples = []
        
        if classification.problem_type == ProblemType.EQUATION:
            examples.extend(["2x + 7 = 22", "x² - 9 = 0", "2x + 3y = 12, x - y = 2"])
        if classification.problem_type == ProblemType.DERIVATIVE:
            examples.extend(["d/dx(x³ + 2x²)", "d/dx(sin(x²))", "d/dx(e^x * ln(x))"])
        if MathSubject.GEOMETRY in classification.subjects:
            examples.extend(["Find area of circle with radius 5", "Find perimeter of rectangle 3×4"])

        return examples

    def _get_practice_tips(self, classification: ClassificationResult) -> List[str]:
        tips = []
        
        if classification.problem_type == ProblemType.EQUATION:
            tips.extend([
                "Always check your answer by substituting back",
                "Work step by step to avoid errors",
                "Remember to simplify at each step"
            ])
        if classification.problem_type == ProblemType.DERIVATIVE:
            tips.extend([
                "Identify the function type first",
                "Apply rules systematically",
                "Simplify the final result"
            ])

        return tips

    def _identify_learning_objectives(self, classification: ClassificationResult) -> List[str]:
        objectives = []
        
        if classification.problem_type == ProblemType.EQUATION:
            objectives.append("Solve linear and quadratic equations")
            objectives.append("Apply algebraic manipulation techniques")
        if classification.problem_type == ProblemType.DERIVATIVE:
            objectives.append("Apply differentiation rules correctly")
            objectives.append("Understand rate of change concepts")
        if MathSubject.GEOMETRY in classification.subjects:
            objectives.append("Calculate areas and perimeters")
            objectives.append("Apply geometric formulas")

        return objectives

    def _suggest_next_steps(self, classification: ClassificationResult, steps: List[StepExplanation]) -> List[str]:
        next_steps = []
        
        if classification.problem_type == ProblemType.EQUATION:
            next_steps.extend([
                "Practice with more complex equations",
                "Learn about systems of equations",
                "Study quadratic formula applications"
            ])
        if classification.problem_type == ProblemType.DERIVATIVE:
            next_steps.extend([
                "Practice chain rule applications",
                "Learn about applications in physics",
                "Study optimization problems"
            ])

        return next_steps

    def _generate_practice_problems(self, classification: ClassificationResult) -> List[Dict[str, str]]:
        problems = []
        
        if classification.problem_type == ProblemType.EQUATION:
            problems.extend([
                {"problem": "Solve: 3x + 7 = 22", "difficulty": "Easy"},
                {"problem": "Solve: x² - 9 = 0", "difficulty": "Medium"},
                {"problem": "Solve: 2x + 3y = 12, x - y = 2", "difficulty": "Hard"}
            ])
        if classification.problem_type == ProblemType.DERIVATIVE:
            problems.extend([
                {"problem": "Find d/dx(x³ + 2x²)", "difficulty": "Easy"},
                {"problem": "Find d/dx(sin(x²))", "difficulty": "Medium"},
                {"problem": "Find d/dx(e^x * ln(x))", "difficulty": "Hard"}
            ])

        return problems

    def _generate_fallback_explanation(self, problem: str, classification: ClassificationResult) -> Dict[str, Any]:
        return {
            "problem": problem,
            "classification": classification.to_dict(),
            "error": "Explanation generation failed",
            "fallback": {
                "basic_steps": ["Analyze the problem", "Apply mathematical rules", "Check your answer"],
                "general_advice": "Work step by step and verify each step"
            }
        }

    def _build_concept_database(self) -> Dict[str, ConceptExplanation]:
        return {
            "ALGEBRA_Equation": ConceptExplanation(
                concept="Algebraic Equations",
                definition="Mathematical statements with variables that can be solved for specific values",
                examples=["2x + 3 = 7", "x² - 4 = 0", "3x + 2y = 10"],
                common_mistakes=["Forgetting to do the same operation on both sides", "Sign errors"],
                prerequisites=["Basic arithmetic", "Understanding of variables"],
                related_concepts=["Linear equations", "Quadratic equations", "Systems of equations"]
            ),
            "CALCULUS_Derivative": ConceptExplanation(
                concept="Derivatives",
                definition="The rate of change of a function with respect to its variable",
                examples=["d/dx(x²) = 2x", "d/dx(sin x) = cos x"],
                common_mistakes=["Forgetting chain rule", "Incorrect power rule application"],
                prerequisites=["Understanding of functions", "Basic algebra"],
                related_concepts=["Limits", "Integration", "Applications in physics"]
            )
        }

    def _build_explanation_templates(self) -> Dict[str, str]:
        return {
            "equation_solve": "To solve this equation, we need to isolate the variable by performing inverse operations.",
            "derivative_find": "To find the derivative, we apply the appropriate differentiation rules systematically.",
            "geometry_calculate": "For this geometric problem, we identify the relevant formula and substitute known values."
        }

    def _build_voice_patterns(self) -> Dict[str, List[str]]:
        return {
            "emphasis": ["important", "key", "crucial", "essential"],
            "transition": ["now", "next", "then", "finally"],
            "explanation": ["because", "since", "therefore", "thus"]
        }

    def _build_difficulty_adjustments(self) -> Dict[str, Dict[str, Any]]:
        return {
            "elementary": {"detail_level": "high", "examples": "many", "pace": "slow"},
            "intermediate": {"detail_level": "medium", "examples": "some", "pace": "moderate"},
            "advanced": {"detail_level": "low", "examples": "few", "pace": "fast"}
        }

    def _generate_dynamic_concept_explanation(self, classification: ClassificationResult) -> ConceptExplanation:
        return ConceptExplanation(
            concept=f"{classification.problem_type.value} in {list(classification.subjects)[0].name}",
            definition="A mathematical problem requiring systematic solution",
            examples=["Example 1", "Example 2"],
            common_mistakes=["Common error 1", "Common error 2"],
            prerequisites=["Basic mathematical knowledge"],
            related_concepts=["Related topic 1", "Related topic 2"]
        )

    def _simplify_definition(self, definition: str) -> str:
        return definition.split('.')[0] + "."

