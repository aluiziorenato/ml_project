import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Calendar, Clock, TrendingUp, TrendingDown, Play, Pause, AlertTriangle, CheckCircle } from 'lucide-react';
import endpoints from '../../api/endpoints';

const CampaignAutomationDashboard = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [overview, setOverview] = useState({});
  const [pendingActions, setPendingActions] = useState([]);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch all dashboard data
      const [campaignsRes, overviewRes, pendingRes] = await Promise.all([
        fetch(`http://localhost:8014${endpoints.campaignAutomation.campaigns}`),
        fetch(`http://localhost:8014${endpoints.campaignAutomation.dashboardOverview}`),
        fetch(`http://localhost:8014${endpoints.campaignAutomation.pendingApprovals}`)
      ]);

      const campaignsData = await campaignsRes.json();
      const overviewData = await overviewRes.json();
      const pendingData = await pendingRes.json();

      setCampaigns(Object.values(campaignsData.campaigns || {}));
      setOverview(overviewData.overview || {});
      setPendingActions(pendingData.pending_actions || []);
      
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApproveAction = async (actionId) => {
    try {
      const response = await fetch(`http://localhost:8014${endpoints.campaignAutomation.approveAction(actionId)}`, {
        method: 'POST'
      });
      
      if (response.ok) {
        await fetchDashboardData(); // Refresh data
      }
    } catch (error) {
      console.error('Error approving action:', error);
    }
  };

  const handleRejectAction = async (actionId, reason = '') => {
    try {
      const response = await fetch(`http://localhost:8014${endpoints.campaignAutomation.rejectAction(actionId)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ reason })
      });
      
      if (response.ok) {
        await fetchDashboardData(); // Refresh data
      }
    } catch (error) {
      console.error('Error rejecting action:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'paused': return 'bg-yellow-100 text-yellow-800';
      case 'pending_approval': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getActionTypeIcon = (actionType) => {
    switch (actionType) {
      case 'activate': return <Play className="w-4 h-4" />;
      case 'pause': return <Pause className="w-4 h-4" />;
      case 'adjust_bid': return <TrendingUp className="w-4 h-4" />;
      default: return <AlertTriangle className="w-4 h-4" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Automação de Campanhas</h1>
        <Badge variant="outline" className="text-sm">
          <Clock className="w-4 h-4 mr-1" />
          Última atualização: {new Date().toLocaleTimeString()}
        </Badge>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="flex items-center p-6">
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-8 w-8 text-blue-600" />
              <div>
                <p className="text-2xl font-bold">{overview.total_campaigns || 0}</p>
                <p className="text-xs text-muted-foreground">Total de Campanhas</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center p-6">
            <div className="flex items-center space-x-2">
              <Play className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-2xl font-bold">{overview.active_campaigns || 0}</p>
                <p className="text-xs text-muted-foreground">Campanhas Ativas</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center p-6">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-8 w-8 text-orange-600" />
              <div>
                <p className="text-2xl font-bold">{overview.pending_approvals || 0}</p>
                <p className="text-xs text-muted-foreground">Aprovações Pendentes</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center p-6">
            <div className="flex items-center space-x-2">
              <TrendingDown className="h-8 w-8 text-purple-600" />
              <div>
                <p className="text-2xl font-bold">{(overview.avg_acos * 100).toFixed(1)}%</p>
                <p className="text-xs text-muted-foreground">ACOS Médio</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="campaigns" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="campaigns">Campanhas</TabsTrigger>
          <TabsTrigger value="approvals">Aprovações</TabsTrigger>
          <TabsTrigger value="calendar">Calendário</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* Campaigns Tab */}
        <TabsContent value="campaigns" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Campanhas Gerenciadas</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {campaigns.map((campaign) => (
                  <div key={campaign.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div>
                        <h3 className="font-semibold">{campaign.name}</h3>
                        <p className="text-sm text-muted-foreground">ID: {campaign.id}</p>
                      </div>
                      <Badge className={getStatusColor(campaign.status)}>
                        {campaign.status}
                      </Badge>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium">R$ {campaign.budget?.toFixed(2)}</span>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSelectedCampaign(campaign)}
                      >
                        Detalhes
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Approvals Tab */}
        <TabsContent value="approvals" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Ações Pendentes de Aprovação</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {pendingActions.length === 0 ? (
                  <div className="text-center py-8">
                    <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
                    <p className="text-muted-foreground">Nenhuma ação pendente de aprovação</p>
                  </div>
                ) : (
                  pendingActions.map((action) => (
                    <div key={action.action_id} className="p-4 border rounded-lg">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-3">
                          {getActionTypeIcon(action.action_type)}
                          <div>
                            <h4 className="font-semibold">{action.action_type}</h4>
                            <p className="text-sm text-muted-foreground">{action.reason}</p>
                            <p className="text-xs text-muted-foreground mt-1">
                              Campanha: {action.campaign_id} | Confiança: {(action.confidence_score * 100).toFixed(1)}%
                            </p>
                          </div>
                        </div>
                        <div className="flex space-x-2">
                          <Button
                            size="sm"
                            onClick={() => handleApproveAction(action.action_id)}
                            className="bg-green-600 hover:bg-green-700"
                          >
                            Aprovar
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleRejectAction(action.action_id)}
                          >
                            Rejeitar
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Calendar Tab */}
        <TabsContent value="calendar" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Calendário de Automação</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-7 gap-2 mb-4">
                {['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'].map((day) => (
                  <div key={day} className="p-2 text-center font-semibold bg-gray-100 rounded">
                    {day}
                  </div>
                ))}
              </div>
              <div className="text-center py-8 text-muted-foreground">
                <Calendar className="h-12 w-12 mx-auto mb-4" />
                <p>Calendário interativo será implementado aqui</p>
                <p className="text-sm">Configure horários de ativação por dia da semana</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Análise de Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h4 className="font-semibold">Métricas Principais</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm">ACOS Médio</span>
                      <span className="text-sm font-medium">{(overview.avg_acos * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Margem Média</span>
                      <span className="text-sm font-medium">{overview.avg_margin?.toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Regras Ativas</span>
                      <span className="text-sm font-medium">{overview.total_rules}</span>
                    </div>
                  </div>
                </div>
                <div className="space-y-4">
                  <h4 className="font-semibold">Concorrência</h4>
                  <div className="text-center py-4 text-muted-foreground">
                    <TrendingUp className="h-8 w-8 mx-auto mb-2" />
                    <p className="text-sm">Monitoramento de top 20 anúncios</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Campaign Details Modal */}
      {selectedCampaign && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <CardHeader>
              <CardTitle className="flex justify-between items-center">
                {selectedCampaign.name}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSelectedCampaign(null)}
                >
                  Fechar
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium">Status</p>
                    <Badge className={getStatusColor(selectedCampaign.status)}>
                      {selectedCampaign.status}
                    </Badge>
                  </div>
                  <div>
                    <p className="text-sm font-medium">Orçamento</p>
                    <p className="text-lg">R$ {selectedCampaign.budget?.toFixed(2)}</p>
                  </div>
                </div>
                <div>
                  <p className="text-sm font-medium mb-2">Previsão de ACOS</p>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={async () => {
                      try {
                        const response = await fetch(`http://localhost:8014${endpoints.campaignAutomation.predictAcos(selectedCampaign.id)}`);
                        const prediction = await response.json();
                        alert(`ACOS Previsto: ${(prediction.predicted_acos * 100).toFixed(1)}%\nRecomendação: ${prediction.recommendation}`);
                      } catch (error) {
                        alert('Erro ao gerar previsão');
                      }
                    }}
                  >
                    Gerar Previsão
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default CampaignAutomationDashboard;