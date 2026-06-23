"""
melhor_eficiencia.py — máxima eficiência de paralelização.

Estratégia: pipeline produtor/consumidor com sobreposição de I/O e CPU.
  • 1 thread lê o arquivo em blocos de 256 MB (I/O puro, sem GIL)
  • N processos consomem os blocos e processam em paralelo (CPU puro)
  • I/O e CPU rodam AO MESMO TEMPO — sem workers disputando o disco

Uso:
    python melhor_eficiencia.py          # usa todos os núcleos
    python melhor_eficiencia.py 8        # força 8 workers
"""

import os, sys, time, threading, multiprocessing as mp
from multiprocessing import Process, Queue

ARQUIVO  = "BolsaFamilia_Out2025_Jan2026.csv"
ENCODING = "latin-1"
BUF_IO   = 256 * 1024 * 1024    # 256 MB por bloco de leitura
FILA_MAX = 3                     # blocos em buffer (RAM = FILA_MAX × BUF_IO × N)

MESES = {
    "202601": "Jan/2026",
    "202512": "Dez/2025",
    "202511": "Nov/2025",
    "202510": "Out/2025",
}

def brl(v):
    return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")


# ── Produtor: lê e distribui blocos (roda em thread) ─────────────────────────
def produtor(arquivo, filas, buf_size):
    sobra = b""
    idx   = 0
    n     = len(filas)
    with open(arquivo, "rb") as f:
        f.readline()                  # pula cabeçalho
        while True:
            bloco = f.read(buf_size)
            if not bloco:
                break
            bloco = sobra + bloco
            nl    = bloco.rfind(b"\n")
            sobra = bloco[nl + 1:]
            bloco = bloco[:nl + 1]
            filas[idx % n].put(bloco)
            idx += 1
    # envia sinal de fim para cada worker
    for fila in filas:
        fila.put(None)


# ── Worker: processa blocos (roda em processo separado) ──────────────────────
def worker_proc(fila_entrada, fila_saida):
    acc = {}
    while True:
        bloco = fila_entrada.get()
        if bloco is None:             # fim — envia resultado acumulado
            fila_saida.put(acc)
            fila_saida.put(None)      # sinaliza fim deste worker
            break

        for linha in bloco.split(b"\n"):
            if not linha:
                continue
            row = linha.split(b";")
            if len(row) < 9:
                continue
            mes_b = row[0].strip(b'"')
            uf_b  = row[2].strip(b'"')
            nom_b = row[4].strip(b'"')
            rv    = row[8].strip().strip(b'"')
            if not rv or rv == b"VALOR PARCELA":
                continue
            try:
                valor = float(rv.replace(b".", b"").replace(b",", b"."))
            except ValueError:
                continue

            ms = mes_b.decode(ENCODING)
            us = uf_b.decode(ENCODING)
            ns = nom_b.decode(ENCODING)

            if ms not in acc:
                acc[ms] = {"max": None, "min": None,
                           "soma": 0.0, "count": 0, "totais": {}}
            a = acc[ms]
            if a["max"] is None or valor > a["max"][0]: a["max"] = (valor, us, ns)
            if a["min"] is None or valor < a["min"][0]: a["min"] = (valor, us, ns)
            a["soma"]  += valor
            a["count"] += 1
            chave = us + "|" + ns
            t = a["totais"]
            if chave in t:
                t[chave][1] += valor
                t[chave][2] += 1
            else:
                t[chave] = [us, valor, 1]


# ── Redução final ─────────────────────────────────────────────────────────────
def reduzir(parciais):
    merged = {}
    for acc in parciais:
        for ms, a in acc.items():
            if ms not in merged:
                merged[ms] = {"max": None, "min": None,
                              "soma": 0.0, "count": 0, "totais": {}}
            m = merged[ms]
            if a["max"] and (m["max"] is None or a["max"][0] > m["max"][0]):
                m["max"] = a["max"]
            if a["min"] and (m["min"] is None or a["min"][0] < m["min"][0]):
                m["min"] = a["min"]
            m["soma"]  += a["soma"]
            m["count"] += a["count"]
            for k, (uf, total, qtd) in a["totais"].items():
                if k in m["totais"]:
                    m["totais"][k][1] += total
                    m["totais"][k][2] += qtd
                else:
                    m["totais"][k] = [uf, total, qtd]
    final = {}
    for ms, m in merged.items():
        media = m["soma"] / m["count"] if m["count"] else 0.0
        final[ms] = (m["max"], m["min"], media, m["count"], m["totais"])
    return final


# ── Impressão ─────────────────────────────────────────────────────────────────
def imprimir(mes_cod, max_v, min_v, media, count, totais):
    rotulo = MESES.get(mes_cod, mes_cod)
    print(f"\n{'═'*62}")
    print(f"  📅  {rotulo}  —  {count:,} registros")
    print(f"{'═'*62}")
    print(f"\n  MAIOR PAGAMENTO INDIVIDUAL")
    print(f"  Valor: {brl(max_v[0])}  |  {max_v[2]} ({max_v[1]})")
    print(f"\n  MENOR PAGAMENTO INDIVIDUAL")
    print(f"  Valor: {brl(min_v[0])}  |  {min_v[2]} ({min_v[1]})")
    print(f"\n  MÉDIA ARITMÉTICA: {brl(media)}")
    for titulo, rev in [("TOP 5 — MAIORES VOLUMES TOTAIS", True),
                        ("TOP 5 — MENORES VOLUMES TOTAIS", False)]:
        print(f"\n  {titulo}")
        print(f"  {'─'*56}")
        for i, (chave, (uf, total, qtd)) in enumerate(
                sorted(totais.items(), key=lambda x: x[1][1], reverse=rev)[:5], 1):
            nome = chave.split("|")[1]
            print(f"  {i}. {nome} ({uf})  —  {brl(total)}  |  {qtd:,} pagamentos")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    num_workers = int(sys.argv[1]) if len(sys.argv) > 1 else mp.cpu_count()

    print("=" * 62)
    print(f"  BOLSA FAMÍLIA — PIPELINE PRODUTOR/CONSUMIDOR")
    print("=" * 62)

    if not os.path.exists(ARQUIVO):
        print(f"  ⚠️  Arquivo não encontrado: {ARQUIVO}")
        return

    tam = os.path.getsize(ARQUIVO)
    print(f"  Arquivo  : {ARQUIVO}")
    print(f"  Tamanho  : {tam/1e9:.2f} GB")
    print(f"  Workers  : {num_workers}")
    print(f"  Bloco I/O: {BUF_IO//1024//1024} MB\n")

    t0 = time.perf_counter()

    # cada worker tem sua própria fila de entrada
    filas_entrada = [Queue(maxsize=FILA_MAX) for _ in range(num_workers)]
    fila_saida    = Queue()

    # inicia workers
    procs = []
    for i in range(num_workers):
        p = Process(target=worker_proc,
                    args=(filas_entrada[i], fila_saida), daemon=True)
        p.start()
        procs.append(p)

    # inicia produtor em thread (I/O não bloqueia o GIL)
    thread_prod = threading.Thread(
        target=produtor,
        args=(ARQUIVO, filas_entrada, BUF_IO),
        daemon=True
    )
    thread_prod.start()

    # coleta resultados: cada worker envia acc + None ao terminar
    parciais = []
    fins     = 0
    while fins < num_workers:
        item = fila_saida.get()
        if item is None:
            fins += 1
        else:
            parciais.append(item)

    thread_prod.join()
    for p in procs:
        p.join()

    t_proc = time.perf_counter() - t0

    por_mes   = reduzir(parciais)
    t_total   = time.perf_counter() - t0
    total_reg = sum(v[3] for v in por_mes.values())

    for mes_cod in sorted(MESES.keys(), reverse=True):
        if mes_cod in por_mes:
            imprimir(mes_cod, *por_mes[mes_cod])

    print(f"\n{'═'*62}")
    print(f"  RESUMO — PIPELINE {num_workers} WORKERS")
    print(f"{'═'*62}")
    for mes_cod in sorted(MESES.keys(), reverse=True):
        if mes_cod in por_mes:
            print(f"  {MESES[mes_cod]}: {por_mes[mes_cod][3]:,} registros")
    print(f"  {'─'*40}")
    print(f"  TOTAL REGISTROS    : {total_reg:,}")
    print(f"  Processamento      : {t_proc:.2f}s")
    print(f"  Redução + exibição : {t_total - t_proc:.2f}s")
    print(f"  TEMPO TOTAL        : {t_total:.2f}s")
    print(f"{'═'*62}\n")


if __name__ == "__main__":
    main()
