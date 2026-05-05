# Log de Treino e Progressão

Planilha LibreOffice Calc para registro e progressão de treino, com bot Telegram para anotar pesos e RPE direto da academia — sem tocar no PC.

![Toguro](toguro.gif)

---

## Fluxo principal

```
Celular (Telegram)
  /gerar A          →  bot insere linhas no ODS, envia tabela com exercícios e pesos anteriores
  80 8              →  bot registra carga 80kg RPE 8 no exercício atual
  /sync             →  aplica no ODS os registros pendentes (quando houver)
  /status           →  mostra progresso da sessão
  /undo             →  desfaz último registro
```

O PC fica ligado com `python telegram_poller.py` rodando. O ODS é atualizado diretamente pelo Python, sem precisar abrir o LibreOffice.

---

## Arquivos

```
log-de-treino-e-progressao.ods   # LibreOffice Calc (arquivo principal)
ods_ops.py                       # Manipulação direta do ODS via Python
telegram_poller.py               # Bot Telegram (polling)
.env                             # TELEGRAM_TOKEN=... (não versionado)
```

---

## Bot Telegram

### Iniciar

```bash
python telegram_poller.py
```

### Comandos

| Comando       | Descrição                                             |
| ------------- | ----------------------------------------------------- |
| `/gerar A`    | Gera treino A no ODS e envia tabela com pesos sugeridos |
| `/gerar B`    | Gera treino B                                         |
| `/gerar C`    | Gera treino C                                         |
| `/sync`       | Aplica no ODS os registros salvos em `pending_log.csv` |
| `80`          | Registra 80kg no próximo exercício pendente           |
| `80 8`        | Registra 80kg + RPE 8                                 |
| `/status`     | Mostra exercício atual e quantos foram concluídos     |
| `/undo`       | Desfaz último registro                                |
| `/help`       | Lista todos os comandos                               |

### Fallback (ODS aberto no LibreOffice)

Se o ODS estiver aberto quando você mandar o peso, o bot salva em `pending_log.csv`.  
Depois de fechar o LibreOffice, use `/sync` no Telegram para aplicar os dados pendentes no ODS.

---

## Fluxo atual (somente bot Telegram)

O fluxo por macro do LibreOffice foi removido deste repositório.

Toda a operação de treino (gerar, registrar carga/RPE e sincronizar pendências) deve ser feita via comandos do bot Telegram.

---

## O que o bot preenche automaticamente

| Coluna           | Origem   | Descrição                                              |
| ---------------- | -------- | ------------------------------------------------------ |
| `Data`           | Bot      | Data do treino                                         |
| `Semana`         | Fórmula  | Semana ISO (`2026-W18`)                                |
| `Treino`         | Bot      | A, B ou C                                              |
| `Exercício`      | Bot      | Nome lido de EXERCICIOS                                |
| `Séries`         | Bot      | Séries planejadas                                      |
| `Reps`           | Bot      | Reps planejadas                                        |
| `Carga_kg`       | Bot/Manual | Carga utilizada em kg                                |
| `RPE_final`      | Bot/Manual | Percepção de esforço (6–10)                          |
| `Volume`         | Fórmula  | Séries × Reps × Carga_kg                              |
| `Decisão`        | Fórmula  | AUMENTAR / MANTER / REDUZIR                           |
| `Carga_anterior` | Fórmula  | Última carga registrada para o exercício               |
| `Próxima_carga`  | Fórmula  | Sugestão baseada na Decisão (±2,5 kg)                 |

**Lógica de Decisão:**
- RPE ≤ 8 → **AUMENTAR** (verde)
- RPE = 9 → **MANTER** (azul)
- RPE = 10 → **REDUZIR** (vermelho)

---

## Estrutura das Abas

| Aba          | Descrição                                                                  |
| ------------ | -------------------------------------------------------------------------- |
| `TREINOS`    | Registro de cada exercício com progressão automática                       |
| `EXERCICIOS` | Catálogo de exercícios (ordem fixa) com séries e reps planejadas           |
| `DIETA`      | Metas diárias, totais consolidados e log de refeições com macros e micros  |
| `ALIMENTOS`  | Tabela de referência nutricional dos alimentos cadastrados                 |

### Estrutura de `EXERCICIOS`

Sem cabeçalho. Colunas: `Exercicio | Series | Reps`

Ordem atual (linhas 1–13):
- Agachamento (barra) — 3x5
- Supino reto (barra) — 3x5
- Remada curvada (barra) — 3x8
- Desenvolvimento (barra em pé) — 3x5
- Stiff com barra — 3x8
- Pullover (barra) — 3x10
- Elevação lateral — 3x10
- Crucifixo invertido — 3x10
- Encolhimento com barra — 2x10
- Rosca direta — 3x8
- Tríceps testa — 3x8
- Wrist curl (barra) — 2x15
- Reverse wrist curl (barra) — 2x15
