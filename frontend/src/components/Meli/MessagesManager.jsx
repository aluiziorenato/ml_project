import React, { useState, useEffect } from 'react';
import { endpoints } from '../../api/endpoints';

const MessagesManager = ({ userId, accessToken }) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMessage, setSelectedMessage] = useState(null);
  const [aiSuggestions, setAiSuggestions] = useState([]);
  const [filter, setFilter] = useState({ unreadOnly: false });

  useEffect(() => {
    if (userId && accessToken) {
      fetchMessages();
    }
  }, [userId, accessToken, filter]);

  const fetchMessages = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        user_id: userId,
        unread_only: filter.unreadOnly.toString()
      });

      const response = await fetch(`${endpoints.meli.messages.list}?${params}`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      });

      const data = await response.json();
      
      if (data.success) {
        setMessages(data.data);
      }
    } catch (error) {
      console.error('Error fetching messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAISuggestions = async (messageContent) => {
    try {
      const params = new URLSearchParams({
        message_content: messageContent
      });

      const response = await fetch(`${endpoints.meli.messages.aiSuggestions}?${params}`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      });

      const data = await response.json();
      
      if (data.success) {
        setAiSuggestions(data.data.suggestions || []);
      }
    } catch (error) {
      console.error('Error fetching AI suggestions:', error);
    }
  };

  const handleMessageSelect = (message) => {
    setSelectedMessage(message);
    if (message.text) {
      fetchAISuggestions(message.text);
    }
  };

  const MessageCard = ({ message }) => (
    <div 
      className={`p-4 border rounded-lg cursor-pointer hover:bg-gray-50 ${
        message.status === 'unread' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
      }`}
      onClick={() => handleMessageSelect(message)}
    >
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <p className="text-sm text-gray-600">
            De: {message.from?.user_id || 'Desconhecido'}
          </p>
          <p className="mt-1 text-gray-900">{message.text}</p>
          <p className="mt-2 text-xs text-gray-500">
            {new Date(message.date_created).toLocaleDateString()}
          </p>
        </div>
        <div className="flex flex-col items-end">
          <span className={`px-2 py-1 text-xs rounded-full ${
            message.status === 'unread' 
              ? 'bg-blue-100 text-blue-800' 
              : 'bg-gray-100 text-gray-800'
          }`}>
            {message.status === 'unread' ? 'Não lida' : 'Lida'}
          </span>
        </div>
      </div>
    </div>
  );

  const AISuggestionCard = ({ suggestion }) => (
    <div className="p-3 border border-green-200 rounded-lg bg-green-50">
      <div className="flex justify-between items-start">
        <p className="text-sm text-gray-900">{suggestion.text}</p>
        <span className="text-xs text-green-600 ml-2">
          {Math.round(suggestion.confidence * 100)}%
        </span>
      </div>
      <p className="text-xs text-green-600 mt-1">
        Fonte: {suggestion.source}
      </p>
      <button className="mt-2 text-xs bg-green-600 text-white px-2 py-1 rounded hover:bg-green-700">
        Usar Resposta
      </button>
    </div>
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Gerenciamento de Mensagens
        </h2>
        
        {/* Filters */}
        <div className="flex space-x-4 mb-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={filter.unreadOnly}
              onChange={(e) => setFilter({...filter, unreadOnly: e.target.checked})}
              className="mr-2"
            />
            Apenas não lidas
          </label>
          <button
            onClick={fetchMessages}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Atualizar
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Messages List */}
        <div>
          <h3 className="text-lg font-semibold mb-4">
            Mensagens ({messages.length})
          </h3>
          <div className="space-y-3">
            {messages.map((message) => (
              <MessageCard key={message.id} message={message} />
            ))}
            {messages.length === 0 && (
              <p className="text-gray-500 text-center py-8">
                Nenhuma mensagem encontrada
              </p>
            )}
          </div>
        </div>

        {/* Message Details & AI Suggestions */}
        <div>
          {selectedMessage && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-4">Detalhes da Mensagem</h3>
                <div className="p-4 border rounded-lg bg-gray-50">
                  <p className="text-sm text-gray-600 mb-2">
                    De: {selectedMessage.from?.user_id}
                  </p>
                  <p className="text-gray-900 mb-2">{selectedMessage.text}</p>
                  <p className="text-xs text-gray-500">
                    {new Date(selectedMessage.date_created).toLocaleString()}
                  </p>
                </div>
              </div>

              {aiSuggestions.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-4">
                    Sugestões de Resposta (IA)
                  </h3>
                  <div className="space-y-3">
                    {aiSuggestions.map((suggestion, index) => (
                      <AISuggestionCard key={index} suggestion={suggestion} />
                    ))}
                  </div>
                </div>
              )}

              {/* Manual Response */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Resposta Manual</h3>
                <textarea
                  className="w-full p-3 border rounded-lg resize-none"
                  rows="4"
                  placeholder="Digite sua resposta..."
                />
                <button className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                  Enviar Resposta
                </button>
              </div>
            </div>
          )}
          {!selectedMessage && (
            <div className="text-center py-16">
              <p className="text-gray-500">
                Selecione uma mensagem para ver os detalhes
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessagesManager;