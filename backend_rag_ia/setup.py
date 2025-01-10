from setuptools import setup, find_packages

setup(
    name="backend_rag_ia",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "python-dotenv>=1.0.0",
        "langchain>=0.0.350",
        "supabase>=2.3.0",
        "pydantic>=2.5.2",
        "sqlalchemy>=2.0.23",
        "google-generativeai>=0.3.0",
        "sentence-transformers>=2.2.2"
    ],
) 