# Deploy do Infodonto na Vercel

## Antes de subir

1. Não envie o arquivo `.env` com sua chave real.
2. Suba o projeto para GitHub, GitLab ou Bitbucket.
3. Na Vercel, importe o repositório.

## Variáveis de ambiente

No painel da Vercel, configure:

```env
XAI_API_KEY=sua_chave_da_xai
XAI_MODEL=grok-4
```

## Build

A Vercel reconhece Flask automaticamente quando existe um `app.py` com a variável `app`.
O arquivo `.python-version` fixa Python 3.12 para evitar incompatibilidade de runtime.

## Arquivos estáticos

Os arquivos CSS e JS também foram copiados para `public/static`, que é o padrão recomendado pela Vercel para assets públicos.

## Teste pós-deploy

Depois do deploy, abra:

- `/`
- `/especialidade/implantodontia`
- `/procedimento/extracao-de-siso`
- `/api/procedimentos`

Depois teste o chat dentro de uma página de procedimento.
