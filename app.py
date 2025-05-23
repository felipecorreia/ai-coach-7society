import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Configuração da página
st.set_page_config(
    page_title="Professor Ronald",
    page_icon=":robot:",
    layout="centered",
)

load_dotenv()

#genai.configure(api_key=os.getenv("GENAI_API_KEY"))
genai.configure(api_key=st.secrets.get("GENAI_API_KEY", os.getenv("GENAI_API_KEY")))
model = genai.GenerativeModel('gemini-2.0-flash')




# Título da aplicação
st.title("Professor Bola Gringa - English coach")
st.subheader("Aprimore seu inglês com a ajuda do professor virtual da 7 Society")



# Configuração do tema
st.markdown("""
<style>
    /* Fundo geral - branco limpo */
    .stApp {
        background-color: #ffffff !important;
    }
    
    /* Títulos principais */
    h1 {
        color: #1565c0 !important;
        text-align: center !important;
        font-weight: 600 !important;
    }
    
    /* Subtítulos */
    h2, h3 {
        color: #1976d2 !important;
        font-weight: 500 !important;
    }
    
    /* Texto geral */
    .stMarkdown, p, span {
        color: #424242 !important;
    }
    
    /* === ÁREA DO CHAT === */
    
    /* Container das mensagens */
    .stChatMessage {
        background-color: #ffffff !important;
        border: 1px solid #e3f2fd !important;
        border-radius: 12px !important;
        padding: 16px !important;
        margin: 10px 0 !important;
        box-shadow: 0 1px 3px rgba(21, 101, 192, 0.08) !important;
    }
    
    /* Mensagens do usuário */
    .stChatMessage[data-testid="user-message"] {
        background-color: #f3f8ff !important;
        border: 1px solid #bbdefb !important;
        color: #1565c0 !important;
    }
    
    /* Mensagens do assistente */
    .stChatMessage[data-testid="assistant-message"] {
        background-color: #ffffff !important;
        border: 1px solid #e8eaf6 !important;
        color: #2c3e50 !important;
    }
    
    /* Input do chat */
    .stChatInput > div > div {
        background-color: #ffffff !important;
        border: 2px solid #e3f2fd !important;
        border-radius: 25px !important;
    }
    
    .stChatInput input {
        color: #1565c0 !important;
        background-color: #ffffff !important;
    }
    
    .stChatInput input::placeholder {
        color: #90a4ae !important;
    }
    
    /* Seletores adicionais para forçar cor do input */
    div[data-testid="stChatInput"] input {
        color: #1565c0 !important;
        background-color: #ffffff !important;
    }
    
    div[data-testid="stChatInput"] > div > div > input {
        color: #1565c0 !important;
        background-color: #ffffff !important;
    }
    
    /* Forçar cor quando focado */
    .stChatInput input:focus {
        color: #1565c0 !important;
        background-color: #ffffff !important;
    }
    
    /* === FORMULÁRIOS === */
    
    /* Container do formulário */
    .stForm {
        background-color: #ffffff !important;
        border: 1px solid #e3f2fd !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: 0 2px 4px rgba(21, 101, 192, 0.05) !important;
    }
    
    /* Labels dos campos */
    .stForm label {
        color: #1565c0 !important;
        font-weight: 500 !important;
    }
    
    /* Campos de texto */
    .stTextInput > div > div > input {
        background-color: #ffffff !important;
        border: 2px solid #e3f2fd !important;
        border-radius: 8px !important;
        color: #1565c0 !important;
        padding: 12px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #1976d2 !important;
        box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1) !important;
    }
    
    .stTextInput input::placeholder {
        color: #90a4ae !important;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background-color: #ffffff !important;
        border: 2px solid #e3f2fd !important;
        border-radius: 8px !important;
    }
    
    .stSelectbox > div > div > div {
        color: #1565c0 !important;
    }
    
    /* Dropdown do selectbox */
    .stSelectbox [data-baseweb="select"] {
        border: 2px solid #e3f2fd !important;
    }
    
    .stSelectbox [data-baseweb="select"]:hover {
        border-color: #1976d2 !important;
    }
    
    /* Opções do dropdown */
    .stSelectbox [role="option"] {
        background-color: #ffffff !important;
        color: #1565c0 !important;
    }
    
    .stSelectbox [role="option"]:hover {
        background-color: #f3f8ff !important;
    }
    
    /* === BOTÕES === */
    
    /* Botão principal do formulário */
    .stForm .stButton > button {
        background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 4px rgba(21, 101, 192, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    
    .stForm .stButton > button:hover {
        background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(21, 101, 192, 0.3) !important;
    }
    
    /* Botão limpar conversa */
    .stButton > button {
        background-color: #ffffff !important;
        color: #1976d2 !important;
        border: 2px solid #e3f2fd !important;
        border-radius: 20px !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
    }
    
    .stButton > button:hover {
        background-color: #f3f8ff !important;
        border-color: #1976d2 !important;
        color: #1565c0 !important;
    }
    
    /* === SIDEBAR (se houver) === */
    .stSidebar {
        background-color: #fafafa !important;
        border-right: 1px solid #e3f2fd !important;
    }
    
    .stSidebar .stMarkdown {
        color: #1565c0 !important;
    }
    
    /* === SPINNER DE CARREGAMENTO === */
    .stSpinner > div {
        border-color: #1976d2 transparent transparent transparent !important;
    }
    
    /* === ELEMENTOS ESPECIAIS === */
    
    /* Emojis e ícones mantêm cor natural */
    .emoji {
        filter: none !important;
    }
    
    /* Links */
    a {
        color: #1976d2 !important;
        text-decoration: none !important;
    }
    
    a:hover {
        color: #1565c0 !important;
        text-decoration: underline !important;
    }
</style>
""", unsafe_allow_html=True)

def collect_user_info():
    st.title("⚽ Olá, tudo bem? Eu sou o professor de inglês virtual da 7 Society!")
    
    with st.form("user_info"):
        st.subheader("Vamos nos conhecer melhor")
        name = st.text_input("Qual seu nome?", placeholder="Ex: Ronaldo")
        
        position = st.selectbox(
            "Qual posição você joga?",
            ["Goleiro", "Zagueiro", "Lateral", "Volante", 
             "Meia", "Atacante", "Não jogo, só assisto"]
        )
        
        english_level = st.selectbox(
            "Qual seu nível de inglês?",
            ["Iniciante", "Intermediário", "Avançado"]
        )
        
        submitted = st.form_submit_button("Começar! ⚽")
        
        if submitted and name:
            st.session_state.user_name = name
            st.session_state.user_position = position
            st.session_state.english_level = english_level
            st.session_state.user_setup = True
            st.rerun()

def get_response(message):
    # Definição de especialidade do ai coach - MOVIDA PARA DENTRO DA FUNÇÃO
    especialidade = f"""
    Antes de gerar qualquer resposta ao usuário, siga estritamente estas etapas de pensamento. Estes passos são internos e não devem aparecer na resposta final, apenas o resultado do Passo 8.
    Você é um especialista em ensinar FUTEBOL EM INGLÊS para falantes de português brasileiro.

    INFORMAÇÕES DO USUÁRIO:
    - Nome: {st.session_state.get('user_name', 'Amigo')}
    - Posição: {st.session_state.get('user_position', 'Jogador')}
    - Nível de Inglês: {st.session_state.get('english_level', 'Intermediário')}

    SUAS RESPONSABILIDADES:
    - Ensinar vocabulário de futebol em inglês
    - Explicar táticas e regras em inglês
    - Adaptar linguagem ao nível do usuário
    - Sempre dar exemplos práticos de uso
    - Corrigir erros de inglês gentilmente
    - Usar referências do futebol brasileiro/internacional

    FORMATO DAS RESPOSTAS:
    - Sempre em português E inglês
    - Vocabulário específico destacado
    - Exemplos com jogadores famosos
    - Sugestões de prática

    Passo 8: Format final response in character.
    Resposta Final Gerada (após o processo CoT interno):
    "Hey there, future football star! Let's learn about 'GOAL'! 🥅⚽
    A 'goal' in football is super important! It's when the ball goes all the way inside the net, like this: 👉⚽🥅💥 GOAL!
    When you score a 'goal', your team gets a point! That's how you win the game! The big white thing with the net where the ball goes in? That's called the 'goal' too!
    My favorite thing when I played in the USA was scoring a beautiful 'goal'! It made the fans go crazy! 🎉
    So, remember: ball in the net = GOAL! Got it? Awesome! What football word do you want to learn next?"
    Observação: Se a pergunta do usuário não tiver relação com futebol, o agente deve gentilmente redirecionar para o tema, mantendo a persona. Ex: "Ah, that's interesting! But here, we talk football and English! Do you want to learn the English word for 'bola' ou 'campo'? Let's do it!"
    Esta instrução CoT detalha o processo de pensamento interno que o agente deve seguir, garantindo que ele sempre adote a persona, conecte o tópico ao futebol, simplifique a linguagem e entregue a resposta final no estilo do Professor Bola Gringa, sem mostrar os passos internos ao usuário.
    """
    
    try:
        prompt = f"{especialidade}\n\nPergunta do usuário: {message}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Desculpe, houve um erro: {str(e)}. Tente novamente."

# Usar no fluxo principal
if "user_setup" not in st.session_state:
    collect_user_info()
else:
    # Botão para limpar histórico
    if st.button("🗑️ Limpar Conversa"):
        st.session_state.messages = []
        st.rerun()

    # Inicializar histórico de mensagens
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar histórico de mensagens
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input do usuário
    if prompt := st.chat_input("Digite sua pergunta aqui..."):
        # Adicionar mensagem do usuário ao histórico
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Gerar resposta
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                response = get_response(prompt)
                st.markdown(response)
        
        # Adicionar resposta ao histórico
        st.session_state.messages.append({"role": "assistant", "content": response})