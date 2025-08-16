import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { CalendarIcon, ClockIcon, TagIcon, ExclamationTriangleIcon } from '@heroicons/react/24/solid';

const SpecialDatesCalendar = ({ onDateSelect, selectedDate }) => {
  const [specialDates, setSpecialDates] = useState([]);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'calendar'

  const defaultSpecialDates = [
    {
      id: 1,
      name: "Black Friday",
      description: "Black Friday - maior data de vendas do ano",
      start_date: "2024-11-29",
      end_date: "2024-11-29",
      budget_multiplier: 3.0,
      acos_adjustment: 10.0,
      is_active: true,
      color: "red",
      icon: "🛍️",
      priority_categories: ["eletronicos", "moda", "casa"],
      peak_hours: [
        { start: 8, end: 12, label: "Manhã" },
        { start: 18, end: 23, label: "Noite" }
      ]
    },
    {
      id: 2,
      name: "Cyber Monday",
      description: "Cyber Monday - foco em eletrônicos e tecnologia",
      start_date: "2024-12-02",
      end_date: "2024-12-02",
      budget_multiplier: 2.5,
      acos_adjustment: 8.0,
      is_active: true,
      color: "blue",
      icon: "💻",
      priority_categories: ["eletronicos", "informatica", "games"],
      peak_hours: [
        { start: 9, end: 11, label: "Manhã" },
        { start: 14, end: 16, label: "Tarde" },
        { start: 20, end: 22, label: "Noite" }
      ]
    },
    {
      id: 3,
      name: "Natal",
      description: "Período natalino - presentes e decoração",
      start_date: "2024-12-15",
      end_date: "2024-12-24",
      budget_multiplier: 2.0,
      acos_adjustment: 5.0,
      is_active: true,
      color: "green",
      icon: "🎄",
      priority_categories: ["presentes", "decoracao", "brinquedos"],
      peak_hours: [
        { start: 19, end: 22, label: "Noite" }
      ]
    },
    {
      id: 4,
      name: "Dia dos Namorados",
      description: "Dia dos Namorados - produtos românticos",
      start_date: "2024-06-10",
      end_date: "2024-06-12",
      budget_multiplier: 1.8,
      acos_adjustment: 5.0,
      is_active: true,
      color: "pink",
      icon: "💕",
      priority_categories: ["presentes", "joias", "flores", "perfumes"],
      peak_hours: [
        { start: 10, end: 12, label: "Manhã" },
        { start: 19, end: 21, label: "Noite" }
      ]
    },
    {
      id: 5,
      name: "Dia das Mães",
      description: "Dia das Mães - produtos para mães",
      start_date: "2024-05-10",
      end_date: "2024-05-12",
      budget_multiplier: 2.2,
      acos_adjustment: 7.0,
      is_active: true,
      color: "purple",
      icon: "🌸",
      priority_categories: ["presentes", "beleza", "casa", "flores"],
      peak_hours: [
        { start: 9, end: 11, label: "Manhã" },
        { start: 15, end: 17, label: "Tarde" }
      ]
    }
  ];

  useEffect(() => {
    setSpecialDates(defaultSpecialDates);
  }, []);

  const getColorClasses = (color, isSelected = false) => {
    const colors = {
      red: isSelected 
        ? 'border-red-500 bg-red-50 ring-red-500' 
        : 'border-red-200 hover:border-red-300 hover:bg-red-50',
      blue: isSelected 
        ? 'border-blue-500 bg-blue-50 ring-blue-500' 
        : 'border-blue-200 hover:border-blue-300 hover:bg-blue-50',
      green: isSelected 
        ? 'border-green-500 bg-green-50 ring-green-500' 
        : 'border-green-200 hover:border-green-300 hover:bg-green-50',
      pink: isSelected 
        ? 'border-pink-500 bg-pink-50 ring-pink-500' 
        : 'border-pink-200 hover:border-pink-300 hover:bg-pink-50',
      purple: isSelected 
        ? 'border-purple-500 bg-purple-50 ring-purple-500' 
        : 'border-purple-200 hover:border-purple-300 hover:bg-purple-50'
    };
    return colors[color] || colors.blue;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const isDateActive = (specialDate) => {
    const today = new Date();
    const startDate = new Date(specialDate.start_date);
    const endDate = new Date(specialDate.end_date);
    return today >= startDate && today <= endDate && specialDate.is_active;
  };

  const getDaysUntil = (dateString) => {
    const today = new Date();
    const targetDate = new Date(dateString);
    const diffTime = targetDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return "Passou";
    if (diffDays === 0) return "Hoje";
    if (diffDays === 1) return "Amanhã";
    return `${diffDays} dias`;
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Datas Especiais e Campanhas
          </h2>
          <p className="text-gray-600">
            Configure estratégias específicas para datas comemorativas
          </p>
        </div>
        
        <div className="flex space-x-2">
          <button
            onClick={() => setViewMode('grid')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              viewMode === 'grid' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Grade
          </button>
          <button
            onClick={() => setViewMode('calendar')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              viewMode === 'calendar' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Calendário
          </button>
        </div>
      </div>

      {viewMode === 'grid' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {specialDates.map((specialDate) => {
            const isSelected = selectedDate?.id === specialDate.id;
            const isActive = isDateActive(specialDate);
            const daysUntil = getDaysUntil(specialDate.start_date);
            
            return (
              <motion.div
                key={specialDate.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`relative p-6 rounded-lg border-2 cursor-pointer transition-all duration-200 ${getColorClasses(specialDate.color, isSelected)} ${isSelected ? 'ring-2' : ''}`}
                onClick={() => onDateSelect(specialDate)}
              >
                {isActive && (
                  <div className="absolute -top-2 -right-2">
                    <div className="bg-green-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                      ATIVA
                    </div>
                  </div>
                )}

                <div className="flex items-start justify-between mb-4">
                  <div className="text-3xl">{specialDate.icon}</div>
                  <div className="text-right">
                    <div className="text-xs font-medium text-gray-500 uppercase">
                      {daysUntil}
                    </div>
                    <div className="text-xs text-gray-600">
                      {formatDate(specialDate.start_date)}
                    </div>
                  </div>
                </div>

                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {specialDate.name}
                </h3>
                
                <p className="text-sm text-gray-600 mb-4">
                  {specialDate.description}
                </p>

                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Orçamento:</span>
                    <span className="font-medium text-gray-900">
                      {specialDate.budget_multiplier}x
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">ACOS:</span>
                    <span className="font-medium text-gray-900">
                      +{specialDate.acos_adjustment}%
                    </span>
                  </div>

                  {specialDate.peak_hours && specialDate.peak_hours.length > 0 && (
                    <div>
                      <div className="text-xs font-medium text-gray-500 mb-1 flex items-center">
                        <ClockIcon className="h-3 w-3 mr-1" />
                        Horários de Pico:
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {specialDate.peak_hours.map((hour, index) => (
                          <span 
                            key={index}
                            className="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded"
                          >
                            {hour.start}h-{hour.end}h
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {specialDate.priority_categories && specialDate.priority_categories.length > 0 && (
                    <div>
                      <div className="text-xs font-medium text-gray-500 mb-1 flex items-center">
                        <TagIcon className="h-3 w-3 mr-1" />
                        Categorias Prioritárias:
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {specialDate.priority_categories.slice(0, 3).map((category, index) => (
                          <span 
                            key={index}
                            className="inline-block bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded"
                          >
                            {category}
                          </span>
                        ))}
                        {specialDate.priority_categories.length > 3 && (
                          <span className="inline-block bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded">
                            +{specialDate.priority_categories.length - 3}
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      )}

      {viewMode === 'calendar' && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="text-center text-gray-500 py-12">
            <CalendarIcon className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p className="text-lg font-medium">Visualização do Calendário</p>
            <p className="text-sm">Em desenvolvimento - será implementada uma visualização em calendário completa</p>
          </div>
        </div>
      )}

      {selectedDate && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <ExclamationTriangleIcon className="h-5 w-5 text-blue-500 mr-2" />
            Configuração para {selectedDate.name}
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Multiplicador de Orçamento
              </label>
              <input
                type="number"
                step="0.1"
                min="0.1"
                max="5.0"
                defaultValue={selectedDate.budget_multiplier}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ajuste de ACOS (%)
              </label>
              <input
                type="number"
                step="1"
                min="-50"
                max="50"
                defaultValue={selectedDate.acos_adjustment}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Status
              </label>
              <select
                defaultValue={selectedDate.is_active ? 'active' : 'inactive'}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="active">Ativa</option>
                <option value="inactive">Inativa</option>
              </select>
            </div>
          </div>
          
          <div className="flex justify-end mt-4 space-x-3">
            <button className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 transition-colors">
              Cancelar
            </button>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
              Salvar Configuração
            </button>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default SpecialDatesCalendar;