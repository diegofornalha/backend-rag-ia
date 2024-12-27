@app.get("/api/v1/documents/check/{document_hash}")
async def check_document(document_hash: str):
    """Verifica se um documento já existe baseado no hash."""
    try:
        # Consulta o Supabase
        response = supabase.table("documents").select("id").eq("document_hash", document_hash).execute()
        
        # Se encontrou algum documento, retorna 200
        if len(response.data) > 0:
            return {"exists": True, "message": "Documento já existe"}
        
        # Se não encontrou, retorna 404
        return JSONResponse(
            status_code=404,
            content={"exists": False, "message": "Documento não encontrado"}
        )
    except Exception as e:
        logger.error(f"Erro ao verificar documento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 

@app.post("/api/v1/documents/")
async def add_document(document: Document):
    try:
        # Extrai o document_hash dos metadados
        document_hash = document.metadata.get("document_hash")
        
        # Verifica se já existe um documento com este hash
        if document_hash:
            existing = supabase.table("documents").select("id").eq("document_hash", document_hash).execute()
            if len(existing.data) > 0:
                return JSONResponse(
                    status_code=409,  # Conflict
                    content={"message": "Documento já existe"}
                )
        
        # Gera o embedding
        embedding = model.get_embedding(document.content)
        
        # Prepara os dados para inserção
        data = {
            "content": document.content,
            "metadata": document.metadata,
            "embedding": embedding,
            "document_hash": document_hash  # Adiciona o hash
        }
        
        # Insere no Supabase
        response = supabase.table("documents").insert(data).execute()
        
        return response.data[0]
        
    except Exception as e:
        logger.error(f"Erro ao adicionar documento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 