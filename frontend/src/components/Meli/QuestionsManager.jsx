import React, { useState, useEffect } from 'react';
import { endpoints } from '../../api/endpoints';

const QuestionsManager = ({ userId, accessToken }) => {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [aiSuggestions, setAiSuggestions] = useState([]);
  const [filter, setFilter] = useState({ unansweredOnly: false });
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    if (userId && accessToken) {
      fetchQuestions();
      fetchAnalytics();
    }
  }, [userId, accessToken, filter]);

  const fetchQuestions = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        user_id: userId,
        unanswered_only: filter.unansweredOnly.toString()
      });

      const response = await fetch(`${endpoints.meli.questions.list}?${params}`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      });

      const data = await response.json();
      
      if (data.success) {
        setQuestions(data.data);
      }
    } catch (error) {
      console.error('Error fetching questions:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const params = new URLSearchParams({ user_id: userId });
      const response = await fetch(`${endpoints.meli.questions.analytics}?${params}`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      });

      const data = await response.json();
      if (data.success) {
        setAnalytics(data.data.analytics);
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  const fetchAISuggestions = async (questionText) => {
    try {
      const params = new URLSearchParams({
        question_text: questionText
      });

      const response = await fetch(`${endpoints.meli.questions.aiSuggestions}?${params}`, {
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

  const handleQuestionSelect = (question) => {
    setSelectedQuestion(question);
    if (question.text) {
      fetchAISuggestions(question.text);
    }
  };

  const answerQuestion = async (questionId, answerText) => {
    try {
      const response = await fetch(endpoints.meli.questions.answer, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question_id: questionId,
          answer: answerText
        })
      });

      const data = await response.json();
      
      if (data.success) {
        // Refresh questions list
        fetchQuestions();
        setSelectedQuestion(null);
        alert('Pergunta respondida com sucesso!');
      }
    } catch (error) {
      console.error('Error answering question:', error);
      alert('Erro ao responder pergunta');
    }
  };

  const QuestionCard = ({ question }) => (
    <div 
      className={`p-4 border rounded-lg cursor-pointer hover:bg-gray-50 ${
        question.status === 'UNANSWERED' ? 'border-orange-500 bg-orange-50' : 'border-gray-200'
      }`}
      onClick={() => handleQuestionSelect(question)}
    >
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <p className="text-sm text-gray-600">
            Item: {question.item_id}
          </p>
          <p className="mt-1 text-gray-900 font-medium">{question.text}</p>
          <p className="mt-2 text-xs text-gray-500">
            {new Date(question.date_created).toLocaleDateString()}
          </p>
        </div>
        <div className="flex flex-col items-end">
          <span className={`px-2 py-1 text-xs rounded-full ${
            question.status === 'UNANSWERED' 
              ? 'bg-orange-100 text-orange-800' 
              : 'bg-green-100 text-green-800'
          }`}>
            {question.status === 'UNANSWERED' ? 'Não respondida' : 'Respondida'}
          </span>
          {question.ai_suggestion && (
            <span className="mt-1 px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
              IA disponível
            </span>
          )}
        </div>
      </div>
    </div>
  );

  const AISuggestionCard = ({ suggestion, onUse }) => (
    <div className="p-3 border border-blue-200 rounded-lg bg-blue-50">
      <div className="flex justify-between items-start">
        <p className="text-sm text-gray-900">{suggestion.text}</p>
        <span className="text-xs text-blue-600 ml-2">
          {Math.round(suggestion.confidence * 100)}%
        </span>
      </div>
      <p className="text-xs text-blue-600 mt-1">
        Fonte: {suggestion.source}
      </p>
      <button 
        onClick={() => onUse(suggestion.text)}
        className="mt-2 text-xs bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-700"
      >
        Usar Resposta
      </button>
    </div>
  );

  const AnalyticsCard = () => {
    if (!analytics) return null;

    return (
      <div className="bg-white p-6 rounded-lg shadow-lg border">
        <h3 className="text-lg font-semibold mb-4">Analytics de Perguntas</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-600">{analytics.total}</p>
            <p className="text-sm text-gray-600">Total</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-green-600">{analytics.answered}</p>
            <p className="text-sm text-gray-600">Respondidas</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-orange-600">{analytics.unanswered}</p>
            <p className="text-sm text-gray-600">Pendentes</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-purple-600">
              {Math.round(analytics.answer_rate * 100)}%
            </p>
            <p className="text-sm text-gray-600">Taxa de Resposta</p>
          </div>
        </div>
      </div>
    );
  };

  const [answerText, setAnswerText] = useState('');

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
          Gerenciamento de Perguntas e Respostas
        </h2>
        
        {/* Analytics */}
        <AnalyticsCard />
        
        {/* Filters */}
        <div className="flex space-x-4 mb-4 mt-6">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={filter.unansweredOnly}
              onChange={(e) => setFilter({...filter, unansweredOnly: e.target.checked})}
              className="mr-2"
            />
            Apenas não respondidas
          </label>
          <button
            onClick={fetchQuestions}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Atualizar
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Questions List */}
        <div>
          <h3 className="text-lg font-semibold mb-4">
            Perguntas ({questions.length})
          </h3>
          <div className="space-y-3">
            {questions.map((question) => (
              <QuestionCard key={question.id} question={question} />
            ))}
            {questions.length === 0 && (
              <p className="text-gray-500 text-center py-8">
                Nenhuma pergunta encontrada
              </p>
            )}
          </div>
        </div>

        {/* Question Details & AI Suggestions */}
        <div>
          {selectedQuestion && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-4">Detalhes da Pergunta</h3>
                <div className="p-4 border rounded-lg bg-gray-50">
                  <p className="text-sm text-gray-600 mb-2">
                    Item: {selectedQuestion.item_id}
                  </p>
                  <p className="text-gray-900 mb-2 font-medium">{selectedQuestion.text}</p>
                  <p className="text-xs text-gray-500">
                    {new Date(selectedQuestion.date_created).toLocaleString()}
                  </p>
                  <span className={`inline-block mt-2 px-2 py-1 text-xs rounded-full ${
                    selectedQuestion.status === 'UNANSWERED' 
                      ? 'bg-orange-100 text-orange-800' 
                      : 'bg-green-100 text-green-800'
                  }`}>
                    {selectedQuestion.status === 'UNANSWERED' ? 'Pendente' : 'Respondida'}
                  </span>
                </div>
              </div>

              {aiSuggestions.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-4">
                    Sugestões de Resposta (IA)
                  </h3>
                  <div className="space-y-3">
                    {aiSuggestions.map((suggestion, index) => (
                      <AISuggestionCard 
                        key={index} 
                        suggestion={suggestion} 
                        onUse={(text) => setAnswerText(text)}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Answer Form */}
              {selectedQuestion.status === 'UNANSWERED' && (
                <div>
                  <h3 className="text-lg font-semibold mb-4">Responder Pergunta</h3>
                  <textarea
                    value={answerText}
                    onChange={(e) => setAnswerText(e.target.value)}
                    className="w-full p-3 border rounded-lg resize-none"
                    rows="4"
                    placeholder="Digite sua resposta..."
                  />
                  <div className="flex space-x-2 mt-2">
                    <button 
                      onClick={() => answerQuestion(selectedQuestion.id, answerText)}
                      disabled={!answerText.trim()}
                      className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400"
                    >
                      Enviar Resposta
                    </button>
                    <button 
                      onClick={() => setAnswerText('')}
                      className="px-4 py-2 bg-gray-400 text-white rounded hover:bg-gray-500"
                    >
                      Limpar
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
          {!selectedQuestion && (
            <div className="text-center py-16">
              <p className="text-gray-500">
                Selecione uma pergunta para ver os detalhes
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default QuestionsManager;