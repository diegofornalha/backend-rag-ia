import axios, { AxiosError, AxiosInstance } from 'axios';
import chalk from 'chalk';

interface Endpoint {
  path: string;
  method: 'GET' | 'POST';
  name: string;
  body?: any;
}

const API_URL = 'https://backend-rag-ia.onrender.com';
const ENDPOINTS: Endpoint[] = [
  { path: '/api/v1/health', method: 'GET', name: 'Health Check' },
  { path: '/api/v1/documents/count', method: 'GET', name: 'Document Count' },
  { path: '/api/v1/documents/check/1', method: 'GET', name: 'Check Document' },
  { path: '/api/v1/search/', method: 'POST', name: 'Search', body: { query: 'test', k: 4 } }
];

const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

async function testEndpoint(endpoint: Endpoint): Promise<boolean> {
  try {
    console.log(chalk.blue(`\nTestando ${endpoint.name}...`));
    console.log(chalk.gray(`${endpoint.method} ${API_URL}${endpoint.path}`));
    
    const startTime = Date.now();
    const response = endpoint.method === 'GET' 
      ? await api.get(endpoint.path)
      : await api.post(endpoint.path, endpoint.body);
    const endTime = Date.now();
    
    console.log(chalk.green('✓ Sucesso!'));
    console.log(chalk.gray('Status:'), chalk.cyan(response.status));
    console.log(chalk.gray('Tempo:'), chalk.cyan(`${endTime - startTime}ms`));
    console.log(chalk.gray('Resposta:'), chalk.cyan(JSON.stringify(response.data, null, 2)));
    
    return true;
  } catch (error) {
    const axiosError = error as AxiosError;
    console.log(chalk.red('✗ Erro!'));
    console.log(chalk.gray('Status:'), chalk.red(axiosError.response?.status || 'N/A'));
    console.log(chalk.gray('Mensagem:'), chalk.red(axiosError.message));
    if (axiosError.response?.data) {
      console.log(chalk.gray('Detalhes:'), chalk.red(JSON.stringify(axiosError.response.data, null, 2)));
    }
    return false;
  }
}

async function runTests(): Promise<void> {
  console.log(chalk.yellow('\n=== Iniciando testes de conexão com a API ===\n'));
  
  let successCount = 0;
  let failCount = 0;
  
  for (const endpoint of ENDPOINTS) {
    const success = await testEndpoint(endpoint);
    success ? successCount++ : failCount++;
  }
  
  console.log(chalk.yellow('\n=== Resumo dos testes ==='));
  console.log(chalk.green(`✓ Sucesso: ${successCount}`));
  console.log(chalk.red(`✗ Falhas: ${failCount}`));
  console.log(chalk.yellow('========================\n'));
}

// Executa os testes a cada 10 segundos
console.log(chalk.cyan('Iniciando monitoramento da API...'));
console.log(chalk.gray('Pressione Ctrl+C para parar\n'));

runTests();
setInterval(runTests, 10000); 