import os
import urllib.error
import urllib.request
from pathlib import Path

from flask import Flask, abort, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "procedimentos.json"
ENV_FILE = BASE_DIR / ".env"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

app = Flask(__name__)


def load_local_env():
    if not ENV_FILE.exists():
        return

    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_local_env()
GROQ_MODEL = os.getenv("GROQ_MODEL", os.getenv("XAI_MODEL", "llama-3.1-8b-instant"))


def load_data():
    return app.json.loads(DATA_FILE.read_text(encoding="utf-8"))


def get_especialidade(data, especialidade_id):
    return next(
        (item for item in data["especialidades"] if item["id"] == especialidade_id),
        None,
    )


def get_procedimento(data, procedimento_id):
    for especialidade in data["especialidades"]:
        for procedimento in especialidade["procedimentos"]:
            if procedimento["id"] == procedimento_id:
                return especialidade, procedimento
    return None, None


def format_procedimento_context(especialidade, procedimento):
    complicacoes = "\n".join(
        f"- {item['titulo']} ({item['severidade']}): {item['descricao']}"
        for item in procedimento["complicacoes"]
    )
    evolucao = "\n".join(f"- {item}" for item in procedimento["evolucao"])
    cuidados = "\n".join(f"- {item}" for item in procedimento["cuidados"])
    cronograma = "\n".join(
        f"- {item['periodo']}: {item['orientacao']}"
        for item in procedimento["cronograma"]
    )
    alertas = "\n".join(f"- {item}" for item in procedimento["alertas"])

    return f"""
Especialidade: {especialidade['nome']}
Procedimento: {procedimento['nome']}
Resumo: {procedimento['resumo']}

Complicações possíveis:
{complicacoes}

Evolução normal:
{evolucao}

Cuidados essenciais:
{cuidados}

Cronograma de recuperação:
{cronograma}

Sinais de alerta:
{alertas}
""".strip()


def format_general_context(data):
    especialidades = []
    procedimentos = []

    for especialidade in data["especialidades"]:
        especialidades.append(f"- {especialidade['nome']}: {especialidade['descricao']}")
        for procedimento in especialidade["procedimentos"]:
            procedimentos.append(
                f"- {procedimento['nome']} ({especialidade['nome']}): {procedimento['resumo']}"
            )

    return f"""
Escopo geral do Infodonto:
O assistente pode responder duvidas gerais sobre odontologia, cuidados bucais,
orientacoes pos-atendimento, recuperacao, prevencao, sinais de alerta e quando
procurar atendimento odontologico.

Especialidades cadastradas:
{chr(10).join(especialidades)}

Procedimentos cadastrados no portal:
{chr(10).join(procedimentos)}
""".strip()


def call_groq(pergunta, contexto):
    api_key = os.getenv("GROQ_API_KEY", os.getenv("XAI_API_KEY", "")).strip()
    model = os.getenv("GROQ_MODEL", os.getenv("XAI_MODEL", GROQ_MODEL)).strip() or GROQ_MODEL

    if not api_key:
        return {
            "status": "missing_api_key",
            "message": (
                "O chat já está pronto para usar a Groq. Configure a variável "
                "GROQ_API_KEY no arquivo .env e reinicie o Flask para ativar a IA."
            ),
        }

    payload = {
        "model": model,
        "temperature": 0.2,
        "max_tokens": 450,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Você é o Assistente Virtual do Infodonto, um portal acadêmico "
                    "de orientações odontológicas. Responda em português do Brasil, "
                    "com tom claro, clínico e acolhedor. Você pode responder dúvidas "
                    "gerais sobre odontologia e, quando houver um procedimento no "
                    "contexto, priorize as orientações específicas dele. Não diagnostique, "
                    "não prescreva medicamentos, não substitua avaliação profissional e "
                    "não invente informações. Se a pergunta indicar dor intensa, febre, "
                    "sangramento persistente, pus, falta de ar, trauma ou outro sinal de "
                    "alerta, oriente procurar atendimento odontológico."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Contexto disponível:\n{contexto}\n\n"
                    f"Pergunta do paciente:\n{pergunta}"
                ),
            },
        ],
    }

    req = urllib.request.Request(
        GROQ_API_URL,
        data=app.json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "InfOdonto/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            data = app.json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        app.logger.warning("Erro HTTP na API Groq: %s %s", exc.code, detail)
        detail_lower = detail.lower()
        if "incorrect api key" in detail_lower or "invalid api key" in detail_lower:
            return {
                "status": "api_error",
                "message": "A chave da API Groq no arquivo .env está inválida. Gere uma nova chave no console da Groq, atualize GROQ_API_KEY e reinicie o servidor.",
            }
        if "model" in detail_lower and ("not found" in detail_lower or "invalid" in detail_lower):
            return {
                "status": "api_error",
                "message": "O modelo configurado em GROQ_MODEL não foi aceito pela API Groq. Verifique o nome do modelo no console da Groq e reinicie o servidor.",
            }
        return {
            "status": "api_error",
            "message": "Não consegui consultar a Groq agora. Verifique a chave, o modelo configurado e tente novamente.",
        }
    except urllib.error.URLError as exc:
        app.logger.warning("Erro de conexão com a API Groq: %s", exc)
        return {
            "status": "api_error",
            "message": "Não consegui conectar à API da Groq agora. Confira sua internet e tente novamente.",
        }

    answer = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
        .strip()
    )

    if not answer:
        return {
            "status": "empty_response",
            "message": "A Groq não retornou uma resposta utilizável. Tente reformular a pergunta.",
        }

    return {"status": "ok", "message": answer}


@app.get("/")
def index():
    data = load_data()
    return render_template(
        "index.html",
        especialidades=data["especialidades"],
        active_especialidade=None,
        procedimentos=None,
    )


@app.get("/especialidade/<especialidade_id>")
def especialidade(especialidade_id):
    data = load_data()
    selected = get_especialidade(data, especialidade_id)
    if selected is None:
        abort(404)

    return render_template(
        "index.html",
        especialidades=data["especialidades"],
        active_especialidade=selected,
        procedimentos=selected["procedimentos"],
    )


@app.get("/procedimento/<procedimento_id>")
def procedimento(procedimento_id):
    data = load_data()
    especialidade, selected = get_procedimento(data, procedimento_id)
    if selected is None:
        abort(404)

    return render_template(
        "procedimento.html",
        especialidade=especialidade,
        procedimento=selected,
    )


@app.get("/api/procedimentos")
def api_procedimentos():
    return jsonify(load_data())


@app.post("/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    pergunta = payload.get("message", "").strip()
    procedimento_id = payload.get("procedimento_id", "").strip()

    if not pergunta:
        return jsonify(
            {
                "status": "invalid_request",
                "message": "Digite uma pergunta para o assistente responder.",
            }
        ), 400

    data = load_data()
    contexto = format_general_context(data)

    if procedimento_id:
        especialidade, selected = get_procedimento(data, procedimento_id)
        if selected is not None:
            contexto = format_procedimento_context(especialidade, selected)

    result = call_groq(pergunta, contexto)
    return jsonify({**result, "received": pergunta})


if __name__ == "__main__":
    app.run(debug=True)
