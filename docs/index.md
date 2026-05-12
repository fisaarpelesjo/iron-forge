# IronForge Documentation

This folder contains detailed project documentation.

Training-science notes are separated under
[`training-references/`](training-references/) so the root of `docs/` stays
focused on the software project.

## Project Docs

- [System Overview](system-overview.md): what the project does, what each file
  is responsible for, and how data moves through the app.
- [Architecture](architecture.md): package layout, module boundaries, launchers,
  local state, and dependency direction.
- [Database](database.md): SQLite file location, table schemas, relationships,
  source-of-truth rules, and safe inspection commands.
- [Telegram Bot](telegram-bot.md): command behavior, input parsing, message flow,
  polling loop, and failure modes.
- [Testing](testing.md): smoke test, end-to-end test, what each test proves, and
  how to add more tests safely.
- [Portability](portability.md): Windows, Linux, macOS, WSL, weak machines,
  terminal color, Python setup, and common environment problems.
- [Operations](operations.md): daily usage, setup from a fresh clone, backup,
  troubleshooting, and maintenance checklist.

## Training References

The `training-references/` folder contains research notes and training reference
material that support the project but are not part of the software architecture:

- [Strength and hypertrophy: low vs high load](training-references/forca_hipertrofia_carga_baixa_vs_alta.md)
- [Strength and hypertrophy preprint notes](training-references/forca_hipertrofia_carga_baixa_vs_alta_preprint.md)
- [Training frequency and hypertrophy](training-references/frequencia_treino_hipertrofia.md)
- [Maximizing strength for athletes](training-references/maximizando_forca_atletas.md)
- [Flexible nonlinear periodization](training-references/periodizacao_nao_linear_flexivel.md)

## Fast Path

From the repository root:

```bash
pip install -r requirements.txt
python tests/smoke_test.py
python tests/e2e_training_flow_test.py
python start_bot.py
```

On Linux and macOS, use `python3` if `python` does not point to Python 3:

```bash
python3 tests/smoke_test.py
python3 tests/e2e_training_flow_test.py
python3 start_bot.py
```
