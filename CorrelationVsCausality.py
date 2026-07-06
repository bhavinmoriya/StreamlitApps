import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from dowhy import CausalModel
import warnings
warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(
    page_title="Correlation vs. Causality Explorer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #ffc107;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<p class="main-header">🔍 Correlation vs. Causality Explorer</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Upload your dataset and explore the difference between correlation and causality</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload a CSV file",
        type=["csv"],
        help="Upload a CSV file with numerical columns to analyze."
    )
    
    # Example datasets
    st.subheader("📊 Example Datasets")
    example_choice = st.selectbox(
        "Or use an example dataset:",
        ["None", "Ice Cream vs. Drowning", "Smoking vs. Lung Cancer", "Vitamin D vs. Mental Health"]
    )
    
    # Confounder selection
    st.subheader("🔗 Confounders")
    use_confounder = st.checkbox("Add a confounder variable", value=True)
    
    # Visualization settings
    st.subheader("🎨 Visualization")
    plot_type = st.selectbox("Plot type for correlation:", ["Scatter", "Heatmap", "Pairplot"])
    show_regression_line = st.checkbox("Show regression line", value=True)

# Load or generate data
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ Dataset loaded successfully!")
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
        df = None
elif example_choice != "None":
    if example_choice == "Ice Cream vs. Drowning":
        np.random.seed(42)
        n = 100
        temperature = np.random.normal(25, 10, n)
        ice_cream = temperature + np.random.normal(0, 2, n)
        drowning = temperature + np.random.normal(0, 3, n)
        df = pd.DataFrame({
            'Temperature': temperature,
            'Ice_Cream_Sales': ice_cream,
            'Drowning_Incidents': drowning
        })
        st.info("🍦 Example: Ice cream sales and drowning incidents (confounded by temperature)")
    
    elif example_choice == "Smoking vs. Lung Cancer":
        np.random.seed(42)
        n = 200
        smoking = np.random.binomial(1, 0.4, n)
        age = np.random.randint(20, 80, n)
        genetics = np.random.binomial(1, 0.3, n)
        
        # Lung cancer is caused by smoking, age, and genetics
        lung_cancer_prob = (
            0.1 * smoking + 
            0.005 * (age - 20) + 
            0.2 * genetics + 
            np.random.normal(0, 0.1, n)
        )
        lung_cancer = np.where(lung_cancer_prob > 0.3, 1, 0)
        
        df = pd.DataFrame({
            'Smoking': smoking,
            'Age': age,
            'Genetics': genetics,
            'Lung_Cancer': lung_cancer
        })
        st.info("🚬 Example: Smoking and lung cancer (with age and genetics as confounders)")
    
    elif example_choice == "Vitamin D vs. Mental Health":
        np.random.seed(42)
        n = 150
        sunlight = np.random.normal(5, 2, n)
        vitamin_d = sunlight + np.random.normal(0, 1, n)
        exercise = np.random.binomial(1, 0.6, n)
        mental_health = 10 - (0.5 * vitamin_d + 2 * exercise + np.random.normal(0, 1, n))
        
        df = pd.DataFrame({
            'Sunlight_Exposure': sunlight,
            'Vitamin_D': vitamin_d,
            'Exercise': exercise,
            'Mental_Health_Score': mental_health
        })
        st.info("☀️ Example: Vitamin D and mental health (with sunlight and exercise as confounders)")
else:
    df = None

# Main content
if df is not None:
    st.divider()
    
    # Display dataset
    st.subheader("📋 Dataset Preview")
    st.dataframe(df.head())
    
    # Select variables for analysis
    st.subheader("🔬 Select Variables for Analysis")
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) < 2:
        st.warning("⚠️ Your dataset needs at least 2 numerical columns for analysis.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            x_var = st.selectbox("Select X variable (potential cause):", numeric_cols)
        with col2:
            y_var = st.selectbox("Select Y variable (potential effect):", [c for c in numeric_cols if c != x_var])
        
        # Confounder selection
        confounder = None
        if use_confounder and len(numeric_cols) > 2:
            confounder = st.selectbox(
                "Select confounder variable:",
                [c for c in numeric_cols if c not in [x_var, y_var]]
            )
        
        if st.button("🔍 Analyze Relationship"):
            st.divider()
            
            # ===== CORRELATION ANALYSIS =====
            st.header("📊 Correlation Analysis")
            st.markdown("""
            <div class="info-box">
            <strong>What is correlation?</strong> Correlation measures how two variables move together, but it does NOT imply causation.
            A high correlation could be due to:
            <ul>
                <li>X causing Y</li>
                <li>Y causing X</li>
                <li>A third variable (confounder) causing both</li>
                <li>Pure coincidence</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Calculate correlation
            corr_matrix = df[[x_var, y_var]].corr()
            corr_value = corr_matrix.loc[x_var, y_var]
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric("Correlation Coefficient", f"{corr_value:.3f}")
                if abs(corr_value) > 0.7:
                    st.write("➡️ Strong correlation")
                elif abs(corr_value) > 0.3:
                    st.write("➡️ Moderate correlation")
                else:
                    st.write("➡️ Weak or no correlation")
            
            with col2:
                if plot_type == "Scatter":
                    fig, ax = plt.subplots(figsize=(8, 5))
                    sns.scatterplot(data=df, x=x_var, y=y_var, ax=ax)
                    if show_regression_line:
                        sns.regplot(data=df, x=x_var, y=y_var, scatter=False, color='red', ax=ax)
                    ax.set_title(f"{x_var} vs. {y_var}")
                    st.pyplot(fig)
                elif plot_type == "Heatmap":
                    fig, ax = plt.subplots(figsize=(8, 5))
                    sns.heatmap(df[[x_var, y_var]].corr(), annot=True, cmap='coolwarm', ax=ax)
                    ax.set_title("Correlation Heatmap")
                    st.pyplot(fig)
                else:  # Pairplot
                    st.write("Pairplot for all numerical variables:")
                    fig = sns.pairplot(df[numeric_cols])
                    st.pyplot(fig)
            
            # ===== CAUSALITY ANALYSIS =====
            st.divider()
            st.header("🔗 Causality Analysis")
            st.markdown("""
            <div class="info-box">
            <strong>What is causality?</strong> Causality means that changing X <em>directly</em> changes Y, all else being equal.
            To infer causality, we need to:
            <ul>
                <li>Control for confounders (variables that affect both X and Y)</li>
                <li>Use methods like randomization, matching, or causal models</li>
                <li>Validate with domain knowledge</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
            
            if confounder:
                # Create causal model
                st.subheader("📈 Causal Model with Confounder Adjustment")
                
                # Show DAG
                st.markdown("""
                <div class="info-box">
                <strong>Directed Acyclic Graph (DAG):</strong>
                <pre>
                    Confounder → X
                    Confounder → Y
                        X → Y
                </pre>
                This represents our assumption that the confounder affects both X and Y.
                </div>
                """, unsafe_allow_html=True)
                
                # Fit causal model using DoWhy
                try:
                    # Create causal model
                    model = CausalModel(
                        data=df,
                        treatment=x_var,
                        outcome=y_var,
                        common_causes=[confounder]
                    )
                    
                    # Identify causal effect
                    identified_estimand = model.identify_effect(proceed_when_unidentifiable=True)
                    st.write("**Identified Estimand:**")
                    st.code(identified_estimand)
                    
                    # Estimate causal effect using linear regression
                    estimate = model.estimate_effect(
                        identified_estimand,
                        method_name="backdoor.linear_regression",
                        target_units="ate"
                    )
                    
                    st.write("**Causal Effect Estimate:**")
                    st.metric("Average Treatment Effect (ATE)", f"{estimate.value:.3f}")
                    st.caption(f"This means that, on average, a one-unit increase in {x_var} is associated with a {estimate.value:.3f} unit change in {y_var}, after adjusting for {confounder}.")
                    
                    # Compare with naive regression
                    st.subheader("⚖️ Comparison: Naive vs. Causal Estimate")
                    
                    # Naive regression (no confounder adjustment)
                    X_naive = sm.add_constant(df[x_var])
                    y_naive = df[y_var]
                    naive_model = sm.OLS(y_naive, X_naive).fit()
                    naive_coef = naive_model.params[x_var]
                    
                    # Adjusted regression (with confounder)
                    X_adjusted = sm.add_constant(df[[x_var, confounder]])
                    adjusted_model = sm.OLS(y_naive, X_adjusted).fit()
                    adjusted_coef = adjusted_model.params[x_var]
                    
                    comparison_df = pd.DataFrame({
                        'Method': ['Naive Regression', 'Confounder-Adjusted', 'Causal Model (DoWhy)'],
                        'Coefficient': [naive_coef, adjusted_coef, estimate.value]
                    })
                    st.dataframe(comparison_df.style.format({'Coefficient': '{:.3f}'}))
                    
                    st.markdown("""
                    <div class="warning-box">
                    <strong>Key Insight:</strong> The naive regression may over- or under-estimate the true causal effect because it doesn't account for confounders.
                    The causal model gives a more accurate estimate by adjusting for the confounder.
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"❌ Error in causal analysis: {e}")
                    st.info("This might happen if your data has missing values or non-numeric columns. Try cleaning your data or using a different example dataset.")
            else:
                st.markdown("""
                <div class="warning-box">
                <strong>Note:</strong> Without a confounder variable, we cannot perform proper causal inference.
                In real-world scenarios, you would need to:
                <ul>
                    <li>Identify potential confounders (variables that affect both X and Y)</li>
                    <li>Collect data on these confounders</li>
                    <li>Use methods like propensity score matching or instrumental variables</li>
                </ul>
                Try enabling the "Add a confounder variable" option in the sidebar!
                </div>
                """, unsafe_allow_html=True)
                
                # Show what would happen without adjustment
                st.subheader("⚠️ Naive Regression (No Confounder Adjustment)")
                X = sm.add_constant(df[x_var])
                y = df[y_var]
                model = sm.OLS(y, X).fit()
                st.write(f"Regression coefficient: {model.params[x_var]:.3f}")
                st.warning("This estimate may be biased if there are unmeasured confounders!")
    
    # Additional resources
    st.divider()
    st.subheader("📚 Learn More")
    st.markdown("""
    - [DoWhy Documentation](https://www.pywhy.org/dowhy/v0.14/)
    - [Causal Inference: The Mixtape](https://mixtape.scunning.com/) (Free book by Scott Cunningham)
    - [StatsModels Documentation](https://www.statsmodels.org/stable/index.html)
    - [Correlation vs. Causation: A Guide](https://github.com/bhavinmoriya/StreamlitApps/blob/main/CorrelationVsCausality.md)
    """)

else:
    st.markdown("""
    <div class="info-box">
    <h3>📌 How to Use This Dashboard</h3>
    <ol>
        <li><strong>Upload a CSV file</strong> with numerical columns, or</li>
        <li><strong>Select an example dataset</strong> from the sidebar (e.g., Ice Cream vs. Drowning).</li>
        <li>Select your <strong>X (potential cause)</strong> and <strong>Y (potential effect)</strong> variables.</li>
        <li>Optionally, select a <strong>confounder variable</strong> to adjust for in the causal analysis.</li>
        <li>Click <strong>"Analyze Relationship"</strong> to see the difference between correlation and causality!</li>
    </ol>
    
    <h3>💡 Example Use Cases</h3>
    <ul>
        <li>Does <strong>exercise</strong> cause better <strong>mental health</strong>?</li>
        <li>Does <strong>education level</strong> cause higher <strong>income</strong>?</li>
        <li>Does <strong>social media use</strong> cause <strong>anxiety</strong>?</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

linkedin_url = "https://www.linkedin.com/in/bhavin-moriya-ph-d-b0b88b2/"
github_url = "https://github.com/bhavinmoriya"

st.markdown("## Connect with me")

col1, col2 = st.columns(2)

with col1:
    st.link_button("🔗 Follow on LinkedIn", linkedin_url)

with col2:
    st.link_button("💻 Follow on GitHub", github_url)
