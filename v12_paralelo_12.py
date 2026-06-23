"""
Bolsa Família — PARALELO 12 WORKERS
Execute: python v12_paralelo_12.py
"""
import sys
from bolsa_familia_completo import main

if __name__ == "__main__":
    sys.argv = ['v12_paralelo_12.py', '12']
    main()
