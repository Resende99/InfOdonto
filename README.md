# Infodonto

Portal acadêmico de orientações pós-atendimento odontológico para pacientes.

O Infodonto permite que o paciente selecione uma especialidade odontológica, escolha o procedimento realizado e consulte informações sobre complicações possíveis, evolução normal da recuperação, cuidados essenciais, cronograma e sinais de alerta.

## Stack

- Front-end: HTML, CSS e JavaScript
- Back-end: Python com Flask
- Dados: arquivo JSON local
- Chatbot: endpoint preparado para integração com Grok/xAI
- Banco de dados: não utilizado nesta fase

## Funcionalidades

- Listagem de especialidades odontológicas
- Listagem de procedimentos por especialidade
- Página de detalhe do procedimento
- Abas para complicações, evolução normal e cuidados
- Badges de severidade: leve, moderado e atenção
- Sidebar com alertas e cronograma de recuperação
- Breadcrumb de navegação
- Botão flutuante de Assistente Virtual
- Endpoint `/chat` preparado para API de IA
- Deploy preparado para Vercel

## Especialidades

- Implantodontia
- Harmonização Orofacial
- Endodontia
- Cirurgia Oral
- Periodontia

## Estrutura

```text
InfOdonto/
|-- app.py
|-- data/
|   `-- procedimentos.json
|-- public/
|   `-- static/
|       |-- css/style.css
|       `-- js/main.js
|-- static/
|   |-- css/style.css
|   `-- js/main.js
|-- templates/
|   |-- index.html
|   `-- procedimento.html
|-- .env.example
|-- requirements.txt
|-- vercel.json
`-- README.md
```

## Como rodar localmente

1. Clone o repositório:

```bash
git clone https://github.com/Resende99/InfOdonto.git
cd InfOdonto
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:

```bash
cp .env.example .env
```

Edite o arquivo `.env`:

```env
XAI_API_KEY=sua_chave_da_xai
XAI_MODEL=grok-4
```

4. Rode o Flask:

```bash
python app.py
```

5. Acesse:

```text
http://127.0.0.1:5000/
```

## Rotas principais

```text
GET  /                          Página inicial
GET  /especialidade/<id>        Lista procedimentos da especialidade
GET  /procedimento/<id>         Detalhe do procedimento
GET  /api/procedimentos         Retorna o JSON de procedimentos
POST /chat                      Endpoint do assistente virtual
```

## Chatbot com Grok/xAI

O chatbot usa o conteúdo do procedimento selecionado como contexto. Ele foi configurado para responder apenas com base nas informações do Infodonto, sem diagnosticar, prescrever ou substituir avaliação profissional.

Variáveis necessárias:

```env
XAI_API_KEY=sua_chave_da_xai
XAI_MODEL=grok-4
```

Se `XAI_API_KEY` não estiver configurada, o endpoint `/chat` retorna uma mensagem informando que a chave ainda precisa ser adicionada.

## Deploy na Vercel

O projeto está preparado para deploy na Vercel.

1. Suba o projeto para o GitHub.
2. Importe o repositório na Vercel.
3. Configure as variáveis de ambiente no painel da Vercel:

```env
XAI_API_KEY=sua_chave_da_xai
XAI_MODEL=grok-4
```

4. Faça o deploy.

O arquivo `.env` real não deve ser enviado ao GitHub. Ele está protegido pelo `.gitignore`.

## Aviso acadêmico

Este projeto é acadêmico e informativo. As orientações apresentadas não substituem avaliação, diagnóstico ou acompanhamento por profissional habilitado.
