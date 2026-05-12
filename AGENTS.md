# Instrucoes Do Codex Para Este Repositorio

## Contexto Do Projeto

Este projeto e um diario de treino com bot do Telegram e banco SQLite versionado.

Banco principal: `data/ironforge.db`.
Launcher multiplataforma: `start_bot.py`.
Wrapper Windows: `start_bot.bat`.

## Padrao De Idioma

A interface principal do projeto deve ser em PT-BR:

- comandos do Telegram
- mensagens do bot
- documentacao de uso
- mensagens dos launchers
- textos futuros visiveis ao usuario

Aliases antigos em ingles podem continuar existindo para compatibilidade, mas a
documentacao e a ajuda principal devem mostrar os comandos em PT-BR.

## Modulos Principais

Os modulos de runtime ficam no pacote `ironforge/`. Importe codigo de aplicacao
a partir desse pacote, por exemplo `from ironforge import db_ops`.

### `ironforge/telegram_poller.py`

Bot Telegram usado para controlar o treino pelo celular.

Comandos principais:

- `/gerar`
- `/exercicios`
- `/aquecimento`
- `/volume`
- `/status`
- `/desfazer`
- `/ajuda`
- `80` ou `80 8` para registrar carga e RPE opcional

Aliases legados em ingles podem ser aceitos:

- `/generate`
- `/exercises`
- `/warmup`
- `/undo`
- `/help`

Fluxo:

1. `/gerar` cria uma sessao de treino no SQLite e reseta o arquivo de sessao ativa.
2. Entrada de carga e escrita diretamente no SQLite.
3. `/desfazer` limpa o ultimo exercicio registrado.

### `ironforge/ods_ops.py`

Camada auxiliar de sessao de treino.

Funcoes importantes:

- `generate_training()` cria uma sessao SQLite e retorna `(exercises, session_id)`.
- `gerar_treino()` e alias de compatibilidade para scripts locais antigos.
- `read_exercises()` le do SQLite.
- `read_previous_weights()` retorna a carga mais recente por exercicio.
- `write_session()` escreve `session.json`.

Regras importantes:

- Indices ativos: `TRAINING_EXERCISES = range(0, 13)`.
- Manter `TREINO_EXERCISES` apenas como alias de compatibilidade.
- O primeiro exercicio ativo e `Agachamento Zercher` (`3x5`).
- Logs historicos de `Agachamento (barra)` ou `Zercher squat` podem permanecer como historico.

### `ironforge/db_ops.py`

Modulo SQLite para exercicios, logs de treino e dados de dieta.

- Banco versionado: `data/ironforge.db`.
- Tabela principal de exercicios: `exercises` (`name`, `sets`, `reps`, `sort_order`, `active`).
- SQLite e a fonte da verdade para exercicios.
- Mudancas de catalogo que devem valer para bancos novos tambem precisam atualizar `DEFAULT_EXERCISES`.

## Estado Local

Arquivos locais e secretos nao sao versionados:

- `session.json`
- `.env` (`TELEGRAM_TOKEN=...`)

Arquivos auxiliares SQLite nao sao versionados:

- `data/*.db-shm`
- `data/*.db-wal`

Nao versionar segredos. Antes de alterar arquivos de estado local, verificar se a mudanca e necessaria.

## Diretrizes De Mudanca

- Preferir mudancas cirurgicas compativeis com o fluxo atual.
- Manter SQLite como fonte da verdade dos exercicios.
- Preservar a diferenca entre estado local e dados versionados.
- Preferir helpers existentes antes de criar novas abstracoes.

## Padrao De Commit

Usar Conventional Commits no titulo:

`feat: add sync command`

Requisitos:

- Titulo no formato `<type>: <title>` (`feat`, `fix`, `refactor`, `docs`, etc.).
- Corpo do commit e obrigatorio.
- Corpo deve explicar contexto tecnico, escopo e motivo da decisao.
