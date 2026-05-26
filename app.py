import streamlit as st
import requests
import re
from datetime import datetime

# Configuração da página do aplicativo
st.set_page_config(page_title="Automação de Acervo - Tulio Para Udesc FM", page_icon="💿", layout="centered")

st.title("💿 Automatizador de Acervo - Tulio Para Udesc FM")
st.markdown("Insira a lista de músicas baixadas para cadastrar diretamente no Google Sheets de forma 100% gratuita.")

# 🔗 COLE AQUI A SUA URL DO APPLICATIVO WEB DO GOOGLE (APPS SCRIPT)
URL_ENVIO_GOOGLE = "https://script.google.com/macros/s/AKfycbzrmUS2n2dGgNFa5Q18hF7J1PrJMCAxdkVTpL_YKIUn7upwm8JeyAdyQuTH0n8vnvZj/exec"

def processar_linha_musica(linha_bruta):
    # Remove aspas extras se o texto vier copiado com elas
    linha_bruta = linha_bruta.strip().replace('"', '') 
    if not linha_bruta:
        return None
        
    # 🧹 LIMPEZA DE PASTA E EXTENSÃO: Remove o caminho (M:\...\) e o (.mp3)
    if "\\" in linha_bruta:
        linha_bruta = linha_bruta.split("\\")[-1] # Mantém apenas o que vem após a última barra
    if linha_bruta.lower().endswith(".mp3"):
        linha_bruta = linha_bruta[:-4] # Recorta os 4 caracteres do .mp3
        
    artista = ""
    participacao = ""
    musica = ""
    formato = ""
    ano = ""
    compositores = ""
    
    # 1. Isola os Compositores se eles existirem na linha ex: (comp. Fulano)
    padrao_comp = r'\((comp\.|compa)[^)]+\)'
    busca_comp = re.search(padrao_comp, linha_bruta, flags=re.IGNORECASE)
    
    if busca_comp:
        compositores_com_parentese = busca_comp.group(0)
        compositores = re.sub(r'\((comp\.|compa)\s*', '', compositores_com_parentese, flags=re.IGNORECASE).rstrip(')')
        linha_trabalho = linha_bruta.replace(compositores_com_parentese, "").replace("  ", " ")
    else:
        linha_trabalho = linha_bruta

    # 2. Divide a linha pelos hífens principais " - "
    partes = [p.strip() for p in linha_trabalho.split(" - ")]
    
    # Validação mínima necessária
    if len(partes) < 2:
        return None
        
    artista = partes[0]
    
    # Captura Participação se houver logo após o artista
    indice_atual = 1
    if indice_atual < len(partes) and ("part." in partes[indice_atual].lower() or "part " in partes[indice_atual].lower()):
        participacao = re.sub(r'\(?part\.?\s*', '', partes[indice_atual], flags=re.IGNORECASE).rstrip(')')
        indice_atual += 1
        
    # Captura a Música
    if indice_atual < len(partes):
        musica = partes[indice_atual]
        indice_atual += 1
        
    # Captura o Formato (Álbum, EP, Single...)
    if indice_atual < len(partes):
        if indice_atual == len(partes) - 1 and partes[indice_atual].isdigit():
            pass
        else:
            formato = partes[indice_atual]
            indice_atual += 1
            
    # Captura o Ano se o último elemento for numérico
    if len(partes) > indice_atual and partes[-1].isdigit():
        ano = partes[-1]

    # 3. Reconstrução do Nome do Arquivo Formatado (Coluna N)
    part_str = f" - (part. {participacao})" if participacao else ""
    comp_str = f" (comp. {compositores})" if compositores else " (comp. )"
    formato_str = f" - {formato}" if formato else ""
    ano_str = f" - {ano}" if ano else ""
    
    nome_arquivo_formatado = f"{artista}{part_str} {musica}{comp_str}{formato_str}{ano_str}"
    nome_arquivo_formatado = re.sub(r'\s+', ' ', nome_arquivo_formatado).strip()

    # Retorna os dados mapeados na ordem exata das colunas da planilha (A até N)
    return [
        musica, artista, compositores, formato, ano,
        "", "", "", "", "", "", datetime.now().strftime("%d/%m/%Y"), 
        participacao, nome_arquivo_formatado
    ]

# Interface do Usuário no Navegador
if URL_ENVIO_GOOGLE == "COLE_AQUI_A_URL_DO_APPS_SCRIPT" or not URL_ENVIO_GOOGLE:
    st.error("⚠️ Configuração incompleta: Insira a URL do seu Apps Script na linha 14 do código.")
else:
    texto_bruto = st.text_area("Cole aqui as linhas brutas das músicas baixadas (pode conter caminhos e .mp3):", height=300,
                               placeholder="Exemplo:\nM:\\Bolsista - Tulio\\Aaron Frazer - It’s A Shame - Single - 2026.mp3")

    if st.button("Lançar Músicas no Acervo 🚀", type="primary"):
        if texto_bruto:
            linhas = texto_bruto.split('\n')
            pacote_dados = []
            
            # Processa e limpa cada uma das linhas inseridas
            for linha in linhas:
                dados_linha = processar_linha_musica(linha)
                if dados_linha:
                    pacote_dados.append(dados_linha)
            
            if pacote_dados:
                with st.spinner(f"Processando e enviando lote de {len(pacote_dados)} músicas para o Sheets..."):
                    try:
                        # Envia todo o lote de uma vez só para o Google Sheets
                        resposta = requests.post(URL_ENVIO_GOOGLE, json=pacote_dados)
                        
                        if resposta.status_code == 200:
                            res_json = resposta.json()
                            inseridos = res_json.get("inseridos", 0)
                            ignorados = res_json.get("ignorados", 0)
                            
                            # Feedbacks visuais na tela baseados na resposta do Google
                            if inseridos > 0:
                                st.success(f"🎉 Alvo atingido! {inseridos} música(s) novas foram adicionadas com sucesso!")
                            if ignorados > 0:
                                st.warning(f"⚠️ Aviso: {ignorados} música(s) foram descartadas por já existirem na planilha (evitando duplicados).")
                                
                            st.balloons()
                        else:
                            st.error(f"Erro na comunicação com o Google. Status: {resposta.status_code}")
                    except Exception as e:
                        st.error(f"Não foi possível conectar ao Google Sheets: {e}")
            else:
                st.warning("Nenhuma das linhas enviadas estava no padrão mínimo reconhecível.")
        else:
            st.warning("Por favor, cole a lista de arquivos antes de clicar no botão.")
