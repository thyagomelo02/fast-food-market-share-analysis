"""
Script para gerar visualizações em HTML a partir do notebook

Este script regenera todos os gráficos Plotly como arquivos HTML
sem precisar dos outputs no notebook, mantendo o arquivo leve.

Uso:
    python generate_outputs.py
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from data_processing import (
    load_csv, drop_trailing_empty_rows, parse_transaction_dates,
    normalize_account_type, merge_profiles, create_user_clusters
)
from improved_analysis import (
    enrich_profile_data, aggregate_transactions, merge_all_data,
    create_segment_profiles, analyze_brand_preferences,
    analyze_payment_preferences, create_value_segments,
    analyze_cross_segment, calculate_segment_performance
)

# Configurar diretório de outputs
OUTPUT_DIR = Path(__file__).parent / 'outputs'
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================================
# CARREGAMENTO E PROCESSAMENTO DOS DADOS
# ============================================================================

print("Carregando dados...")
checking_path = r"C:\Users\thyag\OneDrive\Documentos\Klavi_tech_interview\klavi_case_table_data_scientist\klavi_checking_saving_transactions_market_share_case.csv"
credit_path = r"C:\Users\thyag\OneDrive\Documentos\Klavi_tech_interview\klavi_case_table_data_scientist\klavi_credit_transactions_market_share_case.csv"
profile_path = r"C:\Users\thyag\OneDrive\Documentos\Klavi_tech_interview\klavi_case_table_data_scientist\klavi_profile_market_share_case.csv"

checking_raw = load_csv(checking_path)
credit_raw = load_csv(credit_path)
profile_raw = load_csv(profile_path)

checking = drop_trailing_empty_rows(checking_raw)
credit = drop_trailing_empty_rows(credit_raw)
profile = drop_trailing_empty_rows(profile_raw)

# Processamento
checking = parse_transaction_dates(checking, 'transactionDate')
credit = parse_transaction_dates(credit, 'transactionDate')
checking = normalize_account_type(checking)
credit = normalize_account_type(credit)

profile['age'] = pd.to_numeric(profile['age'], errors='coerce')
profile['income'] = pd.to_numeric(profile['income'], errors='coerce')
profile['sex'] = profile['sex'].astype(str).str.strip()
profile['socialClass'] = profile['socialClass'].astype(str).str.strip()
profile['uf'] = profile['uf'].astype(str).str.strip()
profile['income_clean'] = profile['income'].where(profile['income'] > 0)
profile['age_clean'] = profile['age'].where(profile['age'].between(0, 100))

# Análises avançadas
profile_enriched = enrich_profile_data(profile)
checking_agg, credit_agg = aggregate_transactions(checking, credit)
merged_complete = merge_all_data(profile_enriched, checking_agg, credit_agg)

print(f"✓ Dados carregados: {len(merged_complete)} registros")

# ============================================================================
# GERANDO VISUALIZAÇÕES
# ============================================================================

print("\nGerando visualizações...")

# 1. Segmentação por Renda
segments = create_segment_profiles(merged_complete)

fig_income = px.bar(
    segments['by_income'].reset_index(),
    x='income_bracket',
    y='Gasto_Médio',
    color='Clientes',
    title='Gasto Médio por Classe de Renda',
    labels={'income_bracket': 'Classe de Renda', 'Gasto_Médio': 'Gasto Médio (R$)'},
    text='Gasto_Médio'
)
fig_income.update_traces(texttemplate='R$ %{text:.0f}', textposition='outside')
fig_income.write_html(OUTPUT_DIR / 'segmentacao_renda.html')
print("✓ segmentacao_renda.html")

# 2. Segmentação por Idade
fig_age = px.bar(
    segments['by_age'].reset_index(),
    x='age_group',
    y='Gasto_Médio',
    color='Clientes',
    title='Gasto Médio por Faixa Etária',
    labels={'age_group': 'Faixa Etária', 'Gasto_Médio': 'Gasto Médio (R$)'},
    text='Gasto_Médio'
)
fig_age.update_traces(texttemplate='R$ %{text:.0f}', textposition='outside')
fig_age.write_html(OUTPUT_DIR / 'segmentacao_idade.html')
print("✓ segmentacao_idade.html")

# 3. Segmentação por Região
fig_region = px.bar(
    segments['by_region'].reset_index(),
    x='region',
    y='Gasto_Médio',
    color='Clientes',
    title='Gasto Médio por Região',
    labels={'region': 'Região', 'Gasto_Médio': 'Gasto Médio (R$)'},
    text='Gasto_Médio'
)
fig_region.update_traces(texttemplate='R$ %{text:.0f}', textposition='outside')
fig_region.write_html(OUTPUT_DIR / 'segmentacao_regiao.html')
print("✓ segmentacao_regiao.html")

# 4. Análise de Marca
brand_analysis = analyze_brand_preferences(checking, credit, merged_complete)
brand_by_income_reset = brand_analysis['checking_by_income'].reset_index()

fig_brand_income = px.bar(
    brand_by_income_reset,
    x='income_bracket',
    y='Gasto_Total',
    color='brandName',
    title='Preferência de Marca x Classe de Renda',
    labels={'income_bracket': 'Classe de Renda', 'Gasto_Total': 'Gasto Total (R$)'},
    barmode='group'
)
fig_brand_income.write_html(OUTPUT_DIR / 'marca_por_renda.html')
print("✓ marca_por_renda.html")

# 5. Marca por Região
brand_by_region = brand_analysis['by_region'].reset_index()
fig_brand_region = px.bar(
    brand_by_region,
    x='region',
    y='Gasto_Total',
    color='brandName',
    title='Preferência de Marca por Região Geográfica',
    labels={'region': 'Região', 'Gasto_Total': 'Gasto Total (R$)'},
    barmode='stack'
)
fig_brand_region.write_html(OUTPUT_DIR / 'marca_por_regiao.html')
print("✓ marca_por_regiao.html")

# 6. Análise de Pagamento
payment_analysis = analyze_payment_preferences(checking, merged_complete)
payment_by_income = payment_analysis['by_income'].reset_index()

fig_payment_income = px.bar(
    payment_by_income,
    x='income_bracket',
    y='Gasto_Total',
    color='type',
    title='Método de Pagamento Preferido por Classe de Renda',
    labels={'income_bracket': 'Classe de Renda', 'Gasto_Total': 'Gasto Total (R$)', 'type': 'Tipo'},
    barmode='group'
)
fig_payment_income.write_html(OUTPUT_DIR / 'metodo_pagamento_renda.html')
print("✓ metodo_pagamento_renda.html")

# 7. Segmentação por Valor
merged_with_segments, value_segment_analysis = create_value_segments(merged_complete, n_segments=4)
merged_for_plot = merged_with_segments.copy()
merged_for_plot['valor_segment_str'] = merged_for_plot['valor_segment'].astype(str)

fig_value = px.box(
    merged_for_plot,
    x='valor_segment_str',
    y='total_spend',
    title='Distribuição de Gasto por Segmento de Valor',
    labels={'valor_segment_str': 'Segmento', 'total_spend': 'Gasto Total (R$)'},
    points='all'
)
fig_value.write_html(OUTPUT_DIR / 'segmentacao_valor_boxplot.html')
print("✓ segmentacao_valor_boxplot.html")

# 8. Segmentação de Valor - Pizza
pie_data = value_segment_analysis.reset_index()
pie_data['valor_segment'] = pie_data['valor_segment'].astype(str)

fig_value_pie = px.pie(
    pie_data,
    names='valor_segment',
    values='Clientes',
    title='Distribuição de Clientes por Segmento de Valor',
    labels={'valor_segment': 'Segmento', 'Clientes': 'Número de Clientes'}
)
fig_value_pie.write_html(OUTPUT_DIR / 'segmentacao_valor_pie.html')
print("✓ segmentacao_valor_pie.html")

# 9. Análise Multi-dimensional
cross_segment = analyze_cross_segment(merged_complete)
heatmap_data = cross_segment.reset_index().copy()
heatmap_data = heatmap_data[heatmap_data['Clientes'] >= 5]

fig_heatmap = px.scatter(
    heatmap_data,
    x='Clientes',
    y='Gasto_Médio',
    size='Gasto_Total',
    color='Ticket_Médio',
    hover_data=['income_bracket', 'age_group', 'region'],
    title='Análise Multi-dimensional: Clientes vs Gasto (tamanho = Gasto Total)',
    labels={'Clientes': 'Número de Clientes', 'Gasto_Médio': 'Gasto Médio (R$)',
            'Ticket_Médio': 'Ticket Médio (R$)'},
    color_continuous_scale='Viridis'
)
fig_heatmap.write_html(OUTPUT_DIR / 'analise_multidimensional.html')
print("✓ analise_multidimensional.html")

# 10. Dashboard com KPIs
kpis = calculate_segment_performance(merged_complete)
from plotly.subplots import make_subplots

fig_dashboard = make_subplots(
    rows=2, cols=2,
    subplot_titles=('KPIs Principais', 'Gasto por Classe de Renda', 
                    'Distribuição Geográfica', 'Ticket Médio por Idade'),
    specs=[[{'type': 'indicator'}, {'type': 'bar'}],
           [{'type': 'pie'}, {'type': 'bar'}]]
)

fig_dashboard.add_trace(
    go.Indicator(
        mode='number',
        value=kpis['Gasto Total'],
        title={'text': 'Gasto Total (R$)'},
        domain={'x': [0, 0.5], 'y': [0.5, 1]}
    ),
    row=1, col=1
)

fig_dashboard.add_trace(
    go.Bar(
        x=segments['by_income'].index,
        y=segments['by_income']['Gasto_Médio'],
        name='Gasto Médio',
        marker_color='#1f77b4'
    ),
    row=1, col=2
)

fig_dashboard.add_trace(
    go.Pie(
        labels=segments['by_region'].index,
        values=segments['by_region']['Clientes'],
        name='Clientes'
    ),
    row=2, col=1
)

fig_dashboard.add_trace(
    go.Bar(
        x=segments['by_age'].index,
        y=segments['by_age']['Ticket_Médio'],
        name='Ticket Médio',
        marker_color='#ff7f0e'
    ),
    row=2, col=2
)

fig_dashboard.update_xaxes(title_text='Classe de Renda', row=1, col=2)
fig_dashboard.update_yaxes(title_text='Gasto Médio (R$)', row=1, col=2)
fig_dashboard.update_xaxes(title_text='Faixa Etária', row=2, col=2)
fig_dashboard.update_yaxes(title_text='Ticket Médio (R$)', row=2, col=2)
fig_dashboard.update_layout(height=800, title_text='Dashboard - Market Share Fast Food', showlegend=False)

fig_dashboard.write_html(OUTPUT_DIR / 'dashboard_completo.html')
print("✓ dashboard_completo.html")

print(f"\n✅ Todas as visualizações foram geradas em: {OUTPUT_DIR}")
print("\nArquivos criados:")
for file in sorted(OUTPUT_DIR.glob('*.html')):
    size_kb = file.stat().st_size / 1024
    print(f"  - {file.name} ({size_kb:.1f} KB)")
