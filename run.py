#!/usr/bin/env python3

import os
import sys
import logging
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))

from src.backend.api.routes import app
from src.backend.classifier import MathClassifier
from src.backend.solver import MathSolver
from src.backend.explainer import MathExplainer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting AI Math Tutor...")
    
    try:
        classifier = MathClassifier()
        solver = MathSolver()
        explainer = MathExplainer()
        
        logger.info("All components initialized successfully")
        logger.info("Starting Flask server on http://localhost:5000")
        
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start AI Math Tutor: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
