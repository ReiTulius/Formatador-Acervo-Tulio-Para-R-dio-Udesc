import streamlit as st
import pandas as pd
import re
from datetime import datetime

# Configuração da página do aplicativo
st.set_page_config(page_title="Automatizador de Acervo - Udesc FM", page_icon="💿", layout="wide")

st.title("💿 Automatizador de Acervo Para Udesc FM")
st.markdown("Insira a lista de músicas para limpar, formatar e copiar direto para o Google Sheets sem travamentos.")

def processar_linha_musica(linha_bruta):
    linha_bruta = linha_bruta.strip().replace('"', '') 
    if not linha_bruta:
        return None
        
    # 🧹 LIMPEZA: Remove o caminho da pasta e o .mp3 do final
    if "\\" in linha_bruta:
        linha_bruta = linha_bruta.split("\\")[-1]
    if linha_bruta.lower().endswith(".mp3"):
        linha_bruta = linha_bruta[:-4]
        
    artista = ""
    participacao = ""
    musica = ""
    formato = ""
    ano = ""
    compositores = ""
    
    # 1. Isola os Compositores se existirem
    padrao_comp = r'\((comp\.|compa)[^)]+\)'
    busca_comp = re.search(padrao_comp, linha_bruta, flags=re.IGNORECASE)
    
    if busca_comp:
        compositores_com_parentese = busca_comp.group(0)
        compositores = re.sub(r'\((comp\.|compa)\s*', '', compositores_com_parentese, flags=re.IGNORECASE).rstrip(')')
        linha_trabalho = linha_bruta.replace(compositores_com_parentese, "").replace("  ", " ")
    else:
        linha_trabalho = linha_bruta

    # 2. Divide a linha pelos hífens
    partes = [p.strip() for p in linha_trabalho.split(" - ")]
    
    if len(partes) < 2:
        return None
        
    artista = partes[0]
    
    indice_atual = 1
    if indice_atual < len(partes) and ("part." in partes[indice_atual].lower() or "part " in partes[indice_atual].lower()):
        participacao = re.sub(r'\(?part\.?\s*', '', partes[indice_atual], flags=re.IGNORECASE).rstrip(')')
        indice_atual += 1
        
    if indice_atual < len(partes):
        musica = partes[indice_atual]
        indice_atual += 1
        
    if indice_atual < len(partes):
        if indice_atual == len(partes) - 1 and partes[indice_atual].isdigit():
            pass
        else:
            formato = partes[indice_atual]
            indice_atual += 1
            
    if len(partes) > indice_atual and partes[-1].isdigit():
        ano = partes[-1]

    # 3. Montagem do Nome do Arquivo Formatado (Coluna N)
    # 🎯 SELETOR INTELIGENTE: Só coloca o bloco (comp. ) se houver compositor preenchido
    part_str = f" - (part. {participacao})" if participacao else ""
    comp_str = f" (comp. {compositores})" if compositores else ""
    formato_str = f" - {formato}" if formato else ""
    ano_str = f" - {ano}" if ano else ""
    
    nome_arquivo_formatado = f"{artista}{part_str} - {musica}{comp_str}{formato_str}{ano_str}"
    nome_arquivo_formatado = re.sub(r'\s+', ' ', nome_arquivo_formatado).strip()

    # Retorna exatamente na ordem das colunas da sua planilha (Colunas A até N)
    return {
        "Música": musica,
        "Artista": artista,
        "Compositores": compositores,
        "Formato": formato,
        "Ano": ano,
        "Origem": "",
        "Gênero": "",
        "Gênero Relacionado": "",
        "Idioma": "",
        "Classificação": "",
        "Andamento": "",
        "Data Cadastro": datetime.now().strftime("%d/%m/%Y"),
        "Participações": participacao,
        "Nome do Arquivo": nome_arquivo_formatado
    }

texto_bruto = st.text_area("Cole aqui as linhas brutas das músicas baixadas:", height=250, placeholder="M:\\...")

if st.button("Processar e Formatar Linhas 🚀", type="primary"):
    if texto_bruto:
        linhas = texto_bruto.split('\n')
        lista_resultados = []
        
        for linha in linhas:
            dados_linha = processar_linha_musica(linha)
            if dados_linha:
                lista_resultados.append(dados_linha)
        
        if lista_resultados:
            df = pd.DataFrame(lista_resultados)
            
            # Remove duplicados da lista atual que você acabou de colar
            df.drop_duplicates(subset=["Nome do Arquivo"], keep="first", inplace=True)
            
            st.success(f"🎉 Pronto! {len(df)} músicas limpas e formatadas com sucesso!")
            
            st.markdown("### 📋 Como colocar na sua Planilha:")
            st.markdown("""
            1. Clique em cima de qualquer célula da tabela abaixo.
            2. Use **Ctrl + A** (para selecionar tudo) e depois **Ctrl + C** (para copiar).
            3. Vá na sua planilha do Google Sheets, clique na célula **A4230** (ou na sua primeira linha vazia) e use **Ctrl + V**.
            """)
            
            # Exibe a tabela organizada na tela de forma ultra-rápida
            st.dataframe(df, use_container_width=True)
            st.balloons()
        else:
            st.warning("Nenhuma linha válida encontrada no padrão.")
    else:
        st.warning("Cole os dados antes de processar.")
