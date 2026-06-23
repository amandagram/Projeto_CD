# Bolsa Família — Processamento Paralelo (Out/2025 a Jan/2026)

## Ordem de execução

### 1. Junte os CSVs em um único arquivo
```bash
python unir_planilhas.py
```

### 2. Rode o que quiser

| Script | O que faz |
|---|---|
| `python benchmark.py` | Roda tudo e exibe gráfico comparativo |
| `python v1_serial.py` | Só serial |
| `python v2_paralelo_2.py` | Paralelo com 2 workers |
| `python v4_paralelo_4.py` | Paralelo com 4 workers |
| `python v8_paralelo_8.py` | Paralelo com 8 workers |
| `python v12_paralelo_12.py` | Paralelo com 12 workers |

## Estrutura

```
bolsa_familia_projeto/
├── bolsa_familia_completo.py   ← núcleo com toda a lógica
├── unir_planilhas.py           ← passo 1: une os 4 CSVs
├── benchmark.py                ← roda tudo + gráfico
├── v1_serial.py
├── v2_paralelo_2.py
├── v4_paralelo_4.py
├── v8_paralelo_8.py
├── v12_paralelo_12.py
└── README.md
```

## Arquivos de dados necessários (na mesma pasta)

```
202601_NovoBolsaFamilia.csv   ← Jan/2026
202512_NovoBolsaFamilia.csv   ← Dez/2025
202511_NovoBolsaFamilia.csv   ← Nov/2025
202510_NovoBolsaFamilia.csv   ← Out/2025
```

## Requisitos

- Python 3.10+
- Nenhuma biblioteca externa
