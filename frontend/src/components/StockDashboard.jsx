import React, { useState, useEffect } from 'react';
import axios from 'axios';
import StockGraph from './graph';
import { useLocation } from 'react-router-dom';

const StockDetailsPanel = ({ selectedStock }) => {
  const [stockDetails, setStockDetails] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchStockDetails = async () => {
    if (!selectedStock) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const symbol = selectedStock.toUpperCase();
      console.log('Fetching data for symbol:', symbol);
      
      // Get today's date and one year ago
      const today = new Date();
      const oneYearAgo = new Date();
      oneYearAgo.setFullYear(today.getFullYear() - 1);
      
      const response = await axios.get(`http://localhost:8000/api/stock-data`, {
        params: {
          symbol,
          start_date: oneYearAgo.toISOString().split('T')[0],
          end_date: today.toISOString().split('T')[0],
          aggregate: 'daily'
        }
      });
      
      console.log('API Response:', response.data);
      
      if (response.data && response.data.data && response.data.data.length > 0) {
        const data = response.data.data[0];
        setStockDetails({
          currentPrice: data.avg_close,
          open: data.avg_close,
          high: data.avg_close,
          low: data.avg_close,
          volume: 'N/A',
          riskScore: 'N/A',
          prediction: 'N/A'
        });
      } else {
        setError('No data available for this stock');
      }
    } catch (err) {
      console.error('Error fetching stock details:', err);
      setError('Failed to fetch stock data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStockDetails();
  }, [selectedStock]);

  return (
    <div className="flex flex-col h-full">
      <div className="bg-white/10 backdrop-blur-md backdrop-saturate-150 border border-white/20 p-6 rounded-xl shadow-md flex-1">
        <h2 className="text-xl font-semibold text-white mb-4">{selectedStock} - Stock Details</h2>
        
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
          </div>
        ) : error ? (
          <div className="text-red-500 text-center p-4">
            {error}
            <button
              onClick={fetchStockDetails}
              className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Retry
            </button>
          </div>
        ) : stockDetails ? (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-white/5 p-2.5 rounded-lg">
                <p className="text-white/60 text-xs">Current Price</p>
                <p className="text-white text-base font-medium">${stockDetails.currentPrice?.toFixed(2) || 'N/A'}</p>
              </div>
              <div className="bg-white/5 p-2.5 rounded-lg">
                <p className="text-white/60 text-xs">Open</p>
                <p className="text-white text-base font-medium">${stockDetails.open?.toFixed(2) || 'N/A'}</p>
              </div>
              <div className="bg-white/5 p-2.5 rounded-lg">
                <p className="text-white/60 text-xs">High</p>
                <p className="text-white text-base font-medium">${stockDetails.high?.toFixed(2) || 'N/A'}</p>
              </div>
              <div className="bg-white/5 p-2.5 rounded-lg">
                <p className="text-white/60 text-xs">Low</p>
                <p className="text-white text-base font-medium">${stockDetails.low?.toFixed(2) || 'N/A'}</p>
              </div>
              <div className="bg-white/5 p-2.5 rounded-lg">
                <p className="text-white/60 text-xs">Volume</p>
                <p className="text-white text-base font-medium">{stockDetails.volume || 'N/A'}</p>
              </div>
              <div className="bg-white/5 p-2.5 rounded-lg">
                <p className="text-white/60 text-xs">Risk Score</p>
                <p className="text-white text-base font-medium">{stockDetails.riskScore || 'N/A'}</p>
              </div>
              <div className="bg-white/5 p-2.5 rounded-lg">
                <p className="text-white/60 text-xs">Prediction</p>
                <p className={`text-base font-medium ${
                  stockDetails.prediction === 'Buy' ? 'text-green-500' : 
                  stockDetails.prediction === 'Sell' ? 'text-red-500' : 
                  'text-yellow-500'
                }`}>
                  {stockDetails.prediction || 'N/A'}
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-yellow-500 text-center p-4">
            No data available for {selectedStock}
            <button
              onClick={fetchStockDetails}
              className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Retry
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

const StockDashboard = () => {
  const [selectedStock, setSelectedStock] = useState('AMZN');
  const location = useLocation();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const symbol = params.get('symbol');
    if (symbol) {
      setSelectedStock(symbol.toUpperCase());
    }
  }, [location.search]);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-2 md:p-4 h-full">
      {/* Left side - Graph */}
      <div className="flex flex-col h-full">
        <div className="bg-white/10 backdrop-blur-md backdrop-saturate-150 border border-white/20 p-4 rounded-xl shadow-md flex-1 flex flex-col">
          <StockGraph symbol={selectedStock} />
        </div>
      </div>

      {/* Right side - Stock Details */}
      <StockDetailsPanel selectedStock={selectedStock} />
    </div>
  );
};

export default StockDashboard; 