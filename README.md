# Análise de Market Share - Fast-Food

Análise exploratória completa de dados de transações e perfis de clientes para uma rede de fast-food, com foco em segmentação de mercado, preferências de pagamento e oportunidades estratégicas.

## Estrutura do Projeto

```
klavi_case_table_data_scientist/
├── klavi_market_share_analysis.ipynb          # Notebook principal com análises
├── improved_analysis.py                       # Módulo de análises avançadas
├── data_processing.py                         # Funções de limpeza e processamento
├── test_data_processing.py                    # Testes unitários
├── klavi_checking_saving_transactions_market_share_case-1.csv
├── klavi_credit_transactions_market_share_case-1.csv
├── klavi_profile_market_share_case - 1.csv
└── README.md
```

##  Como Executar

### 1. Instalar Dependências

```bash
pip install pandas numpy matplotlib seaborn plotly scikit-learn statsmodels pytest nbformat chardet
```

### 2. Abrir o Notebook

```bash
jupyter notebook klavi_market_share_analysis.ipynb
```

### 3. Gerar Visualizações HTML (Recomendado)

Para manter o notebook leve no repositório, as visualizações Plotly são salvas como arquivos HTML:

```bash
python generate_outputs.py
```

Isso criará arquivos HTML interativos em `outputs/`:
- `dashboard_completo.html` - Dashboard executivo com KPIs
- `segmentacao_renda.html` - Análise por classe de renda
- `segmentacao_idade.html` - Análise por faixa etária
- `segmentacao_regiao.html` - Análise por região geográfica
- `marca_por_renda.html` - Preferência de marca por renda
- `marca_por_regiao.html` - Preferência de marca por região
- `metodo_pagamento_renda.html` - Método de pagamento por renda
- `segmentacao_valor_boxplot.html` - Distribuição de gasto
- `segmentacao_valor_pie.html` - Distribuição de clientes
- `analise_multidimensional.html` - Análise cruzada (Renda × Idade × Região)

**Nota**: Git LFS é usado para versionar estes arquivos HTML sem deixar o repositório pesado.

### 4. Executar Célula por Célula

O notebook está organizado em seções:

1. **Carregamento e Limpeza** - Ingestão dos CSVs
2. **Enriquecimento de Dados** - Criação de variáveis derivadas
3. **KPIs Consolidados** - Métricas principais
4. **Segmentação por Renda** - Análise demográfica
5. **Segmentação por Idade** - Padrões por faixa etária
6. **Gênero e Região** - Distribuição geográfica
7. **Preferência de Marca** - Análise de marcas por segmento
8. **Método de Pagamento** - PIX vs Cartão vs Outros
9. **Segmentação de Valor** - RFM simplificado
10. **Análise Cruzada** - Nichos multi-dimensionais
11. **Dashboard Executivo** - Visualizações resumidas
12. **Insights Finais** - Recomendações estratégicas

## Módulos Principais

### `improved_analysis.py`

Funções de análise avançada:

- `classify_income_bracket()` - Classifica renda em A/B/C/D/E
- `classify_age_group()` - Agrupa idade em faixas demográficas
- `extract_region_from_city()` - Extrai região geográfica
- `enrich_profile_data()` - Enriquece perfis com derivadas
- `aggregate_transactions()` - Agrega transações por usuário
- `create_segment_profiles()` - Cria segmentação por renda/idade/região
- `analyze_brand_preferences()` - Preferência de marca por segmento
- `analyze_payment_preferences()` - Preferência de método de pagamento
- `create_value_segments()` - Segmentação RFM em quartis
- `analyze_cross_segment()` - Análise cruzada multi-dimensional

### `data_processing.py`

Funções de processamento e limpeza:

- `load_csv()` - Carregamento com pandas
- `drop_trailing_empty_rows()` - Remove linhas vazias
- `parse_transaction_dates()` - Converte datas
- `normalize_account_type()` - Padroniza tipos de conta
- `merge_profiles()` - Merge de perfil com transações
- `create_user_clusters()` - Clustering KMeans

## Variáveis Criadas

### No Perfil Enriquecido:
- `income_bracket` - Classe de renda (A/B/C/D/E)
- `age_group` - Faixa etária (18-24, 25-34, etc.)
- `region` - Zona geográfica (SP: Zona Norte/Sul/Leste/Oeste, Interior/Outro)

### Em Transações Agregadas:
- `checking_tx_count` - Total de transações em débito
- `checking_total` - Gasto total em débito
- `checking_avg` - Gasto médio por transação (débito)
- `credit_tx_count` - Total de transações em crédito
- `credit_total` - Gasto total em crédito
- `credit_avg` - Gasto médio por transação (crédito)
- `checking_preferred_type` - Tipo de pagamento mais usado (PIX/CARTAO/etc)
- `checking_preferred_brand` - Marca preferida (débito)
- `credit_preferred_brand` - Marca preferida (crédito)

### Consolidadas:
- `total_tx_count` - Total de transações (débito + crédito)
- `total_spend` - Gasto consolidado (débito + crédito)
- `avg_ticket` - Ticket médio consolidado
- `has_transactions` - Booleano: tem transações?
- `preferred_channel` - Canal preferido (Débito/PIX, Crédito, Ambos)
- `valor_segment` - Quartil de valor (Baixo, Médio, Alto, Premium)

## Principais Insights

### Por Renda:
- **Classe A (>R$5k)**: Menor volume, maior ticket (~R$70-80)
- **Classe B (R$2.5k-5k)**: Volume médio, ticket de R$50-60
- **Classe C (R$1k-2.5k)**: Maior volume, ticket de R$35-45
- **Classe D/E (<R$1k)**: Baixo volume, ticket mínimo (~R$20-30)

### Por Idade:
- **18-24**: Alta frequência, ticket módico
- **25-34**: Pico de gasto absoluto
- **35-54**: Gasto mantido, menos frequência
- **55+**: Menor atividade, mas ticket interessante

### Por Método:
- **PIX**: 68%+ do volume (predominante em todas as classes)
- **Cartão**: 26%+ (preferência de classes A/B)
- **Outros**: <6% (SAQUE, BOLETO, etc)

### Por Marca:
- **G**: Dominância (85%+ das transações)
- **Q, H, A, M**: Segmentos secundários (<10% cada)

### Por Geografia:
- **SP**: 89% da amostra
- **GO**: 11% da amostra

## Recomendações Estratégicas

1. **Cashback em PIX** → Classe C/D → +15-20% transações
2. **Programa Premium** → Classe A/B → +10% gasto médio
3. **Campanhas regionais** → Zona Leste/Oeste → Novos mercados
4. **Mobile-first** → 25-34 anos → +30% conversão
5. **Crédito facilitado** → Classes C/D → Aumento de ticket médio


## Tecnologias Utilizadas

- **Python 3.12+**
- **Pandas** - Manipulação de dados
- **NumPy** - Operações numéricas
- **Matplotlib & Seaborn** - Visualizações estáticas
- **Plotly** - Visualizações interativas
- **Scikit-learn** - Machine learning (clustering, scaling)
- **Statsmodels** - Análises estatísticas
- **Git LFS** - Versionamento de arquivos grandes (HTML, CSV)

## Armazenamento com Git LFS

Este repositório usa **Git Large File Storage (LFS)** para versionar arquivos grandes sem deixar o repositório pesado:

### Configuração (já realizada)
```bash
git lfs install
git lfs track "*.html"
git lfs track "*.csv"
git lfs track "*.ipynb"
```

### Arquivos rastreados por LFS:
- `*.html` - Visualizações interativas (outputs/)
- `*.csv` - Dados brutos e processados
- `*.ipynb` - Notebook com potencial para outputs grandes

### Para clonar o repositório:
```bash
git clone <repository-url>
git lfs pull  # Baixar arquivos grandes
```

## Contato & Suporte

Para dúvidas sobre a análise ou necessidade de ajustes, consulte a documentação das funções em `improved_analysis.py`.

