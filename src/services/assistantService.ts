import { apiClient } from './apiClient';

export interface KnowledgeSource {
  document_title: string;
  source_organization: string;
  category: string;
  relevance_score: number;
  snippet: string;
}

export interface ChatMessage {
  id: string;
  sender_role: 'user' | 'assistant';
  content: string;
  retrieved_sources: KnowledgeSource[];
  created_at: string;
}

export const assistantService = {
  sendMessage: async (message: string, districtContext: string = 'Almora', conversationId?: string): Promise<ChatMessage> => {
    return apiClient.post<ChatMessage>('/assistant/chat', {
      message,
      district_context: districtContext,
      conversation_id: conversationId
    });
  }
};
