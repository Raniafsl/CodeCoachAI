# 🤖 CodeCoach AI

CodeCoach AI is an AI-powered web application that helps students improve their Python programming skills by combining rule-based static analysis with a local Large Language Model (Llama 3.2 via Ollama).

Users can submit Python code, receive instant feedback, view AI-generated explanations, analyze complexity, and save previous analyses through a secure login system.

---

## ✨ Features

- 🤖 AI-powered code review using Ollama (Llama 3.2)
- 📊 Rule-based static code analysis
- 💯 Automatic code quality scoring
- 🐛 Bug detection and feedback
- ⚡ Time & space complexity analysis
- 💡 AI-generated code improvements
- 🔐 User authentication with hashed passwords
- 📚 Personal history of previous analyses
- 🧪 Unit tests using pytest
- 📱 Responsive web interface

---

## 🛠 Tech Stack

### Backend
- Python
- Flask
- SQLite

### AI
- Ollama
- Llama 3.2

### Frontend
- HTML
- CSS
- Jinja2 Templates

### Testing
- Pytest

---

## 📸 Screenshots

### Home Page

(Add screenshot here)

---

### Code Analysis

(Add screenshot here)

---

### AI Results

(Add screenshot here)

---

### History

(Add screenshot here)

---

## 🚀 Running Locally

Clone the repository

```bash
git clone https://github.com/Raniafsl/CodeCoach.git
```

Go into the project

```bash
cd CodeCoach
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate it

macOS/Linux

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Start Ollama

```bash
ollama serve
```

Run the application

```bash
python app.py
```

Open

```
http://127.0.0.1:5000
```

---

## 📂 Project Structure

```
CodeCoach/
│
├── services/
│   ├── ai_service.py
│   └── analyzer.py
│
├── templates/
│
├── static/
│
├── tests/
│
├── app.py
├── requirements.txt
└── README.md
```

---

## 🌱 Future Improvements

- Export reports as PDF
- Syntax highlighting
- More programming language support
- Instructor dashboard
- Cloud deployment
- AI chat assistant

---

## 👩‍💻 Author

**Rania Faisal**

University of Waterloo — Computer Science

GitHub:
https://github.com/Raniafsl