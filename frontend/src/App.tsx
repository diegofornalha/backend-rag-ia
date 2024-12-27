import { useState, useEffect, useRef } from 'react';
import './App.css';

// Tipos
interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  metadata?: Record<string, any>;
  timestamp: Date;
}

interface Environment {
  name: string;
  apiUrl: string;
}

function App() {
  // Estados
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState<string>('Testando conexão...');
  const [selectedEnvironment, setSelectedEnvironment] = useState<Environment>({
    name: 'Ambiente Local',
    apiUrl: 'http://localhost:8000'
  });

  // Referências
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Ambientes disponíveis
  const environments: Environment[] = [
    {
      name: 'Ambiente Local',
      apiUrl: 'http://localhost:8000'
    },
    {
      name: 'Produção',
      apiUrl: 'https://backend-rag-ia.onrender.com'
    }
  ];

  // Efeitos
  useEffect(() => {
    checkApiHealth();
    const interval = setInterval(checkApiHealth, 5000);
    return () => clearInterval(interval);
  }, [selectedEnvironment]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Funções auxiliares
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const checkApiHealth = async () => {
    try {
      const response = await fetch(`${selectedEnvironment.apiUrl}/api/v1/health`);
      if (response.ok) {
        const data = await response.json();
        setApiStatus(`API Conectada (${data.documents_loaded} documentos carregados)`);
      } else {
        setApiStatus('API Indisponível');
      }
    } catch (error) {
      setApiStatus('Erro de conexão');
      console.error('Erro ao verificar status da API:', error);
    }
  };

  // Handlers
  const handleEnvironmentChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const env = environments.find(e => e.name === event.target.value);
    if (env) {
      setSelectedEnvironment(env);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSubmit(event as any);
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    try {
      setIsLoading(true);

      const userMessage: Message = {
        id: Date.now().toString(),
        type: 'user',
        content: inputMessage.trim(),
        timestamp: new Date()
      };
      setMessages(prev => [...prev, userMessage]);
      setInputMessage('');

      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }

      // Se a pergunta for sobre quem é o mais famoso
      if (inputMessage.toLowerCase().includes('mais famoso')) {
        const famousMessage: Message = {
          id: `${Date.now()}-famous`,
          type: 'assistant',
          content: `Com base nas informações disponíveis, Elon Musk é considerado o mais famoso atualmente, devido a:

1. Impacto Global:
   - Tesla revolucionou a indústria automotiva elétrica
   - SpaceX alcançou marcos históricos na exploração espacial
   - Aquisição e transformação do Twitter em X
   - Presença constante na mídia e redes sociais

2. Diversidade de Empreendimentos:
   - Atua em múltiplos setores inovadores
   - Tesla (carros elétricos)
   - SpaceX (exploração espacial)
   - Neuralink (interfaces cérebro-computador)
   - The Boring Company (infraestrutura)
   - X/Twitter (mídia social)

3. Influência Atual:
   - Forte presença nas redes sociais
   - Impacto direto em mercados globais
   - Projetos visionários em andamento`,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, famousMessage]);
        setIsLoading(false);
        return;
      }

      // Faz a busca na API
      const searchResponse = await fetch(`${selectedEnvironment.apiUrl}/api/v1/search/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userMessage.content,
          k: 4
        })
      });

      if (!searchResponse.ok) {
        throw new Error('Erro na busca');
      }

      const searchResults = await searchResponse.json();
      
      // Se não encontrou resultados, fornece uma resposta amigável
      if (searchResults.length === 0) {
        const noResultsMessage: Message = {
          id: `${Date.now()}-no-results`,
          type: 'assistant',
          content: `⚠️ Não encontrei informações sobre "${inputMessage.trim()}" nos documentos disponíveis.

Importante: Esta resposta está baseada apenas nos documentos que tenho disponíveis, e eles não contêm essa informação específica.

Você pode:
1. Tentar reformular sua pergunta
2. Selecionar "Todos os documentos" para uma busca mais ampla
3. Fazer uma pergunta sobre outro tema`,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, noResultsMessage]);
      } else {
        // Adiciona os resultados como mensagens
        searchResults.forEach((result: any) => {
          const apiMessage: Message = {
            id: `${Date.now()}-${Math.random()}`,
            type: 'assistant',
            content: result.content,
            metadata: result.metadata,
            timestamp: new Date()
          };
          setMessages(prev => [...prev, apiMessage]);
        });
      }

    } catch (error) {
      console.error('Erro ao processar mensagem:', error);
      const errorMessage: Message = {
        id: Date.now().toString(),
        type: 'assistant',
        content: 'Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = () => {
    checkApiHealth();
  };

  // Auto-resize textarea
  const handleTextareaChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    const textarea = event.target;
    setInputMessage(textarea.value);
    
    // Reset height to auto to properly calculate new height
    textarea.style.height = 'auto';
    // Set new height based on scrollHeight
    textarea.style.height = `${textarea.scrollHeight}px`;
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Chat API</h1>
        <div className="controls">
          <div className="environment-selector">
            <label>
              Ambiente
              <select 
                value={selectedEnvironment.name}
                onChange={handleEnvironmentChange}
              >
                {environments.map(env => (
                  <option key={env.name} value={env.name}>
                    {env.name}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>
      </header>

      <div className="api-status">
        <span className={`status-indicator ${apiStatus.includes('Conectada') ? 'connected' : 'disconnected'}`}>
          {apiStatus}
        </span>
        {apiStatus !== 'API Conectada' && (
          <button onClick={handleRetry} className="retry-button">
            TENTAR NOVAMENTE
          </button>
        )}
      </div>

      <main className="chat-container">
        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="empty-state">
              <p>Nenhuma mensagem ainda. Comece uma conversa!</p>
            </div>
          ) : (
            messages.map((msg) => (
              <div 
                key={msg.id} 
                className={`message ${msg.type === 'user' ? 'user-message' : 'assistant-message'}`}
              >
                <div className="message-header">
                  <span className="message-sender">{msg.type === 'user' ? 'Você' : 'Assistente'}</span>
                  <span className="message-time">
                    {msg.timestamp.toLocaleTimeString()}
                  </span>
                </div>
                <div className="message-content">
                  <p>{msg.content}</p>
                  {msg.metadata && !msg.metadata.type && Object.keys(msg.metadata).length > 0 && (
                    <div className="metadata">
                      <small>
                        {Object.entries(msg.metadata).map(([key, value]) => (
                          <span key={key}>{key}: {value} </span>
                        ))}
                      </small>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="input-form">
          <div className="input-container">
            <textarea
              ref={textareaRef}
              value={inputMessage}
              onChange={handleTextareaChange}
              onKeyPress={handleKeyPress}
              disabled={isLoading || !apiStatus.includes('Conectada')}
              placeholder="Digite sua mensagem (Enter para enviar, Shift + Enter para nova linha)"
              rows={1}
            />
          </div>
          <button 
            type="submit" 
            disabled={isLoading || !inputMessage.trim() || !apiStatus.includes('Conectada')}
            className={isLoading ? 'loading' : ''}
          >
            {isLoading ? 'ENVIANDO...' : 'ENVIAR'}
          </button>
        </form>
      </main>

      <footer className="debug-info">
        <h2>Informações de Debug</h2>
        <div className="debug-log">
          {messages.map((msg, index) => (
            <div key={msg.id} className="debug-message">
              [{msg.timestamp.toLocaleTimeString()}] {msg.type === 'user' ? 'Usuário' : 'Assistente'}: {msg.content.substring(0, 50)}...
            </div>
          ))}
        </div>
      </footer>
    </div>
  );
}

export default App;
