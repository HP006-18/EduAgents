import gradio as gr
from agents.llm_agent import LLMAgent
from agents.recommend_agent import RecommendationAgent
from agents.skill_agent import SkillAgent

# Load agents
llm_agent = LLMAgent()
rec_agent = RecommendationAgent()
skill_agent = SkillAgent()

# Default state
def init_state():
    return {
        "given_problems": {},
        "topic": None,
        "subject": None
    }

# --------------------------
# START TOPIC
# --------------------------
def start_topic(subject, topic, state):
    if not topic or topic.strip() == "":
        return "⚠️ Please enter a topic first!", state

    state["subject"] = subject
    state["topic"] = topic.strip()

    return f"### Topic set to **{topic}**\nSubject: **{subject}**\nYou can now ask for explanations or practice problems.", state

# --------------------------
# TUTOR CHAT
# --------------------------
def tutor_chat(user_msg, state):

    if not user_msg.strip():
        return "⚠️ Please type a message.", state

    response = llm_agent.generate(
        user_msg,
        context={
            "topic": state["topic"],
            "subject": state["subject"],
            "given_problems": state["given_problems"]
        }
    )

    # sync memory
    state["given_problems"] = response.get("given_problems", state["given_problems"])

    return response["text"], state

# --------------------------
# RECOMMENDATIONS
# --------------------------
def get_recommendations(filter_subject, difficulty, state):

    skills = skill_agent.estimate_from_history([])

    subject_filter_val = None if filter_subject == "All Subjects" else filter_subject
    difficulty_filter_val = None if difficulty == "Any" else difficulty

    recommendations = rec_agent.generate_recommendations(
        history=[],
        skill_estimates=skills,
        llm_agent=llm_agent,
        top_k=8,
        subject_filter=subject_filter_val,
        difficulty_filter=difficulty_filter_val,
        context={"given_problems": state["given_problems"]}
    )

    if not recommendations:
        return "⚠️ No recommendations found."

    txt = ""
    for r in recommendations:
        badge = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}.get(r["difficulty"], "")
        txt += f"### {r['title']} {badge}\n**Skill:** {r['skill']}\n\n{r['excerpt']}\n\n---\n"

    return txt

# --------------------------
# PRACTICE QUESTION
# --------------------------
def get_practice_question(skill_selected, state):

    response = llm_agent.generate(
        f"Give practice problem for {skill_selected}",
        context={
            "skill": skill_selected,
            "difficulty": None,
            "given_problems": state["given_problems"]
        }
    )

    state["given_problems"] = response.get("given_problems", state["given_problems"])

    return response["text"], state


# -------------------------------------------------------
# BUILDING THE GRADIO UI
# -------------------------------------------------------
with gr.Blocks(title="EduAgents – AI Tutor") as demo:

    state = gr.State(init_state())

    gr.Markdown("# 🎓 EduAgents – AI Tutor for Students")

    # --------------------------
    # SUBJECT + TOPIC SECTION
    # --------------------------
    gr.Markdown("## 📘 Set Topic")
    with gr.Row():
        subject = gr.Dropdown(
            ["Mathematics", "Physics", "Chemistry", "Biology", "History", "Geography", "English", "CS"],
            label="Select Subject"
        )
        topic = gr.Textbox(label="Enter Topic (e.g., Integration, Motion, Genetics)")
        set_topic_btn = gr.Button("Start Topic")

    topic_output = gr.Markdown("")

    set_topic_btn.click(
        start_topic,
        inputs=[subject, topic, state],
        outputs=[topic_output, state]
    )

    # --------------------------
    # TUTOR CHAT SECTION
    # --------------------------
    gr.Markdown("---")
    gr.Markdown("## 💬 Tutor Chat")

    user_msg = gr.Textbox(label="Ask a question")
    send_btn = gr.Button("Send")
    chat_output = gr.Markdown("")

    send_btn.click(
        tutor_chat,
        inputs=[user_msg, state],
        outputs=[chat_output, state]
    )

    # --------------------------
    # RECOMMENDATIONS SECTION
    # --------------------------
    gr.Markdown("---")
    gr.Markdown("## ⭐ Smart Study Recommendations")

    with gr.Row():
        filter_subject = gr.Dropdown(
            ["All Subjects", "Mathematics", "Physics", "Chemistry", "Biology", "History", "Geography", "English", "CS"],
            label="Filter by subject"
        )
        difficulty = gr.Dropdown(["Any", "Easy", "Medium", "Hard"], label="Difficulty")

    rec_output = gr.Markdown("")
    rec_btn = gr.Button("Show Recommendations")

    rec_btn.click(
        get_recommendations,
        inputs=[filter_subject, difficulty, state],
        outputs=rec_output
    )

    # --------------------------
    # PRACTICE PROBLEM SECTION
    # --------------------------
    gr.Markdown("---")
    gr.Markdown("## 📝 Practice Questions")

    skill_list = list(skill_agent.estimate_from_history([]).keys())
    skill_select = gr.Dropdown(sorted(skill_list), label="Choose Skill")

    pq_btn = gr.Button("Get Practice Question")
    pq_output = gr.Markdown("")

    pq_btn.click(
        get_practice_question,
        inputs=[skill_select, state],
        outputs=[pq_output, state]
    )

demo.launch()
