3from datetime import date, datetime, timedelta
import os
import pandas as pd
import streamlit as st

from focusforge import (
    Task, priority_score, recommend_next_task, estimate_daily_load,
    load_tasks, save_tasks, create_task, complete_task, delete_task,
    productivity_summary, export_tasks_csv,
)

st.set_page_config(page_title="FocusForge | Smart Study Planner", page_icon="🎯", layout="wide")

st.markdown("""
<style>
    .block-container {padding-top: 2rem; max-width: 1200px;}
    div[data-testid="stMetric"] {background: rgba(120,120,140,.08); padding: 16px; border-radius: 14px;}
    .hero {padding: 1.5rem 1.7rem; border-radius: 18px; background: linear-gradient(120deg,#14213d,#315c8c); color:white; margin-bottom:1rem;}
    .hero h1 {margin:0; font-size:2.4rem;} .hero p {margin:.45rem 0 0; opacity:.9;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>🎯 FocusForge</h1><p>Your personal productivity copilot — prioritize smarter, plan realistically, and build momentum.</p></div>', unsafe_allow_html=True)

DATA_PATH = "data/tasks.json"
os.makedirs("data", exist_ok=True)
tasks = load_tasks(DATA_PATH)

with st.sidebar:
    st.header("➕ Add a task")
    with st.form("new_task", clear_on_submit=True):
        title = st.text_input("Task name", placeholder="e.g. Finish Python mini-project")
        category = st.selectbox("Category", ["Study", "Project", "Personal", "Career", "Health"])
        due = st.date_input("Due date", value=date.today() + timedelta(days=2))
        minutes = st.number_input("Estimated time (minutes)", min_value=5, max_value=1440, value=45, step=5)
        importance = st.slider("Importance", 1, 5, 3, help="5 = very important")
        energy = st.select_slider("Energy required", options=["Low", "Medium", "High"], value="Medium")
        submitted = st.form_submit_button("Add to my plan", use_container_width=True)
        if submitted:
            if not title.strip():
                st.error("Give your task a name first.")
            else:
                tasks = create_task(tasks, title.strip(), category, due.isoformat(), int(minutes), importance, energy)
                save_tasks(DATA_PATH, tasks)
                st.success("Task added!")
                st.rerun()

if not tasks:
    st.info("Welcome! Add your first task in the sidebar to let FocusForge build your plan.")
    st.markdown("### What makes it useful?")
    c1, c2, c3 = st.columns(3)
    c1.markdown("**🧠 Smart ranking**\n\nCombines urgency, importance, effort, and overdue status.")
    c2.markdown("**📅 Realistic planning**\n\nChecks your available focus time against pending workload.")
    c3.markdown("**📈 Useful insights**\n\nTracks completion and flags overloaded days.")
    st.stop()

pending = [t for t in tasks if not t.get("completed", False)]
completed = [t for t in tasks if t.get("completed", False)]
summary = productivity_summary(tasks)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Open tasks", len(pending))
m2.metric("Completed", len(completed))
m3.metric("Completion rate", f"{summary['completion_rate']:.0f}%")
m4.metric("Pending workload", f"{sum(t['estimated_minutes'] for t in pending) // 60}h {sum(t['estimated_minutes'] for t in pending) % 60}m")

st.divider()
left, right = st.columns([1.25, 1])
with left:
    st.subheader("✨ Your next best move")
    next_task = recommend_next_task(pending, today=date.today().isoformat())
    if next_task:
        score = priority_score(next_task, today=date.today().isoformat())
        st.markdown(f"### {next_task['title']}")
        st.caption(f"{next_task['category']} · {next_task['estimated_minutes']} min · due {next_task['due_date']}")
        st.progress(min(score / 100, 1.0), text=f"Priority score: {score:.0f}/100")
        if next_task["due_date"] < date.today().isoformat():
            st.warning("This task is overdue. Consider tackling it or revising its deadline.")
        elif next_task["due_date"] == date.today().isoformat():
            st.warning("Due today — give this one some attention.")
        else:
            st.success("A good place to start based on urgency, importance, and effort.")
        if st.button("✅ Mark recommended task complete", type="primary"):
            tasks = complete_task(tasks, next_task["id"])
            save_tasks(DATA_PATH, tasks)
            st.rerun()
    else:
        st.success("All clear — you've completed every task. Add another goal when you're ready!")

with right:
    st.subheader("🧭 Daily load check")
    daily = estimate_daily_load(pending, today=date.today().isoformat())
    st.metric("Estimated pending time", f"{daily['total_minutes']} min")
    st.metric("Suggested focus blocks", daily["focus_blocks"])
    st.caption(daily["message"])
    if daily["overloaded"]:
        st.warning("Your workload may be too large for one day. Split tasks or move non-urgent deadlines.")

st.divider()
st.subheader("📋 Task board")
filter_choice = st.radio("Show", ["All", "Pending", "Completed"], horizontal=True)
visible = tasks if filter_choice == "All" else pending if filter_choice == "Pending" else completed
if visible:
    ordered = sorted(visible, key=lambda t: (t.get("completed", False), -priority_score(t) if not t.get("completed", False) else 0))
    for task in ordered:
        with st.container(border=True):
            cols = st.columns([0.45, 3.2, 1.2, 1.1, 1.0, 0.7])
            checked = cols[0].checkbox("Done", value=task.get("completed", False), key=f"done_{task['id']}", label_visibility="collapsed")
            if checked != task.get("completed", False):
                tasks = complete_task(tasks, task["id"]) if checked else [dict(t, completed=False) if t["id"] == task["id"] else t for t in tasks]
                save_tasks(DATA_PATH, tasks)
                st.rerun()
            cols[1].markdown(f"**{task['title']}**" + ("  ~~(completed)~~" if task.get("completed") else ""))
            cols[1].caption(f"{task['category']} · {task['energy']} energy · priority {priority_score(task):.0f}/100")
            cols[2].write(f"📅 {task['due_date']}")
            cols[3].write(f"⏱️ {task['estimated_minutes']} min")
            if cols[4].button("Delete", key=f"del_{task['id']}"):
                tasks = delete_task(tasks, task["id"])
                save_tasks(DATA_PATH, tasks)
                st.rerun()
            cols[5].write("✓" if task.get("completed") else "•")
else:
    st.caption("Nothing in this view yet.")

st.divider()
st.subheader("📊 Progress")
if tasks:
    chart_df = pd.DataFrame([
        {"Status": "Completed", "Tasks": len(completed)},
        {"Status": "Pending", "Tasks": len(pending)}
    ]).set_index("Status")
    st.bar_chart(chart_df)
    st.download_button("⬇️ Export tasks as CSV", data=export_tasks_csv(tasks),
                       file_name="focusforge_tasks.csv", mime="text/csv")
st.caption("FocusForge is a planning aid, not a substitute for your own judgment. Your task data is stored locally in data/tasks.json.")
