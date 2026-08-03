# 🐾 Assistente Virtual de Atendimento - Animal Pets

Este projeto foi desenvolvido como parte do **Challenge Alura Agente**. Trata-se de um assistente de atendimento virtual inteligente baseado na arquitetura **RAG (Retrieval-Augmented Generation)**, capaz de analisar uma base de conhecimento corporativa (FAQ em PDF) e responder a dúvidas de clientes de forma automatizada, empática e contextualizada.

---

## 🏗️ Arquitetura do Projeto

A solução utiliza técnicas modernas de inteligência artificial generativa e engenharia de prompts:
1. **Base de Conhecimento:** Documento oficial de perguntas frequentes em formato PDF localizado na pasta `data/`.
2. **Processamento de Dados:** Divisão do texto em fragmentos lógicos (text chunks) utilizando o `RecursiveCharacterTextSplitter`.
3. **Embeddings Locais:** Geração de vetores semânticos com o modelo open-source leve `BAAI/bge-small-en-v1.5` via HuggingFace, garantindo eficiência de memória na nuvem.
4. **Banco de Vetores:** Armazenamento e busca por similaridade de alta performance utilizando o `ChromaDB`.
5. **Orquestrador LLM:** Uso de pipelines modernos em cadeia (LCEL) interligados à infraestrutura ultra veloz da **Groq Cloud** rodando o modelo `llama-3.3-70b-versatile`.

---

## 🚀 Como Executar a Aplicação Localmente

### Pré-requisitos
* Python 3.10 ou superior instalado.

### Configuração do Ambiente

1. Clone este repositório para a sua máquina:
   ```bash
   git clone https://github.com
   cd agente-ia-alura
   ```

2. Crie e ative o seu ambiente virtual Python:
   ```bash
   python -m venv .venv
   # No Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   # No Linux/Mac:
   source .venv/bin/activate
   ```

3. Instale todas as dependências do projeto contidas no gerenciador:
   ```bash
   pip install -r requirements.txt
   ```

4. Crie um arquivo chamado `.env` na raiz do projeto e configure a sua chave secreta da API da Groq:
   ```env
   GROQ_API_KEY=gsk_sua_chave_aqui
   ```

### Execução das Interfaces

* **Interface de Linha de Comando (Terminal):**
  ```bash
  python src/main.py
   ```

* **Interface Gráfica (Streamlit no Navegador):**
  ```bash
  streamlit run src/app.py
  ```

---

## 🧪 Testes Automatizados

O projeto conta com uma suíte de testes unitários para garantir a confiabilidade da inicialização da IA e a integridade do formato de saída das respostas. Para executá-los, use o comando:

```bash
pytest tests/
```

---

## ☁️ Deploy em Nuvem (Oracle Cloud Infrastructure - OCI)

A aplicação foi projetada de forma otimizada para o ambiente Always Free da **Oracle Cloud (OCI)**, permitindo execução contínua com consumo mínimo de recursos computacionais graças à hibridização de chamadas via API de texto e embeddings locais eficientes.

![Demonstração da Interface](data/print_interface.png)

