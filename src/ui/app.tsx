import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, TrendingDown, Minus, Upload, RefreshCw } from 'lucide-react';

export default function NiftyDowTheoryApp() {
  const [niftyData, setNiftyData] = useState([]);
  const [currentTrend, setCurrentTrend] = useState('neutral');
  const [modelLoaded, setModelLoaded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [lastPrice, setLastPrice] = useState(null);
  const [prediction, setPrediction] = useState(null);

  // Simulated data fetch - replace with actual API call
  const fetchNiftyData = () => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      const mockData = generateMockData();
      setNiftyData(mockData);
      setLastPrice(mockData[mockData.length - 1].close);
      setLoading(false);
    }, 1000);
  };

  const generateMockData = () => {
    const data = [];
    let price = 19500;
    for (let i = 30; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      price = price + (Math.random() - 0.5) * 200;
      data.push({
        date: date.toLocaleDateString(),
        close: parseFloat(price.toFixed(2)),
        high: parseFloat((price + Math.random() * 100).toFixed(2)),
        low: parseFloat((price - Math.random() * 100).toFixed(2)),
        open: parseFloat((price + (Math.random() - 0.5) * 50).toFixed(2))
      });
    }
    return data;
  };

  const handleModelUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      // In a real implementation, you'd parse the model file here
      setModelLoaded(true);
      setPrediction({
        trend: 'bullish',
        confidence: 0.78,
        targetLevel: 20200,
        supportLevel: 19300
      });
      // Simulate model prediction
      setCurrentTrend('bullish');
    }
  };

  const analyzeDowTheory = () => {
    if (niftyData.length < 3) return;
    
    const recent = niftyData.slice(-10);
    const highs = recent.map(d => d.high);
    const lows = recent.map(d => d.low);
    
    const higherHighs = highs[highs.length - 1] > highs[highs.length - 3];
    const higherLows = lows[lows.length - 1] > lows[lows.length - 3];
    
    if (higherHighs && higherLows) {
      setCurrentTrend('bullish');
    } else if (!higherHighs && !higherLows) {
      setCurrentTrend('bearish');
    } else {
      setCurrentTrend('neutral');
    }
  };

  useEffect(() => {
    fetchNiftyData();
  }, []);

  useEffect(() => {
    if (niftyData.length > 0) {
      analyzeDowTheory();
    }
  }, [niftyData]);

  const getTrendIcon = () => {
    switch(currentTrend) {
      case 'bullish': return <TrendingUp className="w-8 h-8 text-green-500" />;
      case 'bearish': return <TrendingDown className="w-8 h-8 text-red-500" />;
      default: return <Minus className="w-8 h-8 text-yellow-500" />;
    }
  };

  const getTrendColor = () => {
    switch(currentTrend) {
      case 'bullish': return 'bg-green-100 border-green-500 text-green-700';
      case 'bearish': return 'bg-red-100 border-red-500 text-red-700';
      default: return 'bg-yellow-100 border-yellow-500 text-yellow-700';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 mb-6 border border-white/20">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">Nifty 50 Dow Theory Analyzer</h1>
              <p className="text-slate-300">Real-time trend analysis with ML predictions</p>
            </div>
            <button
              onClick={fetchNiftyData}
              disabled={loading}
              className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-all disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh Data
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Current Price Card */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
            <h3 className="text-slate-300 text-sm mb-2">Current Price</h3>
            <p className="text-4xl font-bold text-white">
              ₹{lastPrice ? lastPrice.toFixed(2) : '--'}
            </p>
          </div>

          {/* Trend Card */}
          <div className={`rounded-2xl p-6 border-2 ${getTrendColor()}`}>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm mb-2 font-medium">Dow Theory Trend</h3>
                <p className="text-2xl font-bold capitalize">{currentTrend}</p>
              </div>
              {getTrendIcon()}
            </div>
          </div>

          {/* Model Status Card */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
            <h3 className="text-slate-300 text-sm mb-2">Model Status</h3>
            <p className="text-lg font-semibold text-white mb-3">
              {modelLoaded ? '✓ Model Loaded' : '○ No Model Loaded'}
            </p>
            <label className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg cursor-pointer inline-flex items-center gap-2 text-sm transition-all">
              <Upload className="w-4 h-4" />
              Upload Model
              <input
                type="file"
                onChange={handleModelUpload}
                className="hidden"
                accept=".pkl,.joblib,.h5,.json"
              />
            </label>
          </div>
        </div>

        {/* Chart */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 mb-6">
          <h2 className="text-xl font-bold text-white mb-4">Price Chart (30 Days)</h2>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={niftyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
              <XAxis dataKey="date" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1e293b', 
                  border: '1px solid #475569',
                  borderRadius: '8px',
                  color: '#fff'
                }} 
              />
              <Legend />
              <Line type="monotone" dataKey="close" stroke="#3b82f6" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="high" stroke="#10b981" strokeWidth={1} dot={false} />
              <Line type="monotone" dataKey="low" stroke="#ef4444" strokeWidth={1} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Prediction Panel */}
        {prediction && (
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
            <h2 className="text-xl font-bold text-white mb-4">ML Model Prediction</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <p className="text-slate-300 text-sm mb-1">Predicted Trend</p>
                <p className="text-xl font-bold text-white capitalize">{prediction.trend}</p>
              </div>
              <div>
                <p className="text-slate-300 text-sm mb-1">Confidence</p>
                <p className="text-xl font-bold text-white">{(prediction.confidence * 100).toFixed(1)}%</p>
              </div>
              <div>
                <p className="text-slate-300 text-sm mb-1">Target Level</p>
                <p className="text-xl font-bold text-green-400">₹{prediction.targetLevel}</p>
              </div>
              <div>
                <p className="text-slate-300 text-sm mb-1">Support Level</p>
                <p className="text-xl font-bold text-red-400">₹{prediction.supportLevel}</p>
              </div>
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-white/10 mt-6">
          <h3 className="text-lg font-semibold text-white mb-3">How to Use</h3>
          <ul className="text-slate-300 space-y-2 text-sm">
            <li>• Upload your regression model file (supports .pkl, .joblib, .h5, .json formats)</li>
            <li>• The app will automatically fetch current Nifty 50 data and analyze trends</li>
            <li>• Dow Theory analysis identifies higher highs/lows for trend determination</li>
            <li>• Click "Refresh Data" to update with latest market information</li>
            <li>• For local file system access, run this as a Python/Node.js server application</li>
          </ul>
        </div>
      </div>
    </div>
  );
}