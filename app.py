import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import YoutubeLoader
import uuid

api_key = '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'
os.environ['GROQ_API_KEY'] = api_key

chat = ChatGroq(model='meta-llama/llama-4-maverick-17b-128e-instruct')

def resposta_bot(mensagens, documento):
    mensagem_system = '''Você é um assistente amigável que se chama Alie. Você utiliza as seguintes informações para formular as suas respostas: {informacoes}'''
    mensagens_modelo = [('system', mensagem_system)]
    mensagens_modelo += mensagens
    template = ChatPromptTemplate.from_messages(mensagens_modelo)
    chain = template | chat
    return chain.invoke({'informacoes': documento}).content

def carrega_site(url_site):
    loader = WebBaseLoader(url_site)
    lista_documentos = loader.load()
    documento = ''
    for doc in lista_documentos:
        documento = documento + doc.page_content
    return documento

def carrega_youtube(url_youtube):
    loader = YoutubeLoader.from_youtube_url(url_youtube, language=['pt'])
    lista_documentos = loader.load()
    documento = ''
    for doc in lista_documentos:
        documento = documento + doc.page_content
    return documento

def main():
    st.set_page_config(page_title="Alie Chat", layout="wide")
    st.title("Olá, sou a Alie!")
    
    # Estilo CSS para mensagens, botões e campo de entrada
    st.markdown("""
        <style>
        /* Estilo geral para mensagens */
        .message-container {
            margin-bottom: 10px;
            padding: 12px;
            border-radius: 12px;
            max-width: 80%;
            word-wrap: break-word;
        }
        /* Mensagem do usuário (light mode) */
        .user-message-light {
            background-color: #e6f3ff;
            color: #1a1a1a;
            margin-left: auto;
            border: 1px solid #b3d4fc;
        }
        /* Mensagem do assistente (light mode) */
        .assistant-message-light {
            background-color: #f0f0f0;
            color: #1a1a1a;
            margin-right: auto;
            border: 1px solid #d9d9d9;
        }
        /* Mensagem do usuário (dark mode) */
        .user-message-dark {
            background-color: #4a6fa5;
            color: #ffffff;
            margin-left: auto;
            border: 1px solid #6b93d6;
        }
        /* Mensagem do assistente (dark mode) */
        .assistant-message-dark {
            background-color: #2a2a2a;
            color: #ffffff;
            margin-right: auto;
            border: 1px solid #4a4a4a;
        }
        /* Estilo para botões */
        .stButton>button {
            border-radius: 8px;
            padding: 8px 16px;
            margin-right: 10px;
        }
        /* Estilo para o campo de texto */
        .stTextInput input {
            border-radius: 8px;
            padding: 10px;
            border: 1px solid #d9d9d9;
            width: 100%;
        }
        /* Detectar modo dark/light */
        @media (prefers-color-scheme: dark) {
            .user-message {
                background-color: #4a6fa5;
                color: #ffffff;
                border: 1px solid #6b93d6;
            }
            .assistant-message {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #4a4a4a;
            }
            .stTextInput input {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #4a4a4a;
            }
        }
        @media (prefers-color-scheme: light) {
            .user-message {
                background-color: #e6f3ff;
                color: #1a1a1a;
                border: 1px solid #b3d4fc;
            }
            .assistant-message {
                background-color: #f0f0f0;
                color: #1a1a1a;
                border: 1px solid #d9d9d9;
            }
            .stTextInput input {
                background-color: #ffffff;
                color: #1a1a1a;
                border: 1px solid #d9d9d9;
            }
        }
        /* Contêiner de mensagens (somente visível quando há mensagens) */
        .chat-messages-container {
            overflow-y: auto;
            padding: 10px;
            margin-bottom: 10px;
            max-height: 60vh;
            border: 1px solid #d9d9d9;
            border-radius: 8px;
            background-color: #fafafa;
        }
        /* Layout para input e botões */
        .input-button-row {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 0;
        }
        @media (prefers-color-scheme: dark) {
            .chat-messages-container {
                border: 1px solid #4a4a4a;
                background-color: #1a1a1a;
            }
        }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.header("Escolha uma opção:")
    opcoes = ["Carregar site", "Carregar vídeo do YouTube"]
    opcao = st.sidebar.radio("Escolha Site ou YouTube", opcoes)
    
    if opcao == "Carregar site":
        url_site = st.text_input('Digite a URL do site:')
        if url_site:
            documento = carrega_site(url_site)
            st.write("Conteúdo do site carregado com sucesso!")
    
    elif opcao == "Carregar vídeo do YouTube":
        url_youtube = st.text_input('Digite a URL do vídeo do YouTube:')
        if url_youtube:
            documento = carrega_youtube(url_youtube)
            st.write("Conteúdo do vídeo carregado com sucesso!")
    
    # Caso o documento não tenha sido carregado, inicializa uma string vazia
    if 'documento' not in locals():
        documento = ''

    # Inicializar mensagens no session_state
    if 'mensagens' not in st.session_state:
        st.session_state['mensagens'] = []
    
    # Inicializar o estado do campo de entrada
    if 'pergunta' not in st.session_state:
        st.session_state['pergunta'] = ""

    # Contêiner principal
    with st.container():
        # Mostrar o contêiner de mensagens somente se houver mensagens
        if st.session_state['mensagens']:
            st.markdown('<div class="chat-messages-container">', unsafe_allow_html=True)
            for i, msg in enumerate(st.session_state['mensagens']):
                if msg[0] == 'user':
                    st.markdown(f"""
                        <div class="message-container user-message">
                            <strong>Você:</strong> {msg[1]}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class="message-container assistant-message">
                            <strong>Alie:</strong> {msg[1]}
                        </div>
                        """, unsafe_allow_html=True)
            # Auto-rolagem para a última mensagem
            st.markdown("""
                <script>
                    const chatContainer = document.querySelector('.chat-messages-container');
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                </script>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Campo de entrada e botões (aparece abaixo do campo de URL ou das mensagens)
        st.markdown('<div class="input-button-row">', unsafe_allow_html=True)
        pergunta_key = f"pergunta_input_{len(st.session_state['mensagens'])}"
        st.text_input(
            "",
            value=st.session_state['pergunta'],
            key=pergunta_key,
            placeholder="Converse aqui",
            on_change=lambda: st.session_state.update(pergunta=st.session_state[pergunta_key])
        )
        
        # Botões "Enviar" e "Encerrar conversa"
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Enviar"):
                if st.session_state['pergunta']:
                    st.session_state['mensagens'].append(('user', st.session_state['pergunta']))
                    resposta = resposta_bot(st.session_state['mensagens'], documento)
                    st.session_state['mensagens'].append(('assistant', resposta))
                    st.session_state['pergunta'] = ""
                    st.rerun()
        with col2:
            if st.button("Encerrar conversa"):
                st.session_state['mensagens'] = []
                st.session_state['pergunta'] = ""
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
