
🎓 EduAgents — Multi-Subject AI Tutor (Mock LLM, No API Needed)

EduAgents is an interactive AI tutoring system designed for students from Class 8–12, featuring:

🔹 AI Tutor Chat (mock LLM, no API keys required)

🔹 Multi-subject support (Math, Physics, Chemistry, Biology, History, Geography, English, CS)

🔹 Topic explanations, step-by-step

🔹 Practice questions with memory-based non-repetition

🔹 Smart recommendations based on skill weaknesses

🔹 Gradio Web App UI for better speed & deployment

🔹 Fully local, lightweight, safe for submission on Kaggle/GitHub/HuggingFace

This project is ideal for ML learning, capstone submissions, educational tools, or agent-based system demos.

⭐ Features
📘 1. Multi-Subject AI Tutor

Supports major school subjects:

. Mathematics

. Physics

. Chemistry

. Biology

. History

. Geography

. English

. Computer Science

🧠 2. Mock LLM (No API Key Needed)

. All answers & problems come from:

. custom rule-based logic

. canned explanations

. problem banks

. non-repetitive question generation

This makes the app:
✔️ Fully offline
✔️ Zero-cost
✔️ Safe to upload

📝 3. Smart Practice Questions

. Generates unique questions

. Tracks previously shown questions

. Avoids repetition using memory

. Supports skill-specific drilling

⭐ 4. Personalized Study Recommendations

Based on:

. skill difficulty

. estimated mastery

. subject filters

. difficulty filters (Easy / Medium / Hard)

🎛️ 5. Gradio Interface

Fast, clean, mobile-friendly.

📂 Project Structure
EduAgents/
│
├── app.py                  # Gradio app (main UI)
├── memory.py               # Memory utilities (if used)
│
├── agents/
│   ├── llm_agent.py        # Mock LLM Tutor
│   ├── recommend_agent.py  # Recommendation engine
│   └── skill_agent.py      # Skill mastery estimator
│
├── requirements.txt        # Dependencies (Gradio, Python libs)
├── README.md               # Project documentation
└── .gitignore              # Ignore pycache, venv, etc.

🚀 How to Run Locally
1. Install dependencies
pip install -r requirements.txt

2. Launch the app
python app.py


Gradio will open a link like:
http://127.0.0.1:7860

☁️ Deployment (Optional)
HuggingFace Spaces (Gradio)

Create New Space → Gradio

Upload:

. app.py

. agents/

requirements.txt

. README.md

. Deploy.

⚠️ No API keys required because this project uses a mock LLM.

📄 Requirements

requirements.txt includes:

gradio
pandas
numpy


(plus any other optional libraries you add)

🧪 Demo Instructions (For Reviewers)

Here are quick test commands:

Tutor Chat

 . “Explain Newton’s second law.”

 . “What is integration?”

 . “Explain fractions.”

Practice Problems

 . “Give me a practice problem.”

 . From dropdown → Select skill → Get Practice Question

Recommendations

 . Choose subject filter (e.g., Physics)

 . Choose difficulty (Medium)

 . Click Show Recommendations

📘 Why Mock LLM?

. Perfect for students & beginners

. Eliminates dependency on OpenAI/Claude API

. Safe for public GitHub repositories

. Zero cost for deployment

You may upgrade to a real model later by modifying llm_agent.py.

🔒 License

This project is open-source under MIT License.
You may use, modify, and distribute for educational or research use.

🤝 Contributing

Pull requests and suggestions are welcome!
Feel free to improve explanations, add subjects, or expand the problem bank.