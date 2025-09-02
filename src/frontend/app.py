import streamlit as st
import requests
import json
import pandas as pd
from typing import Dict, Any, List

API_BASE_URL = "http://localhost:5000"

st.set_page_config(
    page_title="AI Math Tutor",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧮 AI Math Tutor & Solver")
st.markdown("**Natural Language Processing Powered Math Problem Classification & Solving**")

def check_api_health():
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def classify_problem(problem: str) -> Dict[str, Any]:
    try:
        response = requests.post(
            f"{API_BASE_URL}/classify",
            json={"problem": problem},
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"error": f"API request failed: {str(e)}"}

def solve_problem(problem: str) -> Dict[str, Any]:
    try:
        response = requests.post(
            f"{API_BASE_URL}/solve",
            json={"problem": problem},
            timeout=15
        )
        return response.json()
    except Exception as e:
        return {"error": f"API request failed: {str(e)}"}

def explain_problem(problem: str, style: str = "intermediate") -> Dict[str, Any]:
    try:
        response = requests.post(
            f"{API_BASE_URL}/explain",
            json={"problem": problem, "style": style},
            timeout=20
        )
        return response.json()
    except Exception as e:
        return {"error": f"API request failed: {str(e)}"}

def full_analysis(problem: str, style: str = "intermediate") -> Dict[str, Any]:
    try:
        response = requests.post(
            f"{API_BASE_URL}/full_analysis",
            json={"problem": problem, "style": style},
            timeout=25
        )
        return response.json()
    except Exception as e:
        return {"error": f"API request failed: {str(e)}"}

def display_classification(classification: Dict[str, Any]):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Subject", ", ".join(classification.get("subjects", [])))
    
    with col2:
        st.metric("Problem Type", classification.get("problem_type", "Unknown"))
    
    with col3:
        st.metric("Difficulty", classification.get("difficulty", "Unknown"))
    
    st.metric("Confidence", f"{classification.get('confidence', 0):.2f}")
    
    variables = classification.get("variables", [])
    functions = classification.get("functions", [])
    
    if variables or functions:
        col1, col2 = st.columns(2)
        with col1:
            if variables:
                st.write("**Variables:**", ", ".join(variables))
        with col2:
            if functions:
                st.write("**Functions:**", ", ".join(functions))

def display_solution(solution: Dict[str, Any]):
    if "error" in solution:
        st.error(f"Solution Error: {solution['error']}")
        return
    
    st.subheader("Solution Steps")
    
    steps = solution.get("steps", [])
    if steps:
        for i, step in enumerate(steps, 1):
            with st.expander(f"Step {i}: {step.get('description', 'Step')}"):
                st.write(f"**Expression:** {step.get('expression', 'N/A')}")
                if step.get('latex'):
                    st.latex(step.get('latex'))
                if step.get('reasoning'):
                    st.write(f"**Reasoning:** {step['reasoning']}")
    
    if solution.get("solution"):
        st.success(f"**Final Answer:** {solution['solution']}")

def display_explanation(explanation: Dict[str, Any]):
    if "error" in explanation:
        st.error(f"Explanation Error: {explanation['error']}")
        return
    
    st.subheader("Detailed Explanation")
    
    if "concept_explanation" in explanation:
        concept = explanation["concept_explanation"]
        with st.expander("Concept Explanation"):
            st.write(f"**Concept:** {concept.get('concept', 'N/A')}")
            st.write(f"**Definition:** {concept.get('definition', 'N/A')}")
            
            if concept.get('examples'):
                st.write("**Examples:**")
                for example in concept['examples']:
                    st.write(f"- {example}")
    
    if "strategy_explanation" in explanation:
        strategy = explanation["strategy_explanation"]
        with st.expander("Problem Solving Strategy"):
            st.write(f"**Strategy:** {strategy.get('strategy_name', 'N/A')}")
            st.write(f"**Overview:** {strategy.get('overview', 'N/A')}")
            
            if strategy.get('key_principles'):
                st.write("**Key Principles:**")
                for principle in strategy['key_principles']:
                    st.write(f"- {principle}")
    
    if "educational_content" in explanation:
        content = explanation["educational_content"]
        with st.expander("Educational Content"):
            if content.get('key_concepts'):
                st.write("**Key Concepts:**")
                for concept in content['key_concepts']:
                    st.write(f"- {concept}")
            
            if content.get('formulas'):
                st.write("**Relevant Formulas:**")
                for formula in content['formulas']:
                    st.write(f"- {formula}")

def main():
    if not check_api_health():
        st.error("⚠️ Backend API is not running. Please start the backend server first.")
        st.info("Run `python run.py` in your terminal to start the backend.")
        return
    
    st.success("✅ Backend API is running and ready!")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Problem Solver", "Classification Only", "Full Analysis", "Batch Processing"])
    
    with tab1:
        st.header("Solve Math Problems")
        
        problem_input = st.text_area(
            "Enter your math problem:",
            placeholder="e.g., Solve for x: 2x + 3 = 7\nor\nFind the derivative of x² + 3x",
            height=100
        )
        
        col1, col2 = st.columns([1, 3])
        with col1:
            solve_button = st.button("Solve Problem", type="primary")
        
        if solve_button and problem_input.strip():
            with st.spinner("Solving your problem..."):
                result = solve_problem(problem_input.strip())
                
                if result.get("success"):
                    st.success("Problem solved successfully!")
                    
                    if "classification" in result:
                        st.subheader("Problem Classification")
                        display_classification(result["classification"])
                    
                    if "solution" in result:
                        display_solution(result["solution"])
                else:
                    st.error(f"Failed to solve problem: {result.get('error', 'Unknown error')}")
    
    with tab2:
        st.header("Classify Math Problems")
        
        classify_input = st.text_area(
            "Enter a math problem to classify:",
            placeholder="e.g., Find the area of a circle with radius 5",
            height=100
        )
        
        if st.button("Classify Problem", type="primary") and classify_input.strip():
            with st.spinner("Classifying problem..."):
                result = classify_problem(classify_input.strip())
                
                if result.get("success"):
                    st.success("Problem classified successfully!")
                    display_classification(result["classification"])
                    
                    if "explanation" in result:
                        with st.expander("Classification Explanation"):
                            st.json(result["explanation"])
                else:
                    st.error(f"Classification failed: {result.get('error', 'Unknown error')}")
    
    with tab3:
        st.header("Full Problem Analysis")
        
        analysis_input = st.text_area(
            "Enter a math problem for full analysis:",
            placeholder="e.g., Solve the quadratic equation x² - 5x + 6 = 0",
            height=100
        )
        
        style_options = ["beginner", "intermediate", "advanced", "conversational"]
        selected_style = st.selectbox("Explanation Style:", style_options, index=1)
        
        if st.button("Analyze Problem", type="primary") and analysis_input.strip():
            with st.spinner("Performing full analysis..."):
                result = full_analysis(analysis_input.strip(), selected_style)
                
                if result.get("success"):
                    st.success("Full analysis completed!")
                    
                    if "classification" in result:
                        st.subheader("Problem Classification")
                        display_classification(result["classification"])
                    
                    if "solution" in result:
                        display_solution(result["solution"])
                    
                    if "explanation" in result:
                        display_explanation(result["explanation"])
                else:
                    st.error(f"Analysis failed: {result.get('error', 'Unknown error')}")
    
    with tab4:
        st.header("Batch Problem Processing")
        
        st.info("Upload a CSV file with math problems or enter multiple problems manually.")
        
        uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                if 'problem' in df.columns:
                    problems = df['problem'].tolist()
                    st.success(f"Loaded {len(problems)} problems from CSV")
                    
                    if st.button("Process All Problems", type="primary"):
                        with st.spinner("Processing problems..."):
                            results = []
                            for problem in problems:
                                if str(problem).strip():
                                    result = classify_problem(str(problem).strip())
                                    results.append({
                                        "problem": problem,
                                        "classification": result.get("classification", {}),
                                        "success": result.get("success", False)
                                    })
                            
                            if results:
                                st.subheader("Batch Processing Results")
                                results_df = pd.DataFrame(results)
                                st.dataframe(results_df)
                                
                                success_count = sum(1 for r in results if r["success"])
                                st.info(f"Successfully processed {success_count}/{len(results)} problems")
                else:
                    st.error("CSV must have a 'problem' column")
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")
        
        st.subheader("Or enter problems manually:")
        manual_problems = st.text_area(
            "Enter problems (one per line):",
            placeholder="Solve for x: 2x + 3 = 7\nFind the derivative of x²\nCalculate the area of a circle with radius 5",
            height=150
        )
        
        if st.button("Process Manual Problems", type="primary") and manual_problems.strip():
            problems = [p.strip() for p in manual_problems.split('\n') if p.strip()]
            
            with st.spinner(f"Processing {len(problems)} problems..."):
                results = []
                for problem in problems:
                    result = classify_problem(problem)
                    results.append({
                        "problem": problem,
                        "classification": result.get("classification", {}),
                        "success": result.get("success", False)
                    })
                
                if results:
                    st.subheader("Manual Processing Results")
                    results_df = pd.DataFrame(results)
                    st.dataframe(results_df)
                    
                    success_count = sum(1 for r in results if r["success"])
                    st.info(f"Successfully processed {success_count}/{len(results)} problems")

if __name__ == "__main__":
    main()
