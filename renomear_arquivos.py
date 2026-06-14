"""
SCRIPT PYTHON PARA AUTOMATIZAR RENOMEAÇÃO DE ARQUIVOS
Numeração: 1.1.1, 1.1.2, 1.2.1 + nome original

Para usar:
1. Salve como: renomear_arquivos.py
2. Execute: python renomear_arquivos.py
"""

import os
import re
from pathlib import Path

def obter_numero_diretorio(nome_dir):
    """Extrai o número inicial do nome de um diretório (ex: '1. Introdução' -> '1')"""
    match = re.match(r'^(\d+)', nome_dir)
    if match:
        return match.group(1)
    return None

def padronizar_nome(nome):
    """Padroniza o nome do arquivo substituindo sublinhados/hifens por espaços e ajustando maiúsculas"""
    stem = Path(nome).stem
    ext = Path(nome).suffix.lower()
    
    # Substituir sublinhados e hifens por espaços
    novo_stem = stem.replace('_', ' ').replace('-', ' ')
    
    # Remover espaços múltiplos
    novo_stem = re.sub(r'\s+', ' ', novo_stem).strip()
    
    # Padronizar maiúsculas/minúsculas inteligente (Estilo Título em português)
    palavras = novo_stem.split()
    preposicoes = {'de', 'do', 'da', 'dos', 'das', 'e', 'a', 'o', 'em', 'para', 'com', 'por', 'ou', 'um', 'uma'}
    resultado = []
    
    for i, palavra in enumerate(palavras):
        # Sempre capitaliza a primeira palavra
        if i == 0:
            if palavra.isupper() and len(palavra) > 1:
                resultado.append(palavra)
            else:
                resultado.append(palavra.capitalize())
        # Para as demais, verifica se é preposição
        elif palavra.lower() in preposicoes:
            resultado.append(palavra.lower())
        else:
            # Preserva siglas totalmente maiúsculas (ex: SOC, NAP, SA)
            if palavra.isupper() and len(palavra) > 1:
                resultado.append(palavra)
            else:
                resultado.append(palavra.capitalize())
                
    return " ".join(resultado) + ext

def renomear_arquivos_recursivo(caminho_base, caminho_atual=None, prefixo_pai=""):
    """
    Vasculha as pastas recursivamente e renomeia os arquivos
    com base na numeração das pastas (ex: 1.1. nome do arquivo)
    """
    if caminho_atual is None:
        caminho_atual = Path(caminho_base)
    
    # Determinar o prefixo com base no diretório atual
    if caminho_atual == Path(caminho_base):
        prefixo_atual = ""
    else:
        num = obter_numero_diretorio(caminho_atual.name)
        if num:
            prefixo_atual = f"{prefixo_pai}.{num}" if prefixo_pai else num
        else:
            prefixo_atual = prefixo_pai  # herda o prefixo se a pasta atual não começar com número
            
    # Obter e ordenar arquivos deste diretório (ignorando arquivos ocultos e o próprio script)
    arquivos = [
        f for f in caminho_atual.iterdir() 
        if f.is_file() and not f.name.startswith('.') and f.name != Path(__file__).name
    ]
    arquivos.sort(key=lambda x: x.name)
    
    if prefixo_atual:
        for arquivo in arquivos:
            # Limpar prefixos antigos de numeração do nome do arquivo (ex: '1.1.3_nome.pdf' ou '1.1. nome.pdf')
            nome_limpo = re.sub(r'^\d+(\.\d+)*[_\s.-]+', '', arquivo.name)
            if not nome_limpo:
                nome_limpo = arquivo.name
            
            # Padroniza o nome limpo
            nome_padronizado = padronizar_nome(nome_limpo)
            
            # Formato solicitado: "1.1. Nome do Arquivo"
            novo_nome = f"{prefixo_atual}. {nome_padronizado}"
            novo_path = caminho_atual / novo_nome
            
            if arquivo.name != novo_nome:
                arquivo.rename(novo_path)
                print(f"✓ {arquivo.relative_to(caminho_base)} → {novo_nome}")

                
    # Processar subdiretórios recursivamente
    subdirs = [d for d in caminho_atual.iterdir() if d.is_dir() and not d.name.startswith('.')]
    subdirs.sort(key=lambda x: x.name)
    
    for subdir in subdirs:
        renomear_arquivos_recursivo(caminho_base, subdir, prefixo_atual)

# Exemplo de uso
if __name__ == "__main__":
    import sys
    
    # Se passado via argumento de linha de comando, usa o argumento
    if len(sys.argv) > 1:
        diretorio = sys.argv[1]
    else:
        # Solicita interativamente ao usuário
        print("Digite o caminho do diretório (ou pressione Enter para usar o diretório atual):")
        diretorio = input("> ").strip()
        # Remove aspas caso o usuário tenha arrastado a pasta para o terminal
        diretorio = diretorio.strip("'\"")
        if not diretorio:
            diretorio = "."
    
    try:
        print("\nIniciando renomeação...")
        renomear_arquivos_recursivo(diretorio)

        print("\nRenomeação completa com sucesso!")
    except Exception as e:
        print(f"\nErro ao renomear arquivos: {e}")

