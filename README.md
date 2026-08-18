# Autonomous Containerized ML Agent 🤖📊

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![OpenAI](https://img.shields.io/badge/LLM-OpenAI%20%7C%20Gemini-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

An **autonomous, containerized machine learning engineering agent** designed to execute end-to-end long-horizon tabular machine learning pipelines inside an isolated Docker sandbox container. 

The agent operates in a self-directed loop: profiling raw datasets, cleaning missing data, performing feature selection, training and tuning traditional ML models (Random Forest, Gradient Boosting), logging metrics, exporting trained binaries, generating standalone inference scripts, and auditing token execution costs.

---

## 🌟 Key Features

* **🛡️ Isolated Docker Sandbox Security**: Dual-mount volume separation protects developer source code. User datasets are mounted as `Read/Write` to `/workspace`, while the agent core engine code is mounted as `Read-Only` to `/app`. Built-in command sanitization blocks forbidden system commands (`sudo`, `chmod`, network utilities).
* **🔄 Autonomous Long-Horizon Execution Loop**: Operates over multi-turn reasoning steps (up to 30 steps per run). Maintains long-term state via workspace artifacts (`agent_plan.md`, `data_understanding.md`).
* **💰 Real-Time Token Usage & Cost Observability**: Tracks input/output tokens per step and computes API costs in USD (e.g. `gpt-4o-mini`, `gemini-1.5-flash`). Persists complete step-by-step audit logs to `/workspace/agent_trace.json`.
* **🤖 Standalone Model Inference Interface**: The agent automatically outputs a self-contained `predict.py` script and self-validates its exported model (`final_model.pkl`) before completing tasks.
* **⚡ One-Command CLI Utilities**:
  - `run_agent.sh`: One-command execution to launch the agent on any target dataset folder.
  - `predict_model.sh`: One-command model inference runner for testing raw JSON samples.

---

## 🏗️ Architecture & Mount Strategy

```
 [Host System]
  ├── Code Repository (/home/bharat/explore) ───[RO Mount: /app]─────┐
  │    ├── agent.py (Reasoning Engine)                               │
  │    ├── system_prompt.txt (Directives)                            │
  │    ├── run_agent.sh (Host Launcher)                              │
  │    └── predict_model.sh (Host Inference Helper)                  │
  │                                                                 ▼
  └── User Data Folder (./data) ─────────────[RW Mount: /workspace]─► [Docker Sandbox Container]
       ├── goal.txt (Task Specification)                            python:3.11-slim
       ├── dataset.csv (Raw Input Data)                             (Isolated Sandbox)
       ├── data_understanding.md (EDA & Profiling)
       ├── feature_scores.csv (Feature Ranks)
       ├── model_registry.csv (CV Score Logs)
       ├── final_model.pkl (Trained Model Binary)
       ├── predict.py (Inference Script)
       └── agent_trace.json (JSON Execution Trace)
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine installed and running.
- Python 3.11+ and `bash`.
- OpenAI API Key (`OPENAI_API_KEY`) or Gemini API Key (`GEMINI_API_KEY`).

### 2. Installation & Configuration
Clone the repository and set up environment variables:

```bash
git clone https://github.com/bharat948/Autonomous-Containerized-ML-Agent.git
cd Autonomous-Containerized-ML-Agent

# Copy template and insert your API keys
cp .env.template .env
nano .env # Set OPENAI_API_KEY=your_key_here
```

### 3. Running the Agent on a Dataset
Create a dataset directory (e.g., `./data`), place your CSV dataset and a `goal.txt` file specifying the objective:

```bash
# Example dataset structure:
./data/
  ├── diabetes.csv
  └── goal.txt
```

#### Example `goal.txt`:
```text
Task: Tabular ML Classification
Dataset: diabetes.csv
Target Column: Outcome
Evaluation Metric: 5-Fold Cross-Validation Accuracy
Goal: Analyze features, clean missing/invalid zero values, encode variables, train a Random Forest model, and export final_model.pkl.
```

Launch the agent with a single command:

```bash
./run_agent.sh ./data
```

---

## 🔮 Model Inference Interface (`predict_model.sh`)

Once the agent completes its run, it outputs a trained binary (`final_model.pkl`) and a standalone inference script (`predict.py`) inside `./data`.

You can query predictions directly from your host terminal using `./predict_model.sh`:

```bash
./predict_model.sh ./data '{"Pregnancies": 6, "Glucose": 148, "BloodPressure": 72, "SkinThickness": 35, "Insulin": 0, "BMI": 33.6, "DiabetesPedigreeFunction": 0.627, "Age": 50}'
```

#### Output:
```json
{
  "prediction": 1,
  "prediction_label": "Positive (Diabetes)",
  "probability": 0.89,
  "status": "success"
}
```

---

## 📊 Observability & Trace Schema (`agent_trace.json`)

Every execution generates a structured trace log at `/workspace/agent_trace.json` capturing execution metrics:

```json
{
  "session_id": "614b8493-82a7-4ec7-81b5-dc87b39b9e97",
  "start_time": "2026-08-18T14:35:49Z",
  "model": "gpt-4o-mini",
  "total_steps": 21,
  "total_tokens": {
    "prompt_tokens": 63100,
    "completion_tokens": 1988,
    "total_tokens": 65088
  },
  "total_cost_usd": 0.010658,
  "steps": [ ... ]
}
```

---

## 📁 Repository Structure

```
├── agent.py             # Multi-turn LLM reasoning engine & tool definitions
├── system_prompt.txt    # Long-horizon operational directives & safety rules
├── run_agent.sh         # Unified host entrypoint script
├── predict_model.sh     # Host CLI inference helper script
├── setup_sandbox.sh     # Docker sandbox volume mount initialization
├── teardown.sh          # Container shutdown & cleanup utility
├── .env.template        # Environment variable template
├── .gitignore           # Git ignore configuration
└── README.md            # Project documentation
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue to report bugs or request features.

1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
