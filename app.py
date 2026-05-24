import streamlit as st
import time
import pandas as pd
import pygetwindow as gw
import matplotlib.pyplot as plt
from plyer import notification

# ================= UI STYLE =================
st.markdown("""
<style>

/* Background */
.stApp {
    background-color: #0e1117;
}

/* GLOBAL TEXT FIX */
html, body, [class*="css"] {
    color: #ffffff !important;
}

/* Headings */
h1, h2, h3 {
    color: #ffffff !important;
}

/* Labels */
label {
    color: #ffffff !important;
}

/* Input fields */
input, textarea {
    background-color: #ffffff !important;
    color: #000000 !important;
    border-radius: 8px;
}

/* Table */
thead tr th {
    background-color: #1f2937 !important;
    color: white !important;
}
tbody tr td {
    color: white !important;
}

/* Buttons */
.stButton>button {
    background-color: #ff4b4b;
    color: white;
    border-radius: 10px;
    font-weight: bold;
}

/* Fix faint text issue */
p, span, div {
    color: #e6e6e6 !important;
}

</style>
""", unsafe_allow_html=True)
# ================= SESSION =================
if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "history" not in st.session_state:
    st.session_state.history = []

# ================= AGENTS =================

def get_active_window():
    try:
        window = gw.getActiveWindow()
        return window.title.lower() if window else ""
    except:
        return ""

def behavior_agent(title):
    if any(x in title for x in ["youtube", "yt", "instagram", "netflix", "game"]):
        return "ENTERTAINMENT"
    elif any(x in title for x in ["code", "visual studio", "github", "notepad", "jupyter"]):
        return "PRODUCTIVE"
    elif any(x in title for x in ["edge", "chrome"]):
        return "PRODUCTIVE"
    return "IGNORE"

def task_agent(tasks):
    for t in tasks:
        if t["days"] <= 1:
            t["priority"] = "HIGH"
            t["score"] = 5
        elif t["days"] <= 3:
            t["priority"] = "MEDIUM"
            t["score"] = 3
        else:
            t["priority"] = "LOW"
            t["score"] = 1
    return tasks

def decision_agent(category, tasks):
    urgent = any(t["priority"] in ["HIGH", "MEDIUM"] for t in tasks)

    if category == "ENTERTAINMENT" and urgent:
        return "HIGH_ALERT"
    elif category == "ENTERTAINMENT":
        return "ALERT"
    else:
        return "GOOD"

# ================= UI =================

st.title("🤖 Agentic AI Digital Life System")

col1, col2 = st.columns(2)

with col1:
    task_name = st.text_input("Task Name")

with col2:
    days = st.number_input("Days Left", min_value=0, step=1)

if st.button("➕ Add Task"):
    if task_name:
        st.session_state.tasks.append({
            "task": task_name,
            "days": days,
            "done": False
        })

# ================= TASK DASHBOARD =================

st.subheader("📋 Task Dashboard")

updated_tasks = []

for i, t in enumerate(st.session_state.tasks):

    col1, col2, col3, col4 = st.columns([3,2,2,1])

    with col1:
        st.write(f"**{t['task']}**")

    with col2:
        st.write(f"{t['days']} days")

    if t["days"] <= 1:
        priority = "HIGH"
    elif t["days"] <= 3:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    with col3:
        st.write(priority)

    with col4:
        done = st.checkbox("", key=f"task_{i}")
    
    if not done:
        updated_tasks.append(t)

st.session_state.tasks = updated_tasks

if st.button("🧹 Clear History"):
    st.session_state.history = []

# ================= MONITOR =================

if st.button("🚀 Start Monitoring"):

    st.subheader("🟢 Live Monitoring")

    window_placeholder = st.empty()
    category_placeholder = st.empty()
    decision_placeholder = st.empty()
    action_placeholder = st.empty()

    last_window = ""

    for _ in range(30):

        title = get_active_window()

        if title == last_window:
            time.sleep(2)
            continue

        category = behavior_agent(title)

        if category == "IGNORE":
            last_window = title
            continue

        tasks = task_agent(st.session_state.tasks)
        decision = decision_agent(category, tasks)

        # DISPLAY
        window_placeholder.markdown(f"### 🖥 Active Window\n**{title.upper()}**")
        category_placeholder.markdown(f"### 📊 Category\n**{category}**")
        decision_placeholder.markdown(f"### 🧠 Decision\n**{decision}**")

        # NEXT TASK
        if st.session_state.tasks:
            sorted_tasks = sorted(st.session_state.tasks, key=lambda x: x["days"])
            next_task = sorted_tasks[0]["task"]
        else:
            next_task = None

        # ACTION
        if decision == "HIGH_ALERT":
            action = f"⚠️ STOP! Focus on: {next_task}"
            notification.notify(
                title="🚨 HIGH ALERT",
                message="Stop distraction!",
                timeout=5
            )

        elif decision == "ALERT":
            action = f"⚡ Work on: {next_task}"
            notification.notify(
                title="⚠️ Warning",
                message="Get back to work",
                timeout=5
            )

        else:
            if next_task:
                action = f"✅ Continue → {next_task}"
            else:
                action = "🎉 All tasks completed!"

        # DISPLAY ACTION
        if "STOP" in action:
            action_placeholder.error(action)
        elif "⚡" in action:
            action_placeholder.warning(action)
        else:
            action_placeholder.success(action)

        # HISTORY (no duplicates)
        if not st.session_state.history or st.session_state.history[-1]["Window"] != title:
            st.session_state.history.append({
                "Window": title,
                "Category": category,
                "Decision": decision
            })

        last_window = title
        time.sleep(2)

# ================= HISTORY =================

st.subheader("📜 Activity History")

if st.session_state.history:
    hist_df = pd.DataFrame(st.session_state.history)
    hist_df = hist_df[hist_df["Category"].isin(["PRODUCTIVE", "ENTERTAINMENT"])]
    st.dataframe(hist_df, use_container_width=True)

# ================= GRAPH =================

st.subheader("📊 Activity Analytics")

if st.session_state.history:
    hist_df = pd.DataFrame(st.session_state.history)
    hist_df = hist_df[hist_df["Category"].isin(["PRODUCTIVE", "ENTERTAINMENT"])]

    if not hist_df.empty:
        counts = hist_df["Category"].value_counts()

        fig, ax = plt.subplots()
        counts.plot(kind="bar", ax=ax)

        ax.set_title("Productivity vs Distraction")
        st.pyplot(fig)