import streamlit as st
import requests
import re
from datetime import datetime

st.set_page_config(page_title="Automação de Acervo - Udesc FM", page_icon="💿", layout="centered")

st.title("💿 Automatizador de Acervo - Tulio Para Udesc FM")
st.markdown("Insira a lista de músicas baixadas para cadastrar diretamente no Google Sheets de forma 100% gratuita.")

# 🔗 COLOQUE A SUA URL DO APPS SCRIPT AQUI
URL_ENVIO_GOOGLE = "https://script.google.com/macros/s/AKfycbzsabstAyL4BDJLLVZho73y1LqowQRYun-a1jiaZKEe65XmgcZ78BT_stZFj8hFU43L/exec"

def processar_linha_musica(linha_bruta):
    linha_bruta = \
linha_bruta.strip().replace('"', '') 
    if not \
linha_bruta:
        return None
        
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
    
    padrao_comp = r'\((comp\.|compa)[^)]+\)'
    busca_comp = re.search(padrao_comp, linha_bruta, flags=re.IGNORECASE)
    
    if busca_comp:
        compositores_com_parentese = busca_comp.group(0)
        compositores = re.sub(r'\((comp\.|compa)\s*', '', compositores_com_parentese, flags=re.IGNORECASE).rstrip(')')
        linha_trabalho = linha_bruta.replace(compositores_com_parentese, "").replace("  ", " ")
    else:
        linha_trabalho = linha_bruta

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
        if indice_atual == len(partes) - 1 and \
partes[indice_atual].isdigit():
            pass
        else:
            formato = partes[indice_atual]
            indice_atual += 1
            
    if len(partes) > indice_atual and partes[-1].isdigit():
        ano = partes[-1]

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
                with st.spinner(f"Verificando duplicados e enviando {len(pacote_dados)} músicas..."):
                    try:
                        resposta = requests.post(URL_ENVIO_GOOGLE, json=pacote_dados)
                        if resposta.status_code == 200:
                            res_json = resposta.json()
                            inseridos = res_json.get("inseridos", 0)
                            ignorados = res_json.get("ignorados", 0)
                            
                            if inseridos > 0:
                                st.success(f"🎉 Sucesso! {inseridos} nova(s) música(s) foram cadastradas no acervo!")
                            if ignorados > 0:
                                st.warning(f"⚠️ {ignorados} música(s) foram ignoradas por já existirem na planilha.")
                            st.balloons()
                        else:
                            st.error(f"O Google Sheets retornou um erro. Status: {resposta.status_code}")
                    except Exception as e:
                        st.error(f"Erro ao processar resposta do servidor: {e}")
            else:
                st.warning("Nenhuma linha enviada estava no padrão correto.")
