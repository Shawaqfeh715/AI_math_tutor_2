import logging
from typing import Dict,List,Any,Optional,Tuple
from dataclasses import dataclass
from enum import Enum
import re

from sympy import latex,sympify,Symbol,diff,integrate,factor,expand,simplify
from src.backend.classifier import ClassificationResult,ProblemType,MathSubject,DifficultyLevel
from  src.backend.solver import  StepExplanation

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger=logging.getLogger(__name__)

class ExplanationStyle(Enum):
      BEGINNER="beginner"
      INTERMEDIATE="intermediate"
      ADVANCED="advanced"
      CONVERSATIONAL="conversational"

@dataclass
class ConceptExplanation:
      concept: str
      definition: str
      examples: List[str]
      common_mistakes: List[str]
      prerequisites: List[str]
      related_concepts: List[str]

      def to_dict(self)-> Dict[str,Any]:
           return {
               "concept":self.concept,
                "definition":self.definition,
                 "examples":self.examples,
                  "common_mistakes":self.common_mistakes,
                  "prerequisties": self.prerequisites,
                   "related_concepts":self.related_concepts
           }

@dataclass
class VoiceExplanation:
      text: str
      phonetic_math: str
      pace_markers: List[int]
      emphasis_words: List[str]

      def to_dict(self)->Dict[str,Any]:

          return {
              "text":self.text,
               "phonetic_math":self.phonetic_math,
                "pace_markers":self.pace_markers,
                "emphasis_words":self.emphasis_words
          }

class MathExplainer:

      def __init__(self):
          self.concept_database=self._build_concept_database()
          self.explanation_templates = self._build_explanation_templates()
          self.voice_patterns = self._build_voice_patterns()
          logger.info("MathExplainer initialized with concept database")

      def explain_solution(self,
                           problem: str,
                           classification: ClassificationResult,
                           solution_steps: List[StepExplanation],
                           style: ExplanationStyle = ExplanationStyle.INTERMEDIATE) -> Dict[str, Any]:
          """
          Generate a comprehensive explanation of the solution process
          """
          try:
              # Generate different types of explanations
              step_explanations = self._explain_solution_steps(solution_steps, classification, style)
              concept_explanation = self._explain_underlying_concepts(classification, style)
              strategy_explanation = self._explain_problem_solving_strategy(classification, solution_steps, style)
              voice_explanation = self._generate_voice_explanation(problem, solution_steps, style)

              # Generate adaptive content based on difficulty
              educational_content = self._generate_educational_content(classification, style)

              return {
                  "problem": problem,
                  "classification": classification.to_dict(),
                  "step_explanations": step_explanations,
                  "concept_explanation": concept_explanation.to_dict(),
                  "strategy_explanation": strategy_explanation,
                  "voice_explanation": voice_explanation.to_dict(),
                  "educational_content": educational_content,
                  "learning_objectives": self._identify_learning_objectives(classification),
                  "next_steps": self._suggest_next_steps(classification, solution_steps),
                  "practice_problems": self._generate_practice_problems(classification)
              }

          except Exception as e:
              logger.error(f"Error generating explanation: {str(e)}")
              return self._generate_fallback_explanation(problem, classification)

      def _explain_solution_steps(self,
                                  steps: List[StepExplanation],
                                  classification: ClassificationResult,
                                  style: ExplanationStyle) -> List[Dict[str, Any]]:
          """Generate detailed explanations for each solution step"""
          explained_steps = []

          for i, step in enumerate(steps):
              explanation = {
                  "step_number": step.step_num,
                  "original_description": step.description,
                  "enhanced_explanation": self._enhance_step_explanation(step, classification, style),
                  "mathematical_justification": self._explain_mathematical_reasoning(step, classification),
                  "alternative_approaches": self._suggest_alternative_approaches(step, classification),
                  "common_errors": self._identify_common_errors_for_step(step, classification),
                  "visualization_hints": self._generate_visualization_hints(step, classification),
                  "latex_expression": step.latex_expr,
                  "voice_friendly": self._make_voice_friendly(step, style)
              }

              # Add context from previous steps
              if i > 0:
                  explanation["connection_to_previous"] = self._explain_step_connection(
                      steps[i - 1], step, classification
                  )

              explained_steps.append(explanation)

          return explained_steps

      def _enhance_step_explanation(self,
                                    step: StepExplanation,
                                    classification: ClassificationResult,
                                    style: ExplanationStyle) -> str:
          """Enhance a step explanation based on the style and difficulty level"""

          base_explanation = step.reasoning or step.description
          problem_type = classification.problem_type
          difficulty = classification.difficulty

          # Get style-specific enhancements
          if style == ExplanationStyle.BEGINNER:
              return self._beginner_enhancement(base_explanation, step, classification)
          elif style == ExplanationStyle.CONVERSATIONAL:
              return self._conversational_enhancement(base_explanation, step, classification)
          elif style == ExplanationStyle.ADVANCED:
              return self._advanced_enhancement(base_explanation, step, classification)
          else:  # INTERMEDIATE
              return self._intermediate_enhancement(base_explanation, step, classification)

      def _beginner_enhancement(self, explanation: str, step: StepExplanation,
                                classification: ClassificationResult) -> str:
          """Create beginner-friendly explanations with lots of detail"""
          enhanced = f"Let me walk you through this step carefully. {explanation}"

          # Add encouraging language
          if step.step_num == 1:
              enhanced = f"Great! Let's start solving this problem together. {enhanced}"

          # Explain why we're doing each operation
          if "=" in step.expression:
              enhanced += " Remember, whatever we do to one side of an equation, we must do to the other side to keep it balanced."

          if any(op in step.expression for op in ['+', '-', '*', '/']):
              enhanced += " Think of this as following the order of operations (PEMDAS)."

          return enhanced

      def _conversational_enhancement(self, explanation: str, step: StepExplanation,
                                      classification: ClassificationResult) -> str:
          """Create conversational, engaging explanations"""
          conversation_starters = [
              "Now here's what we're going to do: ",
              "The next logical step is to ",
              "Here's where it gets interesting - ",
              "Let's tackle this by ",
              "Notice how we can "
          ]

          starter = conversation_starters[step.step_num % len(conversation_starters)]
          enhanced = f"{starter}{explanation.lower()}"

          # Add rhetorical questions
          if classification.problem_type == ProblemType.EQUATION:
              enhanced += " Can you see how this gets us closer to isolating our variable?"
          elif classification.problem_type == ProblemType.DERIVATIVE:
              enhanced += " Notice how the power rule makes this straightforward?"

          return enhanced

      def _advanced_enhancement(self, explanation: str, step: StepExplanation,
                                classification: ClassificationResult) -> str:
          """Create advanced explanations with mathematical rigor"""
          enhanced = explanation

          # Add theoretical context
          if classification.problem_type == ProblemType.DERIVATIVE:
              enhanced += " This application of the derivative demonstrates the fundamental theorem connecting rates of change to slopes of tangent lines."
          elif classification.problem_type == ProblemType.EQUATION:
              enhanced += " This transformation preserves the equivalence relation while simplifying the solution set."

          return enhanced

      def _intermediate_enhancement(self, explanation: str, step: StepExplanation,
                                    classification: ClassificationResult) -> str:
          """Create balanced explanations for intermediate learners"""
          enhanced = explanation

          # Add method identification
          if "factor" in explanation.lower():
              enhanced += " This uses factoring techniques to break down complex expressions."
          elif "substitute" in explanation.lower():
              enhanced += " Substitution is a powerful technique for simplification."

          return enhanced

      def _explain_mathematical_reasoning(self, step: StepExplanation,
                                          classification: ClassificationResult) -> str:
          """Explain the mathematical principles behind each step"""

          reasoning_map = {
              ProblemType.EQUATION: {
                  "solve": "We use the properties of equality: adding, subtracting, multiplying, or dividing both sides by the same value maintains the equation's truth.",
                  "factor": "Factoring utilizes the distributive property in reverse: if ab = 0, then a = 0 or b = 0.",
                  "substitute": "Substitution replaces variables with equivalent expressions to simplify or solve."
              },
              ProblemType.DERIVATIVE: {
                  "power rule": "The power rule states that d/dx(x^n) = n·x^(n-1), derived from the definition of limits.",
                  "chain rule": "The chain rule handles composite functions: d/dx[f(g(x))] = f'(g(x))·g'(x).",
                  "product rule": "For products of functions: d/dx[f(x)g(x)] = f'(x)g(x) + f(x)g'(x)."
              },
              ProblemType.WORD_PROBLEM: {
                  "identify": "Problem-solving begins with identifying known and unknown quantities.",
                  "translate": "Mathematical modeling translates word problems into equations or expressions.",
                  "calculate": "Systematic calculation follows mathematical order of operations."
              }
          }

          problem_type = classification.problem_type
          step_content = step.description.lower()

          # Find relevant reasoning
          if problem_type in reasoning_map:
              for key, reasoning in reasoning_map[problem_type].items():
                  if key in step_content:
                      return reasoning

          return "This step follows standard mathematical procedures to progress toward the solution."

      def _explain_underlying_concepts(self, classification: ClassificationResult,
                                       style: ExplanationStyle) -> ConceptExplanation:
          """Explain the fundamental concepts involved in the problem"""

          primary_subject = list(classification.subjects)[0] if classification.subjects else MathSubject.ALGEBRA
          problem_type = classification.problem_type

          concept_key = f"{primary_subject.name}_{problem_type.value}"

          if concept_key in self.concept_database:
              concept = self.concept_database[concept_key]
          else:
              # Generate dynamic concept explanation
              concept = self._generate_dynamic_concept_explanation(classification)

          # Adapt to style
          if style == ExplanationStyle.BEGINNER:
              concept.definition = self._simplify_definition(concept.definition)
              concept.examples = concept.examples[:2]  # Fewer examples for beginners

          return concept

      def _explain_problem_solving_strategy(self, classification: ClassificationResult,
                                            steps: List[StepExplanation],
                                            style: ExplanationStyle) -> Dict[str, Any]:
          """Explain the overall problem-solving strategy used"""

          strategy_explanations = {
              ProblemType.EQUATION: {
                  "strategy_name": "Equation Solving Strategy",
                  "overview": "Isolate the variable by performing inverse operations in reverse order of operations.",
                  "key_principles": [
                      "Maintain equation balance",
                      "Use inverse operations",
                      "Simplify step by step"
                  ],
                  "when_to_use": "When you have an equation and need to find the value(s) of unknown variable(s)."
              },
              ProblemType.DERIVATIVE: {
                  "strategy_name": "Differentiation Strategy",
                  "overview": "Apply differentiation rules systematically to find the rate of change.",
                  "key_principles": [
                      "Identify the function type",
                      "Apply appropriate differentiation rules",
                      "Simplify the result"
                  ],
                  "when_to_use": "When you need to find slopes, rates of change, or optimization points."
              },
              ProblemType.WORD_PROBLEM: {
                  "strategy_name": "Word Problem Strategy",
                  "overview": "Translate the verbal description into mathematical language, then solve.",
                  "key_principles": [
                      "Identify what you're looking for",
                      "Define variables for unknowns",
                      "Translate relationships into equations",
                      "Solve and interpret the result"
                  ],
                  "when_to_use": "When dealing with real-world applications of mathematical concepts."
              }
          }

          strategy = strategy_explanations.get(classification.problem_type, {
              "strategy_name": "General Problem-Solving Strategy",
              "overview": "Break down the problem into manageable steps and solve systematically.",
              "key_principles": ["Understand the problem", "Plan your approach", "Execute step by step",
                                 "Check your answer"],
              "when_to_use": "For any mathematical problem requiring systematic solution."
          })

          # Add step-by-step breakdown
          strategy["step_breakdown"] = self._analyze_solution_pattern(steps)
          strategy["difficulty_adaptations"] = self._get_difficulty_adaptations(classification)

          return strategy

      def _generate_voice_explanation(self, problem: str, steps: List[StepExplanation],
                                      style: ExplanationStyle) -> VoiceExplanation:
          """Generate voice-optimized explanation"""

          # Create voice-friendly text
          voice_text_parts = [
              f"Let's solve the problem: {self._make_math_speakable(problem)}"
          ]

          for step in steps:
              step_text = f"Step {step.step_num}: {step.description}. "
              step_text += f"We have: {self._make_math_speakable(step.expression)}. "
              if step.reasoning:
                  step_text += f"This is because {step.reasoning.lower()}"
              voice_text_parts.append(step_text)

          full_text = " ".join(voice_text_parts)

          # Identify phonetic math expressions
          phonetic_math = self._convert_to_phonetic_math(problem, steps)

          # Mark pause positions (after each step)
          pace_markers = []
          current_pos = 0
          for part in voice_text_parts:
              current_pos += len(part)
              pace_markers.append(current_pos)

          # Identify emphasis words
          emphasis_words = self._identify_emphasis_words(steps)

          return VoiceExplanation(
              text=full_text,
              phonetic_math=phonetic_math,
              pace_markers=pace_markers,
              emphasis_words=emphasis_words
          )

      def _make_math_speakable(self, expression: str) -> str:
          """Convert mathematical expressions to speech-friendly format"""
          speakable = expression

          # Common replacements for better speech
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
              'log': ' log of ',
              'ln': ' natural log of ',
              'pi': ' pi ',
              '(': ' open parenthesis ',
              ')': ' close parenthesis ',
              'x': ' x ',
              'y': ' y '
          }

          for symbol, spoken in replacements.items():
              speakable = speakable.replace(symbol, spoken)

          # Clean up multiple spaces
          speakable = re.sub(r'\s+', ' ', speakable).strip()

          return speakable

      def _convert_to_phonetic_math(self, problem: str, steps: List[StepExplanation]) -> str:
          """Convert all math expressions to phonetic equivalents"""
          phonetic_parts = [f"Problem: {self._make_math_speakable(problem)}"]

          for step in steps:
              phonetic_parts.append(
                  f"Step {step.step_num}: {self._make_math_speakable(step.expression)}"
              )

          return " | ".join(phonetic_parts)

      def _identify_emphasis_words(self, steps: List[StepExplanation]) -> List[str]:
          """Identify words that should be emphasized in speech"""
          emphasis_words = []

          for step in steps:
              # Mathematical operations to emphasize
              if any(word in step.description.lower() for word in ['factor', 'solve', 'substitute']):
                  emphasis_words.extend(['factor', 'solve', 'substitute'])

              # Important mathematical terms
              important_terms = ['derivative', 'integral', 'equation', 'solution', 'answer']
              for term in important_terms:
                  if term in step.description.lower():
                      emphasis_words.append(term)

          return list(set(emphasis_words))  # Remove duplicates

      def _generate_educational_content(self, classification: ClassificationResult,
                                        style: ExplanationStyle) -> Dict[str, Any]:
          """Generate additional educational content"""

          return {
              "key_concepts": self._identify_key_concepts(classification),
              "prerequisite_knowledge": self._identify_prerequisites(classification),
              "common_misconceptions": self._get_common_misconceptions(classification),
              "real_world_applications": self._get_real_world_applications(classification),
              "practice_tips": self._generate_practice_tips(classification, style),
              "memory_aids": self._generate_memory_aids(classification),
              "visual_learning_tips": self._generate_visual_tips(classification)
          }

      def _identify_learning_objectives(self, classification: ClassificationResult) -> List[str]:
          """Identify what students should learn from this problem"""

          objectives_map = {
              ProblemType.EQUATION: [
                  "Understand equation-solving principles",
                  "Apply inverse operations systematically",
                  "Verify solutions by substitution"
              ],
              ProblemType.DERIVATIVE: [
                  "Master differentiation rules",
                  "Understand the concept of instantaneous rate of change",
                  "Apply derivatives to real-world problems"
              ],
              ProblemType.WORD_PROBLEM: [
                  "Translate word problems into mathematical language",
                  "Identify relevant and irrelevant information",
                  "Interpret mathematical solutions in context"
              ]
          }

          base_objectives = objectives_map.get(classification.problem_type, [
              "Apply mathematical reasoning",
              "Follow systematic problem-solving steps",
              "Check and verify answers"
          ])

          # Add subject-specific objectives
          if MathSubject.CALCULUS in classification.subjects:
              base_objectives.append("Connect calculus concepts to geometric interpretations")
          if MathSubject.GEOMETRY in classification.subjects:
              base_objectives.append("Visualize geometric relationships")

          return base_objectives

      def _suggest_next_steps(self, classification: ClassificationResult,
                              solution_steps: List[StepExplanation]) -> List[Dict[str, str]]:
          """Suggest what the student should study or practice next"""

          suggestions = []

          if classification.problem_type == ProblemType.EQUATION:
              if classification.difficulty == DifficultyLevel.HIGH_SCHOOL:
                  suggestions.extend([
                      {
                          "topic": "Quadratic Formula",
                          "description": "Learn to solve quadratic equations that don't factor easily",
                          "difficulty": "Next Level"
                      },
                      {
                          "topic": "Systems of Equations",
                          "description": "Solve problems involving multiple equations simultaneously",
                          "difficulty": "Same Level"
                      }
                  ])

          elif classification.problem_type == ProblemType.DERIVATIVE:
              suggestions.extend([
                  {
                      "topic": "Chain Rule",
                      "description": "Handle more complex composite functions",
                      "difficulty": "Next Level"
                  },
                  {
                      "topic": "Applications of Derivatives",
                      "description": "Use derivatives to solve optimization problems",
                      "difficulty": "Application"
                  }
              ])

          # Add general suggestions based on performance indicators
          suggestions.append({
              "topic": "Practice Similar Problems",
              "description": f"Work through more {classification.problem_type.value.lower()} problems",
              "difficulty": "Reinforcement"
          })

          return suggestions[:5]  # Limit to top 5 suggestions

      def _generate_practice_problems(self, classification: ClassificationResult) -> List[Dict[str, str]]:
          """Generate similar practice problems"""

          practice_problems = []
          problem_type = classification.problem_type
          difficulty = classification.difficulty

          if problem_type == ProblemType.EQUATION:
              if difficulty in [DifficultyLevel.HIGH_SCHOOL, DifficultyLevel.INTERMEDIATE]:
                  practice_problems.extend([
                      {"problem": "2x + 7 = 15", "difficulty": "Easy"},
                      {"problem": "3x² - 12x + 9 = 0", "difficulty": "Medium"},
                      {"problem": "x² + 4x - 5 = 0", "difficulty": "Medium"}
                  ])

          elif problem_type == ProblemType.DERIVATIVE:
              practice_problems.extend([
                  {"problem": "Find d/dx(2x³ + 5x² - 3x + 1)", "difficulty": "Easy"},
                  {"problem": "Find d/dx(sin(x²))", "difficulty": "Hard"},
                  {"problem": "Find d/dx(x·ln(x))", "difficulty": "Medium"}
              ])

          elif problem_type == ProblemType.WORD_PROBLEM:
              if MathSubject.GEOMETRY in classification.subjects:
                  practice_problems.extend([
                      {"problem": "Find the area of a triangle with base 8 and height 6", "difficulty": "Easy"},
                      {"problem": "A rectangle has perimeter 24. If length is twice the width, find dimensions",
                       "difficulty": "Medium"}
                  ])

          return practice_problems[:4]  # Limit to 4 practice problems

          # Helper methods for building databases and templates

      def _build_concept_database(self) -> Dict[str, ConceptExplanation]:
          """Build a database of mathematical concept explanations"""
          return {
              "ALGEBRA_Equation": ConceptExplanation(
                  concept="Algebraic Equations",
                  definition="An equation is a mathematical statement that two expressions are equal, typically containing one or more variables.",
                  examples=["2x + 3 = 7", "x² - 4 = 0", "3x + 2y = 10"],
                  common_mistakes=[
                      "Not performing the same operation on both sides",
                      "Making sign errors when moving terms",
                      "Forgetting to check solutions"
                  ],
                  prerequisites=["Basic arithmetic", "Understanding of variables", "Order of operations"],
                  related_concepts=["Inequalities", "Systems of equations", "Functions"]
              ),
              "CALCULUS_Derivative": ConceptExplanation(
                  concept="Derivatives",
                  definition="The derivative represents the instantaneous rate of change of a function at any given point.",
                  examples=["d/dx(x²) = 2x", "d/dx(sin x) = cos x", "d/dx(eˣ) = eˣ"],
                  common_mistakes=[
                      "Forgetting the chain rule for composite functions",
                      "Incorrectly applying the power rule",
                      "Not simplifying the final answer"
                  ],
                  prerequisites=["Functions", "Limits", "Basic algebra"],
                  related_concepts=["Integrals", "Rate of change", "Optimization"]
              ),
              "GEOMETRY_Word Problem": ConceptExplanation(
                  concept="Geometric Word Problems",
                  definition="Real-world problems that require geometric formulas and spatial reasoning to solve.",
                  examples=["Area problems", "Volume calculations", "Distance and angle problems"],
                  common_mistakes=[
                      "Using wrong formula",
                      "Forgetting to include units",
                      "Misreading the problem setup"
                  ],
                  prerequisites=["Basic geometry formulas", "Unit conversions", "Problem-solving strategies"],
                  related_concepts=["Measurement", "Spatial visualization", "Applied mathematics"]
              )
          }

      def _build_explanation_templates(self) -> Dict[str, str]:
          """Build templates for different types of explanations"""
          return {
              "step_intro": "In this step, we {action} because {reason}.",
              "beginner_encouragement": "Great work! You're making good progress.",
              "concept_connection": "This connects to {concept} which you learned about {context}.",
              "error_prevention": "Watch out for {mistake} - a common error here is {description}."
          }

      def _build_voice_patterns(self) -> Dict[str, List[str]]:
          """Build patterns for voice explanations"""
          return {
              "transitions": [
                  "Next, we'll",
                  "Now let's",
                  "The following step is to",
                  "Moving forward, we"
              ],
              "explanations": [
                  "This works because",
                  "The reason for this is",
                  "We do this in order to",
                  "This step helps us"
              ],
              "encouragement": [
                  "You're doing great!",
                  "Nice work so far!",
                  "Keep going!",
                  "Excellent progress!"
              ]
          }

      def _generate_fallback_explanation(self, problem: str,
                                         classification: ClassificationResult) -> Dict[str, Any]:
          """Generate a basic explanation when detailed analysis fails"""
          return {
              "problem": problem,
              "classification": classification.to_dict(),
              "basic_explanation": f"This is a {classification.problem_type.value} problem in {list(classification.subjects)[0] if classification.subjects else 'mathematics'}.",
              "error": "Detailed explanation generation failed",
              "fallback_advice": "Please try rephrasing your problem or contact support for help."
          }

          # Additional helper methods (abbreviated for space)

      def _generate_dynamic_concept_explanation(self, classification: ClassificationResult) -> ConceptExplanation:
          """Generate concept explanation when not in database"""
          return ConceptExplanation(
              concept=f"{classification.problem_type.value}",
              definition=f"A mathematical problem involving {classification.problem_type.value.lower()}.",
              examples=[],
              common_mistakes=["Not following systematic approach", "Computational errors"],
              prerequisites=["Basic mathematical knowledge"],
              related_concepts=[]
          )

      def _simplify_definition(self, definition: str) -> str:
          """Simplify definition for beginners"""
          # Replace complex terms with simpler ones
          simplifications = {
              "instantaneous": "immediate",
              "composite": "combined",
              "systematic": "step-by-step"
          }

          simplified = definition
          for complex_term, simple_term in simplifications.items():
              simplified = simplified.replace(complex_term, simple_term)

          return simplified

      def _analyze_solution_pattern(self, steps: List[StepExplanation]) -> List[str]:
          """Analyze the pattern of solution steps"""
          patterns = []

          for step in steps:
              if "identify" in step.description.lower():
                  patterns.append("Problem Analysis")
              elif "substitute" in step.description.lower():
                  patterns.append("Substitution")
              elif "solve" in step.description.lower():
                  patterns.append("Solution Finding")
              elif "simplify" in step.description.lower():
                  patterns.append("Simplification")
              else:
                  patterns.append("Mathematical Operation")

          return patterns

      def _get_difficulty_adaptations(self, classification: ClassificationResult) -> List[str]:
          """Get adaptations needed for different difficulty levels"""
          adaptations = []

          if classification.difficulty == DifficultyLevel.ELEMENTARY:
              adaptations.extend([
                  "Use more visual aids",
                  "Break down into smaller steps",
                  "Provide more examples"
              ])
          elif classification.difficulty == DifficultyLevel.ADVANCED:
              adaptations.extend([
                  "Include theoretical background",
                  "Discuss alternative methods",
                  "Connect to advanced concepts"
              ])

          return adaptations

      def _identify_key_concepts(self, classification: ClassificationResult) -> List[str]:
          """Identify key concepts for this problem type"""
          concept_map = {
              ProblemType.EQUATION: ["Variables", "Equality", "Inverse operations"],
              ProblemType.DERIVATIVE: ["Rate of change", "Limits", "Function behavior"],
              ProblemType.WORD_PROBLEM: ["Problem translation", "Mathematical modeling"]
          }

          return concept_map.get(classification.problem_type, ["Mathematical reasoning"])

      def _identify_prerequisites(self, classification: ClassificationResult) -> List[str]:
          prereq_map = {
              ProblemType.EQUATION: ["Basic algebra", "Order of operations"],
              ProblemType.DERIVATIVE: ["Functions", "Limits", "Algebra"],
              ProblemType.WORD_PROBLEM: ["Reading comprehension", "Basic math concepts"]
          }

          return prereq_map.get(classification.problem_type, ["Basic mathematics"])

      def _get_common_misconceptions(self, classification: ClassificationResult) -> List[str]:
          misconception_map = {
              ProblemType.EQUATION: [
                  "Thinking you can only add/subtract to solve equations",
                  "Forgetting to check solutions",
                  "Confusing = with ≈"
              ],
              ProblemType.DERIVATIVE: [
                  "Thinking derivatives are just slopes",
                  "Forgetting the chain rule",
                  "Confusing d/dx with Δx"
              ]
          }

          return misconception_map.get(classification.problem_type, [])

      def _get_real_world_applications(self, classification: ClassificationResult) -> List[str]:
          application_map = {
              ProblemType.EQUATION: ["Engineering calculations", "Financial planning", "Recipe scaling"],
              ProblemType.DERIVATIVE:[]