import streamlit as st
import requests
import re
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Automação de Acervo - Som da Ilha", page_icon="💿", layout="centered")

st.title("💿 Automatizador de Acervo - Som da Ilha")
st.markdown("Insira a lista de músicas baixadas para cadastrar diretamente no Google Sheets de forma 100% gratuita.")

# 🔗 SEU LINK DO APPS SCRIPT AQUI
URL_ENVIO_GOOGLE = "https://script.google.com/macros/s/AKfycbx-Nv65ez9FGmbze1vcrrkaDYnxoClH3-9AjDEHYgkj7oiMcc3ahXxsppvwuwckTgCG/exec"

def processar_linha_musica(linha_bruta):
    linha_bruta = linha_bruta.strip().replace('"', '') # Remove aspas se houver
    if not linha_bruta:
        return None
        
    # 🔥 NOVA LIMPEZA: Se vier com caminho de pasta (M:\...\) ou extensão (.mp3), limpa tudo
    if "\\" in linha_bruta:
        linha_bruta = linha_bruta.split("\\")[-1] # Pega só o final após a última barra
    if linha_bruta.lower().endswith(".mp3"):
        linha_bruta = linha_bruta[:-4] # Remove o .mp3 do final
        
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

    # 3. Montagem do Nome do Arquivo Formatado
    part_str = f" - (part. {participacao})" if participacao else ""
    comp_str = f" (comp. {compositores})" if compositores else " (comp. )"
    formato_str = f" - {formato}" if formato else ""
    ano_str = f" - {ano}" if ano else ""
    
    nome_arquivo_formatado = f"{artista}{part_str} {musica}{comp_str}{formato_str}{ano_str}"
    nome_arquivo_formatado = re.sub(r'\s+', ' ', nome_arquivo_formatado).strip()

    return [
        musica, artista, compositores, formato, ano,
        "", "", "", "", "", "", datetime.now().strftime("%d/%m/%Y"), 
        participacao, nome_arquivo_formatado
    ]

# Interface do usuário
if URL_ENVIO_GOOGLE == "COLE_AQUI_A_URL_DO_APPS_SCRIPT" or not URL_ENVIO_GOOGLE:
    st.error("⚠️ Configuração incompleta: Insira a URL do Apps Script no código.")
else:
    texto_bruto = st.text_area("Cole aqui as linhas brutas das músicas:", height=250)

    if st.button("Lançar Músicas no Acervo 🚀", type="primary"):
        if texto_bruto:
            linhas = texto_bruto.split('\n')
            pacote_dados = []
            
            for linha in linhas:
                dados_linha = processar_linha_musica(linha)
                if dados_linha:
                    pacote_dados.append(dados_linha)
            
            if pacote_dados:
                with st.spinner(f"Enviando lote de {len(pacote_dados)} músicas instantaneamente..."):
                    # Envia TODAS as linhas de uma vez só!
                    resposta = requests.post(URL_ENVIO_GOOGLE, json=pacote_dados)
                    if resposta.status_code == 200:
                        st.success(f"🎉 Alvo atingido! {len(pacote_dados)} músicas foram cadastradas de uma vez só!")
                        st.balloons()
                    else:
                        st.error("Erro ao enviar dados para o Google Sheets.")
            else:
                st.warning("Nenhuma linha enviada estava no padrão correto.")