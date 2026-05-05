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
TREINO_EXERCISES = range(0, 14)
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
- `80` ou `80 8` — registra carga (e RPE) do próximo exercício pendente
- `/status` — mostra progresso da sessão atual
- `/undo` — desfaz último registro
- `/help` — lista comandos

**Fluxo de dados:**
1. `/gerar A` → `ods_ops.gerar_treino()` → grava `session.json`, apaga `pending_log.csv`
2. `80 8` → sempre salva em `pending_log.csv` + tenta gravar direto no ODS (se não estiver bloqueado)
3. Se ODS estiver aberto, usar botão **Sincronizar** no LibreOffice para aplicar o `pending_log.csv`

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

## Macro LibreOffice Basic

O macro `GerarTreino` está embutido no ODS em `Basic/Standard/Module1`. Backup em `GerarTreino.bas`.

**O que o macro faz:**
- Pergunta ao usuário "A", "B" ou "C"
- Detecta a última linha usada em TREINOS
- Insere uma linha por exercício (8 para A, 7 para B, 3 para C)
- Preenche: Data, Semana (fórmula), Treino, Exercício, Séries, Reps
- Insere fórmulas para: Volume, Decisão, Carga_anterior, Próxima_carga
- Recria formato condicional para faixa D2:M{lastRow} e A2:B{lastRow}
- Grava `session.json` e apaga `pending_log.csv`
- Envia tabela Telegram com exercícios e pesos sugeridos

**Detalhes técnicos do macro:**
- `setFormula()` usa ponto e vírgula como separador (locale pt-BR)
- `GetDocDir()` — helper que extrai diretório do ODS via loop manual (LibreOffice Basic não tem `InStrRev`)
- `LerTokenTelegram()` — lê `TELEGRAM_TOKEN=valor` do `.env`
- `EnviarTelegram()` — usa VBScript via `wscript.exe` com `MSXML2.ServerXMLHTTP.6.0`
- `SincronizarTreino()` — lê `pending_log.csv` e preenche colunas G/H

**Estilos de cor (styles.xml do ODS):**
- `ConditionalStyle_1` — cinza `#cccccc` + negrito (separador de sessão em A:B)
- `ConditionalStyle_2` — verde `#d9ead3` (AUMENTAR)
- `ConditionalStyle_3` — vermelho `#f4cccc` (REDUZIR)
- `ConditionalStyle_4` — azul `#cfe2f3` (MANTER)

## Estrutura da Aba EXERCICIOS

Sem cabeçalho. Linhas 1–14 = treino único.
Colunas: A=Exercicio, B=Series, C=Reps (1-indexed no spreadsheet, 0-indexed na API Basic/Python).

## Regenerar o ODS a partir do XLSX

```bash
python add_macro_treino.py
```
Converte xlsx → ods via LibreOffice headless, injeta o macro Basic e o botão.

LibreOffice em: `C:\Program Files\LibreOffice\program\soffice.exe`

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
