# Instrucoes do Codex para este repositorio

## Contexto do projeto

Este projeto e um log de treino em LibreOffice Calc (ODS) com integracao Telegram para registrar cargas durante o treino.
Arquivo principal: `log-de-treino-e-progressao.ods`.

## Arquivos principais

### `ods_ops.py`

Manipula o ODS diretamente via XML (`zipfile` + regex).

Funcoes-chave:
- `gerar_treino()` - insere linhas na aba TREINOS e retorna `{row, name, sets, reps}`
- `update_row_weights(row_0idx, carga, rpe)` - atualiza colunas G/H
- `read_exercises()` - le do SQLite (`data/ironforge.db`)
- `read_previous_weights()` - busca ultima carga por exercicio
- `write_session()` / `clear_pending()` - gerencia `session.json` e `pending_log.csv`
- `is_ods_locked()` - detecta lock do LibreOffice (`.~lock.*#`)

Regras importantes:
- Indices de exercicios: `TREINO_EXERCISES = range(0, 13)`
- Numeracao de linhas:
  - `r = n_data + 2 + idx` (1-based no spreadsheet)
  - `row_0idx = r - 1` (0-based para API)
- Formulas ODS em `content.xml`:
  - Prefixo obrigatorio `of:`
  - Referencias como `[.A1]`, `[.$D$2]`
  - Separador de argumentos: `;` (locale pt-BR)
- Estilos confirmados:
  - `ce22` (data), `ce9` (semana), `ce71` (tipo treino), `ce16` (exercicio)
  - `ce20` (formula), `ce25` (carga/RPE), `ce65` (trailing)
  - Nao usar `ce2` para data (nao existe no ODS deste projeto)

### `telegram_poller.py`

Bot Telegram para controlar o treino sem abrir o PC.

Comandos:
- `/gerar`
- `/exercicios`
- `/lista`
- `/sync`
- `/aquecimento`
- `/volume`
- `80` ou `80 8`
- `/status`
- `/undo`
- `/help`

Fluxo:
1. `/gerar` gera treino no ODS e reinicia pendencias.
2. Entrada de carga salva sempre em `pending_log.csv` e tenta gravar no ODS.
3. Se ODS estiver aberto, fechar o arquivo e usar `/sync` no Telegram para sincronizar.

### `db_ops.py`

Modulo SQLite para a lista de exercicios.

- Banco local versionado: `data/ironforge.db`
- Tabela principal: `exercises` (`name`, `sets`, `reps`, `sort_order`, `active`)
- Sem dependencia da aba `EXERCICIOS` no ODS

## Estado local

Arquivos locais de estado e segredo, nao versionados:
- `session.json`
- `pending_log.csv`
- `.env` (`TELEGRAM_TOKEN=...`)

Arquivos SQLite auxiliares nao versionados:
- `data/*.db-shm`
- `data/*.db-wal`

O banco `data/ironforge.db` e versionado e contem o catalogo de exercicios. Nao versionar segredos. Antes de alterar arquivos de estado, verifique se a mudanca e realmente necessaria para a tarefa.

## Fluxo sem macro

O fluxo de macro no LibreOffice foi descontinuado neste repositorio.
Toda geracao e sincronizacao de treino deve acontecer via comandos do bot Telegram (`/gerar` e `/sync`).

## Lista de exercicios (SQLite)

Fonte unica: tabela `exercises` no banco `data/ironforge.db`.

Ordem atual (linhas 1-13):
1. Agachamento (barra) - 3x5
2. Supino reto (barra) - 3x5
3. Remada curvada (barra) - 3x8
4. Desenvolvimento (barra em pe) - 3x5
5. Stiff com barra - 3x8
6. Pullover (barra) - 3x10
7. Remada alta (barra) - 3x10
8. Crucifixo invertido - 3x10
9. Encolhimento com barra - 2x10
10. Rosca direta - 3x8
11. Triceps testa - 3x8
12. Wrist curl (barra) - 2x15
13. Reverse wrist curl (barra) - 2x15

## Dependencias e execucao

- Dependencias Python: `requests`
- Biblioteca padrao usada no projeto: `sqlite3`, `zipfile`, `re`, `shutil`, `json`, `datetime`, `pathlib`, `time`
- Executar bot: `python telegram_poller.py`
- LibreOffice: `C:\Program Files\LibreOffice\program\soffice.exe`

## Diretrizes para alteracoes

- Priorizar mudancas cirurgicas e compativeis com o fluxo atual.
- Nao quebrar o comportamento de lock/sincronizacao (`is_ods_locked` + `pending_log.csv`).
- Manter consistencia de indices 0-based (API) x linhas 1-based (planilha).
- Em formulas ODS, preservar sintaxe `of:` e separador `;`.
- Para manipulacao estruturada do ODS, preferir APIs e helpers existentes neste repositorio antes de editar XML manualmente.
- Nao substituir o SQLite pela aba `EXERCICIOS`; a fonte unica de exercicios e `data/ironforge.db`.

## Padrao de commit

Adote Conventional Commits no cabecalho, com tipo e titulo objetivo:

`feat: adiciona comando de sincronizacao`

Requisitos:
- O cabecalho deve seguir `<tipo>: <titulo>` (ex.: `feat`, `fix`, `refactor`, `chore`).
- O corpo da mensagem e obrigatorio.
- O corpo deve registrar contexto tecnico, escopo da alteracao e motivo da decisao.
