import os
import glob
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Carregar variáveis de ambiente
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY não encontrado no arquivo .env")

# Inicializa o cliente oficial da SDK v1
client = genai.Client(api_key=API_KEY, http_options={'api_version': 'v1'})

# 2. Buscar PDFs e fazer o upload nativo para a API do Gemini
print("🔍 Buscando PDFs na pasta data/...")
# Ajustado para "../data/*.pdf" caso sua pasta data esteja na raiz e o script em src/
arquivos_pdf = glob.glob("data/*.pdf") or glob.glob("../data/*.pdf")

uploaded_files = []

if not arquivos_pdf:
    print("❌ Erro: Nenhum arquivo PDF foi encontrado.")
else:
    print(f"📚 Encontrados {len(arquivos_pdf)} arquivos de conhecimento.")
    print("🚀 Fazendo upload dos documentos para a API do Gemini (Gerenciamento nativo)...")

    for caminho_pdf in arquivos_pdf:
        try:
            # Faz o upload do arquivo diretamente para os servidores do Gemini
            print(f"Enviando: {caminho_pdf}...")
            file_ref = client.files.upload(file=caminho_pdf)
            uploaded_files.append(file_ref)
            
            # Aguarda o processamento interno do arquivo pelo Google
            while file_ref.state.name == "PROCESSING":
                print(".", end="", flush=True)
                time.sleep(2)
                file_ref = client.files.get(name=file_ref.name)
            
            if file_ref.state.name == "FAILED":
                print(f"\n❌ Falha ao processar o arquivo no servidor: {caminho_pdf}")
            else:
                print(f"\n✅ Arquivo pronto no servidor: {file_ref.display_name}")
                
        except Exception as e:
            print(f"\n⚠️ Erro ao enviar o arquivo {caminho_pdf}: {e}")

    print("✨ Todo o conhecimento foi indexado com sucesso!")
    print("\n🤖 Agente de IA Online! Digite 'sair' para encerrar o chat.")
    print("--------------------------------------------------")

       # 3. Criar a sessão do Chat passando as referências dos arquivos e instruções
    chat = client.chats.create(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=(
                "Você é um assistente virtual público para a loja Animal Pets. "
                "Responda à pergunta do usuário utilizando estritamente as informações "
                "contidas nos documentos anexados a este chat. Se a resposta não estiver "
                "nos arquivos, responda educadamente que não possui essa informação."
            )
        ),
        # CORREÇÃO AQUI: Passando file_uri como parâmetro nomeado correto da SDK nova
        history=[
            types.Content(
                role="user",
                parts=[types.Part.from_uri(file_uri=file.uri) for file in uploaded_files]
            )
        ]
    )


    # 4. Loop de conversação no terminal
    while True:
        pergunta = input("\n👤 Você: ")
        
        if pergunta.lower().strip() == 'sair':
            print("👋 Encerrando o chat. Até logo!")
            # Opcional: Limpar os arquivos do servidor ao sair para organizar seu painel
            for file in uploaded_files:
                try:
                    client.files.delete(name=file.name)
                except:
                    pass
            break
            
        if not pergunta.strip():
            continue

        try:
            resposta = chat.send_message(pergunta)
            print(f"\n🤖 Animal Pets: {resposta.text}")
        except Exception as e:
            print(f"\n⚠️ Erro ao gerar resposta: {e}")
