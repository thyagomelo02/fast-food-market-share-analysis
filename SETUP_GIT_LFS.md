# Configuração Git LFS - Quick Start

Este documento explica como usar Git LFS neste projeto e como gerar visualizações

## Como Usar

### 1. Primeira vez :

```bash
git lfs install
git lfs track "*.html"
git lfs track "*.csv"
git lfs track "*.ipynb"
```

### 2. Gerar Visualizações HTML
Execute o script de geração sempre que atualizar os dados:
```bash
python generate_outputs.py
```
**Saída**: Arquivos HTML interativos serão criados em `outputs/`
```
outputs/
├── dashboard_completo.html
├── segmentacao_renda.html
├── segmentacao_idade.html
├── segmentacao_regiao.html
├── marca_por_renda.html
├── marca_por_regiao.html
├── metodo_pagamento_renda.html
├── segmentacao_valor_boxplot.html
├── segmentacao_valor_pie.html
└── analise_multidimensional.html
```

### 3. Versionar os Outputs
```bash
git add outputs/
git commit -m "Update visualizations"
git push 
```

### 4. Para colegas/outros dispositivos
Ao clonar o repositório:
```bash
git clone <repository-url>
git lfs pull 
```