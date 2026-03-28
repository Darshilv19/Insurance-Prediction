import streamlit as st
import pandas as pd
import pickle
import os
import plotly.express as px

# -------------------------------
# Load model
# -------------------------------
BASE_DIR = os.path.dirname(__file__)
model_path = os.path.join(BASE_DIR, "rf_model.pkl")

with open(model_path, "rb") as f:
    data = pickle.load(f)

model = data["model"]

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="Insurance Dashboard", layout="wide")

st.title("💰 Insurance Premium Prediction Dashboard")

# Sidebar
option = st.sidebar.radio(
    "Select Mode",
    ["🔮 Manual Prediction", "📂 CSV Upload Analysis"]
)

# ==========================================================
# 🔮 MANUAL PREDICTION
# ==========================================================
if option == "🔮 Manual Prediction":

    st.header("Enter Customer Details")

    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("Age", 18, 100, 35)
        gender = st.selectbox("Gender", ["Female", "Male"])
        income = st.number_input("Annual Income", value=50000)
        dependents = st.number_input("Number of Dependents", value=1)
        occupation = st.selectbox("Occupation", ["Salaried", "Self-Employed", "Student"])
        health = st.slider("Health Score", 0, 100, 80)
        policy_type = st.selectbox("Policy Type", ["Basic", "Premium"])

    with col2:
        previous_claims = st.number_input("Previous Claims", value=0)
        credit = st.slider("Credit Score", 300, 900, 700)
        insurance_duration = st.number_input("Insurance Duration", value=5)
        smoking = st.selectbox("Smoking Status", ["No", "Yes"])
        exercise = st.selectbox("Exercise Frequency", ["Low", "Medium", "High"])
        policy_start = st.number_input("Policy Start Year", value=2020)
        policy_age = st.number_input("Policy Age (Years)", value=2)

    input_df = pd.DataFrame([{
        'Age': age,
        'Gender': gender,
        'Annual Income': income,
        'Number of Dependents': dependents,
        'Occupation': occupation,
        'Health Score': health,
        'Policy Type': policy_type,
        'Previous Claims': previous_claims,
        'Credit Score': credit,
        'Insurance Duration': insurance_duration,
        'Smoking Status': smoking,
        'Exercise Frequency': exercise,
        'Policy Start Year': policy_start,
        'Policy Age (Years)': policy_age
    }])

    # Encoding
    input_df['Gender'] = input_df['Gender'].map({"Female": 0, "Male": 1})
    input_df['Smoking Status'] = input_df['Smoking Status'].map({"No": 0, "Yes": 1})
    input_df['Occupation'] = input_df['Occupation'].map({"Salaried": 0,"Self-Employed": 1,"Student": 2})
    input_df['Policy Type'] = input_df['Policy Type'].map({"Basic": 0,"Premium": 1})
    input_df['Exercise Frequency'] = input_df['Exercise Frequency'].map({"Low": 0,"Medium": 1,"High": 2})

    if st.button("Predict Premium"):
        prediction = model.predict(input_df)
        st.success(f"💰 Predicted Premium Amount: {prediction[0]:.2f}")

# ==========================================================
# 📂 CSV UPLOAD SMART DASHBOARD
# ==========================================================
elif option == "📂 CSV Upload Analysis":

    st.header("📊 Smart Interactive Dashboard")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file is not None:

        df = pd.read_csv(uploaded_file)

        st.subheader("📄 Data Preview")
        st.dataframe(df.head())

        # -------------------------------
        # Limit rows for performance
        # -------------------------------
        if len(df) > 1000:
            df = df.sample(1000)

        # -------------------------------
        # Encoding
        # -------------------------------
        mappings = {
            "Gender": {"Female": 0, "Male": 1},
            "Smoking Status": {"No": 0, "Yes": 1},
            "Occupation": {"Salaried": 0, "Self-Employed": 1, "Student": 2},
            "Policy Type": {"Basic": 0, "Premium": 1},
            "Exercise Frequency": {"Low": 0, "Medium": 1, "High": 2}
        }

        for col, mapping in mappings.items():
            if col in df.columns and df[col].dtype == "object":
                df[col] = df[col].map(mapping)

        # -------------------------------
        # Prediction
        # -------------------------------
        required_features = [
            'Age','Gender','Annual Income','Number of Dependents',
            'Occupation','Health Score','Policy Type','Previous Claims',
            'Credit Score','Insurance Duration','Smoking Status',
            'Exercise Frequency','Policy Start Year','Policy Age (Years)'
        ]

        if all(col in df.columns for col in required_features):
            df_model = df[required_features]
            df["Predicted Premium"] = model.predict(df_model)

        # -------------------------------
        # KPI CARDS
        # -------------------------------
        st.subheader("📌 Key Insights")

        numeric_cols = df.select_dtypes(include=['number']).columns

        if "Predicted Premium" in df.columns:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Avg Premium", f"{df['Predicted Premium'].mean():,.0f}")
            c2.metric("Max Premium", f"{df['Predicted Premium'].max():,.0f}")
            c3.metric("Min Premium", f"{df['Predicted Premium'].min():,.0f}")
            c4.metric("Records", len(df))

        # -------------------------------
        # DYNAMIC GRAPH ENGINE
        # -------------------------------
        st.subheader("📊 Dynamic Data Visualization")

        selected_col = st.selectbox("Select Column to Analyze", df.columns)

        # -------------------------------
        # NUMERICAL COLUMN
        # -------------------------------
        if selected_col in numeric_cols:

            st.write("### 📈 Statistical Summary")
            st.write(df[selected_col].describe())

            col1, col2 = st.columns(2)

            with col1:
                fig1 = px.histogram(df, x=selected_col,
                                    title=f"{selected_col} Distribution")
                st.plotly_chart(fig1, use_container_width=True)

            with col2:
                fig2 = px.box(df, y=selected_col,
                              title=f"{selected_col} Spread")
                st.plotly_chart(fig2, use_container_width=True)

        # -------------------------------
        # CATEGORICAL COLUMN
        # -------------------------------
        else:

            value_counts = df[selected_col].value_counts().reset_index()
            value_counts.columns = [selected_col, "Count"]

            col1, col2 = st.columns(2)

            with col1:
                fig3 = px.bar(value_counts,
                              x=selected_col,
                              y="Count",
                              title=f"{selected_col} Distribution")
                st.plotly_chart(fig3, use_container_width=True)

            with col2:
                fig4 = px.pie(value_counts,
                              names=selected_col,
                              values="Count",
                              title=f"{selected_col} Share")
                st.plotly_chart(fig4, use_container_width=True)

        # -------------------------------
        # Download
        # -------------------------------
        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "📥 Download Results",
            csv,
            "predicted_premium.csv",
            "text/csv"
        )