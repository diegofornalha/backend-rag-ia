import os
from langchain_ragie import RagieRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI

# Configurar a chave da API
os.environ["RAGIE_API_KEY"] = os.getenv("NEXT_PUBLIC_RAGIE_API_KEY", "")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")

# Criar o modelo
model = ChatGoogleGenerativeAI(model="gemini-pro")

# Criar o retriever
retriever = RagieRetriever(
    api_key=os.environ["RAGIE_API_KEY"],
    rerank=True,
    limit=3
)

# Template do prompt
template = """Responda a pergunta baseado no contexto fornecido.
Se você não souber a resposta, apenas diga que não sabe.

Contexto: {context}
Pergunta: {question}

Resposta:"""

# Criar o prompt
prompt = ChatPromptTemplate.from_template(template)

# Criar o parser de saída
output_parser = StrOutputParser()

# Montar a chain
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | output_parser
)

# Exemplo de uso
def process_query(query: str) -> str:
    try:
        response = chain.invoke(query)
        return response
    except Exception as e:
        print(f"Erro ao processar a query: {e}")
        return "Desculpe, ocorreu um erro ao processar sua pergunta."

if __name__ == "__main__":
    # Exemplo de uso
    query = "O que é o Ragie?"
    response = process_query(query)
    print(f"\nPergunta: {query}")
    print(f"Resposta: {response}") 