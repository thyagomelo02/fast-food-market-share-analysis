#Módulo de análises avançadas para market share de fast-food.
#Foca em segmentação, enriquecimento de dados e geração de insights.

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

_SP_BAIRROS_MAP = None
ABC_CIDADES = {
    'santo andré', 'são bernardo do campo', 'são caetano do sul', 'diadema',
    'mauá', 'ribeirão pires', 'rio grande da serra'
}


def _load_sp_bairros_map():
    global _SP_BAIRROS_MAP
    if _SP_BAIRROS_MAP is not None:
        return _SP_BAIRROS_MAP

    path = Path(__file__).resolve().parent / 'bairros_e_zonas_SP.csv'
    if not path.exists():
        _SP_BAIRROS_MAP = {}
        return _SP_BAIRROS_MAP

    try:
        df = pd.read_csv(path, dtype=str, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(path, dtype=str, encoding='latin1')
    
    df['Bairro'] = df['Bairro'].astype(str).str.strip().str.lower()
    df['UF'] = df['UF'].astype(str).str.strip().str.upper()
    df['Zona'] = df['Zona'].astype(str).str.strip()
    _SP_BAIRROS_MAP = df.set_index('Bairro')[['Zona', 'Cidade', 'UF']].to_dict(orient='index')
    return _SP_BAIRROS_MAP


def classify_income_bracket(income):
    "Classifica renda em brackets padronizados (A/B/C/D/E)"
    if pd.isna(income) or income <= 0:
        return 'Não informado'
    elif income < 1000:
        return 'D/E (< R$1k)'
    elif income < 2500:
        return 'C (R$1k-2.5k)'
    elif income < 5000:
        return 'B (R$2.5k-5k)'
    else:
        return 'A (> R$5k)'


def classify_age_group(age):
    "Classifica idade em grupos demográficos"
    if pd.isna(age) or age <= 0 or age > 100:
        return 'Não informado'
    elif age < 25:
        return '18-24'
    elif age < 35:
        return '25-34'
    elif age < 45:
        return '35-44'
    elif age < 55:
        return '45-54'
    else:
        return '55+'


def extract_region_from_city(bairro_name, uf, cidade_name=None):
    "Extrai região geográfica baseado em bairro, cidade e estado"
    if pd.isna(bairro_name):
        return 'Não informado'

    bairro = str(bairro_name).strip().lower()
    uf_norm = str(uf).strip().upper() if not pd.isna(uf) else ''
    cidade = str(cidade_name).strip().lower() if cidade_name and not pd.isna(cidade_name) else ''

    if uf_norm in {'GO', 'GOIAS'}:
        return 'GOIAS'

    if cidade in ABC_CIDADES:
        return 'ABC'

    import re
    zona_match = re.search(r'\(\s*zona\s+(\w+)\s*\)', bairro, re.IGNORECASE)
    if zona_match:
        zona_name = zona_match.group(1).lower()
        zona_map = {
            'norte': 'Zona Norte',
            'sul': 'Zona Sul',
            'leste': 'Zona Leste',
            'oeste': 'Zona Oeste',
            'centro': 'Centro'
        }
        if zona_name in zona_map:
            return zona_map[zona_name]

    sp_map = _load_sp_bairros_map()

    variations = [
        bairro,
        re.sub(r'\s+', ' ', bairro),  # Normalize spaces
        re.sub(r'\(zona\s+(\w+)\)', '', bairro).strip(),  # Remove zone info
        re.sub(r'\s*\([^)]*\)\s*', '', bairro).strip(),  # Remove all parentheses
    ]

    for var in variations:
        bairro_info = sp_map.get(var)
        if bairro_info and bairro_info.get('UF') == 'SP':
            zona = bairro_info.get('Zona', '').strip()
            if zona:
                if zona.lower() == 'centro':
                    return 'Centro'
                return f'Zona {zona}'

    return 'Interior/Outro'


def enrich_profile_data(profile_df):
    "Enriquece dados de perfil com classificações derivadas"
    df = profile_df.copy()

    # Limpeza de renda: valores negativos significam "não informado"
    df['income'] = pd.to_numeric(df['income'], errors='coerce')
    df['income_clean'] = df['income'].where(df['income'] > 0, np.nan)
    df['income_missing'] = df['income_clean'].isna()
    df['income'] = df['income_clean']

    df['income_bracket'] = df['income_clean'].apply(classify_income_bracket)
    df['age_group'] = df['age'].apply(classify_age_group)
    df['region'] = df.apply(
        lambda row: extract_region_from_city(row['bairro'], row['uf'], row['cidade']),
        axis=1
    )
    
    # Normalizar sexo
    df['sex'] = df['sex'].map({
        'FEMININO': 'Feminino',
        'MASCULINO': 'Masculino',
        'Other': 'Outro'
    }).fillna(df['sex'])
    
    return df


def aggregate_transactions(checking_df, credit_df):
    "Agrega transações por usuário em ambos os canais"
    checking_clean = checking_df.dropna(subset=['uuid'])
    credit_clean = credit_df.dropna(subset=['uuid'])
    
    checking_agg = checking_clean.groupby('uuid').agg({
        'transactionAmount': ['count', 'sum', 'mean', 'std'],
        'type': lambda x: x.value_counts().idxmax() if len(x) > 0 else 'PIX',
        'brandName': lambda x: x.value_counts().idxmax() if len(x) > 0 else 'G'
    }).reset_index()
    
    checking_agg.columns = [
        'uuid', 'checking_tx_count', 'checking_total', 'checking_avg', 'checking_std',
        'checking_preferred_type', 'checking_preferred_brand'
    ]
    
    credit_agg = credit_clean.groupby('uuid').agg({
        'brazilianAmount': ['count', 'sum', 'mean', 'std'],
        'brandName': lambda x: x.value_counts().idxmax() if len(x) > 0 else 'G'
    }).reset_index()
    
    credit_agg.columns = [
        'uuid', 'credit_tx_count', 'credit_total', 'credit_avg', 'credit_std',
        'credit_preferred_brand'
    ]
    
    return checking_agg, credit_agg


def merge_all_data(profile_df, checking_agg, credit_agg):
    "Merge final de perfil com agregados de transação"
    merged = profile_df.merge(checking_agg, on='uuid', how='left')
    merged = merged.merge(credit_agg, on='uuid', how='left')

    if 'income_clean' in merged.columns:
        merged['income'] = merged['income_clean']
    
    # Preencher NaNs em colunas de transação
    tx_cols = [
        'checking_tx_count', 'checking_total', 'checking_avg', 'checking_std',
        'credit_tx_count', 'credit_total', 'credit_avg', 'credit_std'
    ]
    
    for col in tx_cols:
        if col.endswith('_count') or col.endswith('_total') or col.endswith('_avg'):
            merged[col] = merged[col].fillna(0)
        elif col.endswith('_std'):
            merged[col] = merged[col].fillna(0)
    
    # Indicadores consolidados
    merged['total_tx_count'] = merged['checking_tx_count'] + merged['credit_tx_count']
    merged['total_spend'] = merged['checking_total'] + merged['credit_total']
    merged['avg_ticket'] = np.where(
        merged['total_tx_count'] > 0,
        merged['total_spend'] / merged['total_tx_count'],
        0
    )
    
    merged['has_transactions'] = merged['total_tx_count'] > 0
    
    # Preferência de canal
    merged['preferred_channel'] = np.where(
        merged['checking_total'] > merged['credit_total'],
        'Débito/PIX',
        np.where(
            merged['credit_total'] > merged['checking_total'],
            'Crédito',
            'Ambos/Nenhum'
        )
    )
    
    return merged


def create_segment_profiles(merged_df):
    "Cria perfis de segmentação com múltiplas dimensões"
    
    # Gasto por renda
    segment_by_income = merged_df.groupby('income_bracket').agg({
        'uuid': 'count',
        'total_spend': ['mean', 'median', 'sum'],
        'total_tx_count': 'mean',
        'avg_ticket': 'mean',
        'age': 'mean'
    }).round(2)
    
    segment_by_income.columns = ['Clientes', 'Gasto_Médio', 'Gasto_Mediano', 
                                  'Gasto_Total', 'TX_Médias', 'Ticket_Médio', 'Idade_Média']
    
    # Gasto por idade
    segment_by_age = merged_df.groupby('age_group').agg({
        'uuid': 'count',
        'total_spend': ['mean', 'median'],
        'total_tx_count': 'mean',
        'avg_ticket': 'mean',
        'income': 'mean'
    }).round(2)
    
    segment_by_age.columns = ['Clientes', 'Gasto_Médio', 'Gasto_Mediano',
                              'TX_Médias', 'Ticket_Médio', 'Renda_Média']
    
    # Gasto por região
    segment_by_region = merged_df.groupby('region').agg({
        'uuid': 'count',
        'total_spend': ['mean', 'median'],
        'total_tx_count': 'mean',
        'avg_ticket': 'mean',
        'income': 'mean'
    }).round(2)
    
    segment_by_region.columns = ['Clientes', 'Gasto_Médio', 'Gasto_Mediano',
                                 'TX_Médias', 'Ticket_Médio', 'Renda_Média']
    
    # Gasto por sexo
    segment_by_sex = merged_df.groupby('sex').agg({
        'uuid': 'count',
        'total_spend': ['mean', 'median'],
        'total_tx_count': 'mean',
        'avg_ticket': 'mean',
        'income': 'mean',
        'age': 'mean'
    }).round(2)
    
    segment_by_sex.columns = ['Clientes', 'Gasto_Médio', 'Gasto_Mediano',
                             'TX_Médias', 'Ticket_Médio', 'Renda_Média', 'Idade_Média']
    
    return {
        'by_income': segment_by_income,
        'by_age': segment_by_age,
        'by_region': segment_by_region,
        'by_sex': segment_by_sex
    }


def analyze_brand_preferences(checking_df, credit_df, merged_df):
    "Análise de preferência de marca por segmento"
    
    # Merge de marcas com perfil
    checking_with_profile = checking_df.merge(
        merged_df[['uuid', 'income_bracket', 'age_group', 'sex', 'region']],
        on='uuid',
        how='left'
    )
    
    credit_with_profile = credit_df.merge(
        merged_df[['uuid', 'income_bracket', 'age_group', 'sex', 'region']],
        on='uuid',
        how='left'
    )
    
    # Marca por renda (Checking)
    brand_by_income_check = checking_with_profile.groupby(['income_bracket', 'brandName']).agg({
        'transactionAmount': ['count', 'sum', 'mean']
    }).round(2)
    brand_by_income_check.columns = ['Transações', 'Gasto_Total', 'Gasto_Médio']
    
    # Marca por renda (Credit)
    brand_by_income_credit = credit_with_profile.groupby(['income_bracket', 'brandName']).agg({
        'brazilianAmount': ['count', 'sum', 'mean']
    }).round(2)
    brand_by_income_credit.columns = ['Transações', 'Gasto_Total', 'Gasto_Médio']
    
    # Marca por região
    brand_by_region = checking_with_profile.groupby(['region', 'brandName']).agg({
        'transactionAmount': ['count', 'sum', 'mean']
    }).round(2)
    brand_by_region.columns = ['Transações', 'Gasto_Total', 'Gasto_Médio']
    
    return {
        'checking_by_income': brand_by_income_check,
        'credit_by_income': brand_by_income_credit,
        'by_region': brand_by_region
    }


def analyze_payment_preferences(checking_df, merged_df):
    "Análise de preferência de tipo de pagamento"
    
    checking_with_profile = checking_df.merge(
        merged_df[['uuid', 'income_bracket', 'age_group', 'sex', 'region']],
        on='uuid',
        how='left'
    )
    
    # Tipo de pagamento por renda
    payment_by_income = checking_with_profile.groupby(['income_bracket', 'type']).agg({
        'transactionAmount': ['count', 'sum', 'mean']
    }).round(2)
    payment_by_income.columns = ['Transações', 'Gasto_Total', 'Gasto_Médio']
    
    # Tipo de pagamento por idade
    payment_by_age = checking_with_profile.groupby(['age_group', 'type']).agg({
        'transactionAmount': ['count', 'sum', 'mean']
    }).round(2)
    payment_by_age.columns = ['Transações', 'Gasto_Total', 'Gasto_Médio']
    
    return {
        'by_income': payment_by_income,
        'by_age': payment_by_age
    }


def create_value_segments(merged_df, n_segments=4):
    "Cria segmentação de valor usando quartis de gasto"
    
    merged_copy = merged_df.copy()
    
    # Quartis de gasto total
    try:
        merged_copy['valor_segment'] = pd.qcut(
            merged_copy['total_spend'],
            q=n_segments,
            duplicates='drop'
        )
    except ValueError:

        merged_copy['valor_segment'] = pd.cut(
            merged_copy['total_spend'],
            bins=n_segments,
            labels=['Baixo', 'Médio', 'Alto', 'Premium'][:n_segments]
        )
    
    # Análise por segmento de valor
    value_segment_analysis = merged_copy.groupby('valor_segment').agg({
        'uuid': 'count',
        'total_spend': ['mean', 'median', 'min', 'max'],
        'total_tx_count': 'mean',
        'avg_ticket': 'mean',
        'income': 'mean',
        'age': 'mean'
    }).round(2)
    
    value_segment_analysis.columns = [
        'Clientes', 'Gasto_Médio', 'Gasto_Mediano', 'Gasto_Min', 'Gasto_Max',
        'TX_Médias', 'Ticket_Médio', 'Renda_Média', 'Idade_Média'
    ]
    
    return merged_copy, value_segment_analysis


def analyze_cross_segment(merged_df):
    "Análise cruzada de segmentos Renda x Idade x Região"
    
    cross_analysis = merged_df.groupby(['income_bracket', 'age_group', 'region']).agg({
        'uuid': 'count',
        'total_spend': ['mean', 'sum'],
        'avg_ticket': 'mean',
        'total_tx_count': 'mean'
    }).round(2)
    
    cross_analysis.columns = [
        'Clientes', 'Gasto_Médio', 'Gasto_Total',
        'Ticket_Médio', 'TX_Médias'
    ]
    
    # Ordenar por volume de clientes
    cross_analysis = cross_analysis.sort_values('Clientes', ascending=False)
    
    return cross_analysis


def calculate_segment_performance(merged_df):
    "Calcula KPIs de performance por segmento"

    # Determinar se cliente tem transações
    if 'has_transactions' in merged_df.columns:
        has_tx = merged_df['has_transactions']
    elif 'total_tx_count' in merged_df.columns:
        has_tx = merged_df['total_tx_count'] > 0
    elif 'has_transaction' in merged_df.columns:
        has_tx = merged_df['has_transaction']
    else:        
        has_tx = merged_df.get('total_spend', pd.Series([0] * len(merged_df))) > 0

    kpis = {
        'Total Clientes': len(merged_df),
        'Clientes com Transação': has_tx.sum(),
        'Taxa de Conversão': (has_tx.sum() / len(merged_df) * 100),
        'Gasto Total': merged_df['total_spend'].sum(),
        'Gasto Médio por Cliente': merged_df['total_spend'].mean(),
        'Gasto Médio Transação': merged_df['avg_ticket'].mean(),
        'Ticket Mínimo': merged_df['avg_ticket'].min(),
        'Ticket Máximo': merged_df['avg_ticket'].max(),
        'Renda Média': merged_df['income'].mean(),
        'Idade Média': merged_df['age'].mean(),
        'Total de Transações': merged_df['total_tx_count'].sum(),
        'Transações por Cliente': merged_df['total_tx_count'].mean()
    }

    return pd.Series(kpis)

