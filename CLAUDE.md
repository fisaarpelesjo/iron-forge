# CLAUDE.md

## Projeto

Log de treino e nutrição em LibreOffice Calc (ODS). Arquivo principal: `log-de-treino-e-progressao.ods`.

## Arquivo ODS

Formato ZIP com XML interno. Para inspecionar estrutura:
```python
import zipfile
with zipfile.ZipFile("log-de-treino-e-progressao.ods") as z:
    print(z.namelist())
    content = z.read("content.xml").decode("utf-8")
```

## Macro LibreOffice Basic

O macro `GerarTreino` está embutido no ODS em `Basic/Standard/Module1`. O backup do código está em `GerarTreino.bas`.

**O que o macro faz:**
- Pergunta ao usuário "A", "B" ou "C"
- Detecta a última linha usada em TREINOS
- Insere uma linha por exercício (8 para Treino A, 7 para Treino B, 3 para Treino C)
- Preenche: Data, Semana (fórmula), Treino, Exercício (lido de EXERCICIOS), Séries, Reps
- Insere fórmulas para: Volume, Decisão, Carga_anterior, Próxima_carga
- Recria o formato condicional de cores para toda a faixa D2:M{lastRow} e A2:B{lastRow}

**Detalhes técnicos do macro:**
- `setFormula()` usa ponto e vírgula como separador de argumentos (locale pt-BR)
- Fórmulas de Séries/Reps são valores diretos (não fórmulas), lidos da aba EXERCICIOS
- Formato condicional recriado via `XSheetConditionalFormat.addNew()` com `ConditionOperator.FORMULA`
- Referência de linha nas fórmulas do CF usa offset a partir da linha 0 (header): `$J1` = "mesma linha coluna J"

**Estilos de cor (definidos em styles.xml do ODS):**
- `ConditionalStyle_1` — cinza `#cccccc` + negrito (separador de sessão em A:B)
- `ConditionalStyle_2` — verde `#d9ead3` (AUMENTAR)
- `ConditionalStyle_3` — vermelho `#f4cccc` (REDUZIR)
- `ConditionalStyle_4` — azul `#cfe2f3` (MANTER)

## Estrutura da Aba EXERCICIOS

Sem cabeçalho. Linhas 1–8 = Treino A, linhas 9–15 = Treino B, linhas 16–18 = Treino C.
Colunas: A=Exercicio, B=Series, C=Reps (todas 1-indexed no spreadsheet, 0-indexed na API Basic).

Índices 0-indexed usados pelo macro:
- Treino A: 0–7
- Treino B: 8–14
- Treino C: 15–17

## Regenerar o ODS a partir do XLSX

Se precisar recriar o ODS do zero (ex: dados novos no xlsx):
```bash
python add_macro_treino.py
```
O script converte xlsx → ods via LibreOffice headless, injeta o macro Basic e o botão, e expande os ranges de formato condicional para M10000.

LibreOffice em: `C:\Program Files\LibreOffice\program\soffice.exe`

## Dependências Python

- `openpyxl` — leitura do xlsx
- `pywin32` — automação Excel/COM (não usado atualmente)
- Biblioteca padrão: `zipfile`, `subprocess`, `xml.etree.ElementTree`
