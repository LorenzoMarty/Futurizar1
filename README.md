# 🎓 Futurizar — Banco Inteligente de Questões ENEM com IA

**Futurizar** é uma plataforma educacional que utiliza **Inteligência Artificial** para gerar, corrigir e explicar **simulados no estilo ENEM**, com base **no próprio material de estudo do aluno** (PDFs/TXTs).

O sistema combina **LLMs (OpenAI)**, **RAG (Retrieval-Augmented Generation)**, **Streamlit** e **persistência em banco de dados**, permitindo prática ativa, feedback pedagógico e revisão histórica.

---

## 🚀 Funcionalidades

### 📚 Banco de questões inteligente
- Geração automática de questões **múltipla escolha (A–E)**
- Questões originais, inspiradas no conteúdo real dos PDFs

### 🧠 IA com RAG (baseada no material)
- A IA gera questões **somente a partir dos documentos indexados**
- Evita alucinação e mantém alinhamento pedagógico

### 📝 Simulados interativos
- Escolha da matéria, dificuldade e número de questões
- Interface estilo prova

### ✅ Correção automática
- Cálculo de nota
- Identificação de acertos e erros

### 💬 Feedback explicativo
- Explicação por questão
- Ajuda o aluno a entender o erro

### 🗂️ Histórico e revisão
- Simulados e tentativas ficam salvos
- Revisão posterior questão por questão

---

## 🧠 Como a IA é usada (visão de Engenharia)

### 1️⃣ Indexação (RAG)
- PDFs e textos são carregados por matéria
- O conteúdo é dividido em *chunks*
- Cada *chunk* é transformado em **embedding**
- Tudo é salvo em uma base vetorial (**Chroma**)

### 2️⃣ Geração de questões
- O sistema recupera trechos relevantes **apenas da matéria escolhida**
- Esses trechos são enviados ao LLM como **contexto**
- A IA gera questões originais em **formato estruturado (JSON)**

### 3️⃣ Correção e feedback
- A correção é determinística (resposta marcada vs correta)
- As explicações vêm do conteúdo gerado pela IA
- As tentativas são persistidas para revisão

> 🔒 **Sem documentos indexados**, o sistema funciona em modo genérico.  
> 📌 **Com documentos**, o Futurizar opera como **RAG real**, garantindo fidelidade ao material.

---

## 🏗️ Arquitetura do Projeto

```
Futurizar/
├── app.py                 # Interface Streamlit (UI)
├── src/
│   ├── ingest.py          # Ingestão e chunking de documentos
│   ├── rag_generate.py    # Geração de questões com RAG
│   ├── db.py              # Persistência (SQLite)
├── data/
│   └── docs/
│       ├── matematica/
│       ├── linguagens/
│       ├── humanas/
│       └── natureza/
├── storage/
│   └── chroma/            # Base vetorial persistida
├── futurizar.db           # Banco SQLite
├── requirements.txt
└── README.md
```

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+**
- **Streamlit** — Interface web
- **OpenAI (LLMs)** — Geração de questões e explicações
- **LangChain** — Orquestração de RAG
- **ChromaDB** — Base vetorial
- **SQLite** — Persistência de simulados e tentativas
- **Pydantic** — Validação de dados estruturados

---

## ▶️ Como rodar o projeto

### 1) Clonar o repositório
```bash
git clone https://github.com/LorenzoMarty/Futurizar.git
cd Futurizar
```

### 2) Criar ambiente virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate
```

### 3) Instalar dependências
```bash
pip install -r requirements.txt
```

### 4) Configurar variável de ambiente
Crie um arquivo `.env`:
```env
OPENAI_API_KEY=sua_chave_aqui
```

### 5) Adicionar materiais
Coloque PDFs/TXTs nas pastas:
```
data/docs/matematica/
data/docs/linguagens/
data/docs/humanas/
data/docs/natureza/
```

### 6) Executar
```bash
streamlit run app.py
```

---

## 🧪 Modo de uso

1. Indexe os documentos da matéria desejada  
2. Gere um simulado  
3. Responda às questões  
4. Finalize para correção e feedback  
5. Revise depois no histórico  

---

## 🎯 Objetivo do Projeto

O **Futurizar** foi desenvolvido como:
- 💡 Projeto de **portfólio em Engenharia de IA**
- 🎓 Ferramenta educacional focada no **ENEM**
- 🧪 Estudo prático de **RAG, LLMs e produtos com IA aplicada**

---

## 🔮 Próximas evoluções planejadas

- Feedback personalizado por erro (LLM pós-correção)
- Detecção de tópicos fracos do aluno
- Evitar repetição de questões
- Login de usuários
- Métricas de desempenho por matéria
- Deploy público
