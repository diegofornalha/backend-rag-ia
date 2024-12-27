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
  const [documentsCount, setDocumentsCount] = useState<number>(0);
  const [selectedEnvironment, setSelectedEnvironment] = useState<Environment>({
    name: 'Produção',
    apiUrl: '/api/v1'
  });
  const [showDebug, setShowDebug] = useState(true);

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
        setDocumentsCount(data.documents_count || 0);
      } else {
        console.error('API indisponível:', response.status, response.statusText);
        setApiStatus('API Indisponível');
        setDocumentsCount(0);
      }
    } catch (error) {
      console.error('Erro ao verificar status da API:', error);
      setApiStatus('Erro de conexão');
      setDocumentsCount(0);
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
      <main className="chat-container">
        <div className="chat-header">
          <h1 className="chat-title">Chat API</h1>
          <div className="header-controls">
            {documentsCount > 0 && (
              <div className="documents-info">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M3 2C3 1.44772 3.44772 1 4 1H9L13 5V14C13 14.5523 12.5523 15 12 15H4C3.44772 15 3 14.5523 3 14V2Z" stroke="currentColor" strokeWidth="2"/>
                  <path d="M9 1V5H13" stroke="currentColor" strokeWidth="2"/>
                </svg>
                {documentsCount} documento{documentsCount !== 1 ? 's' : ''}
              </div>
            )}
            <button 
              className="debug-toggle"
              onClick={() => setShowDebug(!showDebug)}
              title={showDebug ? "Ocultar Debug Info" : "Mostrar Debug Info"}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 4V4C8.13401 4 5 7.13401 5 11V12C5 15.866 8.13401 19 12 19V19C15.866 19 19 15.866 19 12V11C19 7.13401 15.866 4 12 4Z" stroke="currentColor" strokeWidth="2"/>
                <path d="M12 15V19M12 8L12 12M15 12H19M5 12H9" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </button>
          </div>
        </div>

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
              placeholder=""
              rows={1}
            />
          </div>
          <div 
            className={`toggle-switch ${apiStatus.includes('Conectada') ? 'connected' : ''}`}
            data-selected={selectedEnvironment.name}
            onClick={() => {
              const newEnv = selectedEnvironment.name === 'Produção' ? 
                environments.find(e => e.name === 'Ambiente Local') : 
                environments.find(e => e.name === 'Produção');
              if (newEnv) {
                setSelectedEnvironment(newEnv);
              }
            }}
          >
            <div className={`toggle-option ${selectedEnvironment.name === 'Produção' ? 'selected' : ''}`}>
              Produção
            </div>
            <div className={`toggle-option ${selectedEnvironment.name === 'Ambiente Local' ? 'selected' : ''}`}>
              Local
            </div>
          </div>
        </form>
      </main>

      {showDebug && (
        <div className="debug-info">
          <div className="debug-log">
            <strong>Debug Info</strong>
            <br />
            API Status: <span style={{ color: apiStatus.includes('Conectada') ? '#68d391' : '#fc8181' }}>{apiStatus}</span>
            <br />
            Ambiente: <span style={{ color: '#90cdf4' }}>{selectedEnvironment.name}</span>
            <br />
            Documentos: <span style={{ color: '#9ae6b4' }}>{documentsCount}</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
