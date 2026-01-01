import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURATION ---
DATA_FILE = "life_metrics.csv"
MY_PASSWORD = "Irish02!!"  # <--- PASSWORD

# --- PAGE SETUP ---
st.set_page_config(page_title="Life Master Grid", page_icon="🛡️", layout="wide")

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

# --- HELPER: GET EXERCISE LETTER ---
def get_exercise_code(exercise_str):
    if pd.isna(exercise_str) or exercise_str == "Rest" or exercise_str == "None":
        return ""
    codes = []
    if "Lifting" in exercise_str: codes.append("L")
    if "Running" in exercise_str: codes.append("R")
    if "Rucking" in exercise_str: codes.append("K")
    if "Walking" in exercise_str: codes.append("W")
    if "Other" in exercise_str: codes.append("O")
    return "+".join(codes) if codes else "✓"

# --- COLORING LOGIC FOR THE GRID ---
def color_grid(val):
    """
    This function looks at the value in a cell and decides the background color.
    Format: 'attribute: value'
    """
    color = ''
    try:
        # HANDLING NUMBERS (Sleep, Drinks, etc)
        if isinstance(val, (int, float)):
            return '' # Let numbers handle themselves below if needed, or specific logic
    except:
        pass
    
    # We use a trick: The cell value will carry the meaning. 
    # But for a pandas style, we need to know WHICH row we are in.
    # Since we can't easily know the row index inside this simple function,
    # we will apply styling differently below.
    return ''

# --- APP BEGINS ---
st.title("🛡️ Life Master Grid")

# --- SIDEBAR: LOGGING (SAME AS BEFORE) ---
with st.sidebar:
    st.header("📝 Log Today")
    with st.form("tracker_form", clear_on_submit=True):
        date = st.date_input("Date", datetime.now())
        st.caption(f"Log for: {date.strftime('%b %d')}")
        
        st.subheader("💤 Sleep & Health")
        sleep_hours = st.number_input("Sleep Hours", 0.0, 24.0, 7.0, step=0.5)
        energy_level = st.slider("Energy (1-10)", 1, 10, 5)
        
        st.subheader("🏋️ Physio")
        exercise_done = st.radio("Exercise?", ["Yes", "No / Rest"], horizontal=True)
        is_ex = (exercise_done == "Yes")
        ex_type = st.multiselect("Type", ["Lifting", "Running", "Rucking", "Walking", "Other"], disabled=not is_ex)
        
        st.subheader("🍸 Vices & Mind")
        drinks = st.number_input("Drinks", min_value=0, step=1)
        meditate = st.checkbox("Meditated?")
        luck = st.checkbox("Felt Lucky?")
        
        submitted = st.form_submit_button("Save Entry")

        if submitted:
            ex_final = ", ".join(ex_type) if (is_ex and ex_type) else "Rest"
            
            new_entry = {
                "Date": date,
                "Sleep": sleep_hours,
                "Energy": energy_level,
                "Exercise": ex_final,
                "Drinks": drinks,
                "Meditate": "Yes" if meditate else "No",
                "Luck": "Yes" if luck else "No"
            }
            
            df_new = pd.DataFrame([new_entry])
            if not os.path.isfile(DATA_FILE):
                df_new.to_csv(DATA_FILE, index=False)
            else:
                df_new.to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.success("Saved!")
            st.rerun()

# --- MAIN DASHBOARD: THE MASTER GRID ---
if os.path.isfile(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Filter to Current Month (Optional: Add a month selector later)
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # 1. PREPARE THE DATA FRAME FOR THE GRID
    # We want Columns = Day of Month (1, 2, 3...)
    # We want Rows = Metrics
    
    # Create a full range of days for the current month so the grid isn't empty
    # (Simplified: Just showing last 30 days or current month days)
    # Let's do: All dates in the file, sorted.
    
    # Pivot logic:
    df['Day'] = df['Date'].dt.day
    df['MonthStr'] = df['Date'].dt.strftime('%B')
    
    # We filter for the LATEST month in the data to keep it clean
    latest_month = df['Date'].dt.month.max()
    df_view = df[df['Date'].dt.month == latest_month].copy()
    
    # Process specific columns for display
    # Exercise -> Letters
    df_view['Exercise'] = df_view['Exercise'].apply(get_exercise_code)
    # Drinks -> Empty string if 0 (to clean up grid)
    df_view['Drinks'] = df_view['Drinks'].apply(lambda x: str(int(x)) if x > 0 else "")
    # Meditate -> M if yes
    df_view['Meditate'] = df_view['Meditate'].apply(lambda x: "M" if x == "Yes" else "")
    # Luck -> 🍀 if yes
    df_view['Luck'] = df_view['Luck'].apply(lambda x: "🍀" if x == "Yes" else "")

    # Set Index to Date/Day so we can pivot
    df_pivot = df_view.set_index('Day')[['Sleep', 'Energy', 'Exercise', 'Drinks', 'Meditate', 'Luck']]
    
    # Transpose: Now Rows = Metrics, Columns = Days
    df_grid = df_pivot.T
    
    st.subheader(f"📅 {datetime.now().strftime('%B')} Grid")
    
    # --- STYLING THE GRID (The "Excel" Look) ---
    def style_master_grid(val):
        """
        Dynamic CSS styling based on values.
        Returns a string like 'background-color: red; color: white'
        """
        style = 'text-align: center; border: 1px solid #eee;' # Default
        
        str_val = str(val)
        
        # DRINKS (Red if high)
        if str_val.isdigit() and int(str_val) >= 3: 
             return style + 'background-color: #ffcccc; color: #cc0000; font-weight: bold;'
        if str_val.isdigit() and int(str_val) > 0: 
             return style + 'background-color: #fff4cc;' # Yellowish
             
        # EXERCISE (Green Letters)
        if any(x in str_val for x in ['L', 'R', 'W', 'K']):
            return style + 'background-color: #ccffcc; color: #006600; font-weight: bold;'
            
        # SLEEP (Red if low, Green if high)
        try:
            f_val = float(str_val)
            if f_val < 6.0: return style + 'background-color: #ffcccc;' # Red
            if f_val >= 7.5: return style + 'background-color: #ccffcc;' # Green
        except:
            pass
            
        # LUCK
        if "🍀" in str_val:
            return style + 'background-color: #e6f7ff;' # Light Blue
            
        return style

    # Apply the styling
    styled_df = df_grid.style.applymap(style_master_grid)
    
    # Render as a static HTML table (looks best for this specific grid view)
    st.write(styled_df.to_html(), unsafe_allow_html=True)

    st.divider()
    
    # --- TRENDS & RAW DATA ---
    t1, t2 = st.tabs(["📈 Trends", "💾 Edit Data"])
    
    with t1:
        st.line_chart(df.set_index("Date")[['Energy', 'Sleep']])
        
    with t2:
        edited = st.data_editor(df, num_rows="dynamic")
        if st.button("Save Changes"):
            edited.to_csv(DATA_FILE, index=False)
            st.success("Updated")

else:
    st.info("👋 Welcome! Log your first day in the sidebar to see the Grid.")

