"""
Bolsa Família — PARALELO 4 WORKERS
Execute: python v4_paralelo_4.py
"""
import sys
from bolsa_familia_completo import main

if __name__ == "__main__":
    sys.argv = ['v4_paralelo_4.py', '4']
    main()
