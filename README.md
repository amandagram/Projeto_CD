# Relatório — Análise de Pagamentos do Bolsa Família (Janeiro/2026)

| Campo | Informacao |
|---|---|
| **Disciplina** | Programação Concorrente e Distribuída |
| **Aluno(s)** | Amanda Ramos e Arthur Poeck |
| **Turma** | SI-2026/ADS-2026 — 5º Semestre |
| **Professor** | Rafael Marconi|


---

## Sumário

1. [Descrição do Problema](#1-descrição-do-problema)
2. [Ambiente Experimental](#2-ambiente-experimental)
3. [Metodologia de Testes](#3-metodologia-de-testes)
4. [Resultados Experimentais](#4-resultados-experimentais)
5. [Cálculo de Speedup e Eficiência](#5-cálculo-de-speedup-e-eficiência)
6. [Tabela de Resultados](#6-tabela-de-resultados)
7. [Gráfico de Tempo de Execução](#7-gráfico-de-tempo-de-execução)
8. [Gráfico de Speedup](#8-gráfico-de-speedup)
9. [Gráfico de Eficiência](#9-gráfico-de-eficiência)
10. [Análise dos Resultados](#10-análise-dos-resultados)
11. [Conclusão](#11-conclusão)

---

## 1. Descrição do Problema

### Relevância e Benefício para a Sociedade

O Bolsa Família é o maior programa de transferência de renda do Brasil, criado em 2003 e reformulado em 2023. Ele atende famílias em situação de pobreza e extrema pobreza por meio do pagamento mensal de benefícios financeiros, condicionados ao cumprimento de condicionalidades nas áreas de saúde e educação.

Com a nova reformulação, o programa passou a ter uma estrutura de benefícios mais ampla, incluindo o Benefício de Renda Familiar per capita, o Benefício Primeira Infância (para crianças de 0 a 6 anos), o Benefício Variável Familiar Nutriz (para gestantes e lactantes) e o Benefício Variável Familiar (para crianças e adolescentes de 7 a 18 anos). Essa estrutura torna o programa mais sensível à composição familiar e às condições socioeconômicas de cada domicílio.

Analisar esse volume massivo de dados de forma eficiente é um desafio computacional que demanda o uso de técnicas avançadas de programação concorrente e distribuída.

A análise computacional dos dados do Bolsa Família não é apenas um exercício acadêmico: ela representa uma ferramenta real de transparência pública, controle social e formulação de políticas. Compreender como os recursos são distribuídos geograficamente, demograficamente e financeiramente  é fundamental para garantir que o programa atinja seus objetivos com eficiência e equidade.

### Por que este projeto importa para a sociedade?

Transparência e controle social;
Apoio à tomada de decisão pública;
Combate a fraudes e irregularidades;
Redução da desigualdade regional;
Eficiência tecnológica a serviço público.

Em suma, este projeto demonstra que a tecnologia, especialmente a programação paralela e distribuída, é uma aliada indispensável na construção de um Estado mais transparente, eficiente e justo. Cada análise realizada sobre os dados do Bolsa Família é, em última instância, uma contribuição para que os recursos públicos cheguem a quem mais precisa.

A análise dos pagamentos do Bolsa Família revela padrões importantes: a concentração de recursos em grandes metrópoles, a heterogeneidade dos valores individuais, a desigualdade regional na distribuição e a existência de municípios com potencial sub-cobertura do programa.

O uso de threads, estruturas concorrentes e processamento paralelo não apenas acelerou a análise, mas tornou viável o processamento de um volume de dados que, de forma sequencial, seria impraticável em tempo hábil. 

---
### Qual é o objetivo do programa?

O programa tem como objetivo processar o dataset oficial de pagamentos do **Bolsa Família** referente ao mês de **janeiro de 2026, dezembro de 2025, novembro de 2025 e outubro de 2025**, extraindo as seguintes métricas:

- **Maior valor de pagamento individual** — com UF e nome do município
- **Menor valor de pagamento individual** — com UF e nome do município
- **Média aritmética nacional** dos valores pagos
- **Ranking dos cinco municípios com maiores volumes totais** de pagamento (UF + valor)
- **Ranking dos cinco municípios com menores volumes totais** de pagamento (UF + valor)

A paralelização visa reduzir drasticamente o tempo de processamento diante do volume massivo de dados (~74,9 M de registros).

### Qual o volume de dados processado?

O dataset utilizado é o arquivo CSV disponibilizado mensalmente no [Portal de Dados Abertos do Governo Federal](https://dados.gov.br). Para os 04 meses, o arquivo contém aproximadamente **~74,9 M de registros (8,1Gb)**, com os campos: `Més de competência`, `Més de referência`, `UF`, `Nome do Município`, `NIS Favorecido`,`Código do Município SIAFI`, `CPF` (anonimizado), `Nome` e `Valor do Benefício`.

### Qual algoritmo foi utilizado? 

Foram utilizados dois algoritmos principais em conjunto:

1. **Divisão e conquista paralela:** o dataset é particionado em blocos de linhas processados em paralelo. Cada worker calcula localmente mín, máx, soma e contagem.
2. **Redução paralela com `ConcurrentHashMap`:** para acumular o total pago por município de forma thread-safe, sem locks explícitos.

### Qual a complexidade aproximada do algoritmo?

| Modo | Complexidade |
|---|---|
| Sequencial | O(n) |
| Paralelo (fase de processamento) | O(n/p) |
| Paralelo (fase de redução) | O(p) |
| **Total paralelo efetivo** | **O(n/p + p)** |

> onde **n** = número de registros (~4M) e **p** = número de threads.

---

## 2. Ambiente Experimental

| Item | Descrição |
|---|---|
| **Processador** | ************** |
| **Número de núcleos** | ******************** |
| **Memória RAM** | 16 GB DDR4 2933 MHz |
| **Sistema Operacional** | ****************** |
| **Linguagem utilizada** | ******************* |
| **Biblioteca de paralelização** | ****************** |
| **Compilador / Versão** | ***************** |

---

## 3. Metodologia de Testes

### Como o tempo de execução foi medido

O tempo foi medido capturado imediatamente antes do início do processamento e logo após a finalização da fase de redução. O resultado é convertido para segundos com precisão de dois decimais. O tempo de leitura inicial do arquivo **está incluído** na medição, pois representa parte integral do processamento real.

### Número de execuções e cálculo da média

Para cada configuração foram realizadas **5 execuções independentes**. A execução com o maior tempo foi descartada (possível outlier por interferência do SO) e calculou-se a **média aritmética simples das 4 execuções restantes**.

### Configurações testadas

| Configuração | Descrição |
|---|---|
| 1 thread | Versão serial — baseline de comparação |
| 2 threads | Paralelismo mínimo |
| 4 threads | Paralelismo moderado |
| 8 threads | Paralelismo avançado (acima dos núcleos físicos) |
| 12 threads | Paralelismo máximo (todos os threads lógicos) |

### Condições de execução

Todos os testes foram executados com a máquina em estado dedicado: sem outros processos em foreground, tela bloqueada e redes desabilitadas. O arquivo CSV foi lido a partir de disco local (SSD NVMe) para minimizar variação de I/O.

## Estrutura do projeto

```
bolsa_familia/
├── comum.py                          # Funções compartilhadas (parser, redução, formatação)
├── paralelo_base.py                  # Lógica paralela base
├── unir_planilhas.py                 # Concatena os 4 CSVs em um único arquivo
├── v1_serial.py                      # Processamento serial
├── v2_paralelo_2.py                  # Paralelo com 2 workers
├── v4_paralelo_4.py                  # Paralelo com 4 workers
├── v8_paralelo_8.py                  # Paralelo com 8 workers
├── v12_paralelo_12.py                # Paralelo com 12 workers
├── benchmark.py                      # Roda todos os modos e exibe gráfico comparativo
└── BolsaFamilia_Out2025_Jan2026.csv  # CSV unificado (gerado por unir_planilhas.py)
```

---

## 4. Resultados Experimentais 

> Tempo médio de execução (média de 4 execuções, com descarte do maior valor).

| Nº Threads/Processos | Tempo de Execução (s) |
|:---:|:---:|
| 1 | 178,27 |
| 2 | 93,02 |
| 4 | 49,51  |
| 8 | 26,26  |
| 12 |16,84 |

---

## 5. Cálculo de Speedup e Eficiência

### Speedup

$$Speedup(p) = \frac{T(1)}{T(p)}$$

onde:
- $T(1)$ = tempo da execução serial
- $T(p)$ = tempo com $p$ threads/processos

### Eficiência

$$Eficiência(p) = \frac{Speedup(p)}{p}$$

onde:
- $p$ = número de threads ou processos

---




## 6. Tabela de Resultados

| Threads (p) | Tempo (s) | Speedup S(p) | Eficiência E(p) |
|:-----------:|:---------:|:------------:|:----------------:|
| 1           | 178.27    | 1.00x        | 100.0%           |
| 2           | 93.02     | 1.92x        | 95.8%            |
| 4           | 49.51     | 3.60x        | 90.0%            |
| 8           | 24.26     | 7.35x        | 91.9%            |
| 12          | 16.84     | 10.59x        | 88.2%            |


---

## 7. Gráfico de Tempo de Execução 

Tempo de Execução (s)

<img width="571" height="361" alt="image" src="https://github.com/user-attachments/assets/d4b9cf1c-da4b-4632-bbb2-fd98eeda5acf" />


---

## 8. Gráfico de Speedup

Speedup × Threads


<img width="579" height="364" alt="image" src="https://github.com/user-attachments/assets/0f4ea0ae-5fb5-4da7-a6e5-9d6286f3ec0f" />



---

## 9. Gráfico de Eficiência

Eficiência (%) × Threads


<img width="569" height="364" alt="image" src="https://github.com/user-attachments/assets/025254ac-fd96-485f-bbf0-1a90b3c30456" />



---

## 10. Análise dos Resultados 

## Análise de resultados

O tempo de execução caiu de forma monotônica conforme threads foram adicionadas: 178,27s (serial) → 93,02s (2) → 49,51s (4) → 24,26s (8) → 16,84s (12). A maior redução proporcional ocorreu nos primeiros incrementos — de 1 para 2 e de 2 para 4 threads o tempo praticamente foi dividido pela metade — enquanto o ganho marginal diminuiu nos níveis mais altos: de 8 para 12 threads (+50% de threads) o tempo caiu apenas de 24,26s para 16,84s.

O speedup cresceu de forma consistente ao longo de todo o intervalo testado, atingindo 1,92x, 3,60x, 7,35x e 10,59x para 2, 4, 8 e 12 threads, respectivamente. Até 8 threads, o speedup acompanhou de perto a curva ideal (linear); a partir desse ponto, o distanciamento da curva ideal se tornou mais perceptível, já que o ganho de 8 para 12 threads (+33% de threads) representou um aumento de apenas 3,24 pontos no speedup, abaixo do esperado num cenário linear (que exigiria chegar a 12,00x).

A eficiência partiu de 100% (caso serial, por definição) e decaiu de forma geral conforme o número de threads aumentou: 95,8% (2), 90,0% (4), 91,9% (8) e 88,2% (12). A queda não foi abrupta nem concentrada em um único ponto — trata-se de uma degradação suave e contínua, típica de sistemas paralelos reais, com uma pequena oscilação não monotônica entre 4 e 8 threads (90,0% → 91,9%) que está dentro da margem normal de variação experimental.

Os três indicadores (tempo, speedup e eficiência) descrevem o mesmo comportamento sob ângulos diferentes: a aplicação escala bem, mas com retornos marginais decrescentes. Esse padrão é esperado e consistente com a Lei de Amdahl — existe uma fração do trabalho que permanece sequencial ou sujeita a overhead de sincronização/comunicação, e essa fração passa a pesar proporcionalmente mais conforme o número de threads cresce. O fato de a eficiência permanecer numa faixa relativamente estreita (88%–96%) e não despencar abruptamente sugere que não há um gargalo crítico isolado (como contenção severa de cache ou um lock muito disputado), e sim um overhead distribuído e moderado, compatível com uma paralelização bem implementada, embora não perfeita.


---

## 11. Conclusão

## Conclusão

Os testes de desempenho realizados com 1, 2, 4, 8 e 12 threads, partindo de um tempo de execução serial de referência de 178.27 segundos, demonstraram que a aplicação possui **boa escalabilidade**, com speedup crescente em todas as configurações testadas, ainda que com perda gradual de eficiência conforme o número de threads aumenta.

### Speedup

O speedup obtido cresce de forma consistente, mas se distancia progressivamente do speedup ideal (linear) a partir de 4 threads:

- 2 threads → speedup de 1.92x (ideal: 2.00x)
- 4 threads → speedup de 3.60x (ideal: 4.00x)
- 8 threads → speedup de 7.35x (ideal: 8.00x)
- 12 threads → speedup de 10.59x (ideal: 12.00x)

O ganho absoluto de desempenho continua aumentando até 12 threads, mas cada thread adicional contribui proporcionalmente menos que a anterior — um comportamento esperado em sistemas paralelos reais.

### Eficiência

A eficiência paralela parte de 95.8% em 2 threads, cai para 90.0% em 4 threads, recupera-se parcialmente para 91.9% em 8 threads e volta a cair para 88.2% em 12 threads. Não há uma queda abrupta em nenhum ponto específico — a tendência geral é de **degradação suave e contínua**, com a eficiência se mantendo numa faixa relativamente estreita (88% a 96%) em todo o intervalo testado.

### Interpretação dos resultados

A queda progressiva de eficiência, sem colapsos abruptos, é consistente com fontes típicas de overhead em paralelização que se acumulam com o aumento do número de threads:

- **Overhead de sincronização**, como locks, mutexes ou barreiras, que se torna proporcionalmente mais custoso à medida que mais threads concorrem pelos mesmos recursos;
- **Contenção de recursos compartilhados**, como cache (false sharing) ou largura de banda de memória, especialmente perceptível quando o número de threads se aproxima do número de núcleos físicos disponíveis;
- **Fração sequencial do algoritmo**, prevista pela Lei de Amdahl — parte do trabalho não pode ser paralelizada e passa a representar uma fatia maior do tempo total conforme mais threads são adicionadas;
- **Custo de criação e gerenciamento de threads**, que cresce com a quantidade total de threads ativas, ainda que de forma menos significativa que os fatores anteriores.

A leve recuperação observada em 8 threads (91.9%, acima dos 90.0% de 4 threads) está dentro de uma variação normal de medição e não indica necessariamente um padrão real — pequenas flutuações como essa são esperadas em benchmarks de sistemas reais, sobretudo se houve qualquer atividade concorrente na máquina durante os testes.


Em síntese, a implementação demonstra escalabilidade sólida, com speedup superior a 10x em 12 threads, mas evidencia overhead de paralelização crescente — um padrão esperado e dentro de parâmetros saudáveis para a maioria das aplicações paralelas reais.
---


### Dados
==============================================================
  BOLSA FAMILIA - OUT/2025 a JAN/2026
==============================================================
  Arquivo : BolsaFamilia_Out2025_Jan2026.csv
  Tamanho : 8.26 GB

==============================================================
  Jan/2026  -  19,374,167 registros
==============================================================

  MAIOR PAGAMENTO INDIVIDUAL
  Valor: R$ 3.956,00  |  NOVA IGUACU (RJ)

  MENOR PAGAMENTO INDIVIDUAL
  Valor: R$ 25,00  |  ITAQUI (RS)

  MEDIA ARITMETICA: R$ 667,25

  TOP 5 - MAIORES VOLUMES TOTAIS
  --------------------------------------------------------
  1. SAO PAULO (SP)  -  R$ 435.243.761,00  |  672,164 pagamentos
  2. RIO DE JANEIRO (RJ)  -  R$ 294.866.057,00  |  454,060 pagamentos
  3. FORTALEZA (CE)  -  R$ 192.402.902,00  |  299,462 pagamentos
  4. SALVADOR (BA)  -  R$ 181.276.552,00  |  282,664 pagamentos
  5. MANAUS (AM)  -  R$ 166.861.010,00  |  245,897 pagamentos

  TOP 5 - MENORES VOLUMES TOTAIS
  --------------------------------------------------------
  1. SANTA TEREZA (RS)  -  R$ 2.780,00  |  5 pagamentos
  2. BRACO DO TROMBUDO (SC)  -  R$ 3.156,00  |  7 pagamentos
  3. MONTAURI (RS)  -  R$ 3.175,00  |  6 pagamentos
  4. CUNHATAI (SC)  -  R$ 3.235,00  |  5 pagamentos
  5. CORONEL PILAR (RS)  -  R$ 3.802,00  |  7 pagamentos

==============================================================
  Dez/2025  -  18,662,331 registros
==============================================================

  MAIOR PAGAMENTO INDIVIDUAL
  Valor: R$ 4.056,00  |  NOVA IGUACU (RJ)

  MENOR PAGAMENTO INDIVIDUAL
  Valor: R$ 25,00  |  TERESINA (PI)

  MEDIA ARITMETICA: R$ 677,34

  TOP 5 - MAIORES VOLUMES TOTAIS
  --------------------------------------------------------
  1. SAO PAULO (SP)  -  R$ 411.457.118,00  |  620,976 pagamentos
  2. RIO DE JANEIRO (RJ)  -  R$ 283.250.459,00  |  427,923 pagamentos
  3. FORTALEZA (CE)  -  R$ 183.789.813,00  |  280,599 pagamentos
  4. SALVADOR (BA)  -  R$ 178.117.669,00  |  273,821 pagamentos
  5. MANAUS (AM)  -  R$ 161.439.090,00  |  232,759 pagamentos

  TOP 5 - MENORES VOLUMES TOTAIS
  --------------------------------------------------------
  1. MONTAURI (RS)  -  R$ 3.175,00  |  6 pagamentos
  2. SANTA TEREZA (RS)  -  R$ 3.310,00  |  5 pagamentos
  3. CUNHATAI (SC)  -  R$ 3.610,00  |  6 pagamentos
  4. CORONEL PILAR (RS)  -  R$ 3.927,00  |  7 pagamentos
  5. BRACO DO TROMBUDO (SC)  -  R$ 4.081,00  |  9 pagamentos

==============================================================
  Nov/2025  -  18,309,734 registros
==============================================================

  MAIOR PAGAMENTO INDIVIDUAL
  Valor: R$ 4.056,00  |  NOVA IGUACU (RJ)

  MENOR PAGAMENTO INDIVIDUAL
  Valor: R$ 25,00  |  QUIXERAMOBIM (CE)

  MEDIA ARITMETICA: R$ 674,57

  TOP 5 - MAIORES VOLUMES TOTAIS
  --------------------------------------------------------
  1. SAO PAULO (SP)  -  R$ 381.144.947,00  |  582,595 pagamentos
  2. RIO DE JANEIRO (RJ)  -  R$ 287.336.806,00  |  434,715 pagamentos
  3. FORTALEZA (CE)  -  R$ 184.148.153,00  |  281,816 pagamentos
  4. SALVADOR (BA)  -  R$ 176.099.820,00  |  271,403 pagamentos
  5. MANAUS (AM)  -  R$ 162.401.380,00  |  235,284 pagamentos

  TOP 5 - MENORES VOLUMES TOTAIS
  --------------------------------------------------------
  1. MONTAURI (RS)  -  R$ 3.175,00  |  6 pagamentos
  2. POCO DAS ANTAS (RS)  -  R$ 3.776,00  |  7 pagamentos
  3. TRES ARROIOS (RS)  -  R$ 3.930,00  |  6 pagamentos
  4. SANTA TEREZA (RS)  -  R$ 3.960,00  |  6 pagamentos
  5. BARRA DO RIO AZUL (RS)  -  R$ 4.000,00  |  7 pagamentos

==============================================================
  Out/2025  -  18,599,089 registros
==============================================================

  MAIOR PAGAMENTO INDIVIDUAL
  Valor: R$ 4.056,00  |  NOVA IGUACU (RJ)

  MENOR PAGAMENTO INDIVIDUAL
  Valor: R$ 25,00  |  FORTALEZA (CE)

  MEDIA ARITMETICA: R$ 673,60

  TOP 5 - MAIORES VOLUMES TOTAIS
  --------------------------------------------------------
  1. SAO PAULO (SP)  -  R$ 386.606.568,00  |  589,803 pagamentos
  2. RIO DE JANEIRO (RJ)  -  R$ 294.928.605,00  |  446,450 pagamentos
  3. FORTALEZA (CE)  -  R$ 187.133.994,00  |  286,868 pagamentos
  4. SALVADOR (BA)  -  R$ 179.243.045,00  |  276,320 pagamentos
  5. MANAUS (AM)  -  R$ 161.253.347,00  |  233,554 pagamentos

  TOP 5 - MENORES VOLUMES TOTAIS
  --------------------------------------------------------
  1. MONTAURI (RS)  -  R$ 3.175,00  |  6 pagamentos
  2. BARRA DO RIO AZUL (RS)  -  R$ 3.675,00  |  6 pagamentos
  3. TRES ARROIOS (RS)  -  R$ 3.930,00  |  6 pagamentos
  4. SANTA TEREZA (RS)  -  R$ 3.960,00  |  6 pagamentos
  5. SAO DOMINGOS DO SUL (RS)  -  R$ 3.981,00  |  6 pagamentos

==============================================================
  RESUMO 
==============================================================
  Jan/2026: 19,374,167 registros
  Dez/2025: 18,662,331 registros
  Nov/2025: 18,309,734 registros
  Out/2025: 18,599,089 registros
  ----------------------------------------
  TOTAL REGISTROS : 74,945,321
  
==============================================================


## 12. Referências

- BRASIL. Portal de Dados Abertos — Pagamentos do Bolsa Família. Disponível em: [<[https://dados.gov.br](https://dados.gov.br/dados/conjuntos-dados/bolsa-familia---pagamentos)>](https://dados.gov.br/dados/conjuntos-dados/bolsa-familia---pagamentos). Acesso em: maio 2026.
- BRASIL. Lei nº 14.601, de 19 de junho de 2023. Institui o Programa Bolsa Família.
- TANENBAUM, Andrew S.; VAN STEEN, Maarten. *Sistemas Distribuídos: Princípios e Paradigmas*. 2. ed. Pearson, 2007.

---

<div align="center">

**Sistemas de Informação/ Análise e Desenvolvimento de Sistemas — 5º Semestre | Programação Concorrente e Distribuída | 2026**

</div>
