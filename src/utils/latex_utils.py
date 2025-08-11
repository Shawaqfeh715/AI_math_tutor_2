from __future__ import annotations

import logging
import re
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum, auto
import random

# Assuming your solver has these structures - adjust as needed
try:
    from .solver import StepExplanation
except ImportError:
    # Fallback definition if solver isn't available yet
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
    """
    Comprehensive mathematical explanation generator that creates detailed,
    educational explanations for math problems with multiple styles and formats.
    """

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
        """
        Generate comprehensive explanation for a mathematical solution.

        Args:
            problem: The original problem statement
            classification: Classification result from MathClassifier
            solution_steps: Step-by-step solution from MathSolver
            style: Explanation style for different skill levels
            include_voice: Whether to generate voice-friendly explanations

        Returns:
            Complete explanation package with multiple formats
        """
        try:
            logger.info(f"Generating explanation for {classification.problem_type} problem")

            # Core explanations
            step_explanations = self._explain_solution_steps(solution_steps, classification, style)
            concept_explanation = self._explain_underlying_concepts(classification, style)
            strategy_explanation = self._explain_problem_solving_strategy(classification, solution_steps, style)

            # Educational content
            educational_content = self._generate_educational_content(classification, style)
            learning_objectives = self._identify_learning_objectives(classification)

            # Recommendations
            next_steps = self._suggest_next_steps(classification, solution_steps)
            practice_problems = self._generate_practice_problems(classification)

            # Voice explanation (if requested)
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
        """Generate detailed explanations for each solution step."""
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

            # Add LaTeX if available
            if hasattr(step, 'latex_expr') and step.latex_expr:
                explanation["latex_expression"] = step.latex_expr

            # Connect to previous step
            if i > 0:
                explanation["connection_to_previous"] = self._explain_step_connection(
                    steps[i - 1], step, classification
                )

            # Voice-friendly version
            explanation["voice_friendly"] = self._make_voice_friendly(step, style)

            explained_steps.append(explanation)

        return explained_steps

    def _enhance_step_explanation(self,
                                  step: StepExplanation,
                                  classification: ClassificationResult,
                                  style: ExplanationStyle) -> str:
        """Enhance step explanation based on style and context."""
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
        """Enhanced explanation for beginners with more detail and encouragement."""
        enhanced = f"Let's work through this step carefully. {explanation}"

        if step.step_num == 1:
            enhanced = f"Great! Let's start solving this problem together. {enhanced}"

        # Add specific guidance based on operations
        if "=" in step.expression:
            enhanced += " Remember, whatever we do to one side of an equation, we must do to the other side to keep it balanced - like a seesaw!"

        if any(op in step.expression for op in ['+', '-', '*', '/']):
            enhanced += " We follow the order of operations (PEMDAS/BODMAS) to make sure we get the right answer."

        if "factor" in explanation.lower():
            enhanced += " Factoring means we're looking for numbers that multiply together to give us our original expression."

        return enhanced

    def _conversational_enhancement(self, explanation: str, step: StepExplanation,
                                    classification: ClassificationResult) -> str:
        """Conversational style explanation with engaging language."""
        starters = [
            "Now here's what we're going to do: ",
            "The next logical step is to ",
            "Here's where it gets interesting - ",
            "Let's tackle this by ",
            "Notice how we can "
        ]

        starter = starters[step.step_num % len(starters)]
        enhanced = f"{starter}{explanation.lower()}"

        # Add engaging follow-ups
        if classification.problem_type == ProblemType.EQUATION:
            enhanced += " Can you see how this gets us closer to isolating our variable?"
        elif classification.problem_type == ProblemType.DERIVATIVE:
            enhanced += " Notice how the derivative rules make this straightforward?"
        elif "solve" in explanation.lower():
            enhanced += " We're making great progress toward our final answer!"

        return enhanced

    def _advanced_enhancement(self, explanation: str, step: StepExplanation,
                              classification: ClassificationResult) -> str:
        """Advanced explanation with theoretical context."""
        enhanced = explanation

        # Add theoretical context
        if classification.problem_type == ProblemType.DERIVATIVE:
            enhanced += " This application demonstrates the fundamental theorem connecting instantaneous rates of change to function behavior."
        elif classification.problem_type == ProblemType.EQUATION:
            enhanced += " This transformation preserves the solution set while simplifying the algebraic structure."
        elif "integral" in explanation.lower():
            enhanced += " This integration technique leverages the fundamental theorem of calculus."

        # Add connections to broader mathematical concepts
        if MathSubject.CALCULUS in classification.subjects:
            enhanced += " This step exemplifies the systematic approach characteristic of rigorous mathematical analysis."

        return enhanced

    def _intermediate_enhancement(self, explanation: str, step: StepExplanation,
                                  classification: ClassificationResult) -> str:
        """Intermediate level explanation with moderate detail."""
        enhanced = explanation

        # Add helpful context without overwhelming detail
        if "factor" in explanation.lower():
            enhanced += " This factoring technique helps us break down complex expressions into simpler parts."
        elif "substitute" in explanation.lower():
            enhanced += " Substitution is a powerful technique that simplifies our work."
        elif "solve" in explanation.lower():
            enhanced += " We're using algebraic manipulation to isolate the variable."

        return enhanced

    def _explain_mathematical_reasoning(self, step: StepExplanation,
                                        classification: ClassificationResult) -> str:
        """Provide mathematical justification for the step."""
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
        """Suggest alternative methods for solving this step."""
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

        return alternatives[:3]  # Limit to most relevant alternatives

    def _identify_common_errors_for_step(self, step: StepExplanation,
                                         classification: ClassificationResult) -> List[str]:
        """Identify common mistakes students make at this step."""
        errors = []
        step_desc = step.description.lower()
        expression = step.expression

        # General errors
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

        # Subject-specific errors
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

        return errors[:4]  # Limit to most important errors

    def _generate_visualization_hints(self, step: StepExplanation,
                                      classification: ClassificationResult) -> List[str]:
        """Generate hints for visualizing this step."""
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
        """Provide difficulty-specific notes for the step."""
        notes = []

        if classification.difficulty == DifficultyLevel.ELEMENTARY:
            notes.extend([
                "Take your time with this step",
                "Double-check your arithmetic",
                "It's okay to use a calculator for complex numbers"
            ])
        elif classification.difficulty == DifficultyLevel.GRADUATE:
            notes.extend([
                "This step requires careful attention to mathematical rigor",
                "Consider the theoretical implications",
                "Multiple solution paths may exist"
            ])

        return notes

    def _make_voice_friendly(self, step: StepExplanation, style: ExplanationStyle) -> str:
        """Convert mathematical notation to voice-friendly format."""
        voice_text = step.description

        # Mathematical symbol replacements
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

        # Clean up extra spaces
        voice_text = re.sub(r'\s+', ' ', voice_text).strip()

        # Add pacing for complex expressions
        if len(voice_text) > 50:
            voice_text = voice_text.replace(',', ', pause,')

        return voice_text

    def _explain_step_connection(self, prev_step: StepExplanation,
                                 current_step: StepExplanation,
                                 classification: ClassificationResult) -> str:
        """Explain how the current step builds on the previous step."""
        connection_templates = [
            "Building on our previous result where we {prev_action}, we now {current_action}",
            "Since we {prev_action}, our next logical step is to {current_action}",
            "The previous step gave us {prev_result}, so now we can {current_action}",
            "Having {prev_action}, we proceed by {current_action}"
        ]

        # Extract key actions from step descriptions
        prev_action = self._extract_key_action(prev_step.description)
        current_action = self._extract_key_action(current_step.description)

        template = connection_templates[0]
        return template.format(prev_action=prev_action, current_action=current_action)

    def _extract_key_action(self, description: str) -> str:
        """Extract the key mathematical action from a step description."""
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
        """Explain the fundamental concepts underlying this problem."""
        # Get primary subject and problem type
        primary_subject = list(classification.subjects)[0] if classification.subjects else MathSubject.ALGEBRA
        problem_type = classification.problem_type

        # Look up concept in database
        concept_key = f"{primary_subject.name}_{problem_type.value.replace(' ', '_')}"

        if concept_key in self.concept_database:
            concept = self.concept_database[concept_key]
        else:
            concept = self._generate_dynamic_concept_explanation(classification)

        # Adapt to style
        if style == ExplanationStyle.BEGINNER:
            concept.definition = self._simplify_definition(concept.definition)
            concept.examples = concept.examples[:2]  # Fewer examples for beginners

        return concept

    def _explain_problem_solving_strategy(self, classification: ClassificationResult,
                                          steps: List[StepExplanation],
                                          style: ExplanationStyle) -> Dict[str, Any]:
        """Explain the overall strategy used to solve this problem."""

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

        # Get base strategy
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

        # Enhance with problem-specific analysis
        base_strategy.update({
            "step_breakdown": self._analyze_solution_pattern(steps),
            "difficulty_adaptations": self._get_difficulty_adaptations(classification),
            "estimated_time": self._estimate_solution_time(classification, len(steps)),
            "required_tools": self._identify_required_tools(classification)
        })

        return base_strategy

    def _analyze_solution_pattern(self, steps: List[StepExplanation]) -> List[Dict[str, str]]:
        """Analyze the pattern of solution steps."""
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
        """Get difficulty-specific adaptations for the strategy."""
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
            DifficultyLevel.GRADUATE: [
                "Emphasize rigor and proof techniques",
                "Discuss generalizations and extensions",
                "Consider edge cases and assumptions"
            ],
            DifficultyLevel.RESEARCH: [
                "Provide complete theoretical framework",
                "Discuss current research connections",
                "Consider multiple proof approaches"
            ]
        }

        return difficulty_map.get(classification.difficulty, [])

    def _estimate_solution_time(self, classification: ClassificationResult, num_steps: int) -> str:
        """Estimate how long the solution should take."""
        base_time = num_steps * 2  # 2 minutes per step as baseline

        # Adjust for difficulty
        difficulty_multipliers = {
            DifficultyLevel.ELEMENTARY: 1.5,
            DifficultyLevel.HIGH_SCHOOL: 1.0,
            DifficultyLevel.UNDERGRADUATE: 1.2,
            DifficultyLevel.GRADUATE: 1.8,
            DifficultyLevel.RESEARCH: 3.0
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
        """Identify tools/resources needed for this problem."""
        tools = ["Paper and pencil"]

        if classification.difficulty in [DifficultyLevel.UNDERGRADUATE, DifficultyLevel.GRADUATE]:
            tools.append("Scientific calculator")

        if MathSubject.CALCULUS in classification.subjects:
            tools.append("Graphing capability (optional)")

        if classification.problem_type == ProblemType.WORD_PROBLEM:
            tools.append("Unit conversion references (if needed)")

        if any(subj in classification.subjects for subj in [MathSubject.STATISTICS, MathSubject.PROBABILITY]):
            tools.append("Statistical tables or calculator")

        return tools

    def _generate_voice_explanation(self, problem: str, steps: List[StepExplanation],
                                    style: ExplanationStyle) -> VoiceExplanation:
        """Generate voice-friendly explanation with proper pacing and emphasis."""

        # Build voice text
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

        # Combine all parts
        full_voice_text = " ".join(voice_parts)

        # Generate phonetic math notation
        phonetic_math = self._create_phonetic_math(full_voice_text)

        # Identify pace markers (pauses for complex parts)
        pace_markers = self._identify_pace_markers(full_voice_text)

        # Identify emphasis words
        emphasis_words = self._identify_emphasis_words(full_voice_text, style)

        return VoiceExplanation(
            text=full_voice_text,
            phonetic_math=phonetic_math,
            pace_markers=pace_markers,
            emphasis_words=emphasis_words
        )

    def _make_math_speakable(self, expression: str) -> str:
        """Convert mathematical expression to speakable format."""
        speakable = expression

        # Mathematical symbol replacements for voice
        voice_replacements = {
            '=': ' equals ',
            '+': ' plus ',
            '-': ' minus ',
            '*': ' times ',
            '/': ' divided by ',
            '^2': ' squared',
            '^3': ' cubed',
            '^': ' to the power of ',
            'sqrt(': ' square root of ',
            'sin(': ' sine of ',
            'cos(': ' cosine of ',
            'tan(': ' tangent of ',
            'log(': ' logarithm of ',
            'ln(': ' natural log of ',
            '(': ' open parenthesis ',
            ')': ' close parenthesis ',
            '[': ' open bracket ',
            ']': ' close bracket ',
            '{': ' open brace ',
            '}': ' close brace ',
            'pi': ' pi ',
            'e': ' e ',
            'infinity': ' infinity ',
            '>=': ' greater than or equal to ',
            '<=': ' less than or equal to ',
            '>': ' greater than ',
            '<': ' less than ',
            '!=': ' not equal to ',
        }

        for symbol, spoken in voice_replacements.items():
            speakable = speakable.replace(symbol, spoken)

        # Clean up multiple spaces
        speakable = re.sub(r'\s+', ' ', speakable).strip()

        return speakable

    def _create_phonetic_math(self, voice_text: str) -> str:
        """Create phonetic version of mathematical content."""
        # This would involve more sophisticated phonetic conversion
        # For now, return a simplified version
        phonetic = voice_text.lower()

        # Replace difficult-to-pronounce mathematical terms
        phonetic_replacements = {
            'coefficient': 'co-ef-fi-cient',
            'derivative': 'de-riv-a-tive',
            'integral': 'in-te-gral',
            'polynomial': 'pol-y-no-mi-al',
            'exponential': 'ex-po-nen-tial',
            'logarithm': 'log-a-rithm',
            'trigonometric': 'trig-o-no-met-ric',
        }

        for word, phonetic_version in phonetic_replacements.items():
            phonetic = phonetic.replace(word, phonetic_version)

        return phonetic

    def _identify_pace_markers(self, text: str) -> List[int]:
        """Identify positions where speaking should slow down."""
        markers = []
        words = text.split()

        # Add markers before complex mathematical terms
        complex_terms = [
            'derivative', 'integral', 'coefficient', 'polynomial',
            'exponential', 'logarithm', 'trigonometric', 'substitution'
        ]

        for i, word in enumerate(words):
            if any(term in word.lower() for term in complex_terms):
                markers.append(i)

        return markers

    def _identify_emphasis_words(self, text: str, style: ExplanationStyle) -> List[str]:
        """Identify words that should be emphasized in speech."""
        emphasis_words = []

        # Mathematical keywords that should be emphasized
        math_keywords = [
            'solve', 'factor', 'simplify', 'derivative', 'integral',
            'substitute', 'equation', 'expression', 'function',
            'equals', 'therefore', 'because', 'final', 'answer'
        ]

        words = text.lower().split()
        for word in words:
            if any(keyword in word for keyword in math_keywords):
                emphasis_words.append(word)

        # Add style-specific emphasis
        if style == ExplanationStyle.BEGINNER:
            emphasis_words.extend(['remember', 'important', 'careful', 'step'])
        elif style == ExplanationStyle.CONVERSATIONAL:
            emphasis_words.extend(['notice', 'see', 'interesting', 'great'])

        return list(set(emphasis_words))  # Remove duplicates

    def _generate_educational_content(self,
                                      classification: ClassificationResult,
                                      style: ExplanationStyle) -> Dict[str, Any]:
        """Generate additional educational content."""
        content = {
            "key_concepts": self._identify_key_concepts(classification),
            "prerequisite_knowledge": self._identify_prerequisites(classification),
            "common_applications": self._identify_applications(classification),
            "related_topics": self._identify_related_topics(classification),
            "difficulty_progression": self._suggest_difficulty_progression(classification),
            "visual_aids": self._suggest_visual_aids(classification),
            "interactive_elements": self._suggest_interactive_elements(classification)
        }

        # Adapt content based on style
        if style == ExplanationStyle.BEGINNER:
            content["encouragement"] = self._generate_encouragement()
            content["mnemonics"] = self._suggest_mnemonics(classification)
        elif style == ExplanationStyle.ADVANCED:
            content["theoretical_background"] = self._provide_theoretical_background(classification)
            content["proofs"] = self._suggest_proof_techniques(classification)

        return content

    def _identify_learning_objectives(self, classification: ClassificationResult) -> List[str]:
        """Identify learning objectives for this problem."""
        objectives = []

        # Base objectives by problem type
        type_objectives = {
            ProblemType.EQUATION: [
                "Apply algebraic manipulation to isolate variables",
                "Understand the properties of equality",
                "Verify solutions by substitution"
            ],
            ProblemType.DERIVATIVE: [
                "Apply differentiation rules correctly",
                "Understand the concept of instantaneous rate of change",
                "Interpret derivatives in context"
            ],
            ProblemType.INTEGRAL: [
                "Apply integration techniques appropriately",
                "Understand the relationship between derivatives and integrals",
                "Interpret definite integrals as areas"
            ],
            ProblemType.WORD_PROBLEM: [
                "Translate real-world situations into mathematical models",
                "Identify relevant information and unknowns",
                "Interpret mathematical results in context"
            ]
        }

        objectives.extend(type_objectives.get(classification.problem_type, []))

        # Add difficulty-specific objectives
        if classification.difficulty == DifficultyLevel.ELEMENTARY:
            objectives.append("Build confidence in mathematical problem-solving")
        elif classification.difficulty in [DifficultyLevel.UNDERGRADUATE, DifficultyLevel.GRADUATE]:
            objectives.append("Connect concepts to broader mathematical theory")

        return objectives

    def _suggest_next_steps(self,
                            classification: ClassificationResult,
                            solution_steps: List[StepExplanation]) -> Dict[str, Any]:
        """Suggest next steps for learning progression."""
        next_steps = {
            "immediate_practice": self._suggest_immediate_practice(classification),
            "skill_building": self._suggest_skill_building(classification),
            "advanced_topics": self._suggest_advanced_topics(classification),
            "review_topics": self._suggest_review_topics(classification),
            "assessment_suggestions": self._suggest_assessments(classification)
        }

        return next_steps

    def _generate_practice_problems(self, classification: ClassificationResult) -> List[Dict[str, Any]]:
        """Generate practice problems similar to the solved problem."""
        problems = []

        # Generate problems based on type and difficulty
        if classification.problem_type == ProblemType.EQUATION:
            problems.extend(self._generate_equation_problems(classification))
        elif classification.problem_type == ProblemType.DERIVATIVE:
            problems.extend(self._generate_derivative_problems(classification))
        elif classification.problem_type == ProblemType.INTEGRAL:
            problems.extend(self._generate_integral_problems(classification))
        elif classification.problem_type == ProblemType.WORD_PROBLEM:
            problems.extend(self._generate_word_problems(classification))

        return problems[:5]  # Limit to 5 practice problems

    def _generate_fallback_explanation(self,
                                       problem: str,
                                       classification: ClassificationResult) -> Dict[str, Any]:
        """Generate a basic fallback explanation when main processing fails."""
        return {
            "problem": problem,
            "classification": classification.to_dict() if hasattr(classification, 'to_dict') else {},
            "explanation": "A detailed explanation could not be generated automatically. Please review the problem step by step using standard mathematical procedures.",
            "suggestions": [
                "Break the problem into smaller parts",
                "Identify what you're solving for",
                "Apply relevant mathematical rules and formulas",
                "Check your answer by substitution or verification"
            ],
            "error_occurred": True
        }

    # Database building methods
    def _build_concept_database(self) -> Dict[str, ConceptExplanation]:
        """Build comprehensive concept database."""
        database = {}

        # Algebra concepts
        database["ALGEBRA_linear_equation"] = ConceptExplanation(
            concept="Linear Equations",
            definition="An equation where the highest power of the variable is 1, forming a straight line when graphed.",
            examples=["2x + 3 = 7", "5y - 2 = 13", "3(x + 1) = 12"],
            common_mistakes=[
                "Forgetting to perform the same operation on both sides",
                "Sign errors when moving terms",
                "Incorrect distribution of multiplication"
            ],
            prerequisites=["Basic arithmetic", "Understanding of variables", "Order of operations"],
            related_concepts=["Systems of equations", "Inequalities", "Graphing lines"]
        )

        database["ALGEBRA_quadratic_equation"] = ConceptExplanation(
            concept="Quadratic Equations",
            definition="An equation of the form ax² + bx + c = 0 where a ≠ 0.",
            examples=["x² - 5x + 6 = 0", "2x² + 3x - 1 = 0", "x² = 16"],
            common_mistakes=[
                "Forgetting the ± when taking square roots",
                "Errors in factoring",
                "Incorrect application of quadratic formula"
            ],
            prerequisites=["Linear equations", "Factoring", "Square roots"],
            related_concepts=["Parabolas", "Complex numbers", "Polynomial equations"]
        )

        # Calculus concepts
        database["CALCULUS_derivative"] = ConceptExplanation(
            concept="Derivatives",
            definition="The rate of change of a function at any given point, representing the slope of the tangent line.",
            examples=["d/dx(x²) = 2x", "d/dx(sin x) = cos x", "d/dx(eˣ) = eˣ"],
            common_mistakes=[
                "Forgetting to apply the chain rule",
                "Sign errors with trigonometric derivatives",
                "Incorrect power rule application"
            ],
            prerequisites=["Functions", "Limits", "Basic algebra"],
            related_concepts=["Integrals", "Optimization", "Related rates"]
        )

        database["CALCULUS_integral"] = ConceptExplanation(
            concept="Integrals",
            definition="The reverse process of differentiation, representing accumulation or area under a curve.",
            examples=["∫x² dx = x³/3 + C", "∫sin x dx = -cos x + C", "∫₀¹ x dx = 1/2"],
            common_mistakes=[
                "Forgetting the constant of integration",
                "Incorrect substitution",
                "Sign errors in integration by parts"
            ],
            prerequisites=["Derivatives", "Basic algebra", "Functions"],
            related_concepts=["Fundamental Theorem of Calculus", "Applications of integration",
                              "Differential equations"]
        )

        return database

    def _build_explanation_templates(self) -> Dict[str, str]:
        """Build templates for different explanation styles."""
        return {
            "step_intro_beginner": "Let's work through this step carefully. {explanation}",
            "step_intro_advanced": "Applying {technique}, we {action}.",
            "step_intro_conversational": "Now here's what we're going to do: {explanation}",
            "reasoning_because": "This works because {reason}.",
            "reasoning_therefore": "Therefore, {conclusion}.",
            "connection_since": "Since we {previous_action}, we can now {current_action}.",
            "verification": "We can verify this by {verification_method}."
        }

    def _build_voice_patterns(self) -> Dict[str, Any]:
        """Build voice pattern configurations."""
        return {
            "pause_length": {
                "short": 0.5,
                "medium": 1.0,
                "long": 1.5
            },
            "emphasis_strength": {
                "light": 1.2,
                "medium": 1.5,
                "strong": 2.0
            },
            "speaking_rate": {
                "slow": 0.8,
                "normal": 1.0,
                "fast": 1.2
            }
        }

    def _build_difficulty_adjustments(self) -> Dict[DifficultyLevel, Dict[str, Any]]:
        """Build difficulty-specific adjustments."""
        return {
            DifficultyLevel.ELEMENTARY: {
                "explanation_detail": "high",
                "encouragement_frequency": "high",
                "visual_aids": "extensive",
                "step_granularity": "fine"
            },
            DifficultyLevel.HIGH_SCHOOL: {
                "explanation_detail": "medium",
                "encouragement_frequency": "medium",
                "visual_aids": "moderate",
                "step_granularity": "medium"
            },
            DifficultyLevel.UNDERGRADUATE: {
                "explanation_detail": "medium",
                "encouragement_frequency": "low",
                "visual_aids": "minimal",
                "step_granularity": "coarse",
                "theoretical_context": "moderate"
            },
            DifficultyLevel.GRADUATE: {
                "explanation_detail": "low",
                "encouragement_frequency": "none",
                "visual_aids": "none",
                "step_granularity": "coarse",
                "theoretical_context": "extensive"
            }
        }

    # Helper methods for educational content generation
    def _identify_key_concepts(self, classification: ClassificationResult) -> List[str]:
        """Identify key concepts for this problem type."""
        concept_map = {
            ProblemType.EQUATION: ["Algebraic manipulation", "Properties of equality", "Variable isolation"],
            ProblemType.DERIVATIVE: ["Rate of change", "Differentiation rules", "Function behavior"],
            ProblemType.INTEGRAL: ["Antiderivatives", "Area under curves", "Fundamental theorem"],
            ProblemType.WORD_PROBLEM: ["Mathematical modeling", "Problem analysis", "Unit analysis"]
        }
        return concept_map.get(classification.problem_type, [])

    def _identify_prerequisites(self, classification: ClassificationResult) -> List[str]:
        """Identify prerequisite knowledge."""
        prereq_map = {
            ProblemType.EQUATION: ["Basic arithmetic", "Order of operations", "Variable concepts"],
            ProblemType.DERIVATIVE: ["Functions", "Limits", "Basic algebra"],
            ProblemType.INTEGRAL: ["Derivatives", "Functions", "Area concepts"],
            ProblemType.WORD_PROBLEM: ["Problem-solving strategies", "Unit conversions", "Basic algebra"]
        }
        return prereq_map.get(classification.problem_type, [])

    def _identify_applications(self, classification: ClassificationResult) -> List[str]:
        """Identify real-world applications."""
        app_map = {
            ProblemType.EQUATION: ["Engineering calculations", "Business modeling", "Scientific formulas"],
            ProblemType.DERIVATIVE: ["Physics motion", "Optimization", "Economics marginal analysis"],
            ProblemType.INTEGRAL: ["Area calculations", "Physics work/energy", "Probability distributions"],
            ProblemType.WORD_PROBLEM: ["Daily problem solving", "Project planning", "Resource allocation"]
        }
        return app_map.get(classification.problem_type, [])

    def _identify_related_topics(self, classification: ClassificationResult) -> List[str]:
        """Identify related mathematical topics."""
        topic_map = {
            ProblemType.EQUATION: ["Systems of equations", "Inequalities", "Functions"],
            ProblemType.DERIVATIVE: ["Integrals", "Limits", "Optimization"],
            ProblemType.INTEGRAL: ["Derivatives", "Differential equations", "Series"],
            ProblemType.WORD_PROBLEM: ["Mathematical modeling", "Statistics", "Geometry"]
        }
        return topic_map.get(classification.problem_type, [])

    def _suggest_difficulty_progression(self, classification: ClassificationResult) -> List[str]:
        """Suggest progression to harder problems."""
        if classification.difficulty == DifficultyLevel.ELEMENTARY:
            return ["Try similar problems with different numbers", "Practice more complex equations",
                    "Move to word problems"]
        elif classification.difficulty == DifficultyLevel.HIGH_SCHOOL:
            return ["Solve systems of equations", "Try optimization problems", "Practice with applications"]
        else:
            return ["Explore theoretical aspects", "Try proof-based problems", "Connect to advanced topics"]

    def _suggest_visual_aids(self, classification: ClassificationResult) -> List[str]:
        """Suggest visual aids for understanding."""
        visual_map = {
            ProblemType.EQUATION: ["Balance scale diagrams", "Number line representations", "Graphing solutions"],
            ProblemType.DERIVATIVE: ["Tangent line animations", "Function graphs", "Rate of change visualizations"],
            ProblemType.INTEGRAL: ["Area under curve diagrams", "Riemann sum animations",
                                   "Accumulation visualizations"],
            ProblemType.WORD_PROBLEM: ["Diagrams of scenarios", "Data organization charts", "Solution flowcharts"]
        }
        return visual_map.get(classification.problem_type, [])

    def _suggest_interactive_elements(self, classification: ClassificationResult) -> List[str]:
        """Suggest interactive learning elements."""
        return [
            "Step-by-step practice problems",
            "Interactive equation manipulator",
            "Graphing calculator activities",
            "Peer problem-solving sessions",
            "Online math games related to topic"
        ]

    def _generate_encouragement(self) -> List[str]:
        """Generate encouraging messages for beginners."""
        return [
            "You're making great progress!",
            "Don't worry if this seems challenging - it gets easier with practice.",
            "Remember, every mathematician started as a beginner.",
            "Take your time and work through each step carefully.",
            "Making mistakes is part of learning - keep going!"
        ]

    def _suggest_mnemonics(self, classification: ClassificationResult) -> List[str]:
        """Suggest memory aids for concepts."""
        mnemonic_map = {
            ProblemType.EQUATION: [
                "Whatever you do to one side, do to the other - like a balanced seesaw",
                "PEMDAS: Please Excuse My Dear Aunt Sally"
            ],
            ProblemType.DERIVATIVE: [
                "Derivative = slope of the tangent line",
                "Power rule: Bring down the power, subtract one from the exponent"
            ]
        }
        return mnemonic_map.get(classification.problem_type, [])

    def _provide_theoretical_background(self, classification: ClassificationResult) -> List[str]:
        """Provide theoretical background for advanced students."""
        theory_map = {
            ProblemType.DERIVATIVE: [
                "Derivatives formalize the concept of instantaneous rate of change",
                "The limit definition connects discrete differences to continuous change",
                "Differentiation is a linear operator on the space of differentiable functions"
            ],
            ProblemType.INTEGRAL: [
                "Integration theory extends the concept of summation to continuous domains",
                "The Fundamental Theorem of Calculus connects differentiation and integration",
                "Measure theory provides the rigorous foundation for integration"
            ]
        }
        return theory_map.get(classification.problem_type, [])

    def _suggest_proof_techniques(self, classification: ClassificationResult) -> List[str]:
        """Suggest relevant proof techniques."""
        proof_map = {
            ProblemType.DERIVATIVE: ["Limit definition proofs", "Chain rule proof", "Mean value theorem"],
            ProblemType.INTEGRAL: ["Fundamental theorem proof", "Integration by parts derivation",
                                   "Substitution rule proof"]
        }
        return proof_map.get(classification.problem_type, [])

    # Practice problem generation methods
    def _generate_equation_problems(self, classification: ClassificationResult) -> List[Dict[str, Any]]:
        """Generate equation practice problems."""
        problems = []

        if classification.difficulty == DifficultyLevel.ELEMENTARY:
            problems = [
                {"problem": "Solve: 2x + 5 = 13", "hint": "Subtract 5 from both sides first"},
                {"problem": "Solve: 3x - 7 = 14", "hint": "Add 7 to both sides, then divide by 3"},
                {"problem": "Solve: 4(x + 2) = 20", "hint": "Distribute first, or divide both sides by 4"}
            ]
        else:
            problems = [
                {"problem": "Solve: x² - 6x + 8 = 0", "hint": "Try factoring first"},
                {"problem": "Solve: 2x² + 5x - 3 = 0", "hint": "Use quadratic formula if factoring is difficult"},
                {"problem": "Solve: √(x + 1) = x - 1", "hint": "Square both sides, but check for extraneous solutions"}
            ]

        return problems

    def _generate_derivative_problems(self, classification: ClassificationResult) -> List[Dict[str, Any]]:
        """Generate derivative practice problems."""
        return [
            {"problem": "Find d/dx(x³ + 2x² - 5x + 1)", "hint": "Apply power rule to each term"},
            {"problem": "Find d/dx(sin(2x))", "hint": "Use chain rule"},
            {"problem": "Find d/dx(x²·ln(x))", "hint": "Use product rule"}
        ]

    def _generate_integral_problems(self, classification: ClassificationResult) -> List[Dict[str, Any]]:
        """Generate integral practice problems."""
        return [
            {"problem": "Find ∫(3x² - 2x + 1)dx", "hint": "Use power rule for integration"},
            {"problem": "Find ∫sin(3x)dx", "hint": "Use substitution with u = 3x"},
            {"problem": "Find ∫x·e^x dx", "hint": "Use integration by parts"}
        ]

    def _generate_word_problems(self, classification: ClassificationResult) -> List[Dict[str, Any]]:
        """Generate word practice problems."""
        return [
            {"problem": "A car travels 240 miles in 4 hours. What is its average speed?",
             "hint": "Use distance = rate × time"},
            {
                "problem": "The perimeter of a rectangle is 20 cm. If the length is 3 cm more than the width, find the dimensions.",
                "hint": "Set up equations using perimeter formula"},
            {"problem": "An investment grows at 5% annual interest. If you start with $1000, how much after 3 years?",
             "hint": "Use compound interest formula"}
        ]

    # Additional helper methods
    def _suggest_immediate_practice(self, classification: ClassificationResult) -> List[str]:
        """Suggest immediate practice activities."""
        return [
            "Solve 2-3 similar problems to reinforce understanding",
            "Try the same problem type with different numbers",
            "Practice each step of the solution process separately"
        ]

    def _suggest_skill_building(self, classification: ClassificationResult) -> List[str]:
        """Suggest skill-building activities."""
        skill_map = {
            ProblemType.EQUATION: [
                "Practice algebraic manipulation",
                "Work on factoring techniques",
                "Master order of operations"
            ],
            ProblemType.DERIVATIVE: [
                "Memorize basic derivative formulas",
                "Practice chain rule applications",
                "Work on function recognition"
            ]
        }
        return skill_map.get(classification.problem_type, ["Practice basic mathematical operations"])

    def _suggest_advanced_topics(self, classification: ClassificationResult) -> List[str]:
        """Suggest advanced topics to explore next."""
        advanced_map = {
            ProblemType.EQUATION: ["Systems of equations", "Matrix algebra", "Polynomial theory"],
            ProblemType.DERIVATIVE: ["Multivariable calculus", "Differential equations", "Vector calculus"],
            ProblemType.INTEGRAL: ["Multiple integrals", "Line integrals", "Fourier analysis"]
        }
        return advanced_map.get(classification.problem_type, ["Advanced mathematical topics"])

    def _suggest_review_topics(self, classification: ClassificationResult) -> List[str]:
        """Suggest topics to review."""
        return [
            "Review prerequisite concepts if struggling",
            "Practice basic arithmetic and algebra",
            "Ensure understanding of mathematical notation"
        ]

    def _suggest_assessments(self, classification: ClassificationResult) -> List[str]:
        """Suggest assessment methods."""
        return [
            "Self-check with practice problems",
            "Explain the solution to someone else",
            "Try to solve without looking at notes",
            "Create your own similar problem"
        ]

    def _generate_dynamic_concept_explanation(self, classification: ClassificationResult) -> ConceptExplanation:
        """Generate a concept explanation when not found in database."""
        return ConceptExplanation(
            concept=f"{classification.problem_type.value.title()}",
            definition=f"Mathematical problems involving {classification.problem_type.value.lower()}",
            examples=["Similar problems of this type"],
            common_mistakes=["Common errors in this area"],
            prerequisites=["Basic mathematical knowledge"],
            related_concepts=["Related mathematical topics"]
        )

    def _simplify_definition(self, definition: str) -> str:
        """Simplify definition for beginners."""
        # Remove complex terminology and use simpler language
        simplified = definition.lower()

        # Replace complex terms with simpler ones
        replacements = {
            "instantaneous rate of change": "how fast something is changing",
            "antiderivative": "reverse of derivative",
            "polynomial": "expression with powers of variables",
            "coefficient": "number in front of variable"
        }

        for complex_term, simple_term in replacements.items():
            simplified = simplified.replace(complex_term, simple_term)

        return simplified.capitalize()


# Additional utility functions for the explainer
def create_explanation_summary(explanation_result: Dict[str, Any]) -> str:
    """Create a concise summary of the explanation."""
    problem = explanation_result.get('problem', 'Mathematical problem')
    classification = explanation_result.get('classification', {})
    steps = explanation_result.get('step_explanations', [])

    summary = f"Problem: {problem}\n"
    summary += f"Type: {classification.get('problem_type', 'Unknown')}\n"
    summary += f"Difficulty: {classification.get('difficulty_level', 'Unknown')}\n"
    summary += f"Number of steps: {len(steps)}\n"

    if steps:
        summary += "\nKey steps:\n"
        for i, step in enumerate(steps[:3], 1):  # Show first 3 steps
            summary += f"{i}. {step.get('description', 'Mathematical operation')}\n"
        if len(steps) > 3:
            summary += f"... and {len(steps) - 3} more steps\n"

    return summary