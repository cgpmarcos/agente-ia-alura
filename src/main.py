import os
import glob
import time
from google import genai
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Inicializa o cliente do Gemini
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

print("🔍 Buscando PDFs na pasta data/...")
arquivos_pdf = glob.glob("data/*.pdf")

if not arquivos_pdf:
    print("❌ Erro: Nenhum arquivo PDF foi encontrado dentro da pasta data/.")
else:
    caminho_pdf = arquivos_pdf[0]
    print(f"📄 Arquivo base encontrado: {caminho_pdf}")
    print("☁️ Carregando conhecimento na API do Gemini...")
    
    # Faz o upload do PDF para a API do Gemini
    arquivo_ia = client.files.upload(file=caminho_pdf)
    
    # Aguarda o processamento concluir
    while arquivo_ia.state.name == "PROCESSING":
        time.sleep(2)
        arquivo_ia = client.files.get(name=arquivo_ia.name)
        
    print("✨ Conhecimento carregado com sucesso!")
    print("\n🤖 Agente de IA Online! Digite 'sair' para encerrar o chat.")
    print("--------------------------------------------------")
    
    # Loop de conversação contínua
    while True:
        pergunta = input("\n👤 Você: ")
        
        # Condição de parada do loop
        if pergunta.strip().lower() == "sair":
            print("\n🤖 Agente: Até logo! Encerrando sessão...")
            break
            
        if not pergunta.strip():
            continue
            
        print("🤖 Agente pensando...")
        
        # Envia o arquivo e a pergunta do usuário
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                arquivo_ia, 
                f"Você é um assistente virtual público. Responda à pergunta do usuário utilizando estritamente as informações contidas no documento fornecido. Se a resposta não estiver no documento, diga educadamente que não possui essa informação.\n\nPergunta: {pergunta}"
            ]
        )
        
        print(f"\n🤖 Agente: {response.text}")
        print("-" * 50)
        
    # Limpeza do arquivo após fechar o programa
    client.files.delete(name=arquivo_ia.name)
    print("\n🧹 Limpeza de cache concluída. Sistema encerrado com segurança.")
