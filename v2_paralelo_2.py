"""
Bolsa Família — PARALELO 2 WORKERS
Execute: python v2_paralelo_2.py
"""
import sys
from bolsa_familia_completo import main

if __name__ == "__main__":
    sys.argv = ['v2_paralelo_2.py', '2']
    main()
