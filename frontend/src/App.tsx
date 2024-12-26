import { useState, useEffect } from 'react'
import { 
  Container, 
  Typography, 
  Box, 
  CircularProgress, 
  TextField, 
  Button, 
  Paper, 
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Stack
} from '@mui/material'
import axios from 'axios'

function App() {
  const [status, setStatus] = useState<string>('Carregando...')
  const [message, setMessage] = useState('')
  const [response, setResponse] = useState('')
  const [environment, setEnvironment] = useState('render')
  const [loading, setLoading] = useState(false)
  const [debugInfo, setDebugInfo] = useState<string[]>([])

  const apiUrls = {
    local: 'http://localhost:8000',
    render: '' // URL vazia para usar o proxy
  }

  const apiUrl = environment === 'local' ? apiUrls.local : ''

  const axiosConfig = {
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    timeout: 60000, // 60 segundos
    withCredentials: true // Habilitando credentials para o proxy
  }

  const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

  const addDebugInfo = (info: string) => {
    setDebugInfo(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${info}`])
  }

  const testConnection = async () => {
    try {
      setStatus('Testando conexão...')
      addDebugInfo(`Tentando conectar no endpoint /health`)
      
      // Primeira tentativa
      try {
        const response = await axios.get('/health', axiosConfig)
        addDebugInfo(`Resposta do health check: ${JSON.stringify(response.data)}`)
        setStatus('API conectada com sucesso!')
        return
      } catch (error) {
        if (environment === 'render') {
          addDebugInfo('Serviço Render em cold start, aguardando 50 segundos...')
          setStatus('Iniciando serviço Render (pode demorar até 50 segundos)...')
          await delay(50000) // 50 segundos para cold start
        } else {
          addDebugInfo(`Primeira tentativa falhou, aguardando 2 segundos...`)
          await delay(2000)
        }
      }

      // Segunda tentativa
      try {
        addDebugInfo(`Realizando segunda tentativa...`)
        const response = await axios.get('/health', axiosConfig)
        addDebugInfo(`Resposta do health check: ${JSON.stringify(response.data)}`)
        setStatus('API conectada com sucesso!')
        return
      } catch (error) {
        if (axios.isAxiosError(error)) {
          const errorMessage = environment === 'render' 
            ? `Erro ao conectar com a API do Render. O serviço pode estar iniciando, tente novamente.`
            : `Erro ao conectar com a API: ${error.message}`
          addDebugInfo(`Erro detalhado: ${error.message}`)
          if (error.response) {
            addDebugInfo(`Status: ${error.response.status}`)
            addDebugInfo(`Data: ${JSON.stringify(error.response.data)}`)
          }
          setStatus(errorMessage)
        } else {
          setStatus('Erro ao conectar com a API')
          addDebugInfo(`Erro não-Axios: ${error}`)
        }
        console.error('Erro completo:', error)
      }
    } catch (finalError) {
      addDebugInfo(`Erro fatal: ${finalError}`)
      setStatus('Erro ao conectar com a API')
    }
  }

  useEffect(() => {
    testConnection()
  }, [environment])

  const handleRetry = () => {
    setDebugInfo([])
    testConnection()
  }

  const handleSubmit = async () => {
    if (!message.trim()) return

    setLoading(true)
    try {
      addDebugInfo(`Enviando mensagem para /api/chat`)
      addDebugInfo(`Payload: ${JSON.stringify({ message })}`)
      addDebugInfo(`Headers: ${JSON.stringify(axiosConfig.headers)}`)
      addDebugInfo(`Timestamp: ${new Date().toISOString()}`)

      const response = await axios.post(
        '/api/chat', 
        { message }, 
        axiosConfig
      )

      addDebugInfo(`Resposta recebida com sucesso`)
      addDebugInfo(`Status: ${response.status}`)
      addDebugInfo(`Headers da resposta: ${JSON.stringify(response.headers)}`)
      addDebugInfo(`Dados: ${JSON.stringify(response.data)}`)
      setResponse(response.data.response)
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error)
      if (axios.isAxiosError(error)) {
        addDebugInfo(`Erro no chat: ${error.message}`)
        addDebugInfo(`Código do erro: ${error.code}`)
        
        // Informações detalhadas do erro de rede
        if (error.code === 'ERR_NETWORK') {
          addDebugInfo('Detalhes do erro de rede:')
          addDebugInfo(`- Navigator online: ${navigator.onLine}`)
          addDebugInfo(`- User Agent: ${navigator.userAgent}`)
          
          // Tenta fazer um ping para verificar a conexão
          try {
            const pingResponse = await fetch('/health')
            if (pingResponse.ok) {
              addDebugInfo('- Ping bem sucedido, API está respondendo')
            } else {
              addDebugInfo(`- Ping falhou com status: ${pingResponse.status}`)
            }
          } catch (pingError: any) {
            addDebugInfo(`- Ping falhou: ${pingError?.message || 'Erro desconhecido'}`)
          }
        }

        // Informações da resposta se houver
        if (error.response) {
          addDebugInfo(`Status: ${error.response.status}`)
          addDebugInfo(`Status Text: ${error.response.statusText}`)
          addDebugInfo(`Data: ${JSON.stringify(error.response.data)}`)
        }
      } else {
        addDebugInfo(`Erro não-Axios: ${error}`)
      }
      setResponse('Erro ao processar sua mensagem. Tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxWidth="md" sx={{ 
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <Box sx={{ 
        width: '100%',
        py: 4,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center'
      }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Chat API
        </Typography>

        <FormControl sx={{ m: 1, minWidth: 200 }}>
          <InputLabel>Ambiente</InputLabel>
          <Select
            value={environment}
            label="Ambiente"
            onChange={(e) => setEnvironment(e.target.value)}
          >
            <MenuItem value="render">Ambiente Render (pode demorar até 50s para iniciar)</MenuItem>
            <MenuItem value="local">Ambiente Local</MenuItem>
          </Select>
        </FormControl>

        {environment === 'render' && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
            Nota: No plano gratuito do Render, o serviço pode demorar até 50 segundos para iniciar após ficar inativo.
          </Typography>
        )}

        <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="subtitle1">
            Status da API: {status}
          </Typography>
          {status === 'Testando conexão...' && <CircularProgress size={20} />}
          <Button 
            variant="outlined" 
            size="small" 
            onClick={handleRetry}
            disabled={status === 'Testando conexão...'}
          >
            Tentar Novamente
          </Button>
        </Box>

        <Paper elevation={3} sx={{ p: 3, mt: 3, width: '100%' }}>
          <Stack spacing={2}>
            <TextField
              fullWidth
              label="Digite sua mensagem"
              multiline
              rows={3}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              disabled={loading}
            />
            
            <Button 
              variant="contained" 
              onClick={handleSubmit}
              disabled={loading || !message.trim()}
            >
              Enviar
              {loading && <CircularProgress size={20} sx={{ ml: 1 }} />}
            </Button>

            {response && (
              <Paper elevation={1} sx={{ p: 2, bgcolor: '#f5f5f5' }}>
                <Typography variant="body1">
                  Resposta: {response}
                </Typography>
              </Paper>
            )}
          </Stack>
        </Paper>

        {/* Área de Debug */}
        <Paper elevation={1} sx={{ p: 2, mt: 3, width: '100%', bgcolor: '#f8f9fa' }}>
          <Typography variant="h6" gutterBottom>
            Informações de Debug
          </Typography>
          <Box sx={{ 
            maxHeight: '200px', 
            overflow: 'auto', 
            fontFamily: 'monospace',
            fontSize: '0.875rem',
            bgcolor: '#212529',
            color: '#fff',
            p: 2,
            borderRadius: 1
          }}>
            {debugInfo.map((info, index) => (
              <div key={index}>{info}</div>
            ))}
          </Box>
        </Paper>
      </Box>
    </Container>
  )
}

export default App
