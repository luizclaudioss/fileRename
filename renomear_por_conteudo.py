import os
import re
import sys
from pathlib import Path
import pypdf
import docx
import urllib.request
import ssl
import threading

# Caminho do dicionário local e conjunto de palavras carregado
DICT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "portuguese_words.txt")
WORD_SET = set()

# Lista de palavras comuns para fallback offline imediato
COMMON_PT_WORDS = {
    "contrato", "de", "emprestimo", "trabalho", "servico", "venda", "compra", "aluguel",
    "recibo", "nota", "fiscal", "declaracao", "imposto", "renda", "relatorio", "projeto",
    "fatura", "pagamento", "comprovante", "identidade", "cpf", "rg", "cnh", "certidao",
    "nascimento", "casamento", "obito", "procuracao", "laudo", "medico", "exame",
    "curriculo", "foto", "imagem", "video", "audio", "musica", "aula", "curso",
    "manual", "livro", "artigo", "tcc", "monografia", "dissertacao", "tese",
    "apresentacao", "slide", "tabela", "planilha", "cadastro", "cliente", "fornecedor",
    "funcionario", "empresa", "banco", "extrato", "saldo", "transferencia", "pix",
    "boleto", "seguro", "sinistro", "police", "proposta", "orcamento", "pedido",
    "entrega", "frete", "envio", "recebimento", "devolucao", "troca", "garantia",
    "suporte", "atendimento", "chamado", "reclamacao", "sugestao", "elogio", "pesquisa",
    "satisfacao", "ademicon", "reclame", "aqui", "unidade", "colombo", "hauer",
    "nao", "paga", "comissao", "metas", "abusivas", "rescisao", "desconto", "pj",
    "novo", "terceira", "vez", "falta", "atendimento", "assinatura", "assinado"
}

def carregar_dicionario():
    global WORD_SET
    WORD_SET = set(COMMON_PT_WORDS)
    if os.path.exists(DICT_PATH):
        try:
            with open(DICT_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    word = line.strip().lower()
                    if word:
                        WORD_SET.add(word)
            return
        except Exception:
            pass
            
    # Tenta baixar o dicionário caso não exista localmente
    url = "https://raw.githubusercontent.com/kkrypt0nn/wordlists/main/wordlists/languages/portuguese.txt"
    try:
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(url, timeout=5, context=ctx) as response:
            content = response.read().decode("utf-8")
            with open(DICT_PATH, "w", encoding="utf-8") as f:
                f.write(content)
            for line in content.splitlines():
                word = line.strip().lower()
                if word:
                    WORD_SET.add(word)
    except Exception:
        pass

# Inicia o carregamento em background para não bloquear o startup
threading.Thread(target=carregar_dicionario, daemon=True).start()

def remover_acentos(txt):
    d = {
        'á': 'a', 'à': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'ó': 'o', 'ò': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c', 'ñ': 'n'
    }
    return "".join(d.get(c, c) for c in txt.lower())

def segmentar_palavras(texto_junto):
    if not texto_junto:
        return ""
        
    texto_limpo = remover_acentos(texto_junto)
    n = len(texto_limpo)
    
    dp = [(float('inf'), [])] * (n + 1)
    dp[0] = (0, [])
    
    short_words = {'a', 'o', 'e', 'de', 'do', 'da', 'em', 'um', 'se', 'no', 'na', 'os', 'as'}
    
    for i in range(1, n + 1):
        for j in range(max(0, i - 15), i):
            palavra = texto_limpo[j:i]
            if palavra in WORD_SET or palavra.isdigit() or (len(palavra) == 1 and palavra in short_words):
                custo = dp[j][0] + 1
                if len(palavra) == 1 and palavra not in short_words:
                    custo += 10
                if custo < dp[i][0]:
                    dp[i] = (custo, dp[j][1] + [texto_junto[j:i]])
                    
    if dp[n][0] != float('inf'):
        return " ".join(dp[n][1])
    else:
        palavras = []
        i = 0
        while i < n:
            match = None
            for j in range(min(n, i + 15), i, -1):
                sub = texto_limpo[i:j]
                if sub in WORD_SET or sub.isdigit() or (len(sub) == 1 and sub in short_words):
                    match = texto_junto[i:j]
                    i = j
                    break
            if match is None:
                palavras.append(texto_junto[i])
                i += 1
            else:
                palavras.append(match)
        return " ".join(palavras)

def tentar_segmentar_palavra(palavra):
    if len(palavra) < 6:
        return palavra
    
    palavra_low = remover_acentos(palavra.lower())
    if palavra_low in WORD_SET:
        return palavra
        
    if not palavra_low.isalpha():
        return palavra
        
    segmentada = segmentar_palavras(palavra)
    partes = segmentada.split()
    if len(partes) <= 1:
        return palavra
        
    partes_validas = 0
    for p in partes:
        p_low = remover_acentos(p.lower())
        if len(p_low) == 1:
            if p_low in {'a', 'o', 'e'}:
                partes_validas += 1
        elif p_low in WORD_SET or p_low in {'de', 'do', 'da', 'em', 'um', 'se', 'no', 'na', 'os', 'as'}:
            partes_validas += 1
            
    if partes_validas / len(partes) >= 0.8:
        return segmentada
    return palavra

def obter_numero_diretorio(nome_dir):
    """Extrai o número inicial do nome de um diretório (ex: '1. Introdução' -> '1')"""
    match = re.match(r'^(\d+)', nome_dir)
    if match:
        return match.group(1)
    return None

def limpar_titulo_para_arquivo(titulo):
    if not titulo:
        return ""
    
    # Remover extensões comuns no metadado do arquivo original (.pptx.pptx, .pptx, .pdf, etc.)
    titulo = re.sub(r'\.pptx(\.pptx)?$', '', titulo, flags=re.IGNORECASE)
    titulo = re.sub(r'\.pdf$', '', titulo, flags=re.IGNORECASE)
    
    # Remover "::" ou "|" no início
    titulo = re.sub(r'^[:\s|]+', '', titulo)
    
    # Remover partes pós-separadores de sites comuns
    if " | " in titulo:
        titulo = titulo.split(" | ")[0]
    elif " - " in titulo:
        partes = titulo.split(" - ")
        # Se a segunda parte parecer com nome de site, plataforma ou extensão, descartamos
        if len(partes) > 1 and any(x in partes[1].lower() for x in ['plataforma', 'dica', 'unisuam', 'site', 'revista', 'pdf']):
            titulo = partes[0]
            
    # Substituir caracteres inválidos em nomes de arquivos em qualquer SO
    titulo = re.sub(r'[\\/*?:"<>|]', '', titulo)
    
    # Separar palavras em camelCase / PascalCase e substituir vírgulas por espaços
    titulo = titulo.replace(',', ' ')
    titulo = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', titulo)
    titulo = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', titulo)
    
    # Substituir sublinhados/hifens/sinais de mais por espaços
    titulo = titulo.replace('_', ' ').replace('-', ' ').replace('+', ' ')
    
    # Remover espaços múltiplos
    titulo = re.sub(r'\s+', ' ', titulo).strip()
    
    # Limitar o tamanho do nome do arquivo para evitar erros do sistema de arquivos
    if len(titulo) > 100:
        titulo = titulo[:97] + "..."
        
    # Padronizar título em português (Title Case inteligente)
    palavras = titulo.split()
    preposicoes = {'de', 'do', 'da', 'dos', 'das', 'e', 'a', 'o', 'em', 'para', 'com', 'por', 'ou', 'um', 'uma'}
    resultado = []
    
    for i, palavra in enumerate(palavras):
        palavra_processada = tentar_segmentar_palavra(palavra)
        for sub_palavra in palavra_processada.split():
            if len(resultado) == 0:
                if sub_palavra.isupper() and len(sub_palavra) > 1:
                    resultado.append(sub_palavra)
                else:
                    resultado.append(sub_palavra.capitalize())
            elif sub_palavra.lower() in preposicoes:
                resultado.append(sub_palavra.lower())
            else:
                if sub_palavra.isupper() and len(sub_palavra) > 1:
                    resultado.append(sub_palavra)
                else:
                    resultado.append(sub_palavra.capitalize())
                
    return " ".join(resultado)

def extrair_titulo_do_texto(texto):
    if not texto:
        return None
    
    linhas = [l.strip() for l in texto.split('\n') if l.strip()]
    palavras_descarte = {
        'issn', 'doi:', 'http', 'vol.', 'n.', 'jan.', 'jun.', 'recebido em', 
        'reformulado em', 'revista', 'universidade', 'editorial', 'artigo',
        'submetido', 'aceito', 'publicado', 'anais', 'proceedings', 'page', 'página',
        'blind review', 'diretrizes', 'licença', 'creative commons', 'todos os direitos'
    }
    
    linhas_filtradas = []
    for linha in linhas:
        if re.match(r'^\d+$', linha) or len(linha) < 10:
            continue
        if any(p in linha.lower() for p in palavras_descarte):
            continue
        linhas_filtradas.append(linha)
        
    titulo_partes = []
    for linha in linhas_filtradas:
        if any(p in linha.lower() for p in ['autores', 'authors', 'effects of', 'efectos de', 'resumo', 'abstract', 'resumen']):
            break
        titulo_partes.append(linha)
        if len(titulo_partes) >= 3:
            break
            
    if titulo_partes:
        return " ".join(titulo_partes)
    return None

def obter_titulo_pdf(caminho):
    try:
        reader = pypdf.PdfReader(caminho)
        meta = reader.metadata
        titulo = None
        
        # 1. Tentar pegar o título do metadado
        if meta and meta.title:
            t_meta = meta.title.strip()
            # Ignora se for vazio, somente espaços ou títulos genéricos conhecidos
            titulos_genericos = {
                '', 'untitled', 'document', 'documento', ':: plataforma a', 'plataforma a',
                'capítulo do livro', 'capítulo de livro', 'capitulo do livro', 'capitulo de livro',
                'microsoft word'
            }
            if t_meta.lower() not in titulos_genericos:
                titulo = t_meta
                
        # 2. Se não encontrou título válido no metadado, tenta extrair da primeira página
        if not titulo and reader.pages:
            texto_p1 = reader.pages[0].extract_text()
            titulo = extrair_titulo_do_texto(texto_p1)
            
        return titulo
    except Exception:
        pass
    return None


def obter_titulo_docx(caminho):
    try:
        doc = docx.Document(caminho)
        # Tenta pegar o primeiro parágrafo não vazio
        for p in doc.paragraphs:
            texto = p.text.strip()
            if texto:
                # Se for muito longo, corta para ser um título viável
                if len(texto) > 150:
                    texto = texto[:147] + "..."
                return texto
    except Exception:
        pass
    return None

def renomear_por_conteudo(caminho_base, caminho_atual=None, prefixo_pai=""):
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
            prefixo_atual = prefixo_pai
            
    # Processar arquivos
    arquivos = [
        f for f in caminho_atual.iterdir() 
        if f.is_file() and not f.name.startswith('.') and f.name != Path(__file__).name and f.name != "renomear_arquivos.py"
    ]
    arquivos.sort(key=lambda x: x.name)
    
    if prefixo_atual:
        for arquivo in arquivos:
            novo_titulo = None
            ext = arquivo.suffix.lower()
            
            # Tentar extrair o título real
            if ext == '.pdf':
                novo_titulo = obter_titulo_pdf(arquivo)
            elif ext == '.docx':
                novo_titulo = obter_titulo_docx(arquivo)
                
            # Limpar prefixo de numeração antigo do nome para ver o nome limpo original
            nome_limpo = re.sub(r'^\d+(\.\d+)*[_\s.-]+', '', arquivo.name)
            
            if novo_titulo:
                nome_padronizado = limpar_titulo_para_arquivo(novo_titulo) + ext
            else:
                # Se não conseguiu extrair título, apenas mantém o nome limpo anterior padronizado
                # Mas sem re-adicionar a extensão
                stem = Path(nome_limpo).stem
                nome_padronizado = limpar_titulo_para_arquivo(stem) + ext
                
            # Formato: "prefixo. Nome do Arquivo"
            novo_nome = f"{prefixo_atual}. {nome_padronizado}"
            novo_path = caminho_atual / novo_nome
            
            if arquivo.name != novo_nome:
                arquivo.rename(novo_path)
                print(f"✓ {arquivo.relative_to(caminho_base)} → {novo_nome}")
                
    # Processar subdiretórios
    subdirs = [d for d in caminho_atual.iterdir() if d.is_dir() and not d.name.startswith('.')]
    subdirs.sort(key=lambda x: x.name)
    for subdir in subdirs:
        renomear_por_conteudo(caminho_base, subdir, prefixo_atual)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        diretorio = sys.argv[1]
    else:
        print("Digite o caminho do diretório (ou pressione Enter para usar o diretório atual):")
        diretorio = input("> ").strip().strip("'\"")
        if not diretorio:
            diretorio = "."
            
    print("\nIniciando renomeação por conteúdo...")
    try:
        renomear_por_conteudo(diretorio)
        print("\nRenomeação por conteúdo concluída com sucesso!")
    except Exception as e:
        print(f"\nErro durante a renomeação: {e}")
