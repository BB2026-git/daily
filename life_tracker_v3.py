import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# --- CONFIGURATION ---
DATA_FILE = "life_metrics.csv"
MY_PASSWORD = "Irish02!!"  # <--- PASSWORD

st.set_page_config(page_title="Life Master Grid v8", page_icon="🛡️", layout="wide")

# --- CUSTOM CSS FOR THE GRID ---
st.markdown("""
<style>
    table {
        border-collapse: collapse;
        width: 100%;
        font-family: monospace;
    }
    th {
        background-color: #f0f2f6;
        padding: 5px;
        border: 1px solid #ddd;
        text-align: center;
        font-weight: bold;
        font-size: 14px;
    }
    td {
        padding: 5px;
        border: 1px solid #ddd;
        text-align: center;
        width: 35px;
        height: 35px;
        font-size: 14px;
    }
    tbody th {
        position: sticky;
        left: 0;
        background-color: #fff;
        z-index: 1;
        text-align: right;
        padding-right: 15px;
        min-width: 100px;
    }
</style>
""", unsafe_allow_html=True)

# --- AUTHENTICATION ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    if st.session_state.password_input == MY_PASSWORD:
        st.session_state.authenticated = True
        del st.session_state.password_input
    else:
        st.error("Incorrect password")

if not st.session_state.authenticated:
    st.title("🔒 Login Required")
    st.text_input("Enter Password", type="password", key="password_input", on_change=check_password)
    st.stop()

# --- HELPER FUNCTIONS ---

def get_exercise_code(exercise_str):
    if pd.isna(exercise_str) or exercise_str in ["Rest", "None", "No", ""]:
        return ""
    codes = []
    if "Lifting" in exercise_str: codes.append("L")
    if "Running" in exercise_str: codes.append("R")
    if "Rucking" in exercise_str: codes.append("K")
    if "Walking" in exercise_str: codes.append("W")
    if "Other" in exercise_str: codes.append("O")
    if not codes: return "✓" 
    return "+".join(codes)

# --- APP START ---
st.title("🛡️ Life Master Grid")

# --- SIDEBAR ---
with st.sidebar:
    st.header("📝 Log Today")
    
    if st.button("⚠️ Generate Sample Data"):
        dates = [datetime.now() - timedelta(days=x) for x in range(30)]
        data = []
        for d in dates:
            data.append({
                "Date": d.strftime("%Y-%m-%d"),
                "Sleep": np.random.randint(5, 9),
                "Energy": np.random.randint(1, 10),
                "Exercise": np.random.choice(["Lifting", "Running", "Rest", "Walking"]),
                "Stretching": np.random.choice(["Yes", "No"]),
                "Drinks": np.random.choice([0, 0, 0, 1, 2, 4]),
                "Meditation_Mins": np.random.choice([0, 10, 20, 0]),
                "Luck": np.random.choice(["Yes", "No"])
            })
        df_sample = pd.DataFrame(data)
        df_sample.to_csv(DATA_FILE, index=False)
        st.success("Sample data created!")
        st.rerun()

    with st.form("tracker_form", clear_on_submit=True):
        date = st.date_input("Date", datetime.now())
        
        st.subheader("💤 Sleep & Energy")
        sleep = st.number_input("Sleep Hours", 0.0, 24.0, 7.0, step=0.5)
        energy = st.slider("Energy Level", 1, 10, 5)
        
        st.subheader("🏋️ Physio")
        do_exercise = st.radio("Did you exercise?", ["No", "Yes"], horizontal=True, index=0)
        ex_type = []
        if do_exercise == "Yes":
            ex_type = st.multiselect("Type", ["Lifting", "Running", "Rucking", "Walking", "Other"])
        stretching = st.checkbox("Did you stretch?")
        
        st.subheader("🧘 Mind & Vices")
        meditation_mins = st.number_input("Meditation (mins)", min_value=0, step=1, value=0)
        drinks = st.number_input("Alcoholic Drinks", 0, 20, 0)
        luck = st.checkbox("Felt Lucky?")
        
        submitted = st.form_submit_button("Save Entry")
        
        if submitted:
            if do_exercise == "Yes":
                ex_str = ", ".join(ex_type) if ex_type else "Unspecified"
            else:
                ex_str = "Rest"

            new_entry = {
                "Date": date,
                "Sleep": sleep,
                "Energy": energy,
                "Exercise": ex_str,
                "Stretching": "Yes" if stretching else "No",
                "Drinks": drinks,
                "Meditation_Mins": meditation_mins,
                "Luck": "Yes" if luck else "No"
            }
            
            df_new = pd.DataFrame([new_entry])
            
            if not os.path.isfile(DATA_FILE):
                df_new.to_csv(DATA_FILE, index=False)
            else:
                df_new.to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.success("Saved!")
            st.rerun()

# --- MAIN GRID LOGIC ---
if os.path.isfile(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')

    # View Logic
    current_month_num = datetime.now().month
    df_view = df[df['Date'].dt.month == current_month_num].copy()
    
    if df_view.empty:
        st.info("No data found for this month.")
    else:
        # 1. PROCESS DATA FOR GRID
        df_view['Day'] = df_view['Date'].dt.day
        df_view['Drinks_Display'] = df_view['Drinks'].apply(lambda x: str(int(x)) if x > 0 else "")
        df_view['Exercise_Display'] = df_view['Exercise'].apply(get_exercise_code)
        
        # Retrofit columns if missing
        if 'Stretching' not in df_view.columns: df_view['Stretching'] = "No"
        if 'Meditation_Mins' not in df_view.columns: df_view['Meditation_Mins'] = 0
        
        df_view['Stretch_Display'] = df_view['Stretching'].apply(lambda x: "✓" if x == "Yes" else "")
        df_view['Meditation_Display'] = df_view['Meditation_Mins'].apply(lambda x: str(int(x)) if x > 0 else "")
        df_view['Luck_Display'] = df_view['Luck'].apply(lambda x: "🍀" if x == "Yes" else "")
        df_view['Sleep_Display'] = df_view['Sleep'].astype(str)

        pivot_data = df_view.set_index('Day')[['Sleep_Display', 'Exercise_Display', 'Stretch_Display', 'Drinks_Display', 'Meditation_Display', 'Luck_Display']]
        pivot_data.columns = ['Sleep', 'Exercise', 'Stretch', 'Drinks', 'Meditate', 'Luck']
        
        df_grid = pivot_data.T
        
        max_day = 31
        for d in range(1, max_day + 1):
            if d not in df_grid.columns: df_grid[d] = ""
        df_grid = df_grid.reindex(sorted(df_grid.columns), axis=1)

        # 2. STYLING FUNCTION
        def color_cells(val, row_name):
            base_style = "border: 1px solid #ddd; text-align: center;"
            if row_name == "Drinks":
                try:
                    if int(val) >= 3: return base_style + "background-color: #ffcccc; color: #cc0000;" 
                    if int(val) > 0: return base_style + "background-color: #fff4cc;" 
                    if val == "": return base_style + "background-color: #ccffcc;" 
                except: pass
            if row_name == "Exercise" and val != "":
                return base_style + "background-color: #ccffcc; color: #006600; font-weight: bold;"
            if row_name == "Stretch" and val == "✓":
                return base_style + "background-color: #e6f7ff; color: #0066cc; font-weight: bold;"
            if row_name == "Meditate":
                try:
                    if int(val) > 0: return base_style + "background-color: #e6ffff; color: #009999;" 
                except: pass
            if row_name == "Sleep":
                try:
                    s = float(val)
                    if s >= 7.5: return base_style + "background-color: #ccffcc;" 
                    if s < 6: return base_style + "background-color: #ffcccc;"
                except: pass
            return base_style

        # 3. RENDER GRID
        html = "<table style='width:100%;'><thead><tr><th style='background-color:white; border:none;'></th>"
        for col in df_grid.columns: html += f"<th>{col}</th>"
        html += "</tr></thead>"
        for idx, row in df_grid.iterrows():
            html += f"<tr><th style='text-align:right; padding-right:10px;'>{idx}</th>"
            for col in df_grid.columns:
                html += f"<td style='{color_cells(row[col], idx)}'>{row[col]}</td>"
            html += "</tr>"
        html += "</table>"
        st.write(html, unsafe_allow_html=True)
        
        st.divider()

        # --- 🤖 AI COACH GENERATOR ---
        st.subheader("🤖 AI Coach Output")
        st.caption("Copy this text and paste it into ChatGPT/Claude/Gemini for analysis.")
        
        # Construct the text prompt
        prompt_text = "I am tracking my daily habits. Here is my data for the last 30 days. \n"
        prompt_text += "Please act as a tough but encouraging lifestyle coach. Analyze the correlations between my Sleep, Alcohol, and Exercise.\n"
        prompt_text += "Spot patterns (e.g., 'Do I sleep worse when I drink?'). Here is the raw data:\n\n"
        
        # Convert dataframe to a clean text list
        # We use the raw 'df_view' so we have the actual numbers, not the display codes
        for index, row in df_view.iterrows():
            date_str = row['Date'].strftime('%b %d')
            ex_txt = row['Exercise']
            drink_txt = f"{row['Drinks']} Drinks"
            sleep_txt = f"{row['Sleep']}h Sleep"
            med_txt = f"{row['Meditation_Mins']}m Meditate"
            energy_txt = f"Energy: {row['Energy']}/10"
            stretch_txt = "Stretched" if row.get('Stretching') == "Yes" else "No Stretch"
            
            prompt_text += f"- {date_str}: {sleep_txt}, {drink_txt}, {ex_txt}, {stretch_txt}, {med_txt}, {energy_txt}\n"
            
        prompt_text += "\nBased on this, what is the #1 thing I should focus on improving next week?"
        
        st.code(prompt_text, language=None)

else:
    st.info("👋 Welcome! Log your first entry in the sidebar.")
