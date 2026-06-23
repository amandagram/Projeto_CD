"""
Bolsa Família — UNIFICAÇÃO DE PLANILHAS
Concatena os 4 CSVs mensais em um único arquivo.
Execute ANTES de qualquer outro script.
Execute: python unir_planilhas.py
"""
import os, time

ARQUIVOS = [
    ("Jan/2026", "202601_NovoBolsaFamilia.csv"),
    ("Dez/2025", "202512_NovoBolsaFamilia.csv"),
    ("Nov/2025", "202511_NovoBolsaFamilia.csv"),
    ("Out/2025", "202510_NovoBolsaFamilia.csv"),
]
SAIDA = "BolsaFamilia_Out2025_Jan2026.csv"
BUF   = 64 * 1024 * 1024   # 64 MB

def main():
    print("=" * 62)
    print("  BOLSA FAMÍLIA — UNIFICAÇÃO DE PLANILHAS")
    print("=" * 62)

    faltando = [arq for _, arq in ARQUIVOS if not os.path.exists(arq)]
    if faltando:
        print("⚠️  Arquivos não encontrados:")
        for a in faltando: print(f"   • {a}")
        return

    total = sum(os.path.getsize(arq) for _, arq in ARQUIVOS)
    print(f"\n  Arquivos     : {len(ARQUIVOS)}")
    print(f"  Tamanho total: {total/1e9:.2f} GB")
    print(f"  Saída        : {SAIDA}\n")

    t0 = time.perf_counter()
    cabecalho_ok = False
    total_linhas = 0

    with open(SAIDA, "wb") as out:
        for mes, caminho in ARQUIVOS:
            tam = os.path.getsize(caminho)
            print(f"  ▶ Adicionando {mes}  ({tam/1e9:.2f} GB)...", end=" ", flush=True)
            t_mes = time.perf_counter()
            linhas_mes = 0
            with open(caminho, "rb") as f:
                cab = f.readline()
                if not cabecalho_ok:
                    out.write(cab)
                    cabecalho_ok = True
                while True:
                    bloco = f.read(BUF)
                    if not bloco: break
                    out.write(bloco)
                    linhas_mes += bloco.count(b"\n")
            total_linhas += linhas_mes
            print(f"{linhas_mes:,} registros  —  {time.perf_counter()-t_mes:.1f}s")

    t = time.perf_counter() - t0
    print(f"\n{'═'*62}")
    print(f"  ✅  CONCLUÍDO em {t:.1f}s")
    print(f"  Arquivo : {SAIDA}")
    print(f"  Tamanho : {os.path.getsize(SAIDA)/1e9:.2f} GB")
    print(f"  Total   : ~{total_linhas:,} registros")
    print(f"{'═'*62}\n")

if __name__ == "__main__":
    main()
