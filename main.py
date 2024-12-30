from backend_rag_ia.app import app

# Exporta a aplicação para ser usada pelo uvicorn
__all__ = ['app']

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000) 