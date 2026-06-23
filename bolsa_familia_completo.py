"""
bolsa_familia_completo.py
=========================
Script único com todas as versões de processamento do Bolsa Família.

Contém:
  • Serial
  • Pipeline Paralelo: 2, 4, 8, 12 workers
  • Benchmark automático com tabela e gráfico ASCII

Estratégia (pipeline produtor/consumidor):
  - 1 thread lê o arquivo em blocos de 256 MB  →  I/O máximo do SSD
  - N processos consomem os blocos em paralelo  →  CPU máximo
  - I/O e CPU rodam AO MESMO TEMPO              →  melhor eficiência

Uso:
    python bolsa_familia_completo.py             ← roda benchmark completo
    python bolsa_familia_completo.py serial      ← só serial
    python bolsa_familia_completo.py 8           ← só paralelo com 8 workers
"""

import os
import sys
import time
import threading
import multiprocessing as mp
from multiprocessing import Process, Queue

# ═══════════════════════════════════════════════════════════
#  CONFIGURAÇÕES
# ═══════════════════════════════════════════════════════════
ARQUIVO  = "BolsaFamilia_Out2025_Jan2026.csv"
ENCODING = "latin-1"
BUF_IO   = 256 * 1024 * 1024   # 256 MB por bloco de leitura
FILA_MAX = 3                    # blocos em buffer por worker
CONFIGS  = [1, 2, 4, 8, 12]    # 1 = serial

MESES = {
    "202601": "Jan/2026",
    "202512": "Dez/2025",
    "202511": "Nov/2025",
    "202510": "Out/2025",
}


# ═══════════════════════════════════════════════════════════
#  UTILITÁRIOS
# ═══════════════════════════════════════════════════════════
def brl(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def verificar_arquivo():
    if not os.path.exists(ARQUIVO):
        print(f"  ⚠️  Arquivo não encontrado: {ARQUIVO}")
        print("      Execute unir_planilhas.py primeiro.")
        return False
    print(f"  Arquivo : {ARQUIVO}")
    print(f"  Tamanho : {os.path.getsize(ARQUIVO)/1e9:.2f} GB")
    return True


# ═══════════════════════════════════════════════════════════
#  PRODUTOR — lê o arquivo e distribui blocos (roda em thread)
# ═══════════════════════════════════════════════════════════
def _produtor(arquivo, filas, buf_size):
    sobra = b""
    idx   = 0
    n     = len(filas)
    with open(arquivo, "rb") as f:
        f.readline()                    # pula cabeçalho
        while True:
            bloco = f.read(buf_size)
            if not bloco:
                break
            bloco = sobra + bloco
            nl    = bloco.rfind(b"\n")
            sobra = bloco[nl + 1:]
            bloco = bloco[:nl + 1]
            filas[idx % n].put(bloco)
            idx  += 1
    for fila in filas:
        fila.put(None)                  # sinal de fim para cada worker


# ═══════════════════════════════════════════════════════════
#  WORKER — processa blocos (roda em processo separado)
#  DEVE estar no topo do módulo para o Windows conseguir importar
# ═══════════════════════════════════════════════════════════
def _worker(fila_entrada, fila_saida):
    acc = {}
    while True:
        bloco = fila_entrada.get()
        if bloco is None:
            fila_saida.put(acc)         # envia resultado acumulado
            fila_saida.put(None)        # sinaliza fim deste worker
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


# ═══════════════════════════════════════════════════════════
#  SERIAL
# ═══════════════════════════════════════════════════════════
def _processar_serial():
    acc   = {}
    sobra = b""
    with open(ARQUIVO, "rb") as f:
        f.readline()
        while True:
            bloco = f.read(BUF_IO)
            if not bloco:
                break
            bloco  = sobra + bloco
            nl     = bloco.rfind(b"\n")
            sobra  = bloco[nl + 1:]
            bloco  = bloco[:nl + 1]
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
    return _finalizar(acc)


# ═══════════════════════════════════════════════════════════
#  PARALELO — pipeline produtor/consumidor
# ═══════════════════════════════════════════════════════════
def _processar_paralelo(num_workers):
    filas_entrada = [Queue(maxsize=FILA_MAX) for _ in range(num_workers)]
    fila_saida    = Queue()

    procs = []
    for i in range(num_workers):
        p = Process(target=_worker,
                    args=(filas_entrada[i], fila_saida), daemon=True)
        p.start()
        procs.append(p)

    thread_prod = threading.Thread(
        target=_produtor,
        args=(ARQUIVO, filas_entrada, BUF_IO),
        daemon=True
    )
    thread_prod.start()

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

    return _reduzir(parciais)


# ═══════════════════════════════════════════════════════════
#  REDUÇÃO E FINALIZAÇÃO
# ═══════════════════════════════════════════════════════════
def _finalizar(acc):
    final = {}
    for ms, a in acc.items():
        media = a["soma"] / a["count"] if a["count"] else 0.0
        final[ms] = (a["max"], a["min"], media, a["count"], a["totais"])
    return final

def _reduzir(parciais):
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


# ═══════════════════════════════════════════════════════════
#  IMPRESSÃO
# ═══════════════════════════════════════════════════════════
def _imprimir_mes(mes_cod, max_v, min_v, media, count, totais):
    rotulo = MESES.get(mes_cod, mes_cod)
    print(f"\n{'='*62}")
    print(f"  {rotulo}  -  {count:,} registros")
    print(f"{'='*62}")
    print(f"\n  MAIOR PAGAMENTO INDIVIDUAL")
    print(f"  Valor: {brl(max_v[0])}  |  {max_v[2]} ({max_v[1]})")
    print(f"\n  MENOR PAGAMENTO INDIVIDUAL")
    print(f"  Valor: {brl(min_v[0])}  |  {min_v[2]} ({min_v[1]})")
    print(f"\n  MEDIA ARITMETICA: {brl(media)}")
    for titulo, rev in [("TOP 5 - MAIORES VOLUMES TOTAIS", True),
                        ("TOP 5 - MENORES VOLUMES TOTAIS", False)]:
        print(f"\n  {titulo}")
        print(f"  {'-'*56}")
        for i, (chave, (uf, total, qtd)) in enumerate(
                sorted(totais.items(), key=lambda x: x[1][1], reverse=rev)[:5], 1):
            nome = chave.split("|")[1]
            print(f"  {i}. {nome} ({uf})  -  {brl(total)}  |  {qtd:,} pagamentos")

def _imprimir_resumo(label, por_mes, tempo):
    total_reg = sum(v[3] for v in por_mes.values())
    print(f"\n{'='*62}")
    print(f"  RESUMO - {label}")
    print(f"{'='*62}")
    for mes_cod in sorted(MESES.keys(), reverse=True):
        if mes_cod in por_mes:
            print(f"  {MESES[mes_cod]}: {por_mes[mes_cod][3]:,} registros")
    print(f"  {'-'*40}")
    print(f"  TOTAL REGISTROS : {total_reg:,}")
    print(f"  TEMPO TOTAL     : {tempo:.2f}s")
    print(f"{'='*62}\n")


# ═══════════════════════════════════════════════════════════
#  GRAFICO ASCII
# ═══════════════════════════════════════════════════════════
def _grafico(resultados):
    L = 36

    t_min = min(r[2] for r in resultados)

    print("\n" + "=" * 62)
    print("  BENCHMARK COMPLETO - RESULTADO FINAL")
    print("=" * 62)

    print(f"\n  {'Configuracao':<18} {'Tempo':>8} {'Speedup':>9} {'Eficiencia':>11}")
    print(f"  {'-'*18} {'-'*8} {'-'*9} {'-'*11}")
    for label, workers, tempo, speedup, efic in resultados:
        melhor = " <- MELHOR" if tempo == t_min else ""
        print(f"  {label:<18} {tempo:>7.2f}s {speedup:>8.2f}x {efic:>10.1f}%{melhor}")

    t_max = max(r[2] for r in resultados)
    print(f"\n  TEMPO DE EXECUCAO  (menor = melhor)")
    print(f"  {'-'*58}")
    for label, _, tempo, _, _ in resultados:
        b     = int((tempo / t_max) * L)
        barra = "#" * b + "." * (L - b)
        tag   = " <-" if tempo == t_min else ""
        print(f"  {label:<18} [{barra}] {tempo:.1f}s{tag}")

    s_max = max(r[3] for r in resultados)
    print(f"\n  SPEEDUP            (maior = melhor)")
    print(f"  {'-'*58}")
    for label, workers, _, speedup, _ in resultados:
        if workers == 1:
            continue
        b     = int((speedup / s_max) * L)
        barra = "#" * b + "." * (L - b)
        print(f"  {label:<18} [{barra}] {speedup:.2f}x  (ideal: {workers}x)")

    print(f"\n  EFICIENCIA         (maior = melhor)")
    print(f"  {'-'*58}")
    for label, workers, _, _, efic in resultados:
        if workers == 1:
            continue
        b     = min(int((efic / 100) * L), L)
        barra = "#" * b + "." * (L - b)
        print(f"  {label:<18} [{barra}] {efic:.1f}%")

    melhor = min(resultados, key=lambda x: x[2])
    serial = next(r for r in resultados if r[1] == 1)
    print(f"\n{'='*62}")
    print(f"  MELHOR: {melhor[0]}")
    print(f"  Tempo      : {melhor[2]:.2f}s")
    print(f"  Speedup    : {melhor[3]:.2f}x  (serial: {serial[2]:.2f}s)")
    print(f"  Eficiencia : {melhor[4]:.1f}%")
    print(f"{'='*62}\n")


# ═══════════════════════════════════════════════════════════
#  EXECUÇÃO
# ═══════════════════════════════════════════════════════════
def _executar(cfg):
    t0 = time.perf_counter()
    if cfg == 1:
        por_mes = _processar_serial()
    else:
        por_mes = _processar_paralelo(cfg)
    return por_mes, time.perf_counter() - t0


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "benchmark"

    print("=" * 62)
    print("  BOLSA FAMILIA - OUT/2025 a JAN/2026")
    print("=" * 62)
    if not verificar_arquivo():
        return
    print()

    # modo individual: serial
    if arg == "serial":
        print("  Modo: SERIAL\n")
        por_mes, tempo = _executar(1)
        for mes_cod in sorted(MESES.keys(), reverse=True):
            if mes_cod in por_mes:
                _imprimir_mes(mes_cod, *por_mes[mes_cod])
        _imprimir_resumo("SERIAL", por_mes, tempo)
        return

    # modo individual: N workers
    if arg.isdigit():
        n     = int(arg)
        label = f"PARALELO {n} WORKERS"
        print(f"  Modo: {label}\n")
        por_mes, tempo = _executar(n)
        for mes_cod in sorted(MESES.keys(), reverse=True):
            if mes_cod in por_mes:
                _imprimir_mes(mes_cod, *por_mes[mes_cod])
        _imprimir_resumo(label, por_mes, tempo)
        return

    # modo benchmark completo
    print(f"  Modo: BENCHMARK COMPLETO")
    print(f"  Configuracoes: {CONFIGS}\n")

    t_serial   = None
    resultados = []

    for cfg in CONFIGS:
        label = "Serial" if cfg == 1 else f"Paralelo {cfg:>2}w"
        print(f"  > [{label}]", end="  ", flush=True)

        por_mes, tempo = _executar(cfg)

        if cfg == 1:
            t_serial = tempo

        speedup    = t_serial / tempo
        eficiencia = (speedup / cfg) * 100
        total_reg  = sum(v[3] for v in por_mes.values())

        print(f"{tempo:.2f}s  |  speedup {speedup:.2f}x  |  {total_reg:,} registros")

        for mes_cod in sorted(MESES.keys(), reverse=True):
            if mes_cod in por_mes:
                _imprimir_mes(mes_cod, *por_mes[mes_cod])

        _imprimir_resumo(label, por_mes, tempo)
        resultados.append((label, cfg, tempo, speedup, eficiencia))

    _grafico(resultados)


# ═══════════════════════════════════════════════════════════
#  ENTRY POINT — obrigatorio para Windows + multiprocessing
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    mp.freeze_support()
    main()
