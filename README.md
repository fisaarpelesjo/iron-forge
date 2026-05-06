# IronForge

Sistema de log de treino e dieta com bot Telegram e banco SQLite.

---

## Visão geral

```
┌─────────────────────────────────────────────────────────────┐
│                        IRONFORGE                            │
│                                                             │
│   Celular                  PC (servidor)                    │
│  ┌────────┐   Telegram    ┌───────────────────────────┐     │
│  │  /gerar│ ────────────► │   telegram_poller.py      │     │
│  │  80 8  │ ◄──────────── │                           │     │
│  │ /status│               │  ods_ops.py  db_ops.py    │     │
│  └────────┘               └──────────┬────────────────┘     │
│                                      │                      │
│                                      ▼                      │
│                           ┌─────────────────────┐           │
│                           │   ironforge.db      │           │
│                           │                     │           │
│                           │  exercises          │           │
│                           │  training_sessions  │           │
│                           │  training_logs      │           │
│                           │  foods              │           │
│                           │  diet_targets       │           │
│                           │  diet_entries       │           │
│                           └─────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

---

## Estrutura de arquivos

```
ironforge/
├── telegram_poller.py       # Bot Telegram (long polling)
├── ods_ops.py               # Lógica de sessão de treino
├── db_ops.py                # Todas as operações SQLite
├── session.json             # Estado da sessão ativa (não versionado)
├── .env                     # TELEGRAM_TOKEN=... (não versionado)
└── data/
    └── ironforge.db         # Banco SQLite (versionado)
```

---

## Banco de dados — schema completo

```
┌─────────────────────────────────────────────────────────────┐
│  exercises                                                  │
├────────────┬──────────┬──────────┬────────────┬─────────────┤
│ id (PK)    │ name     │ sets     │ reps       │ sort_order  │
│ INTEGER    │ TEXT     │ INTEGER  │ INTEGER    │ INTEGER     │
│            │ UNIQUE   │          │            │ UNIQUE      │
├────────────┼──────────┼──────────┼────────────┼─────────────┤
│ active     │          │          │            │             │
│ INTEGER(1) │          │          │            │             │
└────────────┴──────────┴──────────┴────────────┴─────────────┘

┌───────────────────────────────────────────────────────────────────┐
│  training_sessions                                                │
├─────────────┬────────────────────┬────────────────────────────────┤
│ id (PK)     │ date               │ training_type                  │
│ INTEGER     │ TEXT (YYYY-MM-DD)  │ TEXT DEFAULT 'TREINO'          │
└─────────────┴────────────────────┴────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│  training_logs                                                           │
├──────────┬────────────┬───────────────┬──────┬──────┬────────┬───────────┤
│ id (PK)  │ session_id │ exercise_name │ sets │ reps │ weight │ rpe       │
│ INTEGER  │ FK→session │ TEXT          │ INT  │ INT  │ REAL   │ REAL      │
├──────────┼────────────┼───────────────┴──────┴──────┴────────┴───────────┤
│sort_order│            │                                                  │
│ INTEGER  │            │                                                  │
└──────────┴────────────┴──────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│  foods                                                                        │
├─────────┬────────────────┬────────┬───────────┬────────────────────────────── ┤
│ id (PK) │ name (UNIQUE)  │ unit   │ serving_g │ protein_g  carbo_g  fat_g     │
│ INTEGER │ TEXT           │ TEXT   │ REAL      │ calories   fiber_g  omega3_g  │
│         │                │        │           │ potassium_mg  magnesium_mg    │
│         │                │        │           │ zinc_mg  vitamin_d_ui         │
└─────────┴────────────────┴────────┴───────────┴───────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  diet_targets  (única linha)                                            │
├────────────┬──────────┬────────┬──────────┬────────┬────────────────────┤
│ protein_g  │ carbo_g  │ fat_g  │ calories │ fiber_g│ omega3_g           │
│ potassium  │ magnesium│ zinc   │ vitaminD │        │                    │
└────────────┴──────────┴────────┴──────────┴────────┴────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  diet_entries                                           │
├─────────┬──────────┬──────────────┬──────────┬──────────┤
│ id (PK) │ meal     │ food_id (FK) │ quantity │sort_order│
│ INTEGER │ TEXT     │ → foods.id   │ REAL     │ INTEGER  │
└─────────┴──────────┴──────────────┴──────────┴──────────┘
```

### Relações

```
exercises ──────────────────────────────────────────── standalone

training_sessions ──┐
                    │ 1:N
                    └──► training_logs

foods ──────────────┐
                    │ 1:N
                    └──► diet_entries

diet_targets ────────────────────────────────────────── standalone (1 row)
```

---

## Fluxo de treino

```
/gerar
  │
  ├── db_ops.get_or_seed_exercises()
  │       └── SELECT FROM exercises ORDER BY sort_order
  │
  ├── db_ops.create_session(date)
  │       └── INSERT INTO training_sessions
  │
  ├── db_ops.log_exercise(session_id, name, sets, reps, idx)  [×13]
  │       └── INSERT INTO training_logs  ← weight=NULL, rpe=NULL
  │
  └── ods_ops.write_session(exercises, session_id)
          └── session.json  {date, session_id, exercises:[{log_id,...}]}


"80 8"  (carga 80kg, RPE 8)
  │
  ├── filled = db_ops.count_filled(log_ids)
  │       └── SELECT COUNT(*) FROM training_logs WHERE id IN (...) AND weight IS NOT NULL
  │
  ├── ex = exercises[filled]   ← próximo exercício sem peso
  │
  └── db_ops.update_log_weight(ex.log_id, 80.0, 8)
          └── UPDATE training_logs SET weight=80, rpe=8 WHERE id=?


/undo
  │
  ├── filled = db_ops.count_filled(log_ids)
  ├── last_ex = exercises[filled - 1]
  └── db_ops.update_log_weight(last_ex.log_id, None, None)
          └── UPDATE training_logs SET weight=NULL, rpe=NULL WHERE id=?
```

---

## Fórmulas de nutrição

Os nutrientes em `foods` são armazenados **por serving** (não por grama).

```
unit = 'g'          → nutrientes por serving_g gramas  (ex: 17g proteína / 100g aveia)
unit = qualquer outra → nutrientes por 1 unidade        (ex: 6g proteína / 1 ovo)
```

### Cálculo de consumo

```
                ┌─────────────────────────────────────────────┐
                │                                             │
  unit = 'g':   │  consumido = qty × nutriente / serving_g    │
                │  ex: 15g aveia → 15 × 17 / 100 = 2.55g      │
                │                                             │
  unit ≠ 'g':   │  consumido = qty × nutriente                │
                │  ex: 4 ovos   → 4 × 6 = 24g                 │
                │                                             │
                └─────────────────────────────────────────────┘

SQL unificado:
  quantity * nutrient / CASE WHEN unit = 'g' THEN serving_g ELSE 1.0 END
```

### Verificação (vs ODS original)

```
Nutriente    Calculado    ODS original   Δ
──────────── ──────────── ────────────── ──
Proteína     214.4 g      214.44 g       ✓
Carboidrato  193.3 g      193.30 g       ✓
Gordura      65.0 g       64.95 g        ✓
Calorias     2178         2178.35        ✓
Fibra        28.3 g       28.29 g        ✓
Ômega-3      2.00 g       2.00 g         ✓
```

---

## Bot Telegram — comandos

```
┌────────────────┬───────────────────────────────────────────────────────┐
│ Comando        │ Descrição                                             │
├────────────────┼───────────────────────────────────────────────────────┤
│ /gerar         │ Cria sessão no SQLite, envia tabela com exercícios    │
│                │ e últimas cargas registradas                          │
├────────────────┼───────────────────────────────────────────────────────┤
│ /exercicios    │ Lista os 13 exercícios ativos com séries e reps       │
│ /lista         │ (alias)                                               │
├────────────────┼───────────────────────────────────────────────────────┤
│ /volume        │ Séries por grupo muscular na sessão + estimativa      │
│                │ semanal (~3.5× por semana)                            │
├────────────────┼───────────────────────────────────────────────────────┤
│ /aquecimento   │ Protocolo de aquecimento completo (12 etapas)         │
├────────────────┼───────────────────────────────────────────────────────┤
│ /status        │ Progresso atual: exercícios feitos / total            │
├────────────────┼───────────────────────────────────────────────────────┤
│ /undo          │ Desfaz o último registro (limpa weight/rpe no SQLite) │
├────────────────┼───────────────────────────────────────────────────────┤
│ /help          │ Lista todos os comandos                               │
├────────────────┼───────────────────────────────────────────────────────┤
│ 80             │ Registra 80 kg no próximo exercício pendente          │
│ 80 8           │ Registra 80 kg + RPE 8                                │
│ 80,5 8         │ Aceita vírgula como decimal                           │
└────────────────┴───────────────────────────────────────────────────────┘
```

### Exemplo de sessão

```
Você:  /gerar

Bot:   Treino
       Exercicio              S   R      Kg
       ────────────────────────────────────
       Agachamento (barra)    3   5      56
       Supino reto (barra)    3   5      36
       Remada curvada (barra) 3   8      40
       ...

Bot:   Treino gerado! Mande carga rpe para cada exercicio.

Você:  60 8
Bot:   Agachamento (barra) ✓ 60kg RPE 8 (1/13)
       ▶ Supino reto (barra) (3x5)

Você:  /undo
Bot:   ↩ Desfeito: Agachamento (barra)

Você:  60 7
Bot:   Agachamento (barra) ✓ 60kg RPE 7 (1/13)
       ▶ Supino reto (barra) (3x5)
```

---

## Lista de exercícios

```
 #  Exercício                      Séries  Reps   Músculos
──  ─────────────────────────────  ──────  ─────  ──────────────────────
 1  Agachamento (barra)               3      5    Quadríceps, Glúteos
 2  Supino reto (barra)               3      5    Peitoral
 3  Remada curvada (barra)            3      8    Dorsais
 4  Desenvolvimento (barra em pé)     3      5    Deltóide anterior
 5  Stiff com barra                   3      8    Isquiotibiais, Glúteos
 6  Pullover (barra)                  3     10    Dorsais
 7  Remada alta (barra)               3     10    Deltóide lateral, Trapézio
 8  Remada curvada alta no peito (barra) 3     10    Deltóide posterior, Trapézio
 9  Encolhimento com barra            2     10    Trapézio
10  Rosca direta                      3      8    Bíceps
11  Tríceps testa                     3      8    Tríceps
12  Wrist curl (barra)                2     15    Antebraço
13  Reverse wrist curl (barra)        2     15    Antebraço
```

### Volume por sessão

```
Grupo muscular       Séries/sessão    Séries/semana (×3.5)
───────────────────  ─────────────    ────────────────────
Quadríceps                  3               ~11
Glúteos                     6               ~21
Isquiotibiais               3               ~11
Peitoral                    3               ~11
Dorsais                     6               ~21
Deltóide anterior           3               ~11
Deltóide lateral            3               ~11
Deltóide posterior          3               ~11
 Trapézio                    8               ~28
Bíceps                      3               ~11
Tríceps                     3               ~11
Antebraço                   4               ~14
```

---

## Dieta — metas e catálogo

### Metas diárias

```
Nutriente      Meta atual    Unidade
─────────────  ──────────    ───────
Proteína            200      g
Carboidrato         200      g
Gordura              70      g
Calorias           2200      kcal
Fibra                30      g
Ômega-3             1.5      g
Potássio           4000      mg
Magnésio            400      mg
Zinco                13      mg
Vitamina D         1000      UI
```

### Refeições (plano atual)

```
Refeição    Alimento                        Qtd   Unidade
──────────  ──────────────────────────────  ────  ───────
Café        Ovo inteiro                      4    unidade
Café        Leite UHT Semidesnatado          1    copo
Café        Vitamina D3 Max Titanium         1    cápsula
Café        Omega 3 Supley                   3    cápsula
Lanche      Leite UHT Semidesnatado          1    copo
Lanche      Banana                           3    unidade
Lanche      Whey protein                     1    porção
Lanche      Aveia                           15    g
Almoço      Arroz branco cozido             50    g
Almoço      Feijão carioca cozido          100    g
Almoço      Filé de peito de frango        250    g
Almoço      Azeite de oliva                 1    colher
Janta       Arroz branco cozido             50    g
Janta       Feijão carioca cozido          100    g
Janta       Filé de peito de frango        250    g
Janta       Azeite de oliva                 1    colher
```

### Catálogo de alimentos (53 itens)

Banco `foods` cobre: ovos, laticínios, pães, cereais, leguminosas, massas,
tubérculos, carnes, proteínas em pó, oleaginosas, óleos, vegetais, frutas,
suplementos (Omega 3, Vitamina D3) e produtos de marca.

---

## Progressão de carga

Lógica baseada em RPE (Rate of Perceived Exertion):

```
RPE registrado    Decisão     Próxima carga
──────────────    ─────────   ─────────────
    ≤ 8           AUMENTAR    carga + 2.5 kg
      9           MANTER      carga atual
    ≥ 10          REDUZIR     carga - 2.5 kg
```

Histórico de cargas consultado via `get_last_weights()`:

```sql
SELECT exercise_name, weight
FROM training_logs
WHERE weight IS NOT NULL AND weight > 0
  AND id IN (
    SELECT MAX(id)
    FROM training_logs
    WHERE weight IS NOT NULL AND weight > 0
    GROUP BY exercise_name
  )
```

---

## Setup

### Pré-requisitos

```
Python 3.10+
pip install requests
```

### Configuração

```bash
# 1. Criar .env com o token do bot
echo "TELEGRAM_TOKEN=seu_token_aqui" > .env

# 2. Iniciar o bot
python telegram_poller.py
```

O banco `data/ironforge.db` é criado automaticamente na primeira execução com
`CREATE TABLE IF NOT EXISTS` para todas as tabelas. Exercícios são populados
com os 13 padrões se a tabela estiver vazia.

### Estado de sessão

```
session.json (não versionado):
{
  "date": "2026-05-05",
  "session_id": 3,
  "exercises": [
    { "log_id": 27, "name": "Agachamento (barra)", "sets": 3, "reps": 5 },
    { "log_id": 28, "name": "Supino reto (barra)",  "sets": 3, "reps": 5 },
    ...
  ]
}
```

Sessão antiga sem `log_id` é detectada automaticamente — bot solicita `/gerar`.

---

## API interna (db_ops.py)

### Treino

```python
# Exercícios
list_exercises()                        → [{"name", "sets", "reps"}]
get_or_seed_exercises()                 → idem (popula se vazio)
replace_exercises(exercises)            → substitui catálogo

# Sessão
create_session(date_iso, type)          → session_id
log_exercise(session_id, name, sets, reps, sort_order) → log_id
update_log_weight(log_id, weight, rpe)  → None  (weight=None para limpar)
get_last_weights()                      → {"exercise_name": last_kg}
count_filled(log_ids)                   → int   (quantos têm peso)
import_log_rows(rows)                   → None  (importação bulk)
```

### Dieta

```python
# Alimentos
upsert_food(name, unit, serving_g, ...nutrientes...)  → food_id
get_food_by_name(name)                                → dict | None
list_foods()                                          → [dict]

# Plano
set_diet_targets(...macros/micros...)   → id
get_diet_targets()                      → dict | None
add_diet_entry(meal, food_id, qty, sort_order) → id
list_diet_entries()                     → [dict com nutrientes calculados]
get_diet_totals()                       → {"totals": {...}, "targets": {...}}
```

---

## Arquitetura de decisão

```
               ┌──────────────────────────────────┐
               │         telegram_poller.py       │
               │                                  │
               │  main() ──► get_updates()        │
               │               │                  │
               │          por mensagem:           │
               │               │                  │
               │    ┌──────────▼──────────┐       │
               │    │  /gerar             │       │
               │    │  handle_gerar()     │       │
               │    │    ods_ops          │       │
               │    │    .gerar_treino()  │       │
               │    └──────────┬──────────┘       │
               │               │                  │
               │    ┌──────────▼──────────┐       │
               │    │  número (ex: 80 8)  │       │
               │    │  handle(text,       │       │
               │    │         session)    │       │
               │    │    filled =         │       │
               │    │    count_filled()   │       │
               │    │    update_log_      │       │
               │    │    weight()         │       │
               │    └─────────────────────┘       │
               └──────────────────────────────────┘
```

---

## Dependências

```
requests          HTTP para Telegram API (polling + send)
sqlite3           stdlib — banco de dados local
json              stdlib — session.json
pathlib           stdlib — paths
datetime          stdlib — data do treino
time              stdlib — sleep do polling loop
re, zipfile       stdlib — usados nos scripts de migração (removidos)
```
