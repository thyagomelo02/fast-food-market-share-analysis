import pandas as pd
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import chardet


def load_csv(path, encoding=None, **kwargs):
    "Carrega CSV com deteccao automatica de encoding."
    path = Path(path)
    
    if encoding is None:
        with open(path, 'rb') as f:
            raw_data = f.read(100000)  # Ler primeiro 100KB
            detected = chardet.detect(raw_data)
            encoding = detected.get('encoding', 'utf-8') or 'utf-8'
    
    try:
        return pd.read_csv(path, low_memory=False, encoding=encoding, **kwargs)
    except (UnicodeDecodeError, LookupError):
        return pd.read_csv(path, low_memory=False, encoding='utf-8', **kwargs)


def drop_trailing_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
    "Remove linhas vazias completas e linhas sem uuid válido."
    cleaned = df.dropna(how='all')
    if 'uuid' in cleaned.columns:
        cleaned = cleaned[cleaned['uuid'].notna()]
    return cleaned.reset_index(drop=True)


def parse_transaction_dates(df: pd.DataFrame, date_col: str = 'transactionDate') -> pd.DataFrame:
    "Converte data de transação para datetime, mantendo rows inválidas como NaT."
    if date_col not in df.columns:
        return df.copy()
    result = df.copy()
    result[date_col] = pd.to_datetime(result[date_col], format='%m/%d/%Y', errors='coerce')
    return result


def normalize_account_type(df: pd.DataFrame) -> pd.DataFrame:
    if 'accountType' not in df.columns:
        return df.copy()
    result = df.copy()
    result['accountType'] = (
        result['accountType']
        .astype(str)
        .str.strip()
        .str.lower()
        .replace({'credit card': 'Credit card', 'checking': 'Checking', 'savings': 'Savings'})
    )
    return result


def aggregate_user_transactions(checking_df: pd.DataFrame, credit_df: pd.DataFrame) -> pd.DataFrame:
    "Cria agregados de transações por usuário"
    checking_clean = drop_trailing_empty_rows(checking_df)
    credit_clean = drop_trailing_empty_rows(credit_df)

    checking_agg = (
        checking_clean.groupby('uuid')
        .agg(
            checking_tx_count=('transactionAmount', 'count'),
            checking_total=('transactionAmount', 'sum'),
            checking_mean=('transactionAmount', 'mean'),
        )
        .reset_index()
    )

    credit_agg = (
        credit_clean.groupby('uuid')
        .agg(
            credit_tx_count=('brazilianAmount', 'count'),
            credit_total=('brazilianAmount', 'sum'),
            credit_mean=('brazilianAmount', 'mean'),
        )
        .reset_index()
    )

    merged = checking_agg.merge(credit_agg, on='uuid', how='outer')
    return merged


def merge_profiles(profile_df: pd.DataFrame, checking_df: pd.DataFrame, credit_df: pd.DataFrame) -> pd.DataFrame:
    "merge perfil com agregados de transações por uuid."
    profile_clean = drop_trailing_empty_rows(profile_df)
    tx_agg = aggregate_user_transactions(checking_df, credit_df)
    merged = profile_clean.merge(tx_agg, on='uuid', how='left')
    return merged


def create_user_clusters(df: pd.DataFrame, features: list[str], n_clusters: int = 3) -> pd.DataFrame:
    "Cria clusters KMeans sobre características de usuário."
    data = df.copy()
    subset = data[features].dropna()
    scaler = StandardScaler()
    X = scaler.fit_transform(subset)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(X)
    subset = subset.assign(cluster=labels)
    return subset
