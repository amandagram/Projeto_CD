"""
Bolsa Família Janeiro 2026 — v2: PARALELO 2 WORKERS
"""

import os, csv, time, multiprocessing as mp

ARQUIVO_CSV = "202601_NovoBolsaFamilia.csv"
ENCODING    = "latin-1"
SEPARADOR   = ";"
NUM_WORKERS = 2

def parse_valor(s):
    return float(s.strip().replace(".", "").replace(",", "."))

def brl(v):
    return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")

def calcular_fatias(caminho, n):
    tamanho = os.path.getsize(caminho)
    fatia_tam = tamanho // n
    fatias = []
    with open(caminho, "rb") as f:
        inicio = len(f.readline())  # pula cabeçalho
        for i in range(n):
            if i == n - 1:
                fim = tamanho
            else:
                f.seek(inicio + fatia_tam)
                f.readline()
                fim = f.tell()
            fatias.append((inicio, fim))
            inicio = fim
    return fatias

def processar_fatia(args):
    caminho, start, end = args
    max_val = min_val = None
    soma = 0.0
    contagem = 0
    totais = {}

    with open(caminho, "rb") as f:
        f.seek(start)
        reader = csv.reader(
            (linha.decode(ENCODING, errors="replace") for linha in f),
            delimiter=SEPARADOR, quotechar='"'
        )
        for row in reader:
            if f.tell() > end:
                break
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
            soma += valor
            contagem += 1
            chave = f"{uf} | {nome}"
            if chave in totais:
                totais[chave][1] += valor
                totais[chave][2] += 1
            else:
                totais[chave] = [uf, valor, 1]

    return max_val, min_val, soma, contagem, totais

def reduzir(resultados):
    max_g = min_g = None
    soma_t = cont_t = 0
    totais_g = {}
    for max_v, min_v, soma, cont, totais in resultados:
        if max_v and (max_g is None or max_v[0] > max_g[0]): max_g = max_v
        if min_v and (min_g is None or min_v[0] < min_g[0]): min_g = min_v
        soma_t += soma
        cont_t += cont
        for k, (uf, total, qtd) in totais.items():
            if k in totais_g:
                totais_g[k][1] += total
                totais_g[k][2] += qtd
            else:
                totais_g[k] = [uf, total, qtd]
    return max_g, min_g, soma_t / cont_t if cont_t else 0, cont_t, totais_g

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
    print(f"  BOLSA FAMÍLIA — JANEIRO 2026  |  PARALELO {NUM_WORKERS} WORKERS")
    print("=" * 60)
    print(f"  Arquivo : {ARQUIVO_CSV}")
    print(f"  Tamanho : {os.path.getsize(ARQUIVO_CSV)/1e9:.2f} GB")
    print(f"  Workers : {NUM_WORKERS}\n")

    t0     = time.perf_counter()
    fatias = calcular_fatias(ARQUIVO_CSV, NUM_WORKERS)
    args   = [(ARQUIVO_CSV, s, e) for s, e in fatias]

    with mp.Pool(NUM_WORKERS) as pool:
        resultados = pool.map(processar_fatia, args)

    max_v, min_v, media, contagem, totais = reduzir(resultados)
    t_total = time.perf_counter() - t0

    print(f"\n{'─'*60}")
    print("  MAIOR PAGAMENTO INDIVIDUAL")
    print(f"{'─'*60}")
    print(f"  Valor    : {brl(max_v[0])}")
    print(f"  UF       : {max_v[1]}")
    print(f"  Município: {max_v[2]}")

    print(f"\n{'─'*60}")
    print("  MENOR PAGAMENTO INDIVIDUAL")
    print(f"{'─'*60}")
    print(f"  Valor    : {brl(min_v[0])}")
    print(f"  UF       : {min_v[1]}")
    print(f"  Município: {min_v[2]}")

    print(f"\n{'─'*60}")
    print("  MÉDIA ARITMÉTICA NACIONAL")
    print(f"{'─'*60}")
    print(f"  Média por pagamento: {brl(media)}")
    print(f"  Total de registros : {contagem:,}")

    imprimir_ranking("TOP 5 — MAIORES VOLUMES TOTAIS", totais, reverso=True)
    imprimir_ranking("TOP 5 — MENORES VOLUMES TOTAIS", totais, reverso=False)

    print(f"\n{'='*60}")
    print(f"  ⏱  Tempo paralelo ({NUM_WORKERS} workers): {t_total:.2f}s")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
