# Instruções do Copilot para este repositório

## Contexto do projeto

Este projeto é um log de treino em LibreOffice Calc (ODS) com integração Telegram para registrar cargas durante o treino.  
Arquivo principal: `log-de-treino-e-progressao.ods`.

## Arquivos principais

### `ods_ops.py`
Manipula o ODS diretamente via XML (`zipfile` + regex).

Funções-chave:
- `gerar_treino(treino_type)` — insere linhas na aba TREINOS e retorna `{row, name, sets, reps}`
- `update_row_weights(row_0idx, carga, rpe)` — atualiza colunas G/H
- `read_exercises()` — lê aba EXERCICIOS
- `read_previous_weights()` — busca última carga por exercício
- `write_session()` / `clear_pending()` — gerencia `session.json` e `pending_log.csv`
- `is_ods_locked()` — detecta lock do LibreOffice (`.~lock.*#`)

Regras importantes:
- Índices de exercícios: `TREINO_EXERCISES = range(0, 14)`
- Numeração de linhas:
  - `r = n_data + 2 + idx` (1-based no spreadsheet)
  - `row_0idx = r - 1` (0-based para API)
- Fórmulas ODS em `content.xml`:
  - Prefixo obrigatório `of:`
  - Referências como `[.A1]`, `[.$D$2]`, `[$EXERCICIOS.A:.A]`
  - Separador de argumentos: `;` (locale pt-BR)
- Estilos confirmados:
  - `ce22` (data), `ce9` (semana), `ce71` (tipo treino), `ce16` (exercício)
  - `ce20` (fórmula), `ce25` (carga/RPE), `ce65` (trailing)
  - Não usar `ce2` para data (não existe no ODS deste projeto)

### `telegram_poller.py`
Bot Telegram para controlar o treino sem abrir o PC.

Comandos:
- `/gerar A`
- `/sync`
- `80` ou `80 8`
- `/status`
- `/undo`
- `/help`

Fluxo:
1. `/gerar A` gera treino no ODS e reinicia pendências.
2. Entrada de carga salva sempre em `pending_log.csv` e tenta gravar no ODS.
3. Se ODS estiver aberto, fechar o arquivo e usar `/sync` no Telegram para sincronizar.

## Estado local (não versionar)

- `session.json`
- `pending_log.csv`
- `.env` (`TELEGRAM_TOKEN=...`)

## Fluxo sem macro

O fluxo de macro no LibreOffice foi descontinuado neste repositório.
Toda geração e sincronização de treino deve acontecer via comandos do bot Telegram (`/gerar` e `/sync`).

## Aba EXERCICIOS

Sem cabeçalho. Linhas 1–14, colunas:
- A = Exercício
- B = Séries
- C = Reps

## Dependências e execução

- Dependências Python: `requests`, `openpyxl`
- Executar bot: `python telegram_poller.py`
- LibreOffice: `C:\Program Files\LibreOffice\program\soffice.exe`

## Diretrizes para alterações

- Priorizar mudanças cirúrgicas e compatíveis com o fluxo atual.
- Não quebrar o comportamento de lock/sincronização (`is_ods_locked` + `pending_log.csv`).
- Manter consistência de índices 0-based (API) x linhas 1-based (planilha).
- Em fórmulas ODS, preservar sintaxe `of:` e separador `;`.

## Padrão de commit

Adote Conventional Commits no cabeçalho, com tipo e título objetivo:

`feat: adiciona comando de sincronização`

Requisitos:
- O cabeçalho deve seguir `<tipo>: <titulo>` (ex.: `feat`, `fix`, `refactor`, `chore`).
- O corpo da mensagem é obrigatório.
- O corpo deve registrar contexto técnico, escopo da alteração e motivo da decisão.
