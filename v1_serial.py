"""
Bolsa Família Janeiro 2026 — v1: SERIAL (1 processo)
"""

import os, csv, time

ARQUIVO_CSV = "202601_NovoBolsaFamilia.csv"
ENCODING    = "latin-1"
SEPARADOR   = ";"

def parse_valor(s):
    return float(s.strip().replace(".", "").replace(",", "."))

def brl(v):
    return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")

def imprimir_ranking(titulo, totais, reverso=True):
    print(f"\n{'─'*60}")
    print(f"  {titulo}")
    print(f"{'─'*60}")
    for i, (chave, (uf, total, qtd)) in enumerate(
            sorted(totais.items(), key=lambda x: x[1][1], reverse=reverso)[:5], 1):
        nome = chave.split(" | ")[1]
        print(f"  {i}. {nome} ({uf})")
        print(f"     Total: {brl(total)}  |  Pagamentos: {qtd:,}")

def main():
    print("=" * 60)
    print("  BOLSA FAMÍLIA — JANEIRO 2026  |  SERIAL")
    print("=" * 60)
    print(f"  Arquivo : {ARQUIVO_CSV}")
    print(f"  Tamanho : {os.path.getsize(ARQUIVO_CSV)/1e9:.2f} GB\n")

    max_val  = None
    min_val  = None
    soma     = 0.0
    contagem = 0
    totais   = {}

    t0 = time.perf_counter()

    with open(ARQUIVO_CSV, "rb") as f:
        f.readline()  # pula cabeçalho
        reader = csv.reader(
            (linha.decode(ENCODING, errors="replace") for linha in f),
            delimiter=SEPARADOR, quotechar='"'
        )
        for row in reader:
            if len(row) < 9:
                continue
            uf, nome, raw = row[2].strip(), row[4].strip(), row[8].strip()
            if not raw or raw == "VALOR PARCELA":
                continue
            try:
                valor = parse_valor(raw)
            except ValueError:
                continue

            if max_val is None or valor > max_val[0]: max_val = (valor, uf, nome)
            if min_val is None or valor < min_val[0]: min_val = (valor, uf, nome)
            soma     += valor
            contagem += 1
            chave = f"{uf} | {nome}"
            if chave in totais:
                totais[chave][1] += valor
                totais[chave][2] += 1
            else:
                totais[chave] = [uf, valor, 1]

    t_total = time.perf_counter() - t0
    media   = soma / contagem if contagem else 0

    print(f"\n{'─'*60}")
    print("  MAIOR PAGAMENTO INDIVIDUAL")
    print(f"{'─'*60}")
    print(f"  Valor    : {brl(max_val[0])}")
    print(f"  UF       : {max_val[1]}")
    print(f"  Município: {max_val[2]}")

    print(f"\n{'─'*60}")
    print("  MENOR PAGAMENTO INDIVIDUAL")
    print(f"{'─'*60}")
    print(f"  Valor    : {brl(min_val[0])}")
    print(f"  UF       : {min_val[1]}")
    print(f"  Município: {min_val[2]}")

    print(f"\n{'─'*60}")
    print("  MÉDIA ARITMÉTICA NACIONAL")
    print(f"{'─'*60}")
    print(f"  Média por pagamento: {brl(media)}")
    print(f"  Total de registros : {contagem:,}")

    imprimir_ranking("TOP 5 — MAIORES VOLUMES TOTAIS", totais, reverso=True)
    imprimir_ranking("TOP 5 — MENORES VOLUMES TOTAIS", totais, reverso=False)

    print(f"\n{'='*60}")
    print(f"  ⏱  Tempo serial: {t_total:.2f}s")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
