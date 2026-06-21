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

---

## 4. Resultados Experimentais 

> Tempo médio de execução (média de 4 execuções, com descarte do maior valor).

| Nº Threads/Processos | Tempo de Execução (s) |
|:---:|:---:|
| 1 | 178,27 |
| 2 | 89,02 |
| 4 | 44,51  |
| 8 | 22,26  |
| 12 |14,84 |

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
| 1           | 178.00    | 1.00x        | 100.0%           |
| 2           | 89.03     | 2.00x        | 100.0%           |
| 4           | 44.51     | 4.00x        | 100.0%           |
| 8           | 22.26     | 8.00x        | 100.0%           |
| 12          | 14.84*    | 11.99x       | ~100.0%*         |
---
> **Melhor speedup:**  | **Melhor eficiência:** 
---

## 7. Gráfico de Tempo de Execução 

Tempo de Execução (s)
<img width="571" height="367" alt="image" src="https://github.com/user-attachments/assets/c43b28ca-e97c-41ac-ab39-a7b8c18c568e" />


---

## 8. Gráfico de Speedup

Speedup × Threads

<img width="576" height="370" alt="image" src="https://github.com/user-attachments/assets/476dae0f-0437-4441-b4ee-d8a5f241aaec" />




---

## 9. Gráfico de Eficiência

Eficiência (%) × Threads

<img width="578" height="368" alt="image" src="https://github.com/user-attachments/assets/d02da96d-3b27-4af4-895f-e822e02e9ab2" />



---

## 10. Análise dos Resultados 

### O speedup obtido foi próximo do ideal?

Sim. Em todos os pontos testados (2, 4, 8 e 12 threads) o speedup ficou praticamente colado na curva ideal (linear): 2.00x, 4.00x, 8.00x e 11.99x para 2, 4, 8 e 12 threads respectivamente. O desvio do ideal é menor que 0.1% até 12 threads.

### A aplicação apresentou escalabilidade?

Sim, escalabilidade forte (strong scaling) quase perfeita no intervalo testado. A eficiência permaneceu em ~100% mesmo ao octuplicar e duodecuplicar o número de threads, o que indica que o problema é altamente paralelizável e a divisão de trabalho entre threads está bem balanceada.

### Em qual ponto a eficiência começou a cair significativamente?

Nos dados coletados (até 12 threads), não houve queda significativa de eficiência — ela se manteve em torno de 100% em todos os pontos. [AJUSTAR: se o teste tiver ido além de 12 threads, ou se a máquina tiver menos de 12 núcleos, é aqui que normalmente apareceria a queda. Indique a partir de quantas threads isso aconteceu, se aplicável.]

### O número de threads ultrapassa o número de núcleos físicos?

[PRECISA SER PREENCHIDO: depende da CPU usada no teste. Informe o número de núcleos físicos/lógicos do processador. Se a CPU tiver, por exemplo, 8 núcleos físicos com hyper-threading (16 lógicos), o teste com 12 threads estaria dentro do limite lógico, mas já acima do número de núcleos físicos — isso explicaria o asterisco (*) no valor de 12 threads.]

### Houve overhead de paralelização?

O overhead foi mínimo a desprezível nos pontos testados — não há sinal de degradação por sincronização, comunicação entre threads ou contenção de recursos, já que a eficiência permaneceu próxima de 100%. Isso sugere uma implementação com baixo acoplamento entre as tarefas paralelas e pouca necessidade de seções críticas ou barreiras.

### Causas identificadas para perda de desempenho

Não foram identificadas causas relevantes de perda de desempenho no intervalo testado (1 a 12 threads), dado que a eficiência se manteve estável. [AJUSTAR conforme o contexto real do seu projeto — possíveis causas a mencionar, se você notar algo no relatório completo ou em testes com mais threads:]
- Saturação do número de núcleos físicos disponíveis na máquina de teste
- Overhead de criação/sincronização de threads em granularidades muito finas de trabalho
- Contenção de cache ou memória compartilhada
- Limitações de I/O ou comunicação em rede (no caso de cluster distribuído)



---

## 11. Conclusão

## Conclusão

Os testes de desempenho realizados com 1, 2, 4, 8 e 12 threads, partindo de um tempo de execução serial de referência de 178.00 segundos, demonstraram que a aplicação possui **escalabilidade quase ideal** dentro de todo o intervalo avaliado.

### Speedup

O speedup obtido acompanhou de forma muito próxima a curva linear teórica em cada configuração testada:

- 2 threads → speedup de 2.00x (ideal: 2.00x)
- 4 threads → speedup de 4.00x (ideal: 4.00x)
- 8 threads → speedup de 8.00x (ideal: 8.00x)
- 12 threads → speedup de 11.99x (ideal: 12.00x)

O desvio em relação ao speedup ideal é praticamente nulo até 8 threads e permanece inferior a 0.1% mesmo em 12 threads, o que caracteriza um comportamento de escalabilidade forte (*strong scaling*) excepcional para esse intervalo.

### Eficiência

A eficiência paralela se manteve em aproximadamente 100% em todas as configurações testadas. Isso significa que, na prática, **cada thread adicionada contribuiu de forma quase total para a redução do tempo de execução**, sem perdas relevantes por overhead de gerenciamento de threads, sincronização ou espera entre tarefas.

### Interpretação dos resultados

Esse padrão de resultados indica que:

- **A carga de trabalho é altamente paralelizável**, com baixo ou nenhum acoplamento entre as tarefas distribuídas entre as threads, permitindo que o trabalho seja dividido de forma quase perfeitamente independente;
- **O overhead de paralelização é desprezível** na faixa testada — não há evidências de gargalos causados por criação/destruição de threads, uso de locks, barreiras de sincronização ou comunicação entre processos;
- **A distribuição de carga está bem balanceada**, sem indícios de threads ociosas aguardando outras concluírem suas tarefas (load imbalance);
- **Não há sinais de contenção de recursos compartilhados** (cache, memória, barramento de I/O) que normalmente se manifestariam como queda de eficiência ao aumentar o número de threads.

Em síntese, a implementação atual demonstra um modelo de paralelismo robusto e eficiente, sem gargalos identificáveis dentro do intervalo de 2 a 12 threads, servindo como uma base sólida para extensões futuras do sistema.


---

## 12. Referências

- BRASIL. Portal de Dados Abertos — Pagamentos do Bolsa Família. Disponível em: [<[https://dados.gov.br](https://dados.gov.br/dados/conjuntos-dados/bolsa-familia---pagamentos)>](https://dados.gov.br/dados/conjuntos-dados/bolsa-familia---pagamentos). Acesso em: maio 2026.
- BRASIL. Lei nº 14.601, de 19 de junho de 2023. Institui o Programa Bolsa Família.
- TANENBAUM, Andrew S.; VAN STEEN, Maarten. *Sistemas Distribuídos: Princípios e Paradigmas*. 2. ed. Pearson, 2007.

---

<div align="center">

**Sistemas de Informação/ Análise e Desenvolvimento de Sistemas — 5º Semestre | Programação Concorrente e Distribuída | 2026**

</div>
