"""
Bolsa Família — PARALELO 8 WORKERS
Execute: python v8_paralelo_8.py
"""
import sys
from bolsa_familia_completo import main

if __name__ == "__main__":
    sys.argv = ['v8_paralelo_8.py', '8']
    main()
