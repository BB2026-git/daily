import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- CONFIGURATION ---
DATA_FILE = "life_metrics.csv"
# *** SECURITY: CHANGE THIS PASSWORD ***
MY_PASSWORD = "Irish02" 

# --- PAGE SETUP ---
st.set_page_config(page_title="My Life OS", page_icon="🛡️", layout="wide")

# --- AUTHENTICATION (PASSWORD CHECK) ---
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
    st.stop()  # Stop code execution here until logged in

# --- APP BEGINS HERE (Only runs if password is correct) ---
st.title("🛡️ Life Operating System")

# --- SIDEBAR: NEW ENTRY ---
with st.sidebar:
    st.header("📝 Log Today")
    with st.form("tracker_form", clear_on_submit=True):
        
        # Date Logic
        date = st.date_input("Date", datetime.now())
        st.caption(f"Logging for: {date.strftime('%A, %B %d')}")
        
        # 1. SLEEP (Clarified)
        st.subheader("💤 Sleep")
        st.caption("Sleep logged today = The sleep you got last night.")
        sleep_hours = st.number_input("Hours Slept", 0.0, 24.0, 7.0, step=0.5)
        sleep_quality = st.selectbox("Quality", ["Good", "Neutral", "Bad"])
        
        # 2. VITALITY & HEALTH
        st.subheader("⚡ Vitality & Health")
        happiness = st.slider("Happiness (1-10)", 1, 10, 7)
        energy_level = st.slider("Energy (1-10)", 1, 10, 5)
        headache = st.checkbox("Headache today?")
        
        st.markdown("**Vitamins Taken:**")
        c1, c2, c3, c4 = st.columns(4)
        vit_d = c1.checkbox("Vit D")
        vit_m = c2.checkbox("Multi")
        vit_c = c3.checkbox("Vit C")
        vit_z = c4.checkbox("Zinc")
        
        st.markdown("**Gut Health:**")
        heartburn = st.checkbox("Heartburn?")
        heartburn_notes = st.text_input("Heartburn Triggers (Food/Time)", disabled=not heartburn, placeholder="e.g., Pizza at 8pm")

        # 3. PHYSIO
        st.subheader("🏋️ Physio")
        exercise_done = st.radio("Did you exercise?", ["Yes", "No / Rest Day"], horizontal=True)
        
        # Logic to hide details if Rest Day
        is_exercise = (exercise_done == "Yes")
        exercise_time = st.selectbox("Time of Day", ["Morning", "Midday", "Evening"], disabled=not is_exercise)
        exercise_type = st.multiselect("Type", ["Lifting", "Running", "Rucking", "Walking", "Other"], disabled=not is_exercise)
        stretching = st.checkbox("Stretching?")

        # 4. LIFESTYLE
        st.subheader("🍸 Lifestyle")
        drinks = st.number_input("Alcoholic Drinks", min_value=0, step=1)
        luck = st.checkbox("Did you feel 'Lucky' today?")

        # 5. MIND
        st.subheader("🧘 Mind")
        meditate = st.checkbox("Did you meditate?")
        # Step=1 allows 1 minute increments
        meditate_min = st.number_input("Minutes", min_value=0, step=1, disabled=not meditate)
        gratitude = st.text_input("Gratitude (One sentence)")
        
        submitted = st.form_submit_button("Save Entry")

        if submitted:
            # Combine Vitamins into string
            vits = []
            if vit_d: vits.append("D")
            if vit_m: vits.append("Multi")
            if vit_c: vits.append("C")
            if vit_z: vits.append("Zinc")
            vits_str = ", ".join(vits) if vits else "None"
            
            # Combine Exercise
            if not is_exercise:
                ex_final = "Rest"
                time_final = "N/A"
            else:
                ex_final = ", ".join(exercise_type) if exercise_type else "Unspecified"
                time_final = exercise_time

            new_entry = {
                "Date": date,
                "Sleep Hours": sleep_hours,
                "Sleep Quality": sleep_quality,
                "Happiness": happiness,
                "Energy": energy_level,
                "Headache": headache,
                "Vitamins": vits_str,
                "Heartburn": heartburn,
                "Heartburn Notes": heartburn_notes if heartburn else "N/A",
                "Exercise": ex_final,
                "Workout Time": time_final,
                "Stretching": stretching,
                "Drinks": drinks,
                "Meditate Min": meditate_min if meditate else 0,
                "Gratitude": gratitude,
                "Luck": luck
            }
            
            df_new = pd.DataFrame([new_entry])
            
            if not os.path.isfile(DATA_FILE):
                df_new.to_csv(DATA_FILE, index=False)
            else:
                df_new.to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.success("Saved!")
            st.rerun() # Force refresh to show new data immediately

# --- MAIN DASHBOARD TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Data Manager", "🤖 AI Coach Prep", "📈 Trends"])

# --- TAB 1: DATA MANAGER (EDIT/DELETE) ---
with tab1:
    st.subheader("🗂️ View & Edit Data")
    if os.path.isfile(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df['Date'] = pd.to_datetime(df['Date']).dt.date # format date cleanly
        
        # EDITABLE DATAFRAME
        edited_df = st.data_editor(
            df, 
            num_rows="dynamic", # Allow adding/deleting rows
            use_container_width=True,
            key="editor"
        )
        
        # Save Button
        if st.button("💾 Save Changes to CSV"):
            edited_df.to_csv(DATA_FILE, index=False)
            st.success("Database updated successfully!")
    else:
        st.info("No data yet. Log your first day in the sidebar!")

# --- TAB 2: AI COACH PREP ---
with tab2:
    st.subheader("🤖 AI Analysis Prompt")
    st.write("Click the button below to generate a report. Copy it and paste it into ChatGPT/Gemini for personalized coaching.")
    
    if os.path.isfile(DATA_FILE) and len(df) > 0:
        if st.button("Generate Coach Report"):
            # Prepare summary stats
            avg_sleep = df['Sleep Hours'].mean()
            avg_happy = df['Happiness'].mean()
            total_drinks = df['Drinks'].sum()
            workouts = len(df[df['Exercise'] != "Rest"])
            
            # Get last 7 entries as text
            recent_data = df.tail(7).to_string()
            
            # Create the Prompt
            prompt = f"""
I need you to act as my Life Coach. Analyze my data from the last week and give me 3 specific observations and 1 actionable piece of advice for next week.

**My Stats:**
- Average Sleep: {avg_sleep:.1f} hours
- Average Happiness: {avg_happy:.1f}/10
- Total Alcohol: {total_drinks} drinks
- Workouts: {workouts}

**Detailed Logs (Last 7 Days):**
{recent_data}

**Focus on:** 1. The relationship between my sleep, alcohol, and happiness.
2. If my workouts are consistent.
3. Any patterns causing heartburn or headaches.
            """
            st.code(prompt, language="text")
    else:
        st.warning("Log some data first!")

# --- TAB 3: TRENDS ---
with tab3:
    if os.path.isfile(DATA_FILE) and len(df) > 0:
        st.subheader("Mood vs. Habits")
        
        # Simple Chart
        chart_data = df.set_index("Date")[['Happiness', 'Energy', 'Sleep Hours']]
        st.line_chart(chart_data)
        
        # Heartburn Analysis
        if df['Heartburn'].sum() > 0:
            st.subheader("🔥 Heartburn Tracker")
            st.write("Recent triggers:")
            st.dataframe(df[df['Heartburn'] == True][['Date', 'Heartburn Notes', 'Drinks']])
    else:
        st.write("Trends will appear here once you have data.")