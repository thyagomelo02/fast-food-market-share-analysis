# Configuração Git LFS - Quick Start

Este documento explica como usar Git LFS neste projeto e como gerar visualizações.

## ✅ O que foi configurado

- [x] Git LFS inicializado no repositório
- [x] `.gitattributes` criado para rastrear:
  - `*.html` (Visualizações Plotly)
  - `*.csv` (Arquivos de dados)
  - `*.ipynb` (Notebooks)
  - `*.png`, `*.svg`, `*.jpg` (Imagens)
- [x] Pasta `outputs/` criada para gerar visualizações
- [x] Script `generate_outputs.py` para regenerar gráficos
- [x] Documentação atualizada no `README.md`

## 🚀 Como Usar

### 1. Primeira vez (já feito para você):

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
# Os arquivos HTML são automaticamente versionados com Git LFS
git add outputs/
git commit -m "Update visualizations"
git push  # Pushará os arquivos via Git LFS
```

### 4. Para colegas/outros dispositivos

Ao clonar o repositório:

```bash
git clone <repository-url>
git lfs pull  # Baixar todos os arquivos grandes
```

## 📊 Benefícios da Configuração

| Aspecto | Antes | Depois |
|--------|-------|--------|
| **Tamanho do repo** | Gigabytes (outputs embutidos) | Kilobytes (Git LFS) |
| **Velocidade de clone** | Lenta | Rápida |
| **Outputs visuais** | ❌ Não disponíveis | ✅ HTML interativo |
| **Notebook limpo** | ❌ Outputs ocupam espaço | ✅ Sem outputs |
| **Facilidade de update** | ❌ Manual | ✅ `python generate_outputs.py` |

## 🔧 Troubleshooting

### Erro: "Git LFS is not installed"

```bash
# Windows (via chocolatey)
choco install git-lfs

# macOS (via homebrew)
brew install git-lfs

# Linux (Debian/Ubuntu)
sudo apt-get install git-lfs
```

### Erro: "Failed to push some refs"

```bash
# Se o push for bloqueado, verifique Git LFS status:
git lfs status

# Empurre os arquivos LFS explicitamente:
git lfs push origin main
```

### Verificar quais arquivos estão em LFS

```bash
git lfs ls-files
```

## 💡 Dicas

1. **Sempre execute `python generate_outputs.py`** após mudanças nos dados
2. **Não comite arquivos grandes manualmente** — Git LFS cuida disso automaticamente
3. **Use `git lfs pull`** ao clonar em outro computador
4. **Os arquivos HTML são completamente funcionais** — abra-os em qualquer navegador

## 📚 Recursos

- [Git LFS Documentation](https://git-lfs.github.com/)
- [GitHub - Git LFS Guide](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage)
