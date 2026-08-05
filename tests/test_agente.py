import sys
import os
import pytest

# Adiciona o diretório 'src' ao caminho do sistema para permitir a importação do main.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from agente_rag import iniciar_agente_animal_pets

@pytest.fixture(scope="module")
def agente_rag():
    """Fixture que inicializa o agente RAG apenas uma vez para todos os testes."""
    return iniciar_agente_animal_pets()

def test_inicializacao_do_agente(agente_rag):
    """Garante que a cadeia RAG foi montada com sucesso e não está vazia."""
    assert agente_rag is not None

def test_resposta_pergunta_valida(agente_rag):
    """Valida se o agente retorna uma string não vazia para uma pergunta padrão."""
    pergunta = "Qual tipo de Pets vocês aceitam?"
    resposta = agente_rag.invoke(pergunta)
    
    assert isinstance(resposta, str)
    assert len(resposta) > 0
