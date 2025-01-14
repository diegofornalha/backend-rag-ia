# Documentação Ragie - Listagem de Documentos

Este documento descreve as diferentes formas de listar documentos do Ragie disponíveis no projeto.

## 1. Interface Web

A interface web oferece uma visualização gráfica dos documentos com recursos interativos.

**Características:**

- Interface gráfica amigável
- Possibilidade de clicar nos IDs para focar a conversa
- Visualização dos modelos disponíveis (Groq, Gemini)
- Exibição de metadados formatados

**Localização:** `/app/(chat)/page.tsx`

## 2. CLI - Opções Disponíveis

### 2.1 Python com Rich (list_documents.py)

```bash
cd /Users/flow/Desktop/Desktop/backend && export NEXT_PUBLIC_RAGIE_API_KEY=YOUR_API_KEY && python3 list_documents.py
```

**Características:**

- Formatação colorida e tabular usando Rich
- Fácil de ler e manter
- Saída bem estruturada
- Ideal para uso em terminal

**Localização:** `/list_documents.py`

### 2.2 Python com LangChain (ragie-langchain.py)

```bash
export NEXT_PUBLIC_RAGIE_API_KEY=YOUR_API_KEY && python3 src/cli/ragie-langchain.py
```

**Características:**

- Integração com o ecossistema LangChain
- Suporte a recuperação semântica
- Ideal para projetos de RAG (Retrieval Augmented Generation)
- Permite encadear com outros componentes do LangChain

**Instalação:**

```bash
pip install langchain-ragie
```

**Localização:** `/src/cli/ragie-langchain.py`

### 2.3 TypeScript com SDK Oficial (ragie-monitor.ts)

```bash
export NEXT_PUBLIC_RAGIE_API_KEY=YOUR_API_KEY && tsx src/cli/ragie-monitor.ts list
```

**Características:**

- Usa o SDK oficial do Ragie
- Tipagem forte com TypeScript
- Integração nativa com a API
- Melhor para projetos TypeScript

**Localização:** `/src/cli/ragie-monitor.ts`

### 2.4 TypeScript com Fetch (ragie-fetch.ts)

```bash
export NEXT_PUBLIC_RAGIE_API_KEY=YOUR_API_KEY && tsx src/cli/ragie-fetch.ts list
```

**Características:**

- Implementação leve usando Fetch nativo
- Sem dependências extras
- Boa para entender a API
- Ideal para projetos pequenos

**Localização:** `/src/cli/ragie-fetch.ts`

### 2.5 TypeScript com Axios (ragie-axios.ts)

```bash
export NEXT_PUBLIC_RAGIE_API_KEY=YOUR_API_KEY && tsx src/cli/ragie-axios.ts list
```

**Características:**

- Usa Axios para requisições HTTP
- Melhor tratamento de erros
- Interceptors disponíveis
- Ideal para projetos maiores

**Localização:** `/src/cli/ragie-axios.ts`

## Estrutura dos Documentos

Cada documento contém as seguintes informações:

- **ID**: Identificador único do documento
- **Nome**: Nome do arquivo
- **Status**: Estado atual (ex: ready)
- **Chunks**: Número de chunks do documento
- **Escopo**: Categoria/contexto do documento
- **Criado em**: Data de criação
- **Atualizado em**: Data da última atualização
- **Metadata**: Informações adicionais em formato JSON

## Exemplo de Documento

```json
{
  "id": "9557ca8b-4936-4b83-a1c9-5afe95bfbfd1",
  "name": "components.json",
  "status": "ready",
  "chunks": 1,
  "metadata": {
    "scope": "components-config"
  }
}
```

## Comparação das Implementações

| Implementação    | Vantagens                    | Desvantagens     |
| ---------------- | ---------------------------- | ---------------- |
| Interface Web    | Visual, interativa           | Requer navegador |
| Python/Rich      | Formatação bonita, simples   | Requer Python    |
| Python/LangChain | Integração RAG, semântica    | Mais complexo    |
| TS/SDK           | Tipagem forte, oficial       | Mais complexo    |
| TS/Fetch         | Leve, sem deps               | Básico           |
| TS/Axios         | Robusto, tratamento de erros | Mais deps        |

## Configuração

Todas as implementações requerem a variável de ambiente:

```bash
NEXT_PUBLIC_RAGIE_API_KEY=seu_token_aqui
```

## Recomendações de Uso

- **Interface Web**: Para uso diário e interação visual
- **Python/Rich**: Para scripts rápidos e visualização em terminal
- **Python/LangChain**: Para projetos de RAG e busca semântica
- **TS/SDK**: Para integração em projetos TypeScript
- **TS/Fetch**: Para implementações simples
- **TS/Axios**: Para projetos que precisam de mais robustez
