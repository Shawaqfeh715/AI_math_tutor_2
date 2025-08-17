AI Math Tutor & Solver (Ongoing)

Natural Language Processing (NLP) Powered Math Problem Classification & Solving

🚀 Project Overview

This project aims to build an intelligent AI Math Tutor that understands and classifies math problems written in natural language, then provides step-by-step solutions.
Currently, the focus is on NLP-driven math problem classification that detects the math subject, problem type, difficulty level, and key elements like variables and functions.

The classifier supports a wide range of topics including Algebra, Calculus, Geometry, Trigonometry, and Statistics.

🧠 Key Features

Robust Math Problem Classifier:
Uses regex and heuristic patterns to classify problems by subject, type, and difficulty with confidence scoring.

Multi-Subject Coverage:
Algebra, Calculus, Geometry, Trigonometry, Statistics.

Detailed Classification Output:

Detected subjects (e.g. Calculus, Algebra)

Problem type (e.g. Derivative, Equation, Word Problem)

Variables and functions found (e.g. x, sin)

Difficulty estimation from Elementary to Advanced

Confidence score for classification reliability

Metadata including complexity indicators and parsed expressions

Explainability:
Generates detailed explanations for classification decisions, making it easier to debug and extend.

Fallback Handling:
Handles ambiguous or malformed inputs gracefully with fallback heuristics.

🧩 Architecture & Components

classifier.py: Core classification logic using regex patterns and heuristics.

NLP preprocessing (in development): To improve semantic understanding beyond pattern matching.

Solver modules (planned): To provide detailed step-by-step solutions based on classification.

🔧 Technologies Used

Python 3.8+

re (regex) for pattern matching

enum, dataclasses for structured output

sympy for symbolic math parsing and validation

Logging for debugging and traceability
