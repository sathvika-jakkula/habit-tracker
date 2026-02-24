"""
🏆 Habit Tracker - Streamlit Application
Run with: streamlit run habit_tracker.py
Requirements: pip install streamlit plotly pandas
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta, datetime
import json
import os
try:
    from streamlit_gsheets import GSheetsConnection
except ImportError:
    GSheetsConnection = None

# ─────────────────────────────────────────────
# Config & Page Setup
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Habit Tracker",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Sidebar Navigation
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧭 Navigation")
    current_tab = st.radio(
        "Menu",
        ["📅  Today's Dashboard", "📊  History & Filters", "💻  DSA Tracker", "📝  Daily Notes", "⚙️  Manage Habits"],
        label_visibility="collapsed"
    )

# Static Light Theme Colors
t_bg = "#f4f4f9"
t_text = "#1a1a2e"
t_card_bg1 = "#ffffff"
t_card_bg2 = "#f8f9fa"
t_card_border = "#e9ecef"
t_text_muted = "#6c757d"
t_stat_bg = "#eef2f5"
t_input_bg = "#ffffff"

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
    /* Main background */
    .stApp {{ background-color: {t_bg}; color: {t_text}; }}

    /* Radio Nav styling (acts like tabs) */
    .stRadio > div {{
        gap: 8px;
    }}
    .stRadio label {{
        padding: 10px 15px;
        background: {t_card_bg1};
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
        border: 1px solid {t_card_border};
    }}
    .stRadio label:hover {{
        background: {t_card_bg2};
    }}

    /* Cards */
    .habit-card {{
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(240,240,245,0.95) 100%);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba( 31, 38, 135, 0.15 );
        border: 1px solid {t_card_border};
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 14px;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        color: {t_text};
    }}
    .habit-card:hover {{
        transform: translateY(-4px) scale(1.01);
        box-shadow: 0 12px 40px 0 rgba(108, 99, 255, 0.25);
        border-color: #6c63ff;
    }}

    .stat-card {{
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(240,245,255,0.9) 100%);
        box-shadow: 0 4px 20px 0 rgba(31, 38, 135, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid {t_card_border};
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        transition: transform 0.3s ease;
    }}
    .stat-card:hover {{
        transform: translateY(-2px);
    }}
    .stat-number {{ font-size: 2.8rem; font-weight: 800; color: #6c63ff; }}
    .stat-label {{ font-size: 0.85rem; color: {t_text_muted}; text-transform: uppercase; letter-spacing: 1px; }}

    .streak-badge {{
        display: inline-block;
        background: linear-gradient(90deg, #f7971e, #ffd200);
        color: #1a1a2e;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.85rem;
        font-weight: 700;
    }}

    /* Buttons */
    .stButton > button {{
        border-radius: 10px;
        font-weight: 600;
        border: none;
        transition: all 0.2s;
    }}
    .stButton > button:hover {{ transform: translateY(-1px); box-shadow: 0 4px 15px rgba(108,99,255,0.3); }}

    /* Inputs */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stTextArea > div > div > textarea {{
        background-color: {t_input_bg};
        border: 1px solid {t_card_border};
        color: {t_text};
        border-radius: 10px;
    }}

    /* Progress bar */
    .progress-container {{
        background: {t_card_border};
        border-radius: 10px;
        height: 10px;
        margin-top: 8px;
    }}
    .progress-fill {{
        height: 10px;
        border-radius: 10px;
        background: linear-gradient(90deg, #6c63ff, #a78bfa);
    }}

    /* Checkmark animation */
    .done-badge {{
        display: inline-block;
        background: #e6f4ea;
        color: #1e8e3e;
        border: 1px solid #1e8e3e;
        border-radius: 8px;
        padding: 2px 10px;
        font-size: 0.8rem;
        font-weight: 700;
    }}
    .pending-badge {{
        display: inline-block;
        background: {t_card_bg1};
        color: {t_text_muted};
        border: 1px solid {t_card_border};
        border-radius: 8px;
        padding: 2px 10px;
        font-size: 0.8rem;
    }}

    h1, h2, h3, h4, h5, h6, label, p, div {{ color: {t_text} !important; }}
    
    .section-title {{
        font-size: 1.3rem;
        font-weight: 700;
        color: #a78bfa !important;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 1px solid {t_card_border};
    }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Data Persistence (JSON file)
# ─────────────────────────────────────────────
DATA_FILE = "habit_data.json"

DEFAULT_DATA = {
    "habits": [
        {"id": 1, "name": "Morning Workout", "icon": "💪", "category": "Health", "target_days": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"], "color": "#6c63ff", "created": str(date.today() - timedelta(days=30))},
        {"id": 2, "name": "Read 30 Minutes",  "icon": "📚", "category": "Learning", "target_days": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"], "color": "#f7971e", "created": str(date.today() - timedelta(days=20))},
        {"id": 3, "name": "Drink 8 Glasses",  "icon": "💧", "category": "Health", "target_days": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"], "color": "#06b6d4", "created": str(date.today() - timedelta(days=15))},
        {"id": 4, "name": "Meditate",          "icon": "🧘", "category": "Wellness", "target_days": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"], "color": "#ec4899", "created": str(date.today() - timedelta(days=10))},
    ],
    "completions": {},  # {"YYYY-MM-DD": {"habit_id": {"time": "", "mode": "", "notes": "", "helped": ""}}}
    "dsa_problems": [], # [{"id": 1, "name": "Two Sum", "url": "https://...", "difficulty": "Easy", "status": "open", "completed_on": None}]
    "daily_notes": []   # [{"date": "YYYY-MM-DD", "note": "..."}]
}

def get_gsheets_conn():
    if GSheetsConnection is None:
        return None
    try:
        # Avoid crashing if secrets are unconfigured by checking secrets keys
        if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            return st.connection("gsheets", type=GSheetsConnection)
    except Exception:
        pass
    return None

def load_data():
    conn = get_gsheets_conn()
    if conn is not None:
        try:
            habits_df = conn.read(worksheet="habits", ttl=0)
            completions_df = conn.read(worksheet="completions", ttl=0)
            dsa_df = conn.read(worksheet="dsa_problems", ttl=0)

            # Parse habits
            habits = []
            if not habits_df.empty:
                for _, row in habits_df.iterrows():
                    if pd.isna(row.get("id")): continue # Skip empty rows
                    h = row.to_dict()
                    h["target_days"] = str(h["target_days"]).split(",") if pd.notna(h.get("target_days")) and h["target_days"] else []
                    h["id"] = int(h["id"])
                    if pd.isna(h.get("icon")): h["icon"] = "⭐"
                    habits.append(h)

            # Parse completions
            completions = {}
            if not completions_df.empty:
                for _, row in completions_df.iterrows():
                    d = str(row["date"])
                    if pd.isna(row.get("habit_id")) or d == "nan": continue
                    hid = str(int(row["habit_id"])) if isinstance(row["habit_id"], float) else str(row["habit_id"])
                    
                    if d not in completions:
                        completions[d] = {}
                    completions[d][hid] = {
                        "duration": str(row["duration"]) if pd.notna(row.get("duration")) else "",
                        "mode": str(row["mode"]) if pd.notna(row.get("mode")) else "",
                        "notes": str(row["notes"]) if pd.notna(row.get("notes")) else "",
                        "helped": str(row["helped"]) if pd.notna(row.get("helped")) else ""
                    }

            # Parse DSA
            dsa = []
            if not dsa_df.empty:
                for _, row in dsa_df.iterrows():
                    if pd.isna(row.get("id")): continue
                    p = row.to_dict()
                    p["id"] = int(p["id"])
                    if pd.isna(p.get("url")): p["url"] = ""
                    if pd.isna(p.get("completed_on")): p["completed_on"] = None
                    dsa.append(p)

            # Parse Daily Notes
            daily_notes = []
            try:
                notes_df = conn.read(worksheet="daily_notes", ttl=0)
                if not notes_df.empty:
                    for _, row in notes_df.iterrows():
                        if pd.isna(row.get("date")): continue
                        daily_notes.append({
                            "date": str(row["date"]),
                            "note": str(row["note"]) if pd.notna(row.get("note")) else ""
                        })
            except Exception:
                pass # Accept missing worksheet temporarily for backward compatibility
            
            return {"habits": habits, "completions": completions, "dsa_problems": dsa, "daily_notes": daily_notes}
            
        except Exception as e:
            st.warning(f"Google Sheets connection issue: {e}. Falling back to local JSON storage.")
            pass # Fallback to JSON below
            
    # --- FALLBACK: Load from local JSON ---
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            migrated = False
            for day, comps in data.get("completions", {}).items():
                if isinstance(comps, list):
                    data["completions"][day] = {str(hid): {} for hid in comps}
                    migrated = True
            if "dsa_problems" not in data:
                data["dsa_problems"] = []
                migrated = True
            if "daily_notes" not in data:
                data["daily_notes"] = []
                migrated = True
            if migrated:
                save_data(data)
            return data
            
    # Use default habits but start with no completions
    data = DEFAULT_DATA.copy()
    data["completions"] = {}
    data["dsa_problems"] = []
    data["daily_notes"] = []
    # Save it first
    save_data(data)
    return data

def save_data(data):
    conn = get_gsheets_conn()
    if conn is not None:
        try:
            # Prepare Habits DF
            habits_list = []
            for h in data.get("habits", []):
                h_copy = h.copy()
                h_copy["target_days"] = ",".join(h.get("target_days", []))
                habits_list.append(h_copy)
            habits_df = pd.DataFrame(habits_list)

            # Prepare Completions DF
            comp_list = []
            for day, day_comps in data.get("completions", {}).items():
                for hid, detail in day_comps.items():
                    comp_list.append({
                        "date": day,
                        "habit_id": hid,
                        "duration": detail.get("duration", ""),
                        "mode": detail.get("mode", ""),
                        "notes": detail.get("notes", ""),
                        "helped": detail.get("helped", "")
                    })
            completions_df = pd.DataFrame(comp_list)

            # Prepare DSA DF
            dsa_df = pd.DataFrame(data.get("dsa_problems", []))

            # Prepare Daily Notes DF
            notes_df = pd.DataFrame(data.get("daily_notes", []))

            # Update Google Sheets (Clear previous content implicitly with empty dfs if needed)
            # The library can occasionally struggle with empty dataframes without columns, so ensure structure
            if habits_df.empty: habits_df = pd.DataFrame(columns=["id", "name", "icon", "category", "target_days", "color", "created"])
            if completions_df.empty: completions_df = pd.DataFrame(columns=["date", "habit_id", "duration", "mode", "notes", "helped"])
            if dsa_df.empty: dsa_df = pd.DataFrame(columns=["id", "name", "url", "difficulty", "status", "completed_on"])
            if notes_df.empty: notes_df = pd.DataFrame(columns=["date", "note"])

            # Clear existing sheets to prevent orphaned data rows when our dataset shrinks (e.g., when unchecking a habit)
            try:
                if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
                    url = st.secrets["connections"]["gsheets"].get("spreadsheet")
                    if url:
                        spreadsheet = conn.client._client.open_by_url(url)
                        for ws_name in ["habits", "completions", "dsa_problems", "daily_notes"]:
                            try:
                                spreadsheet.worksheet(ws_name).clear()
                            except Exception:
                                pass
            except Exception:
                pass

            # It takes time to write, but we push updates
            conn.update(worksheet="habits", data=habits_df)
            conn.update(worksheet="completions", data=completions_df)
            conn.update(worksheet="dsa_problems", data=dsa_df)
            
            try:
                conn.update(worksheet="daily_notes", data=notes_df)
            except Exception:
                pass # Don't completely fail saving if user forgot to create the 4th tab yet!
            
        except Exception as e:
            pass # Fails silently if GSheets is problematic and saves locally instead

    # Backup / local persistence
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_data():
    if "data" not in st.session_state:
        st.session_state.data = load_data()
    return st.session_state.data

@st.dialog("Log Habit Details", width="large")
def log_habit_dialog(habit_id, day_str, h_name):
    data = get_data()
    existing = data.get("completions", {}).get(day_str, {}).get(str(habit_id), {})
    
    st.markdown(f"#### Logging details for **{h_name}** on {day_str}")
    
    dur_opts = ["< 15 minutes", "15 minutes", "30 minutes", "45 minutes", "1 hour", "1.5 hours", "2+ hours"]
    d_idx = dur_opts.index(existing.get("duration", "15 minutes")) if existing.get("duration", "15 minutes") in dur_opts else 1
    duration_val = st.selectbox("Duration", dur_opts, index=d_idx)
    
    st.markdown("**How did it feel?**")
    emoji_modes = ["😭", "😟", "😐", "🙂", "😄", "🚀"]
    m_idx = emoji_modes.index(existing.get("mode", "🙂")) if existing.get("mode", "🙂") in emoji_modes else 3
    mode_val = st.radio("Mode", emoji_modes, index=m_idx, horizontal=True, label_visibility="collapsed")
    
    notes_val = st.text_area("Notes", value=existing.get("notes", ""), placeholder="How did it go?")
    
    h_opts = ["Yes", "No", "Not sure"]
    h_idx = h_opts.index(existing.get("helped", "Yes")) if existing.get("helped", "Yes") in h_opts else 0
    helped_val = st.selectbox("Did it help you?", h_opts, index=h_idx)
    
    if st.button("Save", use_container_width=True):
        data = get_data()
        hid = str(habit_id)
        if day_str not in data["completions"]:
            data["completions"][day_str] = {}
        data["completions"][day_str][hid] = {
            "duration": duration_val,
            "mode": mode_val,
            "notes": notes_val,
            "helped": helped_val
        }
        save_data(data)
        st.rerun()

@st.dialog("Confirm Uncheck")
def confirm_uncheck_dialog(habit_id, day_str, h_name):
    st.warning(f"Are you sure you want to uncheck **{h_name}** for {day_str}? This will delete the logged details for this day.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Uncheck", use_container_width=True):
            remove_completion(habit_id, day_str)
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()

@st.dialog("Confirm Delete")
def confirm_delete_dialog(habit_id, h_name):
    st.warning(f"Are you sure you want to permanently delete **{h_name}** and all its history?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Delete", use_container_width=True):
            data = get_data()
            h_id_int = int(habit_id)
            data["habits"] = [h for h in data["habits"] if h["id"] != h_id_int]
            
            # Clean up completions
            hid_str = str(habit_id)
            for day in data["completions"]:
                if hid_str in data["completions"][day]:
                    del data["completions"][day][hid_str]
                    
            save_data(data)
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()

def remove_completion(habit_id, day_str):
    data = get_data()
    hid = str(habit_id)
    if day_str in data["completions"] and hid in data["completions"][day_str]:
        del data["completions"][day_str][hid]
        save_data(data)

def is_done(habit_id, day_str):
    data = get_data()
    return str(habit_id) in data["completions"].get(day_str, {})

def calculate_streak(habit_id):
    data = get_data()
    streak = 0
    d = date.today()
    hid = str(habit_id)
    while True:
        ds = str(d)
        if hid in data["completions"].get(ds, {}):
            streak += 1
            d -= timedelta(days=1)
        else:
            break
    return streak

def calculate_longest_streak(habit_id):
    data = get_data()
    all_dates = sorted(data["completions"].keys())
    if not all_dates:
        return 0
    best = cur = 0
    prev = None
    hid = str(habit_id)
    for ds in all_dates:
        if hid in data["completions"][ds]:
            d = date.fromisoformat(ds)
            if prev and (d - prev).days == 1:
                cur += 1
            else:
                cur = 1
            best = max(best, cur)
            prev = d
        else:
            cur = 0
            prev = None
    return best

def get_completion_rate(habit_id, days=30):
    data = get_data()
    total = 0
    done = 0
    hid = str(habit_id)
    for i in range(days):
        d = str(date.today() - timedelta(days=i))
        total += 1
        if hid in data["completions"].get(d, {}):
            done += 1
    return (done / total * 100) if total else 0


# ─────────────────────────────────────────────
# Main App
# ─────────────────────────────────────────────
st.markdown("<h1 style='text-align:center; margin-bottom:4px;'>🏆 Habit Tracker</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:{t_text_muted}; margin-bottom:24px;'>{date.today().strftime('%A, %B %d, %Y')}</p>", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 1 — Today's Dashboard
# ══════════════════════════════════════════════
if current_tab == "📅  Today's Dashboard":
    data = get_data()
    
    # ── Handle inline edit links from the HTML badges
    if "edit_habit" in st.query_params and "edit_date" in st.query_params:
        e_id_str = st.query_params["edit_habit"]
        e_date = st.query_params["edit_date"]
        e_name = "Habit"
        for h in data.get("habits", []):
            if str(h["id"]) == e_id_str:
                e_name = h["name"]
                break
        del st.query_params["edit_habit"]
        del st.query_params["edit_date"]
        log_habit_dialog(int(e_id_str), e_date, e_name)
    
    habits = data["habits"]
    today_str = str(date.today())
    today_completions = data["completions"].get(today_str, {})
    total = len(habits)
    done_count = sum(1 for h in habits if str(h["id"]) in today_completions)
    pct = int(done_count / total * 100) if total else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="stat-card" title="Total habits you've checked off today vs. your total active habits">
            <div class="stat-number">{done_count}/{total}</div>
            <div class="stat-label">Completed Today</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-card" title="Percentage of today's habits you've completed">
            <div class="stat-number">{pct}%</div>
            <div class="stat-label">Daily Goal Target</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        best_streak = max((calculate_streak(h["id"]) for h in habits), default=0)
        st.markdown(f"""
        <div class="stat-card" title="The current longest continuous streak among all your habits">
            <div class="stat-number">🔥{best_streak}</div>
            <div class="stat-label">Best Active Streak</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        week_start = date.today() - timedelta(days=6)
        week_done = sum(
            1 for i in range(7)
            for h in habits
            if str(h["id"]) in data["completions"].get(str(date.today()-timedelta(days=i)), {})
        )
        week_total = total * 7
        week_pct = int(week_done / week_total * 100) if week_total else 0
        st.markdown(f"""
        <div class="stat-card" title="Your overall completion rate over the last 7 days">
            <div class="stat-number">{week_pct}%</div>
            <div class="stat-label">Weekly Consistency</div>
        </div>""", unsafe_allow_html=True)

    # ── Week mini-calendar
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">📆 Your Week at a Glance</div>', unsafe_allow_html=True)
    st.caption("A summary of how many habits you've completed each day over the past week.")
    week_cols = st.columns(7)
    for i, col in enumerate(week_cols):
        d = date.today() - timedelta(days=6-i)
        ds = str(d)
        day_completions = data["completions"].get(ds, {})
        done_today = sum(1 for h in habits if str(h["id"]) in day_completions)
        is_today = (d == date.today())
        
        bg_color = "#6c63ff" if is_today else ("#e6f4ea" if done_today == total and total > 0 else t_card_bg1)
        border_color = "2px solid #6c63ff" if is_today else f"1px solid {t_card_border}"
        day_text = 'white' if is_today or done_today==total else "#666"
        frac_text = "#1e8e3e" if done_today==total and total>0 else t_text_muted
        t_w_muted = "#888"

        with col:
            st.markdown(f"""
            <div style="background:{bg_color}; border:{border_color}; border-radius:12px; padding:10px; text-align:center;">
                <div style="font-size:0.7rem; color:{t_w_muted};">{d.strftime('%a')}</div>
                <div style="font-size:1.1rem; font-weight:700; color:{day_text};">{d.day}</div>
                <div style="font-size:0.75rem; color:{frac_text};">{done_today}/{total}</div>
            </div>""", unsafe_allow_html=True)

    # ── Habit checklist
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">✅ Daily Checklist</div>', unsafe_allow_html=True)
    st.caption("Click the ⬜ checkboxes below to mark a habit as complete for today. A popup will ask you for details!")

    if not habits:
        st.info("No habits yet! Go to 'Manage Habits' tab to add some.")
    else:
        for h in habits:
            done = is_done(h["id"], today_str)
            streak = calculate_streak(h["id"])
            rate = get_completion_rate(h["id"])

            col_check, col_info = st.columns([1, 11])
            with col_check:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("✅" if done else "⬜", key=f"toggle_{h['id']}_{today_str}", help="Toggle"):
                    if done:
                        confirm_uncheck_dialog(h["id"], today_str, h["name"])
                    else:
                        log_habit_dialog(h["id"], today_str, h["name"])

            with col_info:
                edit_html = f'<a href="?edit_habit={h["id"]}&edit_date={today_str}" target="_self" style="text-decoration:none; background:{t_card_bg2}; border:1px solid {t_card_border}; padding:2px 6px; border-radius:12px; font-size:0.75rem; color:{t_text_muted}; margin-left:4px;" title="Edit Log Details">✏️ Edit</a>' if done else ''
                badge = f'<span class="done-badge">✓ Done</span>{edit_html}' if done else '<span class="pending-badge">Pending</span>'
                streak_html = f'<span class="streak-badge">🔥 {streak} day streak</span>' if streak > 0 else ''
                
                details_html = ""
                if done:
                    detail = today_completions.get(str(h["id"]), {})
                    if detail.get("duration") or detail.get("mode") or detail.get("notes") or detail.get("helped") or detail.get("time"):
                        parts = []
                        if detail.get("duration"): parts.append(f"⏳ {detail['duration']}")
                        elif detail.get("time"): parts.append(f"⏱️ {detail['time']}")  # fallback for older entries
                        if detail.get("mode"): parts.append(f"🎯 {detail['mode']}")
                        if detail.get("helped"): parts.append(f"💡 {detail['helped']}")
                        details_line = " | ".join(parts)
                        notes_line = f"<div style='margin-top:4px;'>📝 <i>{detail['notes']}</i></div>" if detail.get("notes") else ""
                        details_html = f"<div style='margin-top:12px; padding:10px; background:{t_bg}; border-radius:8px; font-size:0.85rem; border: 1px solid {t_card_border}; color:#a78bfa;'>{'<div>' + details_line + '</div>' if details_line else ''}{notes_line}</div>"
                
                st.markdown(f"""
                <div class="habit-card" style="border-left: 4px solid {h['color']}; {'opacity:0.6; filter: grayscale(40%);' if done else ''}">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <div style="font-size:1.1rem; font-weight:700;">
                            {h['icon']} {h['name']} 
                            <span style="font-size:0.75rem; color:{t_text_muted}; font-weight:400; margin-left:8px;">(Goal: {h['category']})</span>
                        </div>
                        <div style="display:flex; gap:8px; align-items:center;">{streak_html} {badge}</div>
                    </div>
                    {details_html}
                </div>""", unsafe_allow_html=True)

    # ── Motivational footer
    if pct == 100:
        st.balloons()
        st.success("🎉 **Perfect day!** You completed all your habits today!")
    elif pct >= 75:
        st.info("💪 Great progress! You're almost there — keep going!")
    elif pct >= 50:
        st.warning("🌟 Halfway there! Push through the rest of today's habits.")


# ══════════════════════════════════════════════
# TAB 2 — History & Filters + Streaks
# ══════════════════════════════════════════════
elif current_tab == "📊  History & Filters":
    data = get_data()
    habits = data["habits"]

    # ── Filters
    st.markdown('<div class="section-title">🔍 Filters</div>', unsafe_allow_html=True)
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        habit_names = ["All Habits"] + [h["name"] for h in habits]
        sel_habit = st.selectbox("Select Habit", habit_names)
    with col_f2:
        categories = ["All Categories"] + list(set(h["category"] for h in habits))
        sel_cat = st.selectbox("Category", categories)
    with col_f3:
        time_range = st.selectbox("Time Range", ["Last 7 Days", "Last 14 Days", "Last 30 Days", "Last 90 Days"])

    days_map = {"Last 7 Days": 7, "Last 14 Days": 14, "Last 30 Days": 30, "Last 90 Days": 90}
    n_days = days_map[time_range]

    # Filter habits
    filtered_habits = habits
    if sel_habit != "All Habits":
        filtered_habits = [h for h in habits if h["name"] == sel_habit]
    if sel_cat != "All Categories":
        filtered_habits = [h for h in filtered_habits if h["category"] == sel_cat]

    # ── Completion heatmap / bar chart
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">📈 Completion History</div>', unsafe_allow_html=True)

    # Build dataframe
    rows = []
    for i in range(n_days - 1, -1, -1):
        d = date.today() - timedelta(days=i)
        ds = str(d)
        day_completions = data["completions"].get(ds, {})
        for h in filtered_habits:
            rows.append({
                "Date": d,
                "Habit": h["name"],
                "Done": 1 if str(h["id"]) in day_completions else 0,
                "Color": h["color"],
            })

    if rows:
        df = pd.DataFrame(rows)

        # Daily completion rate line chart
        daily = df.groupby("Date")["Done"].mean().reset_index()
        daily["Rate"] = daily["Done"] * 100

        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=daily["Date"], y=daily["Rate"],
            mode="lines+markers",
            line=dict(color="#6c63ff", width=3),
            marker=dict(size=7, color="#a78bfa"),
            fill="tozeroy",
            fillcolor="rgba(108,99,255,0.1)",
            name="Completion %"
        ))
        fig_line.update_layout(
            paper_bgcolor=t_card_bg1, plot_bgcolor=t_card_bg1,
            font=dict(color=t_text),
            yaxis=dict(title="Completion %", range=[0, 105], gridcolor=t_card_border),
            xaxis=dict(gridcolor=t_card_border),
            height=280, margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False
        )
        st.plotly_chart(fig_line, use_container_width=True)

        # Habit heatmap
        if len(filtered_habits) > 1:
            pivot = df.pivot_table(index="Habit", columns="Date", values="Done", aggfunc="sum").fillna(0)
            fig_heat = go.Figure(data=go.Heatmap(
                z=pivot.values,
                x=[str(c) for c in pivot.columns],
                y=pivot.index.tolist(),
                colorscale=[[0, t_card_bg1], [0.5, "#6c63ff"], [1, "#a78bfa"]],
                showscale=False,
                xgap=3, ygap=3,
            ))
            fig_heat.update_layout(
                paper_bgcolor=t_bg, plot_bgcolor=t_bg,
                font=dict(color=t_text),
                height=200 + 40 * len(filtered_habits),
                margin=dict(l=10, r=10, t=10, b=10),
            )
            st.plotly_chart(fig_heat, use_container_width=True)

    # ── Streaks section
    st.markdown('<div class="section-title">🔥 Streaks & Statistics</div>', unsafe_allow_html=True)

    streak_cols = st.columns(len(filtered_habits) if filtered_habits else 1)
    for idx, h in enumerate(filtered_habits):
        streak = calculate_streak(h["id"])
        longest = calculate_longest_streak(h["id"])
        rate_7  = get_completion_rate(h["id"], 7)
        rate_30 = get_completion_rate(h["id"], 30)

        with streak_cols[idx % len(streak_cols)]:
            fire = "🔥" * min(streak, 5) if streak > 0 else "💤"
            st.markdown(f"""
            <div class="habit-card" style="border-left: 4px solid {h['color']};">
                <div style="font-size:1.05rem; font-weight:700; margin-bottom:12px;">{h['icon']} {h['name']}</div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; text-align:center;">
                    <div style="background:{t_bg}; border-radius:10px; padding:10px;">
                        <div style="font-size:1.8rem; font-weight:800; color:#e65100;">{streak}</div>
                        <div style="font-size:0.72rem; color:{t_text_muted};">Current Streak {fire}</div>
                    </div>
                    <div style="background:{t_bg}; border-radius:10px; padding:10px;">
                        <div style="font-size:1.8rem; font-weight:800; color:#6c63ff;">{longest}</div>
                        <div style="font-size:0.72rem; color:{t_text_muted};">Best Ever 🏆</div>
                    </div>
                    <div style="background:{t_bg}; border-radius:10px; padding:10px;">
                        <div style="font-size:1.4rem; font-weight:700; color:#1e8e3e;">{rate_7:.0f}%</div>
                        <div style="font-size:0.72rem; color:{t_text_muted};">7-Day Rate</div>
                    </div>
                    <div style="background:{t_bg}; border-radius:10px; padding:10px;">
                        <div style="font-size:1.4rem; font-weight:700; color:#00838f;">{rate_30:.0f}%</div>
                        <div style="font-size:0.72rem; color:{t_text_muted};">30-Day Rate</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

    # ── Category breakdown donut
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">📂 Category Breakdown</div>', unsafe_allow_html=True)

    cat_data = {}
    for h in habits:
        rate = get_completion_rate(h["id"], n_days)
        cat = h["category"]
        if cat not in cat_data:
            cat_data[cat] = []
        cat_data[cat].append(rate)

    cat_labels = list(cat_data.keys())
    cat_vals = [sum(v)/len(v) for v in cat_data.values()]
    colors_pie = ["#6c63ff","#f7971e","#06b6d4","#ec4899","#4ade80","#a78bfa"]

    fig_donut = go.Figure(data=go.Pie(
        labels=cat_labels, values=cat_vals,
        hole=0.55,
        marker=dict(colors=colors_pie[:len(cat_labels)]),
        textinfo="label+percent",
        insidetextorientation="radial",
    ))
    fig_donut.update_layout(
        paper_bgcolor=t_bg, font=dict(color=t_text),
        height=300, margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        annotations=[dict(text="Avg Rate", x=0.5, y=0.5, font_size=14, showarrow=False, font_color=t_text_muted)]
    )
    col_d1, col_d2 = st.columns([1, 1])
    with col_d1:
        st.plotly_chart(fig_donut, use_container_width=True)
    with col_d2:
        # Bar chart per habit
        bar_habits = [h["name"] for h in habits]
        bar_vals = [get_completion_rate(h["id"], n_days) for h in habits]
        bar_colors = [h["color"] for h in habits]
        fig_bar = go.Figure(go.Bar(
            x=bar_vals, y=bar_habits, orientation="h",
            marker=dict(color=bar_colors),
            text=[f"{v:.0f}%" for v in bar_vals],
            textposition="auto",
        ))
        fig_bar.update_layout(
            paper_bgcolor=t_bg, plot_bgcolor=t_bg,
            font=dict(color=t_text),
            xaxis=dict(range=[0, 105], gridcolor=t_card_border),
            yaxis=dict(gridcolor=t_card_border),
            height=300, margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)


    # ── Detailed Past Logs
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">📝 Past Notes & Details</div>', unsafe_allow_html=True)
    st.caption("View your saved notes, durations, and details for completed habits.")
    
    # Gather logs for the selected habits over the filtered time period
    logs = []
    for i in range(n_days):
        d = date.today() - timedelta(days=i)
        ds = str(d)
        if ds in data.get("completions", {}):
            for h in filtered_habits:
                hid = str(h["id"])
                if hid in data["completions"][ds]:
                    entry = data["completions"][ds][hid]
                    if any(entry.values()): # If any details were actually logged
                        logs.append({
                            "date": d,
                            "habit_name": h["name"],
                            "icon": h["icon"],
                            "color": h["color"],
                            "detail": entry
                        })
    
    if not logs:
        st.info("No detailed notes or logs found for the selected filters.")
    else:
        for log in logs:
            detail = log["detail"]
            parts = []
            if detail.get("duration"): parts.append(f"⏳ {detail['duration']}")
            elif detail.get("time"): parts.append(f"⏱️ {detail['time']}")
            if detail.get("mode"): parts.append(f"🎯 {detail['mode']}")
            if detail.get("helped"): parts.append(f"💡 {detail['helped']}")
            
            details_line = " | ".join(parts)
            notes_line = f"<div style='margin-top:10px; font-style:italic; padding:12px; background:{t_card_bg2}; border-radius:8px; border-left:4px solid {log['color']};'>\" {detail['notes']} \"</div>" if detail.get("notes") else ""
            
            st.markdown(f"""
            <div class="habit-card" style="margin-bottom:10px; padding:16px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <strong>{log['icon']} {log['habit_name']}</strong>
                    <span style="color:{t_text_muted}; font-size:0.85rem;">{log['date'].strftime('%b %d, %Y')}</span>
                </div>
                <div style="font-size:0.85rem; color:{t_text_muted}; margin-top:6px;">{details_line}</div>
                {notes_line}
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 3 — DSA Tracker
# ══════════════════════════════════════════════
elif current_tab == "💻  DSA Tracker":
    data = get_data()
    problems = data.get("dsa_problems", [])

    st.markdown('<div class="section-title">💻 DSA Problem Tracker</div>', unsafe_allow_html=True)
    st.caption("Track data structures and algorithms problems you are practicing.")

    # Top Stats
    solved = [p for p in problems if p["status"] == "completed"]
    easy = len([p for p in solved if p["difficulty"] == "Easy"])
    med = len([p for p in solved if p["difficulty"] == "Medium"])
    hard = len([p for p in solved if p["difficulty"] == "Hard"])
    
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.markdown(f'<div class="stat-card"><div class="stat-number" style="color:#6c63ff;">{len(solved)}</div><div class="stat-label">Total Solved</div></div>', unsafe_allow_html=True)
    with col_s2:
        st.markdown(f'<div class="stat-card"><div class="stat-number" style="color:#4ade80;">{easy}</div><div class="stat-label">Easy</div></div>', unsafe_allow_html=True)
    with col_s3:
        st.markdown(f'<div class="stat-card"><div class="stat-number" style="color:#f7971e;">{med}</div><div class="stat-label">Medium</div></div>', unsafe_allow_html=True)
    with col_s4:
        st.markdown(f'<div class="stat-card"><div class="stat-number" style="color:#ef3c3f;">{hard}</div><div class="stat-label">Hard</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # ── Simple form to add a new problem quickly
    with st.expander("➕ Add New Problem", expanded=False):
        with st.form("add_dsa_form", clear_on_submit=True):
            col_a, col_b, col_c = st.columns([3, 1, 1])
            with col_a: p_name = st.text_input("Problem Name", placeholder="e.g. Two Sum")
            with col_b: p_diff = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
            with col_c: 
                st.markdown("<br>", unsafe_allow_html=True)
                submit_new = st.form_submit_button("Add Problem", use_container_width=True)
            p_url = st.text_input("URL (Optional)", placeholder="https://leetcode.com/...")
            
            if submit_new:
                if p_name.strip():
                    new_id = max((p.get("id", 0) for p in problems), default=0) + 1
                    problems.append({
                        "id": new_id,
                        "name": p_name.strip(),
                        "url": p_url.strip(),
                        "difficulty": p_diff,
                        "status": "open",
                        "completed_on": None
                    })
                    data["dsa_problems"] = problems
                    save_data(data)
                    st.rerun()
                else:
                    st.error("Problem name is required.")

    st.markdown('<h3 style="margin-top:20px; color:#6c63ff;">📋 Problem Summary</h3>', unsafe_allow_html=True)
    st.caption("Edit values directly in the table below like an Excel sheet! Check 'Done' to mark as completed, and click a row to delete it by pressing your backspace/delete key.")

    if not problems:
        st.info("No problems added yet. Add one above!")
    else:
        # Prepare dataframe for data_editor
        df_probs = pd.DataFrame(problems)
        # Map status to a boolean 'Done' column
        df_probs['Done'] = df_probs['status'] == 'completed'
        
        # Select and reorder columns for display
        display_cols = ['Done', 'name', 'difficulty', 'url', 'completed_on']
        df_display = df_probs[display_cols].copy()
        
        # Configure column types and names
        column_config = {
            "Done": st.column_config.CheckboxColumn("Done?", default=False, width="small"),
            "name": st.column_config.TextColumn("Problem Name", required=True, width="large"),
            "difficulty": st.column_config.SelectboxColumn("Difficulty", options=["Easy", "Medium", "Hard"], required=True, width="medium"),
            "url": st.column_config.LinkColumn("Link", display_text="Open Link", width="medium"),
            "completed_on": st.column_config.DateColumn("Completed On", disabled=True, width="medium")
        }
        
        # Display the editor
        edited_df = st.data_editor(
            df_display, 
            column_config=column_config, 
            use_container_width=True,
            num_rows="dynamic",
            hide_index=True,
            key="dsa_editor"
        )
        
        # Sync back to data dictionary if changes made
        if not edited_df.equals(df_display):
            new_problems = []
            for i, row in edited_df.iterrows():
                status = "completed" if row['Done'] else "open"
                
                # Handling completion date logic
                comp_date = row.get('completed_on', None)
                orig_row = df_display.iloc[i] if i < len(df_display) else None
                
                if row['Done'] and (orig_row is None or not orig_row['Done']):
                    # Newly marked as done
                    comp_date = str(date.today())
                elif not row['Done']:
                    # Unchecked
                    comp_date = None
                elif pd.isna(comp_date):
                    comp_date = None
                else:
                    comp_date = str(comp_date)

                new_problems.append({
                    "id": i + 1,
                    "name": row['name'],
                    "url": row['url'] if not pd.isna(row['url']) else "",
                    "difficulty": row['difficulty'],
                    "status": status,
                    "completed_on": comp_date
                })
            
            data["dsa_problems"] = new_problems
            save_data(data)
            st.rerun()


# ══════════════════════════════════════════════
# TAB 4 — Manage Habits
# ══════════════════════════════════════════════
elif current_tab == "⚙️  Manage Habits":
    data = get_data()
    habits = data["habits"]

    col_left, col_right = st.columns([5, 7])

    # ── Add new habit
    with col_left:
        st.markdown('<div class="section-title">➕ Add New Habit</div>', unsafe_allow_html=True)
        with st.form("add_habit_form", clear_on_submit=True):
            new_name = st.text_input("Habit Name", placeholder="e.g. Morning Run")
            col_a, col_b = st.columns(2)
            with col_a:
                new_icon = st.text_input("Emoji Icon", value="⭐", max_chars=2)
                new_color = st.color_picker("Color", value="#6c63ff")
            with col_b:
                new_cat = st.selectbox("Category", ["Health", "Fitness", "Learning", "Wellness", "Productivity", "Social", "Finance", "Other"])
            new_days = st.multiselect(
                "Target Days",
                ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
                default=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
            )
            submitted = st.form_submit_button("✨ Add Habit", use_container_width=True)
            if submitted:
                if new_name.strip():
                    new_id = max((h["id"] for h in habits), default=0) + 1
                    habits.append({
                        "id": new_id,
                        "name": new_name.strip(),
                        "icon": new_icon,
                        "category": new_cat,
                        "target_days": new_days,
                        "color": new_color,
                        "created": str(date.today()),
                    })
                    save_data(data)
                    st.success(f"✅ '{new_name}' added!")
                    st.rerun()
                else:
                    st.error("Please enter a habit name.")

        # ── Mark completions for past dates
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">📅 Log Past Completion</div>', unsafe_allow_html=True)
        past_date = st.date_input("Date", value=date.today(), max_value=date.today())
        past_habit = st.selectbox("Habit", [h["name"] for h in habits] if habits else ["No habits"])
        if st.button("📝 Log Details", use_container_width=True):
            if habits:
                hid = next(h["id"] for h in habits if h["name"] == past_habit)
                if not is_done(hid, str(past_date)):
                    log_habit_dialog(hid, str(past_date), past_habit)
                else:
                    st.info(f"'{past_habit}' is already logged on {past_date}. Uncheck from dashboard if needed.")

    # ── Existing habits list
    with col_right:
        st.markdown('<div class="section-title">📋 Your Configured Habits</div>', unsafe_allow_html=True)
        st.caption("Here is the list of habits you are currently tracking.")
        if not habits:
            st.info("No habits yet. Add your first habit!")
        else:
            for h in habits:
                streak = calculate_streak(h["id"])
                rate = get_completion_rate(h["id"])
                col_h, col_del = st.columns([10, 1])
                with col_h:
                    days_txt = ", ".join(h.get("target_days", []))
                    st.markdown(f"""
                    <div class="habit-card" style="border-left: 4px solid {h['color']};">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div style="font-size:1.05rem; font-weight:700;">{h['icon']} {h['name']}</div>
                            <span class="streak-badge">🔥 {streak} streak</span>
                        </div>
                        <div style="margin-top:8px; font-size:0.8rem; color:{t_text_muted};">
                            📂 {h['category']} &nbsp;|&nbsp; 📅 {days_txt} &nbsp;|&nbsp; 📈 {rate:.0f}% (30d)
                        </div>
                        <div style="margin-top:6px; font-size:0.75rem; color:{t_text_muted};">Added: {h.get('created','—')}</div>
                    </div>""", unsafe_allow_html=True)
                with col_del:
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_{h['id']}", help="Delete habit"):
                        confirm_delete_dialog(h["id"], h["name"])

        # ── Reset data
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("⚠️ Danger Zone"):
            st.warning("This will delete ALL habits and history permanently.")
            if st.button("🔴 Reset All Data", type="secondary"):
                if os.path.exists(DATA_FILE):
                    os.remove(DATA_FILE)
                st.session_state.clear()
                st.rerun()

                st.rerun()

# ══════════════════════════════════════════════
# TAB 5 — Daily Notes
# ══════════════════════════════════════════════
elif current_tab == "📝  Daily Notes":
    data = get_data()
    notes = data.get("daily_notes", [])
    
    st.markdown('<div class="section-title">📝 Daily Notes & Reflections</div>', unsafe_allow_html=True)
    st.caption("Jot down your thoughts, challenges, or highlights for the day.")

    c_left, c_right = st.columns([1, 1.3])

    with c_left:
        st.markdown('<h3 style="margin-top:0px; color:#6c63ff;">Write Note</h3>', unsafe_allow_html=True)
        # Select Date
        selected_date = st.date_input("Select Date", value=date.today(), max_value=date.today())
        date_str = str(selected_date)

        # Pre-fill if note exists
        existing_note = ""
        for n in notes:
            if n["date"] == date_str:
                existing_note = n["note"]
                break
                
        with st.form("daily_note_form", clear_on_submit=False):
            note_content = st.text_area("Your Reflections", value=existing_note, height=250, placeholder="How was your day? Did you struggle with any habits? What went well?")
            submit_btn = st.form_submit_button("Save Note", use_container_width=True)
            
            if submit_btn:
                # Update existing or add new
                found = False
                for n in notes:
                    if n["date"] == date_str:
                        n["note"] = note_content
                        found = True
                        break
                if not found:
                    notes.append({"date": date_str, "note": note_content})
                
                data["daily_notes"] = notes
                save_data(data)
                st.success("Note saved successfully!")
                st.rerun()

    with c_right:
        st.markdown('<h3 style="margin-top:0px; color:#a78bfa;">📜 Past Notes</h3>', unsafe_allow_html=True)
        
        # Display past notes (excluding the currently selected date if we want, or just show all sorted)
        sorted_notes = sorted(notes, key=lambda x: x["date"], reverse=True)
        
        if not sorted_notes:
            st.info("No daily notes written yet.")
        else:
            # Add a small text filter
            search_q = st.text_input("Search notes...", placeholder="Keywords...")
            
            for n in sorted_notes:
                # Apply filter
                if search_q and search_q.lower() not in n["note"].lower():
                    continue
                    
                # Format the date nicely
                try:
                    display_date = datetime.strptime(n['date'], "%Y-%m-%d").strftime("%B %d, %Y")
                except:
                    display_date = n['date']
                    
                # Highlight if it's today
                is_today = n['date'] == str(date.today())
                border_color = "#6c63ff" if is_today else t_card_border
                bg_color = t_card_bg1 if is_today else t_card_bg2
                
                st.markdown(f"""
                <div style="background:{bg_color}; border:1px solid {border_color}; border-radius:10px; padding:16px; margin-bottom:12px;">
                    <div style="font-size:0.85rem; color:{t_text_muted}; margin-bottom:8px; font-weight:600;">
                        🗓️ {display_date} {"(Today)" if is_today else ""}
                    </div>
                    <div style="white-space: pre-wrap; line-height: 1.5;">{n['note']}</div>
                </div>
                """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────
st.markdown(f"""
<hr style="border-color:{t_card_border}; margin-top:40px;">
<p style="text-align:center; color:{t_text_muted}; font-size:0.8rem;">
    🏆 Habit Tracker &nbsp;•&nbsp; Built with Streamlit &nbsp;•&nbsp; Data saved locally as habit_data.json
</p>""", unsafe_allow_html=True)
