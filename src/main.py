import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Carrega a chave do arquivo .env
load_dotenv()

def iniciar_agente_animal_pets():
    # Define o caminho para o seu PDF de FAQ dentro da pasta data
    caminho_pdf = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "Perguntas Frequentes (FAQ) - Animal Pets.pdf"))
    
    if not os.path.exists(caminho_pdf):
        raise FileNotFoundError(f"⚠️ PDF não encontrado em: {caminho_pdf}")

    # 1. Carrega o conteúdo do PDF da Animal Pets
    loader = PyPDFLoader(caminho_pdf)
    documentos = loader.load()
    
    # 2. Divide o texto em blocos menores (chunks) para melhor contexto
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
    fragmentos = text_splitter.split_documents(documentos)
    
    # 3. Cria os Embeddings usando o modelo oficial do Google
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    
    # 4. Armazena os fragmentos temporariamente em um banco de vetores em memória
    banco_vetores = Chroma.from_documents(fragmentos, embeddings)
    retriever = banco_vetores.as_retriever(search_kwargs={"k": 3})
    
    # 5. Configura o modelo de linguagem (Gemini 1.5 Flash)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)
    
    # Prompt personalizado alinhado ao negócio da Animal Pets
    system_prompt = (
        "Você é um assistente de atendimento virtual prestativo, educado e empático da empresa Animal Pets.\n"
        "Sua missão é ajudar os clientes respondendo às dúvidas com base estrita no FAQ fornecido.\n"
        "Regras cruciais:\n"
        "1. Use apenas as informações do contexto abaixo para responder.\n"
        "2. Se a informação não estiver no contexto, responda: 'Desculpe, não encontrei essa informação no meu manual. Por favor, entre em contato com nosso suporte humano para que possamos te ajudar melhor!'\n"
        "3. Nunca invente dados, telefones ou políticas que não estejam descritas no texto.\n\n"
        "FAQ / Contexto:\n{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    # Junta o buscador de PDF ao cérebro da IA
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    return rag_chain

if __name__ == "__main__":
    print("🤖 Carregando a base de conhecimento da Animal Pets...")
    try:
        agente = iniciar_agente_animal_pets()
        print("✅ Agente Animal Pets online e pronto para o atendimento!")
        
        while True:
            pergunta = input("\nCliente: ")
            if pergunta.lower() in ['sair', 'fechar', 'exit']:
                print("Atendimento encerrado. A Animal Pets agradece o contato!")
                break
                
            if not pergunta.strip():
                continue
                
            print("🤖 Processando resposta...")
            resposta = agente.invoke({"input": pergunta})
            print(f"\nAgente Animal Pets: {resposta['answer']}")
            
    except Exception as e:
        print(f"\n❌ Ocorreu um erro ao iniciar o agente: {e}")
