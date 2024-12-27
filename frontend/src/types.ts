export interface Message {
  id?: string;
  type: 'user' | 'assistant';
  content: string;
  metadata?: Record<string, any>;
  timestamp: Date;
} 