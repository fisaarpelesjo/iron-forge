# 🏋️ Log de Treino e Progressão

Planilha estruturada para registro, acompanhamento e análise da progressão de treino em academia. Organizada em múltiplas abas com separação clara entre dados brutos, dicionários de referência e análises.

---

## 📁 Estrutura do Arquivo

| Aba | Descrição |
|---|---|
| `LOG_BRUTO` | Registro detalhado de cada série realizada nos treinos |
| `DICIONARIO` | Catálogo de exercícios por treino (A, B, C) com séries e reps planejadas |
| `DICIONARIO RPE` | Tabela de referência da escala RPE (Rate of Perceived Exertion) |
| `PROGRESSAO` | *(em construção)* Análise de evolução de carga e volume ao longo do tempo |
| `DASHBOARD` | *(em construção)* Visão consolidada e indicadores de desempenho |

---

## 📋 Schema das Abas

### `LOG_BRUTO`

Cada linha representa **uma série executada**.

| Coluna | Tipo | Descrição |
|---|---|---|
| `Data` | Date | Data do treino |
| `Dia` | String | Identificador do treino (`A`, `B` ou `C`) |
| `Sessao_ID` | String | ID único da sessão |
| `Exercicio` | String | Nome do exercício |
| `Serie` | Integer | Número da série |
| `Reps` | Integer | Repetições realizadas |
| `Carga_kg` | Float | Carga utilizada em kg |
| `RPE` | Integer | Percepção de esforço (escala 6–10) |
| `Volume` | Float | Volume da série (`Reps × Carga_kg`) |
| `Séries_planejadas` | Integer | Número de séries previstas para o exercício |
| `Progressão` | String/Float | Indicador de progressão em relação à sessão anterior |

---

### `DICIONARIO`

Catálogo dos exercícios do programa, agrupados por treino.

| Coluna | Descrição |
|---|---|
| `Treino` | Letra do treino (`A`, `B` ou `C`) |
| `Exercicio` | Nome completo do exercício |
| `Series` | Número de séries planejadas |
| `Reps` | Número de repetições planejadas |

**Treinos:**
- **A** — Agachamento, Supino, Puxada, Remada, Desenvolvimento, Roscas e Tríceps
- **B** — Stiff, Supino inclinado, Puxada fechada, Búlgaro, Elevação lateral, Roscas e Tríceps
- **C** — Hack, Supino fechado, Remada barra, Puxada aberta, Elevação inclinada, Roscas unilaterais

---

### `DICIONARIO RPE`

Tabela de referência para a escala de esforço percebido (RPE).

| RPE | Sensação | RIR | Interpretação |
|---|---|---|---|
| 6 | Leve | 4+ | Poderia fazer várias séries a mais |
| 7 | Moderado | 3 | Ainda daria mais 3 repetições |
| 8 | Pesado controlado | 2 | Ainda daria mais 2 repetições |
| 9 | Muito pesado | 1 | Só conseguiria mais 1 repetição |
| 10 | Falha | 0 | Não conseguiria mais nenhuma repetição |

> **RIR** = Reps in Reserve (repetições em reserva)

---

## 🔄 Como Usar

1. **Registrar treinos** — Preencher `LOG_BRUTO` a cada sessão com os dados de cada série
2. **Consultar o programa** — Usar `DICIONARIO` para conferir os exercícios, séries e reps planejados
3. **Calibrar esforço** — Usar `DICIONARIO RPE` para atribuir o RPE correto em cada série
4. **Acompanhar evolução** — *(futuro)* Checar `PROGRESSAO` e `DASHBOARD` para análise da progressão

---

## 📌 Observações

- O campo `Volume` é calculado automaticamente como `Reps × Carga_kg`
- O campo `Progressão` compara a carga/volume atual com a sessão anterior do mesmo exercício
- As abas `PROGRESSAO` e `DASHBOARD` estão reservadas para análises futuras (pivot, gráficos, KPIs)
- O arquivo está disponível nos formatos `.xlsx` e `.ods` para compatibilidade com Excel e LibreOffice

---

## 🗂️ Formato dos Arquivos

```
Log_de_Treino_e_Progressão.xlsx   # Microsoft Excel
Log_de_Treino_e_Progressão.ods    # LibreOffice / Google Sheets
```
