import os, json, uuid
from typing import List, Dict, Any, Tuple

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma

from pydantic import BaseModel, Field, ValidationError

# --------- Schema ----------
class QuizQuestion(BaseModel):
    id: str
    subject: str
    topic: str
    difficulty: str
    stem: str
    options: Dict[str, str]
    correct: str
    explanation: str

class QuizPayload(BaseModel):
    subject: str
    questions: List[QuizQuestion]

# --------- Vectorstore ----------
def get_vectorstore(persist_dir: str):
    os.makedirs(persist_dir, exist_ok=True)
    return Chroma(
        persist_directory=persist_dir,
        embedding_function=OpenAIEmbeddings()
    )

# --------- Generate Quiz with RAG ----------
def generate_quiz_with_rag(
    subject: str,
    n_questions: int,
    difficulty: str,
    persist_dir: str
) -> Dict[str, Any]:
    vs = get_vectorstore(persist_dir)

    # filtra documentos pela matéria (depende do metadata["subject"])
    retriever = vs.as_retriever(
        search_kwargs={"k": 8, "filter": {"subject": subject.lower()}}
    )

    # pega contexto “estilo ENEM” da própria matéria
    docs = retriever.invoke(f"Questões ENEM {subject} nível {difficulty}. Gere questões de múltipla escolha.")
    context = "\n\n".join([d.page_content for d in docs])

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4)

    # IMPORTANTE: força JSON puro
    prompt = f"""
Você é um gerador de questões no estilo ENEM.
Use SOMENTE o contexto abaixo como referência de estilo e conteúdo.
Não copie frases longas literalmente. Crie questões originais, porém similares.

Regras:
- Gere EXATAMENTE {n_questions} questões.
- Cada questão deve ter alternativas A, B, C, D, E (todas preenchidas).
- Apenas uma alternativa correta.
- Retorne SOMENTE um JSON válido (sem markdown, sem texto extra).

Formato JSON:
{{
  "subject": "{subject}",
  "questions": [
    {{
      "id": "Q1",
      "subject": "{subject}",
      "topic": "tópico curto",
      "difficulty": "{difficulty}",
      "stem": "enunciado",
      "options": {{"A":"...","B":"...","C":"...","D":"...","E":"..."}},
      "correct": "A",
      "explanation": "explicação curta do gabarito"
    }}
  ]
}}

Contexto:
\"\"\"{context[:12000]}\"\"\"
"""

    raw = llm.invoke(prompt).content.strip()

    # tenta carregar JSON
    data = json.loads(raw)

    # valida schema
    payload = QuizPayload(**data)

    # normaliza ids únicos
    for i, q in enumerate(payload.questions, start=1):
        q.id = f"{subject[:3].upper()}-{i}-{uuid.uuid4().hex[:6]}"
        q.subject = subject

        # valida opções
        for letter in ["A","B","C","D","E"]:
            if letter not in q.options:
                raise ValueError(f"Questão sem alternativa {letter}")
        if q.correct not in ["A","B","C","D","E"]:
            raise ValueError("Campo correct inválido")

    return payload.model_dump()

def grade_quiz(quiz: Dict[str, Any], answers: Dict[str, str]) -> Tuple[int, List[Dict[str, Any]]]:
    questions = quiz["questions"]
    score = 0
    feedback = []

    for q in questions:
        qid = q["id"]
        marked = answers.get(qid)
        correct = q["correct"]
        ok = (marked == correct)
        if ok:
            score += 1

        feedback.append({
            "id": qid,
            "marked": marked,
            "correct": correct,
            "is_correct": ok,
            "explanation": q["explanation"],
            "stem": q["stem"]
        })

    return score, feedback
