import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Carrega as chaves do arquivo .env
load_dotenv()

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def iniciar_agente_animal_pets():
    # Caminho do PDF dentro da pasta data
    caminho_pdf = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "Perguntas Frequentes (FAQ) - Animal Pets.pdf"))
    
    if not os.path.exists(caminho_pdf):
        raise FileNotFoundError(f"⚠️ PDF não encontrado em: {caminho_pdf}")

    # 1. Carrega o conteúdo do PDF da Animal Pets
    loader = PyPDFLoader(caminho_pdf)
    documentos = loader.load()
    
    # 2. Divide o texto em blocos menores (chunks)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    fragmentos = text_splitter.split_documents(documentos)
    
    # 3. Embeddings locais open-source (BAAI)
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    
    # 4. Armazena temporariamente no banco de vetores ChromaDB
    banco_vetores = Chroma.from_documents(fragmentos, embeddings)
    retriever = banco_vetores.as_retriever(search_kwargs={"k": 3})
    
    # 5. Configura o modelo de linguagem ultra rápido da Groq (Llama 3 8B)
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)
    
    # Prompt de atendimento da Animal Pets
    system_prompt = (
        "Você é um assistente de atendimento virtual prestativo, educado e empático da empresa Animal Pets.\n"
        "Sua missão é ajudar os clientes respondendo às dúvidas com base estrita no FAQ fornecido.\n"
        "Regras cruciais:\n"
        "1. Use apenas as informações do contexto abaixo para responder.\n"
        "2. Se a informação não estiver no contexto, responda exatamente: 'Desculpe, não encontrei essa informação no meu manual. Por favor, entre em contato com nosso suporte humano para que possamos te ajudar melhor!'\n"
        "3. Nunca invente dados, telefones ou políticas que não estejam descritas no texto.\n\n"
        "FAQ / Contexto:\n{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    # 6. Pipeline moderna LCEL
    rag_chain = (
        {"context": retriever | format_docs, "input": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain

if __name__ == "__main__":
    print("🤖 Carregando a base de conhecimento da Animal Pets via Groq...")
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
            resposta = agente.invoke(pergunta)
            print(f"\nAgente Animal Pets: {resposta}")
            
    except Exception as e:
        print(f"\n❌ Ocorreu um erro ao iniciar o agente: {e}")
