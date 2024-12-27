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
    name: 'Produção',
    apiUrl: '/api/v1'
  });

  // Referências
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Ambientes disponíveis
  const environments: Environment[] = [
    {
      name: 'Produção',
      apiUrl: '/api/v1'
    },
    {
      name: 'Ambiente Local',
      apiUrl: '/api/v1'
    }
  ];

  // Efeitos
  useEffect(() => {
    checkApiHealth();
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
      console.log('Verificando saúde da API:', `${selectedEnvironment.apiUrl}/health`);
      const response = await fetch(`${selectedEnvironment.apiUrl}/health`, {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      
      console.log('Resposta da API:', response.status, response.statusText);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Dados da API:', data);
        setApiStatus(`API Conectada`);
      } else {
        console.error('API indisponível:', response.status, response.statusText);
        setApiStatus('API Indisponível');
      }
    } catch (error) {
      console.error('Erro ao verificar status da API:', error);
      setApiStatus('Erro de conexão');
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
    
    if (!inputMessage.trim()) return;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    
    try {
      console.log('Enviando busca para:', `${selectedEnvironment.apiUrl}/search`);
      const response = await fetch(`${selectedEnvironment.apiUrl}/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          query: inputMessage,
          k: 4
        })
      });
      
      console.log('Resposta da busca:', response.status, response.statusText);
      
      if (response.ok) {
        const results = await response.json();
        console.log('Resultados da busca:', results);
        
        if (results.length === 0) {
          const noResultsMessage: Message = {
            id: `${Date.now()}-no-results`,
            type: 'assistant',
            content: `Não encontrei informações sobre "${inputMessage}" nos documentos disponíveis. Por favor, tente reformular sua pergunta ou faça uma pergunta sobre outro tema.`,
            timestamp: new Date()
          };
          setMessages(prev => [...prev, noResultsMessage]);
        } else {
          // Formata os resultados em uma mensagem
          const formattedResults = results.map((doc: any) => 
            `${doc.content}\n\n${Object.entries(doc.metadata || {})
              .map(([key, value]) => `${key}: ${value}`)
              .join('\n')}`
          ).join('\n\n---\n\n');
          
          const assistantMessage: Message = {
            id: `${Date.now()}-results`,
            type: 'assistant',
            content: formattedResults,
            timestamp: new Date()
          };
          
          setMessages(prev => [...prev, assistantMessage]);
        }
      } else {
        console.error('Erro na resposta:', response.status, response.statusText);
        const errorMessage: Message = {
          id: `${Date.now()}-error`,
          type: 'assistant',
          content: 'Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente.',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      const errorMessage: Message = {
        id: `${Date.now()}-error`,
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
