import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# --- CONFIGURATION ---
DATA_FILE = "life_metrics.csv"
MY_PASSWORD = "Irish02!!"  # <--- REMEMBER TO CHANGE THIS IF NEEDED

# --- PAGE SETUP ---
st.set_page_config(page_title="Life OS", page_icon="🛡️", layout="wide")

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
    """Returns a single letter code for the calendar."""
    if pd.isna(exercise_str) or exercise_str == "Rest":
        return ""
    if "Lifting" in exercise_str: return "L"
    if "Running" in exercise_str: return "R"
    if "Rucking" in exercise_str: return "K"
    if "Walking" in exercise_str: return "W"
    return "O" # Other

# --- APP BEGINS ---
st.title("🛡️ Life Operating System")

# --- SIDEBAR: LOGGING ---
with st.sidebar:
    st.header("📝 Log Today")
    with st.form("tracker_form", clear_on_submit=True):
        date = st.date_input("Date", datetime.now())
        st.caption(f"Logging for: {date.strftime('%A, %B %d')}")
        
        # SLEEP
        st.subheader("💤 Sleep")
        st.caption("Last night's sleep:")
        sleep_hours = st.number_input("Hours", 0.0, 24.0, 7.0, step=0.5)
        sleep_quality = st.selectbox("Quality", ["Good", "Neutral", "Bad"])
        
        # HEALTH
        st.subheader("⚡ Vitality")
        happiness = st.slider("Happiness", 1, 10, 7)
        energy_level = st.slider("Energy", 1, 10, 5)
        headache = st.checkbox("Headache?")
        
        st.markdown("**Vitamins:**")
        c1, c2, c3, c4 = st.columns(4)
        vit_d = c1.checkbox("D"); vit_m = c2.checkbox("Multi"); vit_c = c3.checkbox("C"); vit_z = c4.checkbox("Zn")
        
        heartburn = st.checkbox("Heartburn?")
        heartburn_notes = st.text_input("Triggers", disabled=not heartburn)

        # PHYSIO
        st.subheader("🏋️ Physio")
        exercise_done = st.radio("Exercise?", ["Yes", "No / Rest"], horizontal=True)
        is_exercise = (exercise_done == "Yes")
        exercise_time = st.selectbox("Time", ["Morning", "Midday", "Evening"], disabled=not is_exercise)
        exercise_type = st.multiselect("Type", ["Lifting", "Running", "Rucking", "Walking", "Other"], disabled=not is_exercise)
        stretching = st.checkbox("Stretching?")

        # LIFESTYLE
        st.subheader("🍸 Lifestyle")
        drinks = st.number_input("Alcohol Drinks", min_value=0, step=1)
        luck = st.checkbox("Felt Lucky?")
        
        # MIND
        st.subheader("🧘 Mind")
        meditate = st.checkbox("Meditated?")
        meditate_min = st.number_input("Minutes", min_value=0, step=1, disabled=not meditate)
        gratitude = st.text_input("Gratitude")
        
        submitted = st.form_submit_button("Save Entry")

        if submitted:
            # Process Data
            vits = [n for n, v in [("D", vit_d), ("Multi", vit_m), ("C", vit_c), ("Zinc", vit_z)] if v]
            vits_str = ", ".join(vits) if vits else "None"
            
            ex_final = ", ".join(exercise_type) if (is_exercise and exercise_type) else "Rest"
            time_final = exercise_time if is_exercise else "N/A"

            new_entry = {
                "Date": date,
                "Sleep Hours": sleep_hours, "Sleep Quality": sleep_quality,
                "Happiness": happiness, "Energy": energy_level,
                "Headache": headache, "Vitamins": vits_str,
                "Heartburn": heartburn, "Heartburn Notes": heartburn_notes if heartburn else "N/A",
                "Exercise": ex_final, "Workout Time": time_final, "Stretching": stretching,
                "Drinks": drinks, "Meditate Min": meditate_min if meditate else 0,
                "Gratitude": gratitude, "Luck": luck
            }
            
            df_new = pd.DataFrame([new_entry])
            
            if not os.path.isfile(DATA_FILE):
                df_new.to_csv(DATA_FILE, index=False)
            else:
                df_new.to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.success("Saved!")
            st.rerun()

# --- DASHBOARD TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["🗓️ Calendar View", "📊 Data Manager", "🤖 AI Coach", "📈 Trends"])

# --- TAB 1: CALENDAR HEATMAP ---
with tab1:
    st.subheader("Month at a Glance")
    
    if os.path.isfile(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Filter for current month view (or all time)
        # For simplicity, we show the last 30 days or handle it via Plotly logic
        
        # VIEW SELECTOR
        view_option = st.selectbox("Select Lens:", ["Alcohol & Vices", "Exercise & Physio", "Sleep & Energy"])
        
        # Prepare Data for Heatmap
        # We need to map Date -> Day of Week (x) and Week Number (y)
        df = df.sort_values("Date")
        
        # Create a full date range to ensure the calendar looks square (handle missing days)
        if not df.empty:
            full_range = pd.date_range(start=df['Date'].min(), end=df['Date'].max(), freq='D')
            df_cal = df.set_index('Date').reindex(full_range).reset_index()
            df_cal = df_cal.rename(columns={'index': 'Date'})
        else:
            df_cal = df

        # Calculate coordinates
        df_cal['Week'] = df_cal['Date'].dt.isocalendar().week
        df_cal['Day'] = df_cal['Date'].dt.weekday # 0=Mon, 6=Sun
        df_cal['Day Name'] = df_cal['Date'].dt.strftime('%a')
        df_cal['Date Str'] = df_cal['Date'].dt.strftime('%b %d')

        # Logic for each View
        if view_option == "Alcohol & Vices":
            z_data = df_cal['Drinks'].fillna(0)
            text_data = df_cal['Drinks'].apply(lambda x: str(int(x)) if x > 0 else "")
            colors = 'Reds' # Red scale
            title = "Alcohol Intake (Red = Drank)"
            
        elif view_option == "Exercise & Physio":
            # Map exercise strings to 1 (green) or 0 (white)
            z_data = df_cal['Exercise'].apply(lambda x: 0 if (pd.isna(x) or x == "Rest") else 1)
            # Get the code letter
            text_data = df_cal['Exercise'].apply(get_exercise_code)
            colors = 'Greens'
            title = "Workout Consistency (Letter = Type)"
            
        elif view_option == "Sleep & Energy":
            z_data = df_cal['Sleep Hours'].fillna(0)
            text_data = df_cal['Sleep Hours'].apply(lambda x: str(x) if x > 0 else "")
            colors = 'Blues'
            title = "Sleep Duration (Darker = More)"

        # PLOTLY HEATMAP
        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=df_cal['Day Name'],
            y=df_cal['Week'],
            text=text_data,
            texttemplate="%{text}", # Show the text inside the square
            textfont={"size": 14, "color": "grey"}, # visible on dark or light
            colorscale=colors,
            xgap=3, # space between squares
            ygap=3,
            showscale=False
        ))

        fig.update_layout(
            title=title,
            height=400,
            yaxis=dict(title="Week #", dtick=1, autorange="reversed"), # Weeks go down
            xaxis=dict(side="top") # Days on top
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Log data to see the calendar!")

# --- TAB 2: DATA MANAGER ---
with tab2:
    if os.path.isfile(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        if st.button("💾 Save Changes"):
            edited_df.to_csv(DATA_FILE, index=False)
            st.success("Updated!")

# --- TAB 3: AI COACH ---
with tab3:
    st.subheader("🤖 Coach Prompt Generator")
    if os.path.isfile(DATA_FILE):
        if st.button("Create Report"):
            df = pd.read_csv(DATA_FILE)
            recent = df.tail(14).to_string() # Last 14 days
            stats = df.describe().to_string()
            
            prompt = f"""
            Act as my Life Coach. Here is my last 14 days of data:
            {recent}
            
            Aggregate Stats:
            {stats}
            
            Analyze:
            1. My Sleep vs Alcohol correlation.
            2. Workout consistency (I want to lift 3x/week).
            3. Identify any 'Red Flag' days where I crashed.
            """
            st.code(prompt, language="text")

# --- TAB 4: TRENDS ---
with tab4:
    if os.path.isfile(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        st.line_chart(df.set_index("Date")[['Energy', 'Happiness', 'Sleep Hours']])
