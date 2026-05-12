# Documentacao Do IronForge

Esta pasta contem a documentacao detalhada do projeto.

As referencias cientificas e notas de treino ficam separadas em
[`training-references/`](training-references/). A raiz de `docs/` fica focada
na documentacao do software.

## Documentos Do Projeto

- [Visao geral do sistema](system-overview.md): o que o projeto faz, quais
  arquivos importam e como os dados circulam.
- [Arquitetura](architecture.md): layout do pacote, fronteiras de modulos,
  launchers, estado local e direcao de dependencias.
- [Banco de dados](database.md): SQLite, tabelas, relacoes, fonte da verdade e
  comandos seguros de inspecao.
- [Bot Telegram](telegram-bot.md): comandos, parsing de entrada, fluxo de
  mensagens, polling e falhas comuns.
- [Testes](testing.md): smoke test, teste ponta a ponta, o que cada um garante e
  como adicionar novos testes.
- [Portabilidade](portability.md): Windows, Linux, macOS, WSL, maquinas fracas,
  terminal, Python e problemas comuns de ambiente.
- [Operacao](operations.md): uso diario, setup limpo, backup, troubleshooting e
  checklist de manutencao.

## Referencias De Treino

A pasta `training-references/` contem notas de pesquisa e material de treino que
apoiam o projeto, mas nao fazem parte da arquitetura do software:

- [Forca e hipertrofia: carga baixa vs alta](training-references/forca_hipertrofia_carga_baixa_vs_alta.md)
- [Forca e hipertrofia: notas do preprint](training-references/forca_hipertrofia_carga_baixa_vs_alta_preprint.md)
- [Frequencia de treino e hipertrofia](training-references/frequencia_treino_hipertrofia.md)
- [Maximizando forca em atletas](training-references/maximizando_forca_atletas.md)
- [Periodizacao nao linear flexivel](training-references/periodizacao_nao_linear_flexivel.md)
- [Agachamento Zercher e EMG em variacoes de agachamento](training-references/zercher_squat_emg_variations.md)
- [Agachamento Zercher em forca de costas e pernas de jogadores de basquete](training-references/zercher_squat_basketball_strength.md)

## Caminho Rapido

Na raiz do repositorio:

```bash
pip install -r requirements.txt
python tests/smoke_test.py
python tests/e2e_training_flow_test.py
python start_bot.py
```

No Linux/macOS, use `python3` se necessario:

```bash
python3 tests/smoke_test.py
python3 tests/e2e_training_flow_test.py
python3 start_bot.py
```
