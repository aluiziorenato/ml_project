import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/Tabs';

const SEOIntelligenceDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [marketData, setMarketData] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [heatmapData, setHeatmapData] = useState([]);
  const [loading, setLoading] = useState(true);

  // Mock data for development
  useEffect(() => {
    const mockData = {
      overview: {
        totalAnalyses: 1247,
        activeAlerts: 23,
        opportunitiesFound: 156,
        avgROI: '+34.5%'
      },
      heatmap: [
        { keyword: 'smartphone', heat: 0.95, volume: 15000, growth: 25 },
        { keyword: 'laptop', heat: 0.82, volume: 8000, growth: 12 },
        { keyword: 'headphone', heat: 0.78, volume: 12000, growth: 18 },
        { keyword: 'smartwatch', heat: 0.73, volume: 6000, growth: 35 }
      ],
      alerts: [
        {
          id: 1,
          type: 'blue_ocean',
          keyword: 'wireless charger',
          intensity: 0.85,
          description: 'High search volume with low competition detected',
          timestamp: new Date().toISOString()
        },
        {
          id: 2,
          type: 'seasonal_spike',
          keyword: 'summer dress',
          intensity: 0.72,
          description: 'Seasonal demand spike predicted in 14 days',
          timestamp: new Date().toISOString()
        }
      ]
    };

    setMarketData(mockData.overview);
    setHeatmapData(mockData.heatmap);
    setAlerts(mockData.alerts);
    setLoading(false);
  }, []);

  const HeatmapCard = ({ data }) => (
    <Card className="mb-4">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          🔥 Live Keyword Heatmap
          <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">LIVE</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          {data.map((item, index) => (
            <div 
              key={index}
              className={`p-3 rounded-lg border ${
                item.heat > 0.8 ? 'bg-red-50 border-red-200' :
                item.heat > 0.6 ? 'bg-orange-50 border-orange-200' :
                'bg-yellow-50 border-yellow-200'
              }`}
            >
              <div className="flex justify-between items-center">
                <span className="font-medium">{item.keyword}</span>
                <span className={`text-xs px-2 py-1 rounded ${
                  item.heat > 0.8 ? 'bg-red-200 text-red-800' :
                  item.heat > 0.6 ? 'bg-orange-200 text-orange-800' :
                  'bg-yellow-200 text-yellow-800'
                }`}>
                  {(item.heat * 100).toFixed(0)}%
                </span>
              </div>
              <div className="text-sm text-gray-600 mt-1">
                Volume: {item.volume.toLocaleString()} | Growth: +{item.growth}%
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );

  const AlertsCard = ({ alerts }) => (
    <Card className="mb-4">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          ⚡ Market Alerts
          <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
            {alerts.length} ACTIVE
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {alerts.map((alert) => (
            <div key={alert.id} className="p-3 border rounded-lg bg-blue-50">
              <div className="flex justify-between items-start">
                <div>
                  <div className="font-medium text-blue-900">{alert.keyword}</div>
                  <div className="text-sm text-blue-700">{alert.description}</div>
                </div>
                <span className={`text-xs px-2 py-1 rounded ${
                  alert.type === 'blue_ocean' ? 'bg-blue-200 text-blue-800' :
                  'bg-green-200 text-green-800'
                }`}>
                  {alert.type}
                </span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );

  const OverviewCards = ({ data }) => (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <Card>
        <CardContent className="p-4">
          <div className="text-2xl font-bold text-blue-600">{data.totalAnalyses}</div>
          <div className="text-sm text-gray-600">Total Analyses</div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4">
          <div className="text-2xl font-bold text-red-600">{data.activeAlerts}</div>
          <div className="text-sm text-gray-600">Active Alerts</div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4">
          <div className="text-2xl font-bold text-green-600">{data.opportunitiesFound}</div>
          <div className="text-sm text-gray-600">Opportunities Found</div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4">
          <div className="text-2xl font-bold text-purple-600">{data.avgROI}</div>
          <div className="text-sm text-gray-600">Avg ROI Improvement</div>
        </CardContent>
      </Card>
    </div>
  );

  const ModuleCard = ({ title, description, status, port, icon }) => (
    <Card className="mb-4">
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="text-2xl">{icon}</div>
            <div>
              <div className="font-medium">{title}</div>
              <div className="text-sm text-gray-600">{description}</div>
              <div className="text-xs text-gray-500">Port: {port}</div>
            </div>
          </div>
          <span className={`text-xs px-2 py-1 rounded-full ${
            status === 'active' ? 'bg-green-100 text-green-800' :
            status === 'ready' ? 'bg-blue-100 text-blue-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            {status}
          </span>
        </div>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading SEO Intelligence Dashboard...</div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          🧠 SEO Intelligence Dashboard
        </h1>
        <p className="text-gray-600">
          Complete AI-powered SEO system for e-commerce optimization
        </p>
      </div>

      <OverviewCards data={marketData} />

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="market-pulse">Market Pulse</TabsTrigger>
          <TabsTrigger value="ai-predictive">AI Predictive</TabsTrigger>
          <TabsTrigger value="optimization">Optimization</TabsTrigger>
          <TabsTrigger value="modules">All Modules</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <HeatmapCard data={heatmapData} />
            <AlertsCard alerts={alerts} />
          </div>
        </TabsContent>

        <TabsContent value="market-pulse" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>⚡ Real-Time Market Pulse</CardTitle>
              </CardHeader>
              <CardContent>
                <HeatmapCard data={heatmapData} />
                <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                  <div className="text-lg font-medium text-blue-900">Market Heartbeat</div>
                  <div className="text-3xl font-bold text-blue-600">78 BPM</div>
                  <div className="text-sm text-blue-700">Market activity is elevated</div>
                </div>
              </CardContent>
            </Card>
            <div>
              <AlertsCard alerts={alerts} />
            </div>
          </div>
        </TabsContent>

        <TabsContent value="ai-predictive" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>🔮 Market Gap Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="p-3 border rounded-lg">
                    <div className="font-medium">Wireless Earbuds</div>
                    <div className="text-sm text-gray-600">High volume, low competition</div>
                    <div className="text-xs text-green-600">Gap Score: 0.87</div>
                  </div>
                  <div className="p-3 border rounded-lg">
                    <div className="font-medium">Smart Home</div>
                    <div className="text-sm text-gray-600">Emerging market opportunity</div>
                    <div className="text-xs text-green-600">Gap Score: 0.74</div>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>📈 Seasonal Predictions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="p-3 border rounded-lg bg-green-50">
                    <div className="font-medium">Summer Electronics</div>
                    <div className="text-sm text-gray-600">Peak in 30 days</div>
                    <div className="text-xs text-green-600">Confidence: 89%</div>
                  </div>
                  <div className="p-3 border rounded-lg bg-yellow-50">
                    <div className="font-medium">Back to School</div>
                    <div className="text-sm text-gray-600">Prepare inventory</div>
                    <div className="text-xs text-yellow-600">Confidence: 76%</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="optimization" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>📝 Title Optimization</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="p-3 border rounded-lg">
                    <div className="text-sm text-gray-600">Original:</div>
                    <div className="font-medium">Smartphone Samsung</div>
                  </div>
                  <div className="p-3 border rounded-lg bg-green-50">
                    <div className="text-sm text-gray-600">Optimized:</div>
                    <div className="font-medium">🔥 Smartphone Samsung Galaxy - ORIGINAL + FRETE GRÁTIS</div>
                    <div className="text-xs text-green-600">+23% CTR improvement</div>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>💰 Price Optimization</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="p-3 border rounded-lg">
                    <div className="text-sm text-gray-600">Current Price:</div>
                    <div className="font-medium">R$ 899,00</div>
                  </div>
                  <div className="p-3 border rounded-lg bg-blue-50">
                    <div className="text-sm text-gray-600">Optimal Price:</div>
                    <div className="font-medium">R$ 849,00</div>
                    <div className="text-xs text-blue-600">+15% revenue potential</div>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>⏰ Timing Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="p-3 border rounded-lg bg-purple-50">
                    <div className="font-medium">Best Time to Post</div>
                    <div className="text-sm text-gray-600">Tuesday, 7:00 PM</div>
                    <div className="text-xs text-purple-600">92% engagement boost</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="modules" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <ModuleCard
              title="AI Predictive"
              description="Market gap analysis & seasonal predictions"
              status="active"
              port="8004"
              icon="🧠"
            />
            <ModuleCard
              title="Dynamic Optimization"
              description="Title rewriting & price optimization"
              status="active"
              port="8005"
            />
            <ModuleCard
              title="Competitor Intelligence"
              description="Competitor analysis & strategy insights"
              status="ready"
              port="8006"
              icon="🔍"
            />
            <ModuleCard
              title="Cross-Platform"
              description="Multi-marketplace SEO orchestration"
              status="ready"
              port="8007"
              icon="🌐"
            />
            <ModuleCard
              title="Semantic Intent"
              description="Intent prediction & micro-moment optimization"
              status="ready"
              port="8008"
              icon="🎯"
            />
            <ModuleCard
              title="Trend Detector"
              description="Future trend detection & viral prediction"
              status="ready"
              port="8009"
              icon="🔮"
            />
            <ModuleCard
              title="Market Pulse"
              description="Real-time market monitoring"
              status="active"
              port="8010"
              icon="⚡"
            />
            <ModuleCard
              title="Visual SEO"
              description="Image analysis & visual optimization"
              status="ready"
              port="8011"
              icon="🎨"
            />
            <ModuleCard
              title="ChatBot Assistant"
              description="Conversational AI SEO helper"
              status="ready"
              port="8012"
              icon="🤖"
            />
            <ModuleCard
              title="ROI Prediction"
              description="ROI forecasting & budget optimization"
              status="ready"
              port="8013"
              icon="💰"
            />
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default SEOIntelligenceDashboard;