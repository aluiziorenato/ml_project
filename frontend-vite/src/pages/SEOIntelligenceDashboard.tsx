import React, { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  Tabs,
  Tab,
  Box,
} from "@mui/material";

interface Alert {
  id: number;
  message: string;
  severity: string;
}

interface MarketData {
  totalAnalyses: number;
  activeAlerts: number;
  opportunitiesFound: number;
  avgROI: string;
}

interface HeatmapData {
  [key: string]: number;
}

const SEOIntelligenceDashboard: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<number>(0);
  const [marketData, setMarketData] = useState<MarketData>({
    totalAnalyses: 0,
    activeAlerts: 0,
    opportunitiesFound: 0,
    avgROI: "0%",
  });
  const [heatmapData, setHeatmapData] = useState<HeatmapData>({});
  const [alerts, setAlerts] = useState<Alert[]>([]);

  useEffect(() => {
    // Simulação de carregamento de dados
    setTimeout(() => {
      setMarketData({
        totalAnalyses: 120,
        activeAlerts: 3,
        opportunitiesFound: 8,
        avgROI: "17%",
      });
      setHeatmapData({
        "Smartphone": 80,
        "Notebook": 65,
        "Fone": 50,
        "TV": 40,
      });
      setAlerts([
        { id: 1, message: "Oportunidade de otimização de título", severity: "info" },
        { id: 2, message: "Concorrente reduziu preço", severity: "warning" },
        { id: 3, message: "Nova tendência detectada", severity: "success" },
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  const HeatmapCard: React.FC<{ data: HeatmapData }> = ({ data }) => (
    <Card>
      <CardHeader>
        <Box fontWeight="bold" fontSize={18}>SEO Heatmap</Box>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {Object.entries(data).map(([key, value]) => (
            <div key={key} className="flex justify-between">
              <span className="font-medium">{key}</span>
              <span className="text-blue-600">{value}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );

  const AlertsCard: React.FC<{ alerts: Alert[] }> = ({ alerts }) => (
    <Card>
      <CardHeader>
        <Box fontWeight="bold" fontSize={18}>SEO Alerts</Box>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2">
          {alerts.map((alert) => (
            <li key={alert.id} className={`p-2 rounded ${
              alert.severity === "info"
                ? "bg-blue-50 text-blue-800"
                : alert.severity === "warning"
                ? "bg-yellow-50 text-yellow-800"
                : "bg-green-50 text-green-800"
            }`}>
              {alert.message}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );

  const OverviewCards: React.FC<{ data: MarketData }> = ({ data }) => (
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

  interface ModuleCardProps {
    title: string;
    description: string;
    status: string;
    port: string;
    icon?: string;
  }

  const ModuleCard: React.FC<ModuleCardProps> = ({ title, description, status, port, icon }) => (
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
            status === "active"
              ? "bg-green-100 text-green-800"
              : status === "ready"
              ? "bg-blue-100 text-blue-800"
              : "bg-gray-100 text-gray-800"
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
        <h1 className="text-3xl font-bold text-gray-900 mb-2">🧠 SEO Intelligence Dashboard</h1>
        <p className="text-gray-600">Complete AI-powered SEO system for e-commerce optimization</p>
      </div>
      <OverviewCards data={marketData} />
      <Box sx={{ width: '100%', mb: 2 }}>
        <Tabs value={activeTab} onChange={(_e, val) => setActiveTab(val)} aria-label="SEO Dashboard Tabs">
          <Tab label="Overview" />
          <Tab label="Market Pulse" />
          <Tab label="AI Predictive" />
          <Tab label="Optimization" />
          <Tab label="All Modules" />
        </Tabs>
      </Box>
      {activeTab === 0 && (
        <Box className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <HeatmapCard data={heatmapData} />
            <AlertsCard alerts={alerts} />
          </div>
        </Box>
      )}
      {activeTab === 1 && (
        <Box className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-2">
              <CardHeader>
                <Box fontWeight="bold" fontSize={18}>⚡ Real-Time Market Pulse</Box>
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
        </Box>
      )}
      {activeTab === 2 && (
        <Box className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <Box fontWeight="bold" fontSize={18}>🔮 Market Gap Analysis</Box>
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
                <Box fontWeight="bold" fontSize={18}>📈 Seasonal Predictions</Box>
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
        </Box>
      )}
      {activeTab === 3 && (
        <Box className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <Box fontWeight="bold" fontSize={18}>📝 Title Optimization</Box>
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
                <Box fontWeight="bold" fontSize={18}>💰 Price Optimization</Box>
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
                <Box fontWeight="bold" fontSize={18}>⏰ Timing Analysis</Box>
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
        </Box>
      )}
      {activeTab === 4 && (
        <Box className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <ModuleCard title="AI Predictive" description="Market gap analysis & seasonal predictions" status="active" port="8004" icon="🧠" />
            <ModuleCard title="Dynamic Optimization" description="Title rewriting & price optimization" status="active" port="8005" />
            <ModuleCard title="Competitor Intelligence" description="Competitor analysis & strategy insights" status="ready" port="8006" icon="🔍" />
            <ModuleCard title="Cross-Platform" description="Multi-marketplace SEO orchestration" status="ready" port="8007" icon="🌐" />
            <ModuleCard title="Semantic Intent" description="Intent prediction & micro-moment optimization" status="ready" port="8008" icon="🎯" />
            <ModuleCard title="Trend Detector" description="Future trend detection & viral prediction" status="ready" port="8009" icon="🔮" />
            <ModuleCard title="Market Pulse" description="Real-time market monitoring" status="active" port="8010" icon="⚡" />
            <ModuleCard title="Visual SEO" description="Image analysis & visual optimization" status="ready" port="8011" icon="🎨" />
            <ModuleCard title="ChatBot Assistant" description="Conversational AI SEO helper" status="ready" port="8012" icon="🤖" />
            <ModuleCard title="ROI Prediction" description="ROI forecasting & budget optimization" status="ready" port="8013" icon="💰" />
          </div>
        </Box>
      )}
    </div>
  );
};

export default SEOIntelligenceDashboard;
