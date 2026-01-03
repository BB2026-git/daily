import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# --- CONFIGURATION ---
DATA_FILE = "life_metrics.csv"
MY_PASSWORD = "Irish02!!"

st.set_page_config(page_title="Life OS v10", page_icon="🛡️", layout="wide")

# --- CUSTOM CSS FOR THE GRID ---
st.markdown("""
<style>
    table { border-collapse: collapse; width: 100%; font-family: monospace; font-size: 13px; }
    th { background-color: #f0f2f6; padding: 4px; border: 1px solid #ddd; text-align: center; }
    td { padding: 4px; border: 1px solid #ddd; text-align: center; width: 32px; height: 32px; }
    tbody th {
        position: sticky; left: 0; background-color: #fff; z-index: 1;
        text-align: right; padding-right: 10px; min-width: 120px;
        border-right: 2px solid #ccc;
    }
</style>
""", unsafe_allow_html=True)

# --- AUTHENTICATION ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False

def check_password():
    if st.session_state.password_input == MY_PASSWORD:
        st.session_state.authenticated = True
        del st.session_state.password_input
    else: st.error("Incorrect password")

if not st.session_state.authenticated:
    st.title("🔒 Login Required")
    st.text_input("Enter Password", type="password", key="password_input", on_change=check_password)
    st.stop()

# --- HELPER FUNCTIONS ---
def get_exercise_code(exercise_str):
    # Returns "-" for explicit Rest so we can color it RED
    if exercise_str == "Rest" or exercise_str == "No": return "-"
    if pd.isna(exercise_str) or exercise_str == "": return ""
    
    codes = []
    if "Lifting" in exercise_str: codes.append("L")
    if "Running" in exercise_str: codes.append("R")
    if "Rucking" in exercise_str: codes.append("K")
    if "Walking" in exercise_str: codes.append("W")
    if "Other" in exercise_str: codes.append("O")
    return "+".join(codes) if codes else "✓"

def load_data():
    if not os.path.isfile(DATA_FILE): return pd.DataFrame()
    df = pd.read_csv(DATA_FILE)
    df['Date'] = pd.to_datetime(df['Date'])
    return df.sort_values('Date')

# --- APP START ---
st.title("🛡️ Life Operating System")

# --- SIDEBAR: LOGGING ---
with st.sidebar:
    st.header("📝 Daily Log")
    
    with st.form("tracker_form", clear_on_submit=True):
        date = st.date_input("Date", datetime.now())
        
        st.caption("💤 Physiology")
        sleep = st.number_input("Sleep Hours", 0.0, 24.0, 7.0, step=0.5)
        energy = st.slider("Energy (1-10)", 1, 10, 5)
        happiness = st.slider("Happiness (1-10)", 1, 10, 5)
        
        st.caption("🏋️ Movement")
        do_exercise = st.radio("Exercise?", ["No", "Yes"], horizontal=True, index=0)
        ex_type = []
        ex_time = "None"
        if do_exercise == "Yes":
            ex_type = st.multiselect("Type", ["Lifting", "Running", "Rucking", "Walking", "Other"])
            ex_time = st.selectbox("Time of Day", ["Morning", "Midday", "Evening"])
        stretching = st.checkbox("Stretching / Mobility?")
        
        st.caption("🥗 Wellness & Vices")
        c1, c2 = st.columns(2)
        with c1: headache = st.checkbox("Headache?")
        with c2: heartburn = st.checkbox("Heartburn?")
        
        heartburn_notes = ""
        if heartburn:
            heartburn_notes = st.text_input("Heartburn Triggers?", placeholder="e.g. Pizza at 9pm")
            
        st.text("Vitamins Taken:")
        v_d = st.checkbox("Vit D")
        v_m = st.checkbox("Multi")
        v_c = st.checkbox("Vit C")
        v_z = st.checkbox("Zinc")
        
        meditation_mins = st.number_input("Meditation (mins)", 0, 120, 0, step=1)
        drinks = st.number_input("Alcohol Drinks", 0, 20, 0)
        luck = st.checkbox("Felt Lucky?")
        
        submitted = st.form_submit_button("Save Entry")
        
        if submitted:
            if do_exercise == "Yes":
                ex_str = ", ".join(ex_type) if ex_type else "Unspecified"
            else:
                ex_str = "Rest"
            
            vits = []
            if v_d: vits.append("D")
            if v_m: vits.append("M")
            if v_c: vits.append("C")
            if v_z: vits.append("Z")
            vit_str = "+".join(vits) if vits else ""

            new_entry = {
                "Date": date,
                "Sleep": sleep,
                "Energy": energy,
                "Happiness": happiness,
                "Exercise": ex_str,
                "Exercise_Time": ex_time,
                "Stretching": "Yes" if stretching else "No",
                "Headache": "Yes" if headache else "No",
                "Heartburn": "Yes" if heartburn else "No",
                "Heartburn_Notes": heartburn_notes,
                "Vitamins": vit_str,
                "Drinks": drinks,
                "Meditation_Mins": meditation_mins,
                "Luck": "Yes" if luck else "No"
            }
            
            df_new = pd.DataFrame([new_entry])
            if not os.path.isfile(DATA_FILE):
                df_new.to_csv(DATA_FILE, index=False)
            else:
                df_new.to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.success("Entry Saved!")
            st.rerun()

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Master Grid", "🤖 AI Coach", "✏️ Manage Data"])

df = load_data()

# ==========================
# TAB 1: MASTER GRID
# ==========================
with tab1:
    if df.empty:
        st.info("No data yet. Log your first day in the sidebar!")
    else:
        current_month = datetime.now().month
        df_view = df[df['Date'].dt.month == current_month].copy()
        
        if df_view.empty:
            st.warning("No data for this month.")
        else:
            # Retrofit missing cols
            needed_cols = ['Happiness', 'Headache', 'Heartburn', 'Vitamins', 'Exercise_Time']
            for c in needed_cols:
                if c not in df_view.columns: df_view[c] = ""

            df_view['Day'] = df_view['Date'].dt.day
            
            # FORMATTING
            df_view['Sleep_D'] = df_view['Sleep'].astype(str)
            df_view['Energy_D'] = df_view['Energy'].astype(str)
            df_view['Happy_D'] = df_view['Happiness'].astype(str)
            
            df_view['Ex_D'] = df_view['Exercise'].apply(get_exercise_code)
            
            # Stretch: Yes -> "✓"
            df_view['Str_D'] = df_view['Stretching'].apply(lambda x: "✓" if x == "Yes" else "")
            
            # Meditate: Show minutes if > 0
            df_view['Med_D'] = df_view['Meditation_Mins'].apply(lambda x: str(int(x)) if x > 0 else "")
            
            df_view['Drinks_D'] = df_view['Drinks'].apply(lambda x: str(int(x)) if x > 0 else "")
            df_view['Head_D'] = df_view['Headache'].apply(lambda x: "H" if x == "Yes" else "")
            df_view['Burn_D'] = df_view['Heartburn'].apply(lambda x: "🔥" if x == "Yes" else "")
            df_view['Vit_D'] = df_view['Vitamins'].apply(lambda x: "💊" if pd.notna(x) and x != "" else "")

            cols_to_show = {
                'Sleep_D': 'Sleep',
                'Energy_D': 'Energy',
                'Happy_D': 'Happy',
                'Ex_D': 'Exercise',
                'Str_D': 'Stretch',
                'Drinks_D': 'Drinks',
                'Med_D': 'Meditate',
                'Head_D': 'Headache',
                'Burn_D': 'H-Burn',
                'Vit_D': 'Vits'
            }
            
            pivot_data = df_view.set_index('Day')[list(cols_to_show.keys())]
            pivot_data.rename(columns=cols_to_show, inplace=True)
            df_grid = pivot_data.T
            
            # Fill 1-31
            for d in range(1, 32):
                if d not in df_grid.columns: df_grid[d] = ""
            df_grid = df_grid.reindex(sorted(df_grid.columns), axis=1)

            # --- COLOR LOGIC ---
            def color_cells(val, row):
                style = "border: 1px solid #ddd; text-align: center;"
                
                # SLEEP (<=5 Red, 6-7 Yellow, >=8 Green)
                if row == "Sleep":
                    try:
                        s = float(val)
                        if s >= 8.0: return style + "background-color: #ccffcc; color: green;" # Green
                        if s <= 5.0: return style + "background-color: #ffcccc; color: red; font-weight: bold;" # Red
                        return style + "background-color: #fff4cc;" # Yellow (Everything else)
                    except: pass
                
                # ENERGY & HAPPY (<=3 Red, 4-6 Yellow, >=7 Green)
                if row in ["Energy", "Happy"]:
                    try:
                        v = float(val)
                        if v >= 7: return style + "background-color: #ccffcc; color: green;"
                        if v <= 3: return style + "background-color: #ffcccc; color: red; font-weight: bold;"
                        return style + "background-color: #fff4cc;" # Yellow
                    except: pass
                
                # EXERCISE (Red if "-", Green if Letters)
                if row == "Exercise":
                    if val == "-": return style + "background-color: #ffcccc; color: red; font-weight: bold;"
                    if val != "": return style + "background-color: #ccffcc; color: green; font-weight: bold;"
                
                # MEDITATE (Green if > 0)
                if row == "Meditate":
                    try:
                        if int(val) >= 1: return style + "background-color: #ccffcc; color: green;"
                    except: pass

                # STRETCH (Green if checked)
                if row == "Stretch" and val == "✓":
                    return style + "background-color: #ccffcc; color: green; font-weight: bold;"
                
                # HEADACHE (Red if H)
                if row == "Headache" and val == "H":
                    return style + "background-color: #ffcccc; color: red; font-weight: bold;"
                
                # HEARTBURN (Red if Fire)
                if row == "H-Burn" and val == "🔥":
                    return style + "background-color: #ffcccc; color: red;"

                # DRINKS (Existing Logic)
                if row == "Drinks":
                    try:
                        if int(val) >= 3: return style + "background-color: #ffcccc; color: #cc0000;"
                        if int(val) > 0: return style + "background-color: #fff4cc;"
                    except: pass
                
                return style

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

# ==========================
# TAB 2: AI COACH
# ==========================
with tab2:
    st.subheader("🧠 Deep Analysis Prompt")
    if df.empty:
        st.text("No data to analyze.")
    else:
        prompt = "I am tracking my health. Act as a data scientist and life coach.\n"
        prompt += "Analyze my daily logs for correlations:\n"
        prompt += "1. Triggers for Heartburn or Headache?\n"
        prompt += "2. Impact of Vitamin intake, Exercise Time, and Alcohol on my Energy and Sleep?\n"
        prompt += "DATA LOG:\n"
        
        df_ai = df.tail(30).copy()
        for c in ['Heartburn_Notes', 'Exercise_Time', 'Vitamins', 'Happiness', 'Headache']:
            if c not in df_ai.columns: df_ai[c] = "-"
            
        for i, row in df_ai.iterrows():
            d = row['Date'].strftime('%Y-%m-%d')
            s = f"Sleep:{row['Sleep']}h"
            e = f"Energy:{row['Energy']}/10"
            h = f"Happy:{row['Happiness']}/10"
            ex = f"Ex:{row['Exercise']} ({row['Exercise_Time']})" if row['Exercise'] != 'Rest' else "No Ex"
            dr = f"Drinks:{row['Drinks']}"
            vit = f"Vits:{row['Vitamins']}" if row['Vitamins'] else "No Vits"
            med = f"Med:{row['Meditation_Mins']}m"
            
            issues = []
            if row['Headache'] == "Yes": issues.append("HEADACHE")
            if row['Heartburn'] == "Yes": issues.append(f"HEARTBURN ({row['Heartburn_Notes']})")
            issue_str = " | ".join(issues) if issues else "No Pain"
            
            prompt += f"[{d}] {s}, {e}, {h}, {ex}, {dr}, {med}, {vit}, {issue_str}\n"
            
        prompt += "\nGive me 3 actionable insights to improve Happiness and Sleep."
        st.code(prompt, language=None)

# ==========================
# TAB 3: MANAGE DATA
# ==========================
with tab3:
    st.subheader("✏️ Edit / Delete Entries")
    if not df.empty:
        df_edit = df.sort_values('Date', ascending=False).reset_index(drop=True)
        edited_df = st.data_editor(df_edit, num_rows="dynamic", use_container_width=True, key="editor")
        if st.button("💾 Save Changes to CSV"):
            edited_df.to_csv(DATA_FILE, index=False)
            st.success("Database updated!")
            st.rerun()
    else:
        st.info("No data to edit.")
