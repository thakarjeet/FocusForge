# 🎯 FocusForge — Your Explainable Productivity Copilot

**FocusForge** is a local-first task planner that helps students and early-career builders decide what to do next. Instead of a plain to-do list, it ranks tasks using an explainable priority score, estimates near-term workload, tracks progress, and exports your tasks to CSV.

> Built with Python + Streamlit. No API key, paid service, or cloud database required.

## ✨ Features

- **Smart next-task recommendation** — combines deadline urgency, importance, estimated effort, and energy level.
- **Daily workload check** — totals tasks due today or overdue and flags when the workload exceeds a configurable four-hour focus budget.
- **Task management** — add, complete, reopen, filter, and delete tasks.
- **Progress dashboard** — open/completed counts, completion rate, and a chart.
- **CSV export** — take your task data with you.
- **Local-first storage** — tasks live in `data/tasks.json` on your machine.
- **Tested core logic** — unit tests cover scoring, workload estimates, validation, task operations, persistence, and export.

## 🧠 How the priority score works

The score is deliberately **rule-based and explainable**, not a black-box claim of artificial intelligence:

| Signal | Effect |
|---|---|
| Deadline urgency | Tasks due today or overdue rise to the top |
| Importance | User-rated importance contributes up to 30 points |
| Estimated effort | Short tasks receive a modest quick-win bonus |
| Energy required | Low-energy tasks receive a small adjustment |

The final score is clamped to 0–100. This gives you an understandable recommendation you can inspect and improve, rather than pretending a simple app has a trained AI model.

## 🚀 Run locally

### 1. Install Python
Use Python 3.10 or newer. Check your version:

```bash
python --version
```

### 2. Download and unzip this project
Open a terminal in the `focusforge` project folder.

### 3. Create a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt instead:
```bat
.venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Launch the app

```bash
streamlit run app.py
```

Your browser should open the dashboard automatically. If not, Streamlit prints a local address in the terminal.

## 🧪 Run tests

From the project root:

```bash
python -m unittest discover -s tests -v
```

## 📁 Project structure

```text
focusforge/
├── app.py                  # Streamlit dashboard
├── focusforge.py           # Scoring, planning, storage, and export logic
├── tests/
│   └── test_focusforge.py  # Unit tests
├── data/
│   └── .gitkeep            # Keeps the data directory in Git
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

## 🛠️ Tech stack

- **Python** — application logic and data model
- **Streamlit** — interactive web UI
- **Pandas** — simple progress visualization
- **unittest** — standard-library automated tests
- **JSON + CSV** — lightweight local persistence and export

## 🔐 Privacy notes

Tasks are saved locally in `data/tasks.json`. The app does not send task data to a server operated by this project. Avoid entering sensitive personal information. The JSON file is ignored by Git so your personal tasks are not accidentally committed.

## 🗺️ Roadmap ideas

- [ ] Optional calendar import
- [ ] Weekly workload heatmap
- [ ] Pomodoro focus timer
- [ ] Repeating tasks
- [ ] Configurable focus budget
- [ ] Optional language-model integration with user consent
- [ ] Deploy a demo with a clear privacy notice

## 💼 Portfolio talking points

This project demonstrates:
1. Separating business logic from UI code.
2. Designing an explainable ranking algorithm.
3. Input validation and edge-case handling.
4. Local persistence and CSV data export.
5. Automated unit testing.
6. A usable data-driven dashboard.

**Interview-ready explanation:** “I built a local-first productivity dashboard in Python. Its recommendation engine ranks tasks using transparent urgency, importance, effort, and energy signals. I separated the core logic from the Streamlit interface and added unit tests so the logic can be verified independently.”

## 📄 License

MIT — see [`LICENSE`](LICENSE).
