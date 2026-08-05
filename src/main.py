import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, UnstructuredMarkdownLoader
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
    """Formata os documentos recuperados unindo seus conteúdos com quebras de linha."""
    return "\n\n".join(doc.page_content for doc in docs)

def iniciar_agente_animal_pets():
    # Caminho da PASTA data onde ficam os PDFs e arquivos Markdown
    caminho_pasta_data = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    
    if not os.path.exists(caminho_pasta_data):
        raise FileNotFoundError(f"⚠️ Pasta de dados não encontrada em: {caminho_pasta_data}")

    documentos = []
    
    print("📂 Carregando arquivos da pasta data:")
    # Varre a pasta carregando cada arquivo com o leitor correto conforme a extensão
    for arquivo in os.listdir(caminho_pasta_data):
        caminho_completo = os.path.join(caminho_pasta_data, arquivo)
        nome_minusculo = arquivo.lower()
        
        # Processamento de arquivos PDF
        if nome_minusculo.endswith('.pdf'):
            try:
                loader = PyPDFLoader(caminho_completo)
                documentos.extend(loader.load())
                print(f"  ✅ PDF lido com sucesso: {arquivo}")
            except Exception as e:
                print(f"  ❌ Erro ao ler o PDF {arquivo}: {e}")
                
        # Processamento de arquivos Markdown (Tabelas de Preços estruturadas)
        elif nome_minusculo.endswith('.md'):
            try:
                loader = UnstructuredMarkdownLoader(caminho_completo)
                documentos.extend(loader.load())
                print(f"  🎯 Markdown lido com sucesso: {arquivo}")
            except Exception as e:
                print(f"  ❌ Erro ao ler o Markdown {arquivo}: {e}")
                
    if not documentos:
        raise ValueError(f"⚠️ Nenhum conteúdo pôde ser extraído dos arquivos na pasta: {caminho_pasta_data}")
    
    # 2. Divide o texto em blocos menores (chunks) - Tamanho ideal para misturar textos e tabelas
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=150)
    fragmentos = text_splitter.split_documents(documentos)
    
    # 3. Embeddings locais open-source (BAAI)
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    
    # 4. Armazena temporariamente no banco de vetores ChromaDB
    banco_vetores = Chroma.from_documents(fragmentos, embeddings)
    
    # Recupera até 7 blocos de contexto para garantir respostas completas
    retriever = banco_vetores.as_retriever(search_kwargs={"k": 7}) 
    
    # 5. Configura o modelo de linguagem da Groq (Llama 3.3 70B) com baixa temperatura para precisão
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)
    
    # Prompt de atendimento rigoroso da Animal Pets
    system_prompt = (
        "Você é um assistente de atendimento virtual prestativo, educado e empático da empresa Animal Pets.\n"
        "Sua missão é ajudar os clientes respondendo às dúvidas com base estrita nos documentos fornecidos.\n"
        "Regras cruciais:\n"
        "1. Use as informações do contexto fornecido para responder de forma clara.\n"
        "2. Se a informação realmente não estiver descrita em nenhum dos manuais ou tabelas de preços, responda exatamente: "
        "'Desculpe, não encontrei essa informação no meu manual. Por favor, entre em contato com nosso suporte humano para que possamos te ajudar melhor!'\n"
        "3. Nunca invente dados, valores ou políticas que não estejam descritas no texto.\n\n"
        "Documentos Integrados / Contexto:\n{context}"
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
    print("🤖 Inicializando a base de conhecimento híbrida (PDF/MD) da Animal Pets...")
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
