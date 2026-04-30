# Log de Treino e Progressão

Planilha estruturada para registro, acompanhamento e análise da progressão de treino e nutrição. Organizada em múltiplas abas com separação clara entre dados brutos, dicionários de referência e análise nutricional.

![Toguro](toguro.gif)

---

## Arquivo

```
log-de-treino-e-progressao.ods   # LibreOffice Calc (arquivo principal)
GerarTreino.bas                  # Backup do código do macro Basic
```

Abrir no **LibreOffice Calc**. Ao abrir, habilitar macros quando solicitado.

---

## Macro: Gerar Treino

A aba `TREINOS` tem um botão **"Gerar Treino"** que automatiza o registro de cada sessão.

**Como usar:**
1. Clica no botão "Gerar Treino" na aba `TREINOS`
2. Digita `A` ou `B` e pressiona OK
3. As linhas do treino são geradas com data de hoje, exercícios, séries e reps
4. Preenche `Carga_kg` e `RPE_final` após o treino

**O que o macro preenche automaticamente:**
- `Data` — data de hoje
- `Semana` — semana ISO (`YYYY-Www`)
- `Treino` — A ou B
- `Exercício`, `Séries`, `Reps` — vindos da aba `EXERCICIOS`
- `Volume` — fórmula `Séries × Reps × Carga_kg`
- `Decisão` — fórmula baseada no RPE
- `Carga_anterior` — busca automática da última carga registrada
- `Próxima_carga` — sugestão baseada na Decisão

**O que você preenche manualmente:**
- `Carga_kg` — carga utilizada em kg
- `RPE_final` — esforço percebido (6–10)
- `Observações` — notas livres

**Cores automáticas** (aparecem ao preencher RPE):
- Verde — AUMENTAR (RPE ≤ 8)
- Vermelho — REDUZIR (RPE = 10)
- Azul — MANTER (RPE = 9)
- Cinza/negrito em A:B — separador de sessões (quando muda o dia)

---

## Estrutura das Abas

| Aba          | Descrição                                                                 |
| ------------ | ------------------------------------------------------------------------- |
| `TREINOS`    | Registro de cada exercício realizado nos treinos com decisão de progressão |
| `EXERCICIOS` | Catálogo de exercícios por treino (A e B) com séries e reps planejadas    |
| `DIETA`      | Metas diárias, totais consolidados e log de refeições com macros e micros |
| `ALIMENTOS`  | Tabela de referência nutricional dos alimentos cadastrados                |

---

## Schema das Abas

### `TREINOS`

Cada linha representa **um exercício executado em uma sessão**.

| Coluna           | Tipo    | Preenchimento | Descrição                                                  |
| ---------------- | ------- | ------------- | ---------------------------------------------------------- |
| `Data`           | Date    | Macro         | Data do treino                                             |
| `Semana`         | String  | Macro         | Semana ISO do treino (ex: `2026-W15`)                      |
| `Treino`         | String  | Macro         | Identificador do treino (`A` ou `B`)                       |
| `Exercício`      | String  | Macro         | Nome do exercício                                          |
| `Séries`         | Integer | Macro         | Número de séries planejadas                                |
| `Reps`           | Integer | Macro         | Repetições planejadas por série                            |
| `Carga_kg`       | Float   | Manual        | Carga utilizada em kg                                      |
| `RPE_final`      | Integer | Manual        | Percepção de esforço na última série (escala 6–10)         |
| `Volume`         | Float   | Fórmula       | Volume total (`Séries × Reps × Carga_kg`)                  |
| `Decisão`        | String  | Fórmula       | Recomendação de progressão (`AUMENTAR`, `MANTER`, `REDUZIR`) |
| `Carga_anterior` | Float   | Fórmula       | Carga utilizada na sessão anterior do mesmo exercício      |
| `Próxima_carga`  | Float   | Fórmula       | Carga recomendada para a próxima sessão                    |
| `Observações`    | String  | Manual        | Notas livres sobre a execução                              |

**Lógica de `Decisão`:**

- **AUMENTAR** — RPE ≤ 8: carga foi confortável, incremento na próxima sessão
- **MANTER** — RPE = 9: esforço adequado, mantém a mesma carga
- **REDUZIR** — RPE = 10: falha ou limite máximo, reduz carga na próxima sessão

---

### `EXERCICIOS`

Catálogo dos exercícios do programa, agrupados por treino. Sem cabeçalho — linhas 1–8 são Treino A, linhas 9–15 são Treino B.

| Coluna      | Descrição                         |
| ----------- | --------------------------------- |
| `Exercicio` | Nome completo do exercício        |
| `Series`    | Número de séries planejadas       |
| `Reps`      | Número de repetições planejadas   |

**Treinos:**

- **A** — Agachamento (barra), Remada curvada (barra), Supino reto (barra), Pull-over (barra), Elevação lateral (halter), Crucifixo invertido, Rosca direta (barra/halter), Tríceps testa (barra/halter)
- **B** — Agachamento (barra, leve -10%), Stiff com barra, Desenvolvimento (barra em pé), Remada curvada (barra), Crucifixo invertido, Supino reto (barra), Elevação lateral (halter, leve -10%)

---

### `DIETA`

Aba com três seções dispostas verticalmente:

**1. Metas diárias** — linha de referência com os alvos nutricionais:

| Nutriente  | Meta      |
| ---------- | --------- |
| Proteína   | 200 g     |
| Carbo      | 200 g     |
| Gordura    | 70 g      |
| Calorias   | 2200 kcal |
| Fibra      | 30 g      |
| Ômega-3    | 1,5 g     |
| Potássio   | 4000 mg   |
| Magnésio   | 400 mg    |
| Zinco      | 13 mg     |
| Vitamina D | 1000 UI   |

**2. Totais do dia** — soma consolidada dos macros e micros do dia atual.

**3. Log de refeições** — cada linha representa **um alimento em uma refeição**:

| Coluna         | Tipo   | Descrição                                          |
| -------------- | ------ | -------------------------------------------------- |
| `Refeição`     | String | Refeição do dia (ex: Café, Lanche, Almoço, Janta)  |
| `Alimento`     | String | Nome do alimento consumido                         |
| `Quantidade`   | Float  | Quantidade consumida                               |
| `Unidade_base` | String | Unidade de medida (`g`, `unidade`, `copo`, etc.)   |
| `Peso_unit_g`  | Float  | Peso unitário em gramas (referência do dicionário) |
| `Proteína_g`   | Float  | Proteína total da porção (g)                       |
| `Carbo_g`      | Float  | Carboidrato total da porção (g)                    |
| `Gordura_g`    | Float  | Gordura total da porção (g)                        |
| `Calorias`     | Float  | Calorias totais da porção (kcal)                   |
| `Fibra_g`      | Float  | Fibra total da porção (g)                          |
| `Omega3_g`     | Float  | Ômega-3 total da porção (g)                        |
| `Potassio_mg`  | Float  | Potássio total da porção (mg)                      |
| `Magnesio_mg`  | Float  | Magnésio total da porção (mg)                      |
| `Zinco_mg`     | Float  | Zinco total da porção (mg)                         |
| `VitaminaD_UI` | Float  | Vitamina D total da porção (UI)                    |

> Macros e micros calculados automaticamente a partir de `ALIMENTOS` (quantidade × valor por unidade).

---

### `ALIMENTOS`

Tabela de referência nutricional dos alimentos cadastrados.

| Coluna           | Descrição                                       |
| ---------------- | ----------------------------------------------- |
| `Alimento`       | Nome do alimento                                |
| `Unidade`        | Unidade de medida padrão (`g`, `unidade`, etc.) |
| `Peso_unidade_g` | Peso da unidade em gramas                       |
| `Proteina_g`     | Proteína por unidade/100g (g)                   |
| `Carbo_g`        | Carboidrato por unidade/100g (g)                |
| `Gordura_g`      | Gordura por unidade/100g (g)                    |
| `Calorias`       | Calorias por unidade/100g (kcal)                |
| `Fibra_g`        | Fibra por unidade/100g (g)                      |
| `Omega3_g`       | Ômega-3 por unidade/100g (g)                    |
| `Potassio_mg`    | Potássio por unidade/100g (mg)                  |
| `Magnesio_mg`    | Magnésio por unidade/100g (mg)                  |
| `Zinco_mg`       | Zinco por unidade/100g (mg)                     |
| `VitaminaD_UI`   | Vitamina D por unidade/100g (UI)                |
