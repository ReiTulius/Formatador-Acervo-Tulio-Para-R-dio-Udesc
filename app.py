import streamlit as st
import pandas as pd
import re
from datetime import datetime

# Configuração da página do aplicativo
st.set_page_config(page_title="Automatizador de Acervo - Udesc FM", page_icon="💿", layout="wide")

st.title("💿 Automatizador de Acervo Para Udesc FM")
st.markdown("Insira a lista de músicas para limpar, formatar e separar para o Acervo Geral ou Som da Ilha (SC).")

def processar_linha_musica(linha_bruta):
    linha_original = linha_bruta.strip().replace('"', '')
    if not linha_original:
        return None
        
    # 🕵️‍♂️ IDENTIFICAÇÃO DE SC: Verifica se a linha termina com SC (ignorando o .mp3 e espaços)
    linha_limpa_fim = linha_original.lower()
    if linha_limpa_fim.endswith(".mp3"):
        linha_limpa_fim = linha_limpa_fim[:-4].strip()
        
    eh_sc = False
    if linha_limpa_fim.endswith("- sc") or linha_limpa_fim.endswith("-sc"):
        eh_sc = True
        
    # 🧹 LIMPEZA PADRÃO: Remove o caminho da pasta e o .mp3 do final
    if "\\" in linha_original:
        linha_trabalho = linha_original.split("\\")[-1]
    else:
        linha_trabalho = linha_original
        
    if linha_trabalho.lower().endswith(".mp3"):
        linha_trabalho = linha_trabalho[:-4]
        
    # Se for SC, remove o "- SC" do final do texto de trabalho para não atrapalhar o corte do Ano
    if eh_sc:
        linha_trabalho = re.sub(r'\s*-\s*sc\s*$', '', linha_trabalho, flags=re.IGNORECASE).strip()
        
    artista = ""
    participacao = ""
    musica = ""
    formato = ""
    ano = ""
    compositores = ""
    
    # 1. Isola os Compositores se existirem
    padrao_comp = r'\((comp\.|compa)[^)]+\)'
    busca_comp = re.search(padrao_comp, linha_trabalho, flags=re.IGNORECASE)
    
    if busca_comp:
        compositores_com_parentese = busca_comp.group(0)
        compositores = re.sub(r'\((comp\.|compa)\s*', '', compositores_com_parentese, flags=re.IGNORECASE).rstrip(')')
        linha_trabalho = linha_trabalho.replace(compositores_com_parentese, "").replace("  ", " ")
    else:
        linha_trabalho = linha_trabalho

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

    # 3. Montagem do Nome do Arquivo Formatado
    part_str = f" - (part. {participacao})" if participacao else ""
    comp_str = f" (comp. {compositores})" if compositores else ""
    formato_str = f" - {formato}" if formato else ""
    ano_str = f" - {ano}" if ano else ""
    sc_str = " - SC" if eh_sc else ""
    
    nome_arquivo_formatado = f"{artista}{part_str} - {musica}{comp_str}{formato_str}{ano_str}{sc_str}"
    nome_arquivo_formatado = re.sub(r'\s+', ' ', nome_arquivo_formatado).strip()

    # Retorna os dados com a flag indicando se é de SC ou não
    return {
        "eh_sc": eh_sc,
        "Música": musica,
        "Artista": artista,
        "Compositores": compositores,
        "Formato": formato,
        "Ano": ano,
        "Origem": "",
        "Gênero": "",
        "Gênero Relacionado": "",
        "Est/Idioma": "SC" if eh_sc else "",
        "Classificação": "",
        "Andamento": "",
        "Data Cadastro": datetime.now().strftime("%d/%m/%Y"),
        "Participações": participacao,
        "Nome do Arquivo": nome_arquivo_formatado
    }

texto_bruto = st.text_area("Cole aqui as linhas brutas das músicas baixadas (pode misturar normais e com SC):", height=250, placeholder="M:\\...")

if st.button("Processar e Organizar Acervos 🚀", type="primary"):
    if texto_bruto:
        linhas = texto_bruto.split('\n')
        lista_geral = []
        lista_sc = []
        
        for linha in linhas:
            res = processar_linha_musica(linha)
            if res:
                eh_sc = res.pop("eh_sc") # Remove a flag de controle
                
                if eh_sc:
                    # 🎯 ESTRUTURA SOM DA ILHA (SC)
                    dados_sc = {
                        "Música": res["Música"],
                        "Artista": res["Artista"],
                        "Compositores": res["Compositores"],
                        "Formato": res["Formato"],
                        "Ano": res["Ano"],
                        "Origem": res["Origem"],
                        "Gênero": res["Gênero"],
                        "Gênero Relacionado": res["Gênero Relacionado"],
                        "Est": "SC",
                        "Classificação": res["Classificação"],
                        "Andamento": res["Andamento"],
                        "Data Cadastro": res["Data Cadastro"],
                        "Participações": res["Participações"],
                        "Nome do Arquivo": res["Nome do Arquivo"]
                    }
                    lista_sc.append(dados_sc)
                else:
                    # 🎯 ESTRUTURA ACERVO GERAL
                    dados_geral = {
                        "Música": res["Música"],
                        "Artista": res["Artista"],
                        "Compositores": res["Compositores"],
                        "Formato": res["Formato"],
                        "Ano": res["Ano"],
                        "Origem": res["Origem"],
                        "Gênero": res["Gênero"],
                        "Gênero Relacionado": res["Gênero Relacionado"],
                        "Idioma": "",
                        "Classificação": res["Classificação"],
                        "Andamento": res["Andamento"],
                        "Data Cadastro": res["Data Cadastro"],
                        "Participações": res["Participações"],
                        "Nome do Arquivo": res["Nome do Arquivo"]
                    }
                    lista_geral.append(dados_geral)
        
        # --- EXIBIÇÃO DA TABELA DO ACERVO GERAL ---
        if lista_geral:
            df_geral = pd.DataFrame(lista_geral)
            df_geral.drop_duplicates(subset=["Nome do Arquivo"], keep="first", inplace=True)
            
            st.success(f"🎉 {len(df_geral)} músicas prontas para o ACERVO GERAL!")
            st.markdown("👉 *Clique na tabela abaixo, use **Ctrl+A** e **Ctrl+C**, e cole na sua planilha do Acervo Geral.*")
            st.dataframe(df_geral, use_container_width=True)
            
        # --- EXIBIÇÃO DA TABELA DO SOM DA ILHA ---
        if lista_sc:
            df_sc = pd.DataFrame(lista_sc)
            df_sc.drop_duplicates(subset=["Nome do Arquivo"], keep="first", inplace=True)
            
            st.warning(f"🏝️ {len(df_sc)} músicas de Santa Catarina identificadas para o SOM DA ILHA!")
            st.markdown("👉 *Clique na tabela abaixo, use **Ctrl+A** e **Ctrl+C**, e cole na sua planilha do Som da Ilha.*")
            st.dataframe(df_sc, use_container_width=True)
            
        # 🎯 CORRIGIDO: Modificado de list_sc para lista_sc para eliminar o erro
        if lista_geral or lista_sc:
            st.balloons()
        else:
            st.warning("Nenhuma linha válida encontrada no padrão.")
    else:
        st.warning("Cole os dados antes de processar.")
