import streamlit as st
import requests
import re
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Automação de Acervo - Som da Ilha", page_icon="💿", layout="centered")

st.title("💿 Automatizador de Acervo - Som da Ilha")
st.markdown("Insira a lista de músicas baixadas para cadastrar diretamente no Google Sheets de forma 100% gratuita.")

# 🔗 COLE AQUI A URL DO APLICATIVO WEB QUE VOCÊ COPIOU NO PASSO 1
URL_ENVIO_GOOGLE = "https://script.google.com/macros/s/AKfycbz0kAafkah84I03N_o9pVB0zRPMQnhm_wOZxrak91Gqvxb3WYHG47sU-awFruLk8X2U/exec"

def processar_linha_musica(linha_bruta):
    linha_bruta = linha_bruta.strip()
    if not linha_bruta:
        return None
        
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

    # Retorna na ordem exata das colunas da planilha (A até N)
    return [
        musica, artista, compositores, formato, ano,
        "", "", "", "", "", "", datetime.now().strftime("%d/%m/%Y"), 
        participacao, nome_arquivo_formatado
    ]

# Interface do usuário
if URL_ENVIO_GOOGLE == "COLE_AQUI_A_URL_DO_APPS_SCRIPT" or not URL_ENVIO_GOOGLE:
    st.error("⚠️ Configuração incompleta: Insira a URL do Apps Script na linha 11 do código.")
else:
    texto_bruto = st.text_area("Cole aqui as linhas brutas das músicas baixadas (uma por linha):", height=250, 
                               placeholder="Exemplo:\n5 a Seco - (part. Maria Gadù) - Em Paz - Álbum Nós - 2013")

    if st.button("Lançar Músicas no Acervo 🚀", type="primary"):
        if texto_bruto:
            linhas = texto_bruto.split('\n')
            sucessos = 0
            
            barra_progresso = st.progress(0)
            
            for i, linha in enumerate(linhas):
                dados_linha = processar_linha_musica(linha)
                if dados_linha:
                    # Envia linha por linha para o script do Google de forma totalmente segura
                    resposta = requests.post(URL_ENVIO_GOOGLE, json=dados_linha)
                    if resposta.status_code == 200:
                        sucessos += 1
                
                # Atualiza a barra visualmente
                barra_progresso.progress((i + 1) / len(linhas))
            
            if sucessos > 0:
                st.success(f"🎉 Alvo atingido! {sucessos} música(s) foram enviadas diretamente para a sua planilha do Google Sheets!")
                st.balloons()
            else:
                st.warning("Nenhuma linha enviada estava no padrão correto.")
        else:
            st.warning("Por favor, cole os dados antes de clicar.")