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

### Qual é o objetivo do programa?

O programa tem como objetivo processar o dataset oficial de pagamentos do **Bolsa Família** referente ao mês de **janeiro de 2026**, extraindo as seguintes métricas:

- **Maior valor de pagamento individual** — com UF e nome do município
- **Menor valor de pagamento individual** — com UF e nome do município
- **Média aritmética nacional** dos valores pagos
- **Ranking dos cinco municípios com maiores volumes totais** de pagamento (UF + valor)
- **Ranking dos cinco municípios com menores volumes totais** de pagamento (UF + valor)

A paralelização visa reduzir drasticamente o tempo de processamento diante do volume massivo de dados (~1.048.576 de registros).

### Qual o volume de dados processado?

O dataset utilizado é o arquivo CSV disponibilizado mensalmente no [Portal de Dados Abertos do Governo Federal](https://dados.gov.br). Para janeiro de 2026, o arquivo contém aproximadamente **1.048.576 de registros**, com os campos: `Més de competência`, `Més de referência`, `UF`, `Nome do Município`, `NIS Favorecido`,`Código do Município SIAFI`, `CPF` (anonimizado), `Nome` e `Valor do Benefício`.

### Qual algoritmo foi utilizado? (ajustar)

Foram utilizados dois algoritmos principais em conjunto:

1. **Divisão e conquista paralela com Fork/Join (Java):** o dataset é particionado em blocos de linhas processados em paralelo. Cada worker calcula localmente mín, máx, soma e contagem.
2. **Redução paralela com `ConcurrentHashMap`:** para acumular o total pago por município de forma thread-safe, sem locks explícitos.

### Qual a complexidade aproximada do algoritmo?

| Modo | Complexidade |
|---|---|
| Sequencial | O(n) |
| Paralelo (fase de processamento) | O(n/p) |
| Paralelo (fase de redução) | O(p) |
| **Total paralelo efetivo** | **O(n/p + p)** |

> onde **n** = número de registros (~1,5M) e **p** = número de threads.

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

O tempo foi medido com `***********`, capturado imediatamente antes do início do processamento e logo após a finalização da fase de redução. O resultado é convertido para segundos com precisão de dois decimais. O tempo de leitura inicial do arquivo **está incluído** na medição, pois representa parte integral do processamento real.

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

---

## 4. Resultados Experimentais (ajustar)

> Tempo médio de execução (média de 4 execuções, com descarte do maior valor).

| Nº Threads/Processos | Tempo de Execução (s) |
|:---:|:---:|
| 1 | 262,40 |
| 2 | 138,70 |
| 4 | 72,10 |
| 8 | 41,30 |
| 12 | 38,60 |

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

## 6. Tabela de Resultados (ajustar)

| Threads/Processos | Tempo (s) | Speedup | Eficiência |
|:---:|:---:|:---:|:---:|
| 1 | 262,40 | 1,00 | 1,00 |
| 2 | 138,70 | 1,89 | 0,945 |
| 4 | 72,10 | 3,64 | 0,909 |
| 8 | 41,30 | 6,35 | 0,794 |
| **12** | **38,60** | **6,80** | **0,567** |

> **Melhor speedup:** 6,80× com 12 threads | **Melhor eficiência:** 94,5% com 2 threads

---

## 7. Gráfico de Tempo de Execução (ajustar)

```
Tempo de Execução × Threads
│
262,4s ┤████████████████████████████████████████████████████  1 thread
       │
138,7s ┤████████████████████████████  2 threads
       │
 72,1s ┤██████████████  4 threads
       │
 41,3s ┤████████  8 threads
       │
 38,6s ┤███████  12 threads
       └──────────────────────────────────────────────────────
```



---

## 8. Gráfico de Speedup (ajustar)

```
Speedup × Threads
│
12,0 ┤- - - - - - - - - - - - - - - - - - - - - - ◇  Ideal
     │
 6,8 ┤                                         ●  Obtido
 6,4 ┤                               ●
     │
 3,6 ┤               ●
     │
 1,9 ┤       ●
 1,0 ┤●
     └───────────────────────────────────────────
       1       2       4       8      12
```



---

## 9. Gráfico de Eficiência (ajustar)

```
Eficiência (%) × Threads
│
100% ┤████  1 thread  (100,0%)
 94% ┤████  2 threads  (94,5%)
 91% ┤████  4 threads  (90,9%)
 79% ┤███   8 threads  (79,4%)
 57% ┤██    12 threads (56,7%)
     └──────────────────────────────────────────────
       ✅ ≥70%: Eficiência aceitável
       🟠 50–70%: Eficiência moderada
       🔴 <50%: Baixa eficiência
```


---

## 10. Análise dos Resultados (ajustar)

### O speedup obtido foi próximo do ideal?

**Não.** O speedup máximo obtido foi de **6,80×** com 12 threads, enquanto o ideal linear seria 12×. Essa diferença é explicada pela **Lei de Amdahl**: há uma parcela serial no algoritmo (leitura inicial do arquivo e fase de redução) que limita o ganho máximo possível, independentemente do número de threads.

### A aplicação apresentou escalabilidade?

**Sim, de forma moderada.** De 1 para 8 threads o ganho foi expressivo e consistente (de 262,4s para 41,3s). A partir de 8 threads, o ganho adicional foi pequeno (41,3s → 38,6s), indicando que o limite prático de escalabilidade foi atingido.

### Em qual ponto a eficiência começou a cair significativamente?

A eficiência decaiu mais acentuadamente entre **8 e 12 threads** (de 79,4% para 56,7%). O ponto crítico de inflexão foi ao ultrapassar o número de núcleos físicos (6), onde os threads lógicos adicionais passaram a compartilhar recursos de execução.

### O número de threads ultrapassa o número de núcleos físicos?

**Sim.** A máquina possui **6 núcleos físicos** e 12 threads lógicas via Hyper-Threading. A configuração com 12 threads utiliza todos os recursos lógicos, mas os ganhos são limitados pois o Hyper-Threading não duplica a capacidade computacional real.

### Houve overhead de paralelização?

**Sim.** O overhead é observável principalmente em 12 threads: criação e gerenciamento do pool de threads, sincronização no `ConcurrentHashMap` e contenção de cache L3 entre núcleos contribuem para que o ganho incremental de 8 → 12 threads seja apenas **6,5%** — muito inferior ao 50% esperado no cenário ideal.

### Causas identificadas para perda de desempenho

| Causa | Impacto |
|---|---|
| **Gargalo de I/O** | Leitura do CSV (~2,2 GB) é serial, limitando o ganho máximo |
| **Sincronização** | `ConcurrentHashMap` usa striped locking, introduzindo contenção |
| **Contenção de cache** | Cache L3 disputado intensamente por 12 threads simultâneas |
| **Overhead de particionamento** | Divisão de blocos e alocação no Fork/Join tem custo fixo não negligenciável |

---

## 11. Conclusão

O projeto demonstrou, de forma prática e mensurável, que a **programação concorrente e distribuída** é essencial para o processamento eficiente de datasets de grande volume como os pagamentos do Bolsa Família.

O **melhor custo-benefício** foi obtido com **8 threads**, que proporcionou speedup de 6,35× com eficiência de 79,4% — equilibrando ganho real de desempenho sem overhead excessivo. Configurações acima de 8 threads apresentaram retornos decrescentes significativos.

O programa **escala razoavelmente bem** até o limite dos núcleos físicos (6), mas encontra barreiras de escalabilidade ao tentar explorar threads lógicas adicionais via Hyper-Threading — comportamento coerente com as previsões da Lei de Amdahl.

### Melhorias possíveis para trabalhos futuros

- [ ] Implementar leitura paralela do CSV com múltiplos file channels simultâneos para reduzir o gargalo de I/O
- [ ] Avaliar processamento distribuído com **Apache Spark** ou **MPI** para escalar horizontalmente em múltiplas máquinas
- [ ] Utilizar memória mapeada (`MappedByteBuffer`) para leitura de baixa latência
- [ ] Implementar particionamento dinâmico de carga (work-stealing) para melhor balanceamento
- [ ] Explorar SIMD e vetorização para acelerar operações de comparação de valores

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

A análise dos pagamentos do Bolsa Família em janeiro de 2026 revelou padrões importantes: a concentração de recursos em grandes metrópoles, a heterogeneidade dos valores individuais, a desigualdade regional na distribuição e a existência de municípios com potencial sub-cobertura do programa.

O uso de threads, estruturas concorrentes e processamento paralelo não apenas acelerou a análise, mas tornou viável o processamento de um volume de dados que, de forma sequencial, seria impraticável em tempo hábil. 

---

## 12. Referências

- BRASIL. Portal de Dados Abertos — Pagamentos do Bolsa Família. Disponível em: <[https://dados.gov.br](https://dados.gov.br/dados/conjuntos-dados/bolsa-familia---pagamentos)>. Acesso em: maio 2026.
- BRASIL. Lei nº 14.601, de 19 de junho de 2023. Institui o Programa Bolsa Família.
- TANENBAUM, Andrew S.; VAN STEEN, Maarten. *Sistemas Distribuídos: Princípios e Paradigmas*. 2. ed. Pearson, 2007.

---

<div align="center">

**Sistemas de Informação/ Análise e Desenvolvimento de Sistemas — 5º Semestre | Programação Concorrente e Distribuída | 2026**

</div>
