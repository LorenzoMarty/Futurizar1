import streamlit as st
from dotenv import load_dotenv

from src.ingest import load_documents_by_subject
from src.rag_generate import get_vectorstore, generate_quiz_with_rag, grade_quiz
from src.db import init_db, save_quiz, save_attempt, list_attempts, load_attempt

load_dotenv()
init_db()

st.set_page_config(page_title="Futurizar — Simulados ENEM", page_icon="📝", layout="wide")
st.title("📝 Futurizar — Estude para o ENEM com IA")

# -----------------------------
# Config
# -----------------------------
SUBJECTS = {
    "Matemática": "matematica",
    "Linguagens": "linguagens",
    "Humanas": "humanas",
    "Natureza": "natureza",
}

DIFFICULTIES = ["facil", "medio", "dificil"]

BASE_DOCS_DIR = "data/docs"
PERSIST_DIR = "storage/chroma"

# -----------------------------
# Sidebar: Navegação
# -----------------------------
page = st.sidebar.radio("Navegação", ["Fazer Simulado", "Histórico & Revisão"])

st.sidebar.markdown("---")
st.sidebar.caption("Desenvolvido por Lorenzo")

# -----------------------------
# Helpers
# -----------------------------
def reset_current_quiz():
    st.session_state.pop("current_quiz", None)
    st.session_state.pop("current_quiz_id", None)
    st.session_state.pop("current_subject", None)
    st.session_state.pop("current_answers", None)
    st.session_state.pop("last_feedback", None)
    st.session_state.pop("last_score", None)
    st.session_state.pop("last_total", None)

# -----------------------------
# PAGE 1: Fazer Simulado
# -----------------------------
if page == "Fazer Simulado":
    st.subheader("Gerar simulado")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        subj_label = st.selectbox("Matéria", list(SUBJECTS.keys()), index=0)
        subj = SUBJECTS[subj_label]

    with col2:
        difficulty = st.selectbox("Dificuldade", DIFFICULTIES, index=1)

    with col3:
        n_questions = st.number_input("Nº de questões", min_value=3, max_value=30, value=8, step=1)

    gen_col1, gen_col2 = st.columns([1, 3])
    with gen_col1:
        if st.button("✨ Gerar simulado", use_container_width=True):
            with st.spinner("Gerando questões..."):
                quiz = generate_quiz_with_rag(
                    subject=subj_label,
                    n_questions=int(n_questions),
                    difficulty=difficulty,
                    persist_dir=PERSIST_DIR
                )
                quiz_id = save_quiz(subj_label, quiz)

                st.session_state["current_quiz"] = quiz
                st.session_state["current_quiz_id"] = quiz_id
                st.session_state["current_subject"] = subj_label
                st.session_state["current_answers"] = {}

                st.session_state.pop("last_feedback", None)
                st.session_state.pop("last_score", None)
                st.session_state.pop("last_total", None)

    st.markdown("---")

    # Mostrar quiz e formulário
    quiz = st.session_state.get("current_quiz")
    if not quiz:
        st.warning("Nenhum simulado gerado ainda. Clique em **Gerar simulado**.")
        st.stop()

    st.subheader("2) Responder simulado")

    questions = quiz.get("questions", [])
    if not questions:
        st.error("Simulado vazio. Tente gerar novamente.")
        st.stop()

    with st.form("quiz_form"):
        for idx, q in enumerate(questions, start=1):
            st.markdown(f"### Questão {idx}")
            st.write(q["stem"])

            opts = q["options"]
            choices = [f"{k}) {opts[k]}" for k in ["A", "B", "C", "D", "E"]]

            # valor inicial (se usuário recarregar)
            prev = st.session_state["current_answers"].get(q["id"])
            if prev in ["A","B","C","D","E"]:
                default_index = ["A","B","C","D","E"].index(prev)
            else:
                default_index = 0

            selected = st.radio(
                "Escolha uma alternativa",
                options=choices,
                index=default_index,
                key=f"q_{q['id']}"
            )

            marked_letter = selected.split(")")[0].strip()
            st.session_state["current_answers"][q["id"]] = marked_letter

            st.markdown("---")

        submitted = st.form_submit_button("✅ Finalizar e corrigir")

    if submitted:
        answers = st.session_state.get("current_answers", {})
        score, feedback = grade_quiz(quiz, answers)

        attempt_id = save_attempt(
            quiz_id=st.session_state["current_quiz_id"],
            answers=answers,
            score=score,
            feedback=feedback
        )

        st.session_state["last_score"] = score
        st.session_state["last_total"] = len(questions)
        st.session_state["last_feedback"] = feedback
        st.session_state["last_attempt_id"] = attempt_id

        st.success(f"Simulado corrigido e salvo! Nota: {score}/{len(questions)} (tentativa #{attempt_id})")

    # Mostrar feedback se existir
    if st.session_state.get("last_feedback"):
        st.subheader("3) Feedback (explicando seus erros)")

        score = st.session_state["last_score"]
        total = st.session_state["last_total"]
        st.metric("Resultado", f"{score}/{total}")

        for idx, fb in enumerate(st.session_state["last_feedback"], start=1):
            status = "✅ Correta" if fb["is_correct"] else "❌ Incorreta"
            st.markdown(f"### Questão {idx} — {status}")
            st.write(fb["stem"])

            st.write(f"**Você marcou:** {fb['marked']}")
            st.write(f"**Correta:** {fb['correct']}")
            st.write(f"**Explicação:** {fb['explanation']}")
            st.markdown("---")

        colA, colB = st.columns([1, 1])
        with colA:
            if st.button("🔁 Gerar outro simulado"):
                reset_current_quiz()
                st.rerun()
        with colB:
            st.info("As tentativas ficam salvas em **Histórico e Revisão**.")

# -----------------------------
# PAGE 2: Histórico e Revisão
# -----------------------------
else:
    st.subheader("📚 Histórico de tentativas (para revisão futura)")

    rows = list_attempts(limit=30)
    if not rows:
        st.warning("Nenhuma tentativa salva ainda. Faça um simulado para aparecer aqui.")
        st.stop()

    # Seleção
    options = []
    for (attempt_id, quiz_id, submitted_at, score, subject) in rows:
        options.append(f"#{attempt_id} | {subject} | {score} pts | {submitted_at}")

    chosen = st.selectbox("Selecione uma tentativa", options, index=0)
    attempt_id = int(chosen.split("|")[0].strip().replace("#", ""))

    row = load_attempt(attempt_id)
    if not row:
        st.error("Tentativa não encontrada.")
        st.stop()

    (_, quiz_id, submitted_at, score, answers_json, feedback_json, quiz_json, subject) = row

    st.write(f"**Matéria:** {subject}")
    st.write(f"**Enviado em:** {submitted_at}")
    st.metric("Pontuação", score)

    import json
    quiz = json.loads(quiz_json)
    feedback = json.loads(feedback_json)

    st.markdown("---")
    st.subheader("Revisão (questão por questão)")

    for idx, fb in enumerate(feedback, start=1):
        status = "✅ Correta" if fb["is_correct"] else "❌ Incorreta"
        st.markdown(f"### Questão {idx} — {status}")
        st.write(fb["stem"])
        st.write(f"**Você marcou:** {fb['marked']}")
        st.write(f"**Correta:** {fb['correct']}")
        st.write(f"**Explicação:** {fb['explanation']}")
        st.markdown("---")
