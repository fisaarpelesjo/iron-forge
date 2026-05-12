# Banco De Dados

IronForge usa SQLite.

Arquivo principal:

```text
data/ironforge.db
```

Esse banco e versionado e e a fonte da verdade para exercicios, sessoes, logs e
dados de dieta.

## Modulo SQLite

Todo acesso direto ao banco fica em:

```text
ironforge/db_ops.py
```

`DB_PATH` aponta para `data/ironforge.db` na raiz do repositorio.

## Tabelas

### `exercises`

Catalogo de exercicios.

```text
id          INTEGER PRIMARY KEY AUTOINCREMENT
name        TEXT NOT NULL UNIQUE
sets        INTEGER NOT NULL
reps        INTEGER NOT NULL
sort_order  INTEGER NOT NULL UNIQUE
active      INTEGER NOT NULL DEFAULT 1
```

### `training_sessions`

Uma linha por sessao gerada.

```text
id             INTEGER PRIMARY KEY AUTOINCREMENT
date           TEXT NOT NULL
training_type  TEXT NOT NULL DEFAULT 'TREINO'
```

### `training_logs`

Uma linha por exercicio dentro de uma sessao.

```text
id             INTEGER PRIMARY KEY AUTOINCREMENT
session_id     INTEGER NOT NULL REFERENCES training_sessions(id)
exercise_name  TEXT NOT NULL
sets           INTEGER NOT NULL
reps           INTEGER NOT NULL
weight         REAL
rpe            REAL
sort_order     INTEGER NOT NULL DEFAULT 0
```

`weight` e `rpe` comecam como `NULL`. A entrada `80 8` preenche a proxima linha
pendente da sessao ativa.

### Dieta

Tambem existem:

- `foods`
- `diet_targets`
- `diet_entries`

Essas tabelas guardam alimentos, metas e entradas de dieta.

## Catalogo Atual

Primeiro exercicio ativo:

```text
sort_order 1
name       Agachamento Zercher
sets       3
reps       5
```

Ele substituiu o agachamento com barra para sessoes futuras por falta de rack.
Historico antigo deve permanecer como historico salvo no SQLite.

Ao mudar o catalogo para frente, atualize:

- `data/ironforge.db`
- `ironforge/db_ops.py`, em `DEFAULT_EXERCISES`

## Criacao De Sessao

```text
ods_ops.generate_training()
  -> ods_ops.read_exercises()
     -> db_ops.get_or_seed_exercises()
  -> seleciona TRAINING_EXERCISES = range(0, 13)
  -> db_ops.create_session(today)
  -> db_ops.log_exercise(...) para cada exercicio
```

`session.json` guarda `session_id` e `log_id` para o bot saber qual linha
atualizar quando o usuario envia carga.

## Progresso

`count_filled(log_ids)` conta quantos logs tem `weight IS NOT NULL`.

```text
filled = 0  -> proximo exercicio exercises[0]
filled = 1  -> proximo exercicio exercises[1]
filled = 13 -> treino completo
```

## Inspecao Segura

```bash
sqlite3 data/ironforge.db ".tables"
sqlite3 data/ironforge.db ".schema exercises"
sqlite3 data/ironforge.db "SELECT name, sets, reps FROM exercises ORDER BY sort_order;"
```

## Nao Versionar

```text
data/*.db-shm
data/*.db-wal
session.json
.env
temp/
```

## Isolamento Dos Testes

O E2E troca temporariamente `DB_PATH`, `DATA_DIR`, `SESSION_FILE` e `send` para
nao tocar no banco real nem chamar Telegram.
