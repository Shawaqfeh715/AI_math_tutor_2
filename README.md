# 🧮 AI Math Tutor & Solver

A comprehensive AI-powered math tutoring system that understands, classifies, solves, and explains mathematical problems written in natural language.

## 🚀 Features

- **Smart Problem Classification**: Automatically detects math subjects, problem types, and difficulty levels
- **Step-by-Step Solutions**: Provides detailed solutions with explanations for each step
- **Multiple Explanation Styles**: Beginner, intermediate, advanced, and conversational explanations
- **Comprehensive Coverage**: Algebra, Calculus, Geometry, Trigonometry, and Statistics
- **Confidence Scoring**: Reliability metrics for classification accuracy
- **Educational Content**: Learning objectives, practice problems, and concept explanations
- **Voice-Friendly Output**: Math expressions converted to speech-friendly text
- **RESTful API**: Full backend API for integration with other applications
- **Modern Web Interface**: Beautiful Streamlit frontend for easy interaction

## 🏗️ Architecture

```
src/
├── backend/
│   ├── classifier.py      # Math problem classification engine
│   ├── solver.py          # Mathematical problem solver
│   ├── explainer.py       # Educational explanation generator
│   └── api/
│       └── routes.py      # Flask REST API endpoints
├── frontend/
│   └── app.py            # Streamlit web interface
├── data/
│   └── problems.json     # Test dataset
└── utils/                # Utility functions
```

## 📋 Requirements

- Python 3.8+
- Flask 2.3.3+
- Streamlit 1.28.1+
- SymPy 1.14.0+
- Pandas 2.1.3+

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd AI_math_tutor_2
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Quick Start

### Option 1: Web Interface (Recommended)

1. **Start the backend API:**
   ```bash
   python run.py
   ```

2. **In a new terminal, start the frontend:**
   ```bash
   streamlit run src/frontend/app.py
   ```

3. **Open your browser to:** `http://localhost:8501`

### Option 2: API Only

1. **Start the backend:**
   ```bash
   python run.py
   ```

2. **API will be available at:** `http://localhost:5000`

### Option 3: Command Line Testing

1. **Run the test suite:**
   ```bash
   python test_system.py
   ```

## 📚 Usage Examples

### Basic Problem Classification

```python
from src.backend.classifier import MathClassifier

classifier = MathClassifier()
result = classifier.classify("Solve for x: 2x + 3 = 7")

print(f"Problem Type: {result.problem_type}")
print(f"Subjects: {result.subjects}")
print(f"Difficulty: {result.difficulty}")
print(f"Confidence: {result.confidence:.2f}")
```

### Problem Solving

```python
from src.backend.classifier import MathClassifier
from src.backend.solver import MathSolver

classifier = MathClassifier()
solver = MathSolver()

classification = classifier.classify("Find the derivative of x² + 3x")
solution = solver.solve_problem(classification, "x² + 3x")

print(f"Solution: {solution['solution']}")
print(f"Steps: {len(solution['steps'])}")
```

### Full Problem Analysis

```python
from src.backend.explainer import MathExplainer, ExplanationStyle

explainer = MathExplainer()
explanation = explainer.explain_solution(
    problem="Solve for x: 2x + 3 = 7",
    classification=classification,
    solution_steps=solution['steps'],
    style=ExplanationStyle.BEGINNER
)
```

## 🌐 API Endpoints

### Health Check
```bash
GET /health
```

### Classify Problem
```bash
POST /classify
{
  "problem": "Solve for x: 2x + 3 = 7"
}
```

### Solve Problem
```bash
POST /solve
{
  "problem": "Find the derivative of x² + 3x"
}
```

### Explain Problem
```bash
POST /explain
{
  "problem": "Solve for x: 2x + 3 = 7",
  "style": "beginner"
}
```

### Full Analysis
```bash
POST /full_analysis
{
  "problem": "Find the derivative of x² + 3x",
  "style": "intermediate"
}
```

### Batch Classification
```bash
POST /batch_classify
{
  "problems": [
    "Solve for x: 2x + 3 = 7",
    "Find the derivative of x² + 3x"
  ]
}
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_system.py
```

This will test:
- Problem classification accuracy
- Mathematical solving capabilities
- Explanation generation
- System integration
- Performance benchmarks

## 📊 Supported Problem Types

### Algebra
- Linear equations
- Quadratic equations
- Factoring
- Simplification
- Systems of equations

### Calculus
- Derivatives (power rule, chain rule, product rule)
- Integrals
- Limits

### Geometry
- Area calculations
- Perimeter calculations
- Volume calculations
- Word problems

### Trigonometry
- Trigonometric functions
- Trigonometric equations
- Angle calculations

### Statistics
- Mean, median, mode
- Standard deviation
- Probability problems

## 🎯 Explanation Styles

- **Beginner**: Detailed explanations with extra context and examples
- **Intermediate**: Balanced explanations with key concepts
- **Advanced**: Concise explanations for experienced learners
- **Conversational**: Friendly, engaging explanations

## 🔧 Configuration

The system automatically detects:
- Mathematical subjects
- Problem complexity
- Required mathematical tools
- Difficulty levels
- Confidence scores

## 🚧 Limitations & Future Work

### Current Limitations
- Limited to basic mathematical operations
- Some complex word problems may not be fully parsed
- Advanced calculus topics (partial derivatives, multiple integrals) not yet implemented

### Planned Improvements
- Integration with advanced NLP models
- Support for more complex mathematical domains
- Interactive step-by-step guidance
- Integration with graphing calculators
- Mobile app development
- Multi-language support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- SymPy for symbolic mathematics
- Flask for the web framework
- Streamlit for the user interface
- Mathematical education community for problem examples

## 📞 Support

For questions, issues, or contributions, please open an issue on GitHub or contact the development team.

---

**Happy Learning! 🎓✨**