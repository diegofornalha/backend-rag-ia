"""
Testes de performance para o sistema de embates.
"""

import asyncio
import time
from datetime import datetime

import pytest

from backend_rag_ia.cli.embates.manager import EmbateManager
from backend_rag_ia.cli.embates.models import Embate
from backend_rag_ia.cli.embates.storage import MemoryStorage
from backend_rag_ia.monitoring.metrics import Metrica


@pytest.mark.monitoring
@pytest.mark.asyncio
async def test_create_embate_performance():
    """Testa performance da criação de embates."""
    # Arrange
    manager = EmbateManager()
    embate = create_test_embate()
    
    # Act
    start_time = time.time()
    result = await manager.create_embate(embate)
    end_time = time.time()
    
    # Assert
    duration = end_time - start_time
    assert duration < 1.0  # Deve levar menos de 1 segundo
    assert result["status"] == "success"


@pytest.mark.monitoring
@pytest.mark.asyncio
async def test_search_embates_performance():
    """Testa performance da busca de embates."""
    # Arrange
    manager = EmbateManager()
    
    # Cria alguns embates para buscar
    embates = [
        create_test_embate(
            titulo=f"Teste de Performance {i}",
            contexto=f"Contexto para teste de performance {i}"
        )
        for i in range(10)
    ]
    
    for embate in embates:
        await manager.create_embate(embate)
    
    # Act
    start_time = time.time()
    results = await manager.search_embates("performance")
    end_time = time.time()
    
    # Assert
    duration = end_time - start_time
    assert duration < 2.0  # Deve levar menos de 2 segundos
    assert len(results) > 0


@pytest.mark.monitoring
@pytest.mark.asyncio
async def test_update_embate_performance():
    """Testa performance da atualização de embates."""
    # Arrange
    manager = EmbateManager()
    embate = create_test_embate()
    result = await manager.create_embate(embate)
    embate_id = result["id"]
    
    updates = {
        "titulo": "Teste Atualizado",
        "status": "resolvido"
    }
    
    # Act
    start_time = time.time()
    result = await manager.update_embate(embate_id, updates)
    end_time = time.time()
    
    # Assert
    duration = end_time - start_time
    assert duration < 1.0  # Deve levar menos de 1 segundo
    assert result["status"] == "success"


@pytest.mark.monitoring
@pytest.mark.asyncio
async def test_export_embates_performance():
    """Testa performance da exportação de embates."""
    # Arrange
    manager = EmbateManager()
    
    # Cria alguns embates para exportar
    embates = [
        create_test_embate(
            titulo=f"Teste para Exportação {i}",
            status="aberto"
        )
        for i in range(5)
    ]
    
    for embate in embates:
        await manager.create_embate(embate)
    
    # Act
    start_time = time.time()
    results = await manager.export_embates({"status": "aberto"})
    end_time = time.time()
    
    # Assert
    duration = end_time - start_time
    assert duration < 1.5  # Deve levar menos de 1.5 segundos
    assert len(results) >= 5


@pytest.mark.monitoring
@pytest.mark.asyncio
async def test_concurrent_operations_performance():
    """Testa performance de operações concorrentes."""
    # Arrange
    manager = EmbateManager()
    embates = [
        create_test_embate(
            titulo=f"Teste Concorrente {i}",
            contexto=f"Contexto para teste concorrente {i}"
        )
        for i in range(3)
    ]
    
    # Act
    start_time = time.time()
    
    # Executa operações concorrentemente
    create_tasks = [manager.create_embate(embate) for embate in embates]
    search_task = manager.search_embates("concorrente")
    export_task = manager.export_embates({"status": "aberto"})
    
    # Aguarda todas as operações
    results = await asyncio.gather(
        *create_tasks,
        search_task,
        export_task
    )
    
    end_time = time.time()
    
    # Assert
    duration = end_time - start_time
    assert duration < 3.0  # Deve levar menos de 3 segundos
    
    # Verifica resultados
    create_results = results[:3]
    search_results = results[3]
    export_results = results[4]
    
    assert all(r["status"] == "success" for r in create_results)
    assert len(search_results) > 0
    assert len(export_results) > 0 


@pytest.mark.monitoring
@pytest.mark.asyncio
async def test_continuous_embate_performance():
    """Testa performance do loop contínuo de embates com contenção."""
    # Arrange
    manager = EmbateManager()
    ciclo = 1
    intervencao_manual = False
    
    metrica = Metrica(
        nome="performance_loop",
        valor=1.0,
        timestamp=datetime.now()
    )
    
    # Cria embate sobre storage persistente
    embate_storage = Embate(
        titulo="Implementar Storage Persistente",
        tipo="tecnico",
        contexto="""
        Problema: Buscas e exportações retornando 0 resultados
        Causa: Ausência de storage persistente no ambiente de teste
        Impacto: Impossibilidade de validar completamente o fluxo de dados
        """,
        status="aberto",
        criado_em=datetime.now(),
        argumentos=[]
    )
    
    # Adiciona argumentos técnicos
    embate_storage.argumentos.append({
        "autor": "Sistema",
        "tipo": "tecnico",
        "conteudo": """
        Proposta de Solução:
        1. Implementar storage em memória para testes
        2. Usar SQLite como alternativa leve
        3. Criar mock do Supabase para testes
        """,
        "data": datetime.now()
    })
    
    while not intervencao_manual:
        print(f"\n🔄 Iniciando Ciclo {ciclo} de Performance")
        print("=" * 50)
        
        # 1. Criação de embates
        start_time = time.time()
        embates = [
            Embate(
                titulo=f"Teste Ciclo {ciclo} - {i}",
                tipo="tecnico",
                contexto=f"Contexto do ciclo {ciclo}",
                status="aberto",
                criado_em=datetime.now(),
                argumentos=[]
            )
            for i in range(3)
        ]
        
        # Adiciona embate do storage no primeiro ciclo
        if ciclo == 1:
            embates.append(embate_storage)
            print("\n🔍 Detectado problema com storage persistente")
            print("Iniciando embate técnico sobre a questão...")
        
        for embate in embates:
            resultado = metrica.incrementar_tools()
            if resultado:
                result = await manager.create_embate(embate)
                print(f"✅ Embate criado: {embate.titulo}")
                
                if embate.titulo == "Implementar Storage Persistente":
                    print("\n📝 Registrando regra sobre storage persistente:")
                    print("- Ambiente de teste deve usar storage em memória")
                    print("- Implementar mock do Supabase para testes")
                    print("- Considerar SQLite para testes de integração")
            else:
                print(f"⏸️ Sistema em contenção")
                await asyncio.sleep(2)
                if not metrica.embate_ativo:
                    intervencao_manual = True
                    break
        
        if intervencao_manual:
            break
            
        # 2. Busca e exportação
        search_result = await manager.search_embates(f"Ciclo {ciclo}")
        export_result = await manager.export_embates({"status": "aberto"})
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n📊 Métricas do Ciclo {ciclo}:")
        print(f"- Tempo total: {duration:.2f}s")
        print(f"- Embates encontrados: {len(search_result)}")
        print(f"- Embates exportados: {len(export_result)}")
        
        if len(search_result) == 0 or len(export_result) == 0:
            print("\n⚠️ Alerta: Resultados vazios detectados")
            print("Causa: Storage não persistente")
            print("Ação: Consultar embate técnico sobre implementação de storage")
        
        # Aguarda antes do próximo ciclo
        print("\nAguardando próximo ciclo...")
        await asyncio.sleep(2)
        
        ciclo += 1
    
    print(f"\n✨ Teste concluído após {ciclo-1} ciclos")
    
    # Assertions
    assert ciclo > 1, "Deve completar pelo menos um ciclo"
    assert not metrica.modo_contencao, "Não deve estar em modo de contenção ao final" 


@pytest.mark.monitoring
@pytest.mark.asyncio
async def test_embate_resolucao_pendencias():
    """Testa o embate resolvendo questões pendentes e backlog."""
    # Inicializa com storage em memória
    storage = MemoryStorage()
    manager = EmbateManager(storage=storage)
    
    # Registra o problema do storage como pendência
    embate_storage = Embate(
        titulo="Storage Persistente nos Testes",
        tipo="tecnico",
        contexto="""
        Problema atual: Buscas e exportações retornando 0 resultados
        Impacto: Impossibilidade de validar fluxo de dados
        Prioridade: Alta - Bloqueia validação de funcionalidades
        """,
        status="pendente",
        criado_em=datetime.now(),
        argumentos=[]
    )
    
    # Registra outras pendências técnicas
    embate_mock = Embate(
        titulo="Mock do Supabase para Testes",
        tipo="tecnico",
        contexto="Necessidade de simular Supabase nos testes",
        status="backlog",
        criado_em=datetime.now(),
        argumentos=[]
    )
    
    embate_sqlite = Embate(
        titulo="Implementar SQLite para Testes",
        tipo="tecnico",
        contexto="Storage leve para testes de integração",
        status="backlog",
        criado_em=datetime.now(),
        argumentos=[]
    )
    
    # Cria os embates no sistema
    result = await manager.create_embate(embate_storage)
    embate_storage.id = result["id"]
    
    result = await manager.create_embate(embate_mock)
    embate_mock.id = result["id"]
    
    result = await manager.create_embate(embate_sqlite)
    embate_sqlite.id = result["id"]
    
    # Inicia métrica para monitorar ações
    metrica = Metrica(
        nome="resolucao_pendencias",
        valor=1.0,
        timestamp=datetime.now()
    )
    
    # Lista pendências atuais
    pendencias = await manager.search_embates("pendente")
    backlog = await manager.search_embates("backlog")
    
    print("\n📋 Situação Atual:")
    print(f"- Pendências: {len(pendencias)} item(s)")
    print(f"- Backlog: {len(backlog)} item(s)")
    
    # Embate entra em ação para resolver storage
    print("\n🔄 Embate entrando em ação para resolver storage...")
    
    # Adiciona argumento com análise
    analise = {
        "autor": "Embate",
        "tipo": "tecnico",
        "conteudo": """
        Análise do problema:
        1. Storage atual não persiste entre testes
        2. Dependência do Supabase dificulta testes
        3. Necessidade de solução local para testes
        
        Proposta de implementação:
        1. Criar StorageMemory para testes unitários
        2. Implementar StorageSQLite para integração
        3. Desenvolver MockSupabase para testes e2e
        """,
        "data": datetime.now()
    }
    embate_storage.argumentos.append(analise)
    
    # Atualiza status e adiciona decisão
    updates = {
        "status": "em_andamento",
        "decisao": "Implementar storage em memória como primeira etapa",
        "razao": """
        1. Solução mais rápida para testes unitários
        2. Não requer configuração adicional
        3. Permite validar lógica de negócio
        """
    }
    await manager.update_embate(embate_storage.id, updates)
    
    # Prioriza próximas ações
    print("\n📝 Próximas ações definidas pelo embate:")
    print("1. Implementar StorageMemory para testes unitários")
    print("2. Criar testes para validar persistência")
    print("3. Atualizar documentação de testes")
    
    # Atualiza backlog
    mock_updates = {
        "status": "pronto",
        "prioridade": "alta"
    }
    await manager.update_embate(embate_mock.id, mock_updates)
    
    sqlite_updates = {
        "status": "pronto",
        "prioridade": "media"
    }
    await manager.update_embate(embate_sqlite.id, sqlite_updates)
    
    print("\n✨ Resultado do embate:")
    print("- Storage em memória priorizado para implementação")
    print("- Mock do Supabase movido para próximo sprint")
    print("- SQLite planejado para fase de integração")
    
    # Verifica estado final
    embate_atualizado = await manager.get_embate(embate_storage.id)
    assert embate_atualizado.status == "em_andamento", "Embate deve estar em andamento"
    assert len(embate_atualizado.argumentos) > 0, "Deve ter análise registrada"
    assert embate_atualizado.decisao is not None, "Deve ter decisão registrada" 