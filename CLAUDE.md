# CLAUDE.md

## Projeto

Log de treino em LibreOffice Calc (ODS) com bot Telegram para registro de pesos durante o treino. Arquivo principal: `log-de-treino-e-progressao.ods`.

## Arquivos Python

### `ods_ops.py`
Módulo de manipulação direta do ODS via XML (zipfile + regex). Funções principais:

- `gerar_treino(treino_type)` — insere linhas na aba TREINOS, retorna lista de `{row, name, sets, reps}`
- `update_row_weights(row_0idx, carga, rpe)` — atualiza colunas G/H de uma linha existente
- `read_exercises()` — lê todos os exercícios da aba EXERCICIOS
- `read_previous_weights()` — retorna `{nome_exercicio: última_carga}` do histórico TREINOS
- `write_session(treino_type, exercises)` / `clear_pending()` — gerencia `session.json` / `pending_log.csv`
- `is_ods_locked()` — verifica se ODS está aberto no LibreOffice (arquivo `.~lock.*#`)

**Índices de exercícios (0-indexed):**
```python
TREINO_EXERCISES = range(0, 13)
```

**Numeração de linhas:**
- `r = n_data + 2 + idx` — número 1-based da linha no spreadsheet
- `row_0idx = r - 1` — índice 0-based para `getCellByPosition`

**Sintaxe de fórmulas ODS (content.xml):**
- Prefixo `of:` obrigatório: `table:formula="of:=IF(...)"`
- Referências: `[.A1]`, `[.$D$2]`, `[$EXERCICIOS.A:.A]`
- Separador de argumentos: ponto e vírgula (locale pt-BR)

**Estilos de célula confirmados (content.xml):**
- `ce22` = data (style:data-style-name="N120", date format), `ce9` = semana (fórmula), `ce71` = tipo treino, `ce16` = nome exercício
- `ce20` = células com fórmula, `ce25` = carga/RPE (número), `ce65` = trailing (repeat 16371)
- ATENÇÃO: `ce2` não existe no ODS → LibreOffice usa datetime padrão (bug). Usar `ce22` para datas.

### `telegram_poller.py`
Bot Telegram que permite controle total do treino pelo celular, sem abrir o PC.

**Comandos:**
- `/gerar A` — gera treino no ODS, envia tabela com exercícios e pesos anteriores
- `/sync` — aplica no ODS os registros pendentes de `pending_log.csv`
- `80` ou `80 8` — registra carga (e RPE) do próximo exercício pendente
- `/status` — mostra progresso da sessão atual
- `/undo` — desfaz último registro
- `/help` — lista comandos

**Fluxo de dados:**
1. `/gerar A` → `ods_ops.gerar_treino()` → grava `session.json`, apaga `pending_log.csv`
2. `80 8` → sempre salva em `pending_log.csv` + tenta gravar direto no ODS (se não estiver bloqueado)
3. Se ODS estiver aberto, fechar o arquivo e executar `/sync` no Telegram para aplicar o `pending_log.csv`

**Arquivos de estado (no .gitignore):**
- `session.json` — sessão ativa: treino, data, lista de exercícios com row index
- `pending_log.csv` — pesos pendentes: `row,carga,rpe` por linha
- `.env` — `TELEGRAM_TOKEN=...`

**Executar:**
```bash
python telegram_poller.py
```

## Arquivo ODS

Formato ZIP com XML interno. Para inspecionar estrutura:
```python
import zipfile
with zipfile.ZipFile("log-de-treino-e-progressao.ods") as z:
    print(z.namelist())
    content = z.read("content.xml").decode("utf-8")
```

## Estrutura da Aba EXERCICIOS

Sem cabeçalho. Linhas 1–13 = treino único.
Colunas: A=Exercicio, B=Series, C=Reps (1-indexed no spreadsheet, 0-indexed na API Basic/Python).

Ordem atual (linhas 1–13):
1. Agachamento (barra) — 3x5
2. Supino reto (barra) — 3x5
3. Remada curvada (barra) — 3x8
4. Desenvolvimento (barra em pé) — 3x5
5. Stiff com barra — 3x8
6. Pullover (barra) — 3x10
7. Elevação lateral — 3x10
8. Crucifixo invertido — 3x10
9. Encolhimento com barra — 2x10
10. Rosca direta — 3x8
11. Tríceps testa — 3x8
12. Wrist curl (barra) — 2x15
13. Reverse wrist curl (barra) — 2x15

## Dependências Python

- `requests` — chamadas Telegram API
- `openpyxl` — leitura do xlsx
- Biblioteca padrão: `zipfile`, `re`, `shutil`, `json`, `datetime`, `pathlib`

## Padrão de commit

Adote Conventional Commits no cabeçalho, com tipo e título objetivo:

`feat: adiciona comando de sincronização`

Requisitos:
- O cabeçalho deve seguir `<tipo>: <titulo>` (ex.: `feat`, `fix`, `refactor`, `chore`).
- O corpo da mensagem é obrigatório.
- O corpo deve registrar contexto técnico, escopo da alteração e motivo da decisão.
