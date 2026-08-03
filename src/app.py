import streamlit as st
from main import iniciar_agente_animal_pets

# Configuração da página do navegador
st.set_page_config(page_title="Assistente Animal Pets", page_icon="🐾", layout="centered")

st.title("🐾 Atendimento Virtual - Animal Pets")
st.write("Bem-vindo ao canal de suporte inteligente da Animal Pets. Faça sua pergunta abaixo!")

# Inicializa o agente na sessão do Streamlit para não reprocessar o PDF a cada clique
if "agente" not in st.session_state:
    with st.spinner("🤖 Carregando base de conhecimento e inicializando agente..."):
        try:
            st.session_state.agente = iniciar_agente_animal_pets()
            st.success("✅ Agente pronto para atendimento!")
        except Exception as e:
            st.error(f"Erro ao carregar o agente: {e}")

# Inicializa o histórico de mensagens na tela
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe as mensagens anteriores do chat na tela
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Caixa de entrada para a pergunta do usuário
if prompt := st.chat_input("Digite sua dúvida aqui..."):
    # Exibe a pergunta do usuário na tela
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gera a resposta usando o nosso agente RAG
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                resposta = st.session_state.agente.invoke(prompt)
                st.markdown(resposta)
                # Salva a resposta no histórico
                st.session_state.messages.append({"role": "assistant", "content": resposta})
            except Exception as e:
                st.error(f"Erro ao processar a resposta: {e}")
