from setuptools import find_packages, setup

setup(
    name="backend_rag_ia",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "python-dotenv>=1.0.0",
        "supabase>=1.0.3",
        "sentence-transformers>=2.2.2",
        "rich>=13.4.2",
        "numpy>=1.24.3",
    ],
    python_requires=">=3.11",
) 