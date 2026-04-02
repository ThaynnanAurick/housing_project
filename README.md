# Projeto_habitação

# 📊 Análise da Acessibilidade Habitacional (2018–2025)

## 📌 Sobre o Projeto

Este projeto analisa a evolução da acessibilidade à habitação entre 2018 e 2025, investigando a relação entre:

* Preço médio da habitação
* Salário médio anual
* Inflação
* Imigração

O objetivo é entender se os imóveis estão se tornando menos acessíveis e quais fatores podem estar influenciando esse cenário.

---

## 🎯 Problema de Negócio

* A habitação está ficando menos acessível?
* Os salários acompanham o aumento dos preços?
* A imigração impacta o mercado imobiliário?

---

## 📂 Estrutura dos Dados

Os dados utilizados incluem:

* `pais`
* `ano`
* `preco_medio_habitacao_usd`
* `salario_medio_anual_usd`
* `salario_medio_mensal_usd`
* `inflacao_anual_pct`
* `preco_rendimento_ratio`
* `imigracao_liquida`
* `populacao_total`
* `taxa_imigracao_pct`

---

## ⚙️ Metodologia

### 🔹 1. Coleta de Dados

Dados obtidos de fontes confiáveis:

* Instituto Nacional de Estatística (INE)
* PORDATA
* Eurostat

---

### 🔹 2. Tratamento de Dados

* Limpeza e padronização com Pandas
* Integração de bases (merge)
* Criação de variáveis derivadas

---

### 🔹 3. Análise Exploratória

Foram criadas visualizações para analisar:

* Evolução dos preços da habitação
* Evolução dos salários
* Inflação ao longo do tempo
* Indicador de acessibilidade (Preço/Rendimento)

---

### 🔹 4. Integração com Imigração

* União dos dados de habitação com dados populacionais
* Análise da relação entre imigração e preços

---

### 🔹 5. Análise Estatística

Foi realizado um teste de correlação de Pearson entre:

* Imigração líquida
* Variação percentual dos preços

**Resultados:**

* Correlação: 0.1359
* p-valor: 0.4362

---

## 📈 Principais Insights

* 📊 Os preços da habitação cresceram significativamente (ex: +43% entre 2018–2022 em Portugal)
* 💼 Os salários cresceram em ritmo muito mais lento (~8%)
* 📉 A acessibilidade habitacional piorou ao longo do tempo
* 📈 A inflação aumentou principalmente após 2021
* 🌍 A imigração aumentou, mas não apresenta correlação estatisticamente significativa com os preços

---

## 📊 Visualizações

O projeto inclui:

* Gráficos de linha (preço, salário, inflação)
* Indicador de acessibilidade habitacional
* Gráfico combinado (imigração vs preço)
* Heatmap de correlação

---

## 🧪 Tecnologias Utilizadas

* Python
* Pandas
* Streamlit
* Altair
* Matplotlib
* SciPy

---

## 🚀 Como Executar o Projeto

### 1. Clonar o repositório

```bash
git clone <seu-repositorio>
cd housing_project
```

### 2. Criar ambiente virtual

```bash
python -m venv housing-project
```

### 3. Ativar ambiente

Windows:

```bash
housing-project\Scripts\activate
```

Linux/Mac:

```bash
source housing-project/bin/activate
```

### 4. Instalar dependências

```bash
pip install -r requirements.txt
```

### 5. Rodar o projeto

```bash
streamlit run app1_analitico.py
```

---

## 📌 Conclusão

A análise mostra que:

* O aumento dos preços dos imóveis supera significativamente o crescimento salarial
* A acessibilidade à habitação está em deterioração
* A inflação contribui para a perda de poder de compra
* Não há evidência estatística suficiente para afirmar que a imigração seja a principal causa do aumento dos preços

---

## 📎 Próximos Passos

* Incluir mais países na análise
* Criar modelos preditivos
* Análise regional (por cidades)
* Integração com dados de juros e crédito

---

## 👤 Autor

Thaynna

---

## ⭐ Observação

Este projeto foi desenvolvido como parte de um portfólio para análise de dados, com foco em problemas reais do mercado imobiliário.
