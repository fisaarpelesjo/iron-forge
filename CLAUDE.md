# CLAUDE.md

## Projeto

Log de treino com bot Telegram para registro de pesos durante o treino. Dados armazenados em SQLite (`data/ironforge.db`). Arquivo `log-de-treino-e-progressao.ods` mantido apenas para outras abas — aba TREINOS removida.

## Arquivos Python

### `ods_ops.py`
Módulo de operações de treino (sem dependência de ODS para o diário).

- `gerar_treino()` — cria sessão no SQLite, retorna `(exercises, session_id)` onde exercises é lista de `{log_id, name, sets, reps}`
- `read_exercises()` — lê exercícios do SQLite
- `read_previous_weights()` — retorna `{nome_exercicio: última_carga}` do SQLite
- `write_session(exercises, session_id)` — grava `session.json`
- `MUSCLE_MAP` — mapeamento exercício → grupos musculares
- `TREINO_EXERCISES` — `range(0, 13)`, índices dos exercícios ativos

### `db_ops.py`
Módulo SQLite — fonte única de dados.

- Banco local: `data/ironforge.db`
- Tabelas:
  - `exercises` (`name`, `sets`, `reps`, `sort_order`, `active`)
  - `training_sessions` (`date`, `training_type`)
  - `training_logs` (`session_id`, `exercise_name`, `sets`, `reps`, `weight`, `rpe`, `sort_order`)
- Sem dependência de ODS

**Funções principais:**
- `create_session(date_iso, training_type='TREINO')` → `session_id`
- `log_exercise(session_id, name, sets, reps, sort_order)` → `log_id`
- `update_log_weight(log_id, weight, rpe=None)` — atualiza ou limpa (None) peso/RPE
- `get_last_weights()` → `{exercise_name: last_weight}`
- `count_filled(log_ids)` → int — quantos log_ids têm weight definido
- `import_log_rows(rows)` — importação em bulk (usado pela migração)

### `telegram_poller.py`
Bot Telegram.

**Comandos:**
- `/gerar` — cria sessão SQLite, envia tabela com exercícios e pesos anteriores
- `/exercicios` / `/lista` — lista exercícios atuais
- `/aquecimento` — lista de aquecimento recomendado
- `/volume` — séries por grupo muscular por sessão e estimativa semanal
- `80` ou `80 8` — registra carga (e RPE) no SQLite imediatamente
- `/status` — mostra progresso da sessão atual
- `/undo` — desfaz último registro (limpa weight/rpe no SQLite)
- `/help` — lista comandos

**Fluxo de dados:**
1. `/gerar` → `ods_ops.gerar_treino()` → cria sessão + logs no SQLite → grava `session.json`
2. `80 8` → `db_ops.update_log_weight(log_id, carga, rpe)` imediato
3. `/undo` → `db_ops.update_log_weight(log_id, None, None)` do último exercício preenchido

**Arquivos de estado:**
- `session.json` — sessão ativa: `{date, session_id, exercises: [{log_id, name, sets, reps}]}`
- `data/ironforge.db` — banco SQLite (versionado)
- `data/*.db-shm` / `data/*.db-wal` — auxiliares SQLite (não versionados)
- `.env` — `TELEGRAM_TOKEN=...`

**Executar:**
```bash
python telegram_poller.py
```

## Scripts utilitários

- `migrate_ods_to_db.py` — migração one-time do ODS TREINOS → SQLite (já executado)
- `remove_treinos_sheet.py` — remove aba TREINOS do ODS (já executado)

## Lista de exercícios (SQLite)

Fonte única: tabela `exercises` no banco `data/ironforge.db`.

Ordem atual (linhas 1–13):
1. Agachamento (barra) — 3x5
2. Supino reto (barra) — 3x5
3. Remada curvada (barra) — 3x8
4. Desenvolvimento (barra em pé) — 3x5
5. Stiff com barra — 3x8
6. Pullover (barra) — 3x10
7. Remada alta (barra) — 3x10
8. Crucifixo invertido — 3x10
9. Encolhimento com barra — 2x10
10. Rosca direta — 3x8
11. Tríceps testa — 3x8
12. Wrist curl (barra) — 2x15
13. Reverse wrist curl (barra) — 2x15

## Dependências Python

- `requests` — chamadas Telegram API
- Biblioteca padrão: `sqlite3`, `zipfile`, `re`, `shutil`, `json`, `datetime`, `pathlib`, `time`

## Padrão de commit

Adote Conventional Commits no cabeçalho, com tipo e título objetivo:

`feat: adiciona comando de sincronização`

Requisitos:
- O cabeçalho deve seguir `<tipo>: <titulo>` (ex.: `feat`, `fix`, `refactor`, `chore`).
- O corpo da mensagem é obrigatório.
- O corpo deve registrar contexto técnico, escopo da alteração e motivo da decisão.
