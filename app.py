import streamlit as st
import pandas as pd
import pickle
import os
import io
import plotly.express as px

# -------------------------------
# Load model
# -------------------------------
BASE_DIR = os.path.dirname(__file__)
model_path = os.path.join(BASE_DIR, "rf_model.pkl")

# Check if model exists before loading
if os.path.exists(model_path):
    with open(model_path, "rb") as f:
        data = pickle.load(f)
    model = data["model"]
else:
    model = None
    st.error("Model file 'rf_model.pkl' not found. Please ensure it is in the same directory.")

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="SmartPolicy Dashboard", layout="wide")

st.title("💰 Insurance Premium Prediction Dashboard")

# Updated mappings to match clean_dataset.csv values
mappings = {
    "Gender": {"Female": 0, "Male": 1},
    "Smoking Status": {"No": 0, "Yes": 1},
    "Occupation": {
        "Salaried": 0, "Self-Employed": 1, "Student": 2, 
        "Employed": 0, "Unemployed": 3, "Unknown": 4
    },
    "Policy Type": {"Basic": 0, "Premium": 1, "Comprehensive": 2},
    "Exercise Frequency": {
        "Low": 0, "Medium": 1, "High": 2,
        "Rarely": 0, "Monthly": 1, "Weekly": 1, "Daily": 2
    }
}

required_features = [
    'Age','Gender','Annual Income','Number of Dependents',
    'Occupation','Health Score','Policy Type','Previous Claims',
    'Credit Score','Insurance Duration','Smoking Status',
    'Exercise Frequency','Policy Start Year','Policy Age (Years)'
]

# Sidebar
option = st.sidebar.radio(
    "Select Mode",
    ["🔮 Manual Prediction", "📂 CSV Upload Analysis", "🔍 Bulk Scanner"]
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
        occupation = st.selectbox("Occupation", ["Salaried", "Self-Employed", "Student", "Employed", "Unemployed", "Unknown"])
        health = st.slider("Health Score", 0, 100, 80)
        policy_type = st.selectbox("Policy Type", ["Basic", "Premium", "Comprehensive"])

    with col2:
        previous_claims = st.number_input("Previous Claims", value=0)
        credit = st.slider("Credit Score", 300, 900, 700)
        insurance_duration = st.number_input("Insurance Duration", value=5)
        smoking = st.selectbox("Smoking Status", ["No", "Yes"])
        exercise = st.selectbox("Exercise Frequency", ["Daily", "Weekly", "Monthly", "Rarely"])
        policy_start = st.number_input("Policy Start Year", value=2020)
        policy_age = st.number_input("Policy Age (Years)", value=2)

    if st.button("Predict Premium") and model:
        input_df = pd.DataFrame([{
            'Age': age, 'Gender': gender, 'Annual Income': income,
            'Number of Dependents': dependents, 'Occupation': occupation,
            'Health Score': health, 'Policy Type': policy_type,
            'Previous Claims': previous_claims, 'Credit Score': credit,
            'Insurance Duration': insurance_duration, 'Smoking Status': smoking,
            'Exercise Frequency': exercise, 'Policy Start Year': policy_start,
            'Policy Age (Years)': policy_age
        }])
        
        for col, mapping in mappings.items():
            input_df[col] = input_df[col].map(mapping)

        prediction = model.predict(input_df)
        st.success(f"💰 Predicted Premium Amount: ${prediction[0]:,.2f}")

# ==========================================================
# 🔍 BULK SCANNER
# ==========================================================
elif option == "🔍 Bulk Scanner":
    st.header("🔎 Bulk Premium Scanner")
    
    st.subheader("1. Download Sample Templates")
    sample_df = pd.DataFrame([{
        'Age': 30, 'Gender': 'Male', 'Annual Income': 60000, 'Number of Dependents': 2,
        'Occupation': 'Salaried', 'Health Score': 85, 'Policy Type': 'Basic', 
        'Previous Claims': 0, 'Credit Score': 750, 'Insurance Duration': 10, 
        'Smoking Status': 'No', 'Exercise Frequency': 'Monthly', 
        'Policy Start Year': 2023, 'Policy Age (Years)': 1
    }])

    sc1, sc2, sc3 = st.columns(3)
    csv_sample = sample_df.to_csv(index=False).encode('utf-8')
    sc1.download_button("📄 Download CSV Sample", csv_sample, "sample.csv", "text/csv")

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        sample_df.to_excel(writer, index=False)
    sc2.download_button("📊 Download Excel Sample", buffer.getvalue(), "sample.xlsx", "application/vnd.ms-excel")

    json_sample = sample_df.to_json(orient='records')
    sc3.download_button("📦 Download JSON Sample", json_sample, "sample.json", "application/json")

    st.divider()
    st.subheader("2. Upload File to Scan")
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "json"], key="bulk_upload")

    if uploaded_file and model:
        if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'): df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith('.json'): df = pd.read_json(uploaded_file)

        st.write("📄 **File Preview (Top 3 Rows):**")
        st.dataframe(df.head(3), use_container_width=True)

        if st.button("🚀 Start Bulk Scan"):
            df_encoded = df.copy()
            for col, mapping in mappings.items():
                if col in df_encoded.columns:
                    df_encoded[col] = df_encoded[col].map(mapping)

            if all(col in df_encoded.columns for col in required_features):
                preds = model.predict(df_encoded[required_features])
                df["Predicted Premium ($)"] = preds
                st.success("✅ Scanning Complete!")
                st.dataframe(df.head(10), use_container_width=True)

                st.subheader("3. Download Results")
                processed_csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Scanned File", processed_csv, "scanned_results.csv", "text/csv")
            else:
                st.error("Error: The file is missing columns required for prediction.")

# ==========================================================
# 📂 CSV UPLOAD ANALYSIS (Updated with Automatic File Load)
# ==========================================================
elif option == "📂 CSV Upload Analysis":
    st.header("📊 Smart Interactive Dashboard")
    
    # Feature: Choice between local dataset or manual upload
    data_source = st.radio("Select Data Source", ["Use clean_dataset.csv (Default)", "Upload your own CSV"])
    
    df = None
    if data_source == "Use clean_dataset.csv (Default)":
        if os.path.exists("clean_dataset.csv"):
            df = pd.read_csv("clean_dataset.csv")
            st.info("Loaded `clean_dataset.csv` from local storage.")
        else:
            st.error("`clean_dataset.csv` not found. Please upload it manually.")
    else:
        uploaded_file = st.file_uploader("Upload CSV for Analytics", type=["csv"])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)

    if df is not None:
        # Sample for performance if file is massive
        if len(df) > 5000: 
            st.warning("Dataset is large. Analyzing a random sample of 5,000 records for performance.")
            df_display = df.sample(5000)
        else:
            df_display = df.copy()

        # Preprocessing & Prediction for the Analytics Dashboard
        if model:
            df_encoded = df_display.copy()
            for col, mapping in mappings.items():
                if col in df_encoded.columns:
                    df_encoded[col] = df_encoded[col].map(mapping)
            
            # Fill missing mapping values with 0 to prevent prediction error
            df_encoded = df_encoded.fillna(0)

            if all(col in df_encoded.columns for col in required_features):
                df_display["Predicted Premium"] = model.predict(df_encoded[required_features])

        # KPI CARDS
        st.subheader("📌 Key Insights")
        c1, c2, c3, c4 = st.columns(4)
        if "Predicted Premium" in df_display.columns:
            c1.metric("Avg Premium", f"${df_display['Predicted Premium'].mean():,.0f}")
            c2.metric("Max Premium", f"${df_display['Predicted Premium'].max():,.0f}")
        else:
            c1.metric("Avg Income", f"${df_display['Annual Income'].mean():,.0f}")
            c2.metric("Max Income", f"${df_display['Annual Income'].max():,.0f}")
        
        c3.metric("Avg Health Score", f"{df_display['Health Score'].mean():.1f}")
        c4.metric("Total Records", f"{len(df):,}")

        # Dynamic Graph Engine
        st.subheader("📊 Dynamic Data Visualization")
        selected_col = st.selectbox("Select Column to Analyze", df_display.columns)
        
        if df_display[selected_col].dtype in ['int64', 'float64']:
            st.write(df_display[selected_col].describe())
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(px.histogram(df_display, x=selected_col, title=f"{selected_col} Distribution", color_discrete_sequence=['#636EFA']), use_container_width=True)
            with col2:
                st.plotly_chart(px.box(df_display, y=selected_col, title=f"{selected_col} Spread", color_discrete_sequence=['#EF553B']), use_container_width=True)
        else:
            value_counts = df_display[selected_col].value_counts().reset_index()
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(px.bar(value_counts, x=selected_col, y=value_counts.columns[1], title=f"{selected_col} Count"), use_container_width=True)
            with col2:
                st.plotly_chart(px.pie(value_counts, names=selected_col, values=value_counts.columns[1], title=f"{selected_col} Share"), use_container_width=True)
