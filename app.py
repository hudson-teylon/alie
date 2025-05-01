import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import YoutubeLoader
import json

# Definindo a chave da API
api_key = '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'
os.environ['GROQ_API_KEY'] = api_key

# Inicializando o chat
chat = ChatGroq(model='llama-3.3-70b-versatile')

# Função que gera a resposta do bot
def resposta_bot(mensagens, documento):
    mensagem_system = '''Você é um assistente amigável que se chama Alie. Você utiliza as seguintes informações para formular as suas respostas: {informacoes}'''
    mensagens_modelo = [('system', mensagem_system)]
    mensagens_modelo += mensagens
    template = ChatPromptTemplate.from_messages(mensagens_modelo)
    chain = template | chat

    try:
        return chain.invoke({'informacoes': documento}).content
    except Exception as e:
        try:
            err_data = json.loads(str(e).split("Error code:")[-1].strip())
            if err_data.get("error", {}).get("code") == "rate_limit_exceeded":
                wait = err_data["error"]["message"].split("in ")[1].split(".")[0]
                return f"O meu limite de uso gratuito excedeu, posso responder novamente em {wait}."
        except:
            pass
        return "Houve um erro ao tentar responder. Tente novamente mais tarde."

# Função para carregar o conteúdo do site
def carrega_site(url_site):
    loader = WebBaseLoader(url_site)
    lista_documentos = loader.load()
    documento = ''
    for doc in lista_documentos:
        documento = documento + doc.page_content
    return documento

# Função para carregar o conteúdo do vídeo do YouTube
def carrega_youtube(url_youtube):
    try:
        loader = YoutubeLoader.from_youtube_url(url_youtube, language=['pt'])
        lista_documentos = loader.load()
        documento = ''.join(doc.page_content for doc in lista_documentos)
        return documento
    except Exception as e:
        return "Não foi possível carregar a transcrição deste vídeo. Verifique se ele possui legendas em português e está acessível."

def main():
    st.set_page_config(page_title="Alie Chat", layout="wide")
    st.title("Olá, sou a Alie!")

    st.markdown("""
    <style>
    .chat-messages-container {
        padding: 10px;
        max-height: 55vh;
        overflow-y: auto;
        margin-bottom: 10px;
    }
    .input-button-row {
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin-top: 15px;
    }
    .message-container {
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 1px solid #ccc;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

    opcoes = ["Site", "YouTube"]
    opcao = st.radio("Sou uma IA criada para te ajudar a resumir, destacar pontos importantes ou qualquer outra coisa que precise fazer com um site ou vídeo do YouTube específico. Qual você prefere agora?", opcoes)

    if opcao == "Site":
        url_site = st.text_input('Digite a URL do site:')
        if url_site:
            documento = carrega_site(url_site)
            st.write("Conteúdo do site carregado com sucesso!")

    elif opcao == "YouTube":
        url_youtube = st.text_input('Digite a URL do vídeo do YouTube:')
        if url_youtube:
            documento = carrega_youtube(url_youtube)
            st.write("Conteúdo do vídeo carregado com sucesso!")

    if 'documento' not in locals():
        documento = ''

    if 'mensagens' not in st.session_state:
        st.session_state['mensagens'] = []

    if 'pergunta' not in st.session_state:
        st.session_state['pergunta'] = ''

    if st.session_state['mensagens']:
        with st.container():
            st.markdown('<div class="chat-messages-container">', unsafe_allow_html=True)
            for i, msg in enumerate(st.session_state['mensagens']):
                remetente = "Você" if msg[0] == 'user' else "Alie"
                st.markdown(f"<div class='message-container'><strong>{remetente}:</strong> {msg[1]}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="input-button-row">', unsafe_allow_html=True)
        pergunta_key = f"pergunta_input_{len(st.session_state['mensagens'])}"

        def enviar_pergunta():
            pergunta = st.session_state[pergunta_key].strip()
            if pergunta:
                st.session_state['mensagens'].append(('user', pergunta))
                resposta = resposta_bot(st.session_state['mensagens'], documento)
                st.session_state['mensagens'].append(('assistant', resposta))
                st.session_state['pergunta'] = ""

        st.text_input(
            "Mensagem",
            value=st.session_state['pergunta'],
            key=pergunta_key,
            placeholder="Converse aqui",
            on_change=enviar_pergunta
        )

        if st.button("Enviar", key=f"enviar_{len(st.session_state['mensagens'])}"):
            enviar_pergunta()

        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
