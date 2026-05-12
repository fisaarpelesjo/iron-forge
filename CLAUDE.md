# Notas Do Repositorio

IronForge e um diario de treino com bot do Telegram e armazenamento SQLite.

## Modulos Principais

Os modulos de runtime ficam no pacote `ironforge/`. Importe codigo de aplicacao
com `from ironforge import db_ops`, `ods_ops` ou `telegram_poller`.

### `ironforge/telegram_poller.py`

Bot Telegram com long polling.

Comandos principais em PT-BR:

- `/gerar` cria uma sessao de treino e envia a tabela de exercicios.
- `/exercicios` lista exercicios atuais.
- `/aquecimento` mostra o aquecimento.
- `/volume` mostra series por grupo muscular.
- `/status` mostra progresso da sessao ativa.
- `/desfazer` limpa o ultimo exercicio registrado.
- `/ajuda` lista comandos.
- `80` ou `80 8` registra carga e RPE opcional.

Aliases antigos em ingles podem permanecer para compatibilidade.

### `ironforge/ods_ops.py`

Helpers de operacao de treino:

- `generate_training()` cria sessao e linhas de treino no SQLite.
- `gerar_treino()` permanece como alias de compatibilidade.
- `read_exercises()` le exercicios do SQLite.
- `read_previous_weights()` retorna cargas recentes do SQLite.
- `write_session()` escreve estado ativo em `session.json`.

Catalogo atual:

- Primeiro exercicio ativo: `Agachamento Zercher` (`3x5`).
- Substitui o agachamento com barra para sessoes futuras por falta de rack adequado.
- Logs historicos podem permanecer com nomes antigos.

### `ironforge/db_ops.py`

Operacoes SQLite:

- `get_or_seed_exercises()`
- `list_exercises()`
- `create_session()`
- `log_exercise()`
- `update_log_weight()`
- `get_last_weights()`
- `count_filled()`

## Dados E Estado

- Banco versionado: `data/ironforge.db`.
- Estado local: `session.json`, nao versionado.
- Configuracao secreta: `.env`, nao versionada.
- Sidecars SQLite (`*.db-shm`, `*.db-wal`) nao sao versionados.

SQLite e a fonte da verdade dos exercicios. Nao mover a gestao de exercicios de volta para ODS.
Mudancas de catalogo devem sincronizar `data/ironforge.db` e `ironforge/db_ops.py`
quando tambem precisarem valer para bancos novos.

## Estilo De Commit

Use Conventional Commits:

```text
feat: add sync command

Explique contexto tecnico, escopo e motivo da mudanca.
```
