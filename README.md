# Organizador de Arquivos Inteligente 🗂️✨

Um aplicativo desktop com interface web local para renomear e organizar arquivos de forma inteligente, com suporte a extração automática de títulos de arquivos PDF e Word (DOCX), segmentação de palavras e numeração sequencial estruturada.

## 🚀 Funcionalidades

- **Renomeação por Conteúdo**: Extrai automaticamente o título de arquivos PDF e DOCX (Word) a partir do metadados ou das primeiras páginas para sugerir um novo nome representativo.
- **Segmentação Inteligente**: Separa palavras unidas (ex: `documentoimportante` vira `Documento Importante`) utilizando um dicionário em português.
- **Padronização de Nomes**:
  - Opção para remover espaços ou aplicar `camelCase`.
  - Correção automática de preposições para minúsculas (de, do, da, etc.).
- **Numeração Sequencial**: Gera prefixos numerados baseados na estrutura de pastas (ex: `1.1. Nome do Arquivo.pdf`).
- **Sistema de Desfazer (Undo)**: Desfaça a última renomeação em lote caso queira reverter as alterações.
- **Busca por Conteúdo**: Filtre arquivos que contenham um termo específico dentro do seu texto (PDF, DOCX, TXT, etc.).
- **Interface Nativa**: Interface gráfica limpa executada diretamente na área de trabalho através do `pywebview`.

## 📦 Pré-requisitos

Para rodar o projeto localmente do código-fonte, você precisará do Python instalado e das seguintes bibliotecas:

```bash
pip install pypdf python-docx pywebview
```

## 🛠️ Como Executar

Execute o servidor local que iniciará a interface gráfica nativa:

```bash
python servidor.py
```

## 🏗️ Como Compilar (Criar Executável `.app` ou `.exe`)

Se você quiser compilar o aplicativo para um executável independente utilizando o **PyInstaller**:

1. Instale o PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Compile utilizando o arquivo de especificação já configurado:
   ```bash
   pyinstaller "Organizador de Arquivos.spec" --clean
   ```

O executável final estará disponível dentro da pasta `dist/`.

## 📂 Estrutura do Repositório

- `servidor.py`: Código do backend local em Python que gerencia a API de manipulação de arquivos e abre a janela gráfica.
- `index.html`: Interface visual (HTML/CSS/JS) consumida pelo aplicativo.
- `renomear_por_conteudo.py` / `renomear_arquivos.py`: Scripts auxiliares com a lógica de renomeação.
- `Organizador de Arquivos.spec`: Configurações de compilação do PyInstaller.
- `.gitignore`: Arquivo para evitar o envio de lixo de compilação ou arquivos pessoais ao GitHub.
