import React from 'react';
import {
    CartesianGrid,
    Line,
    LineChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from 'recharts';

const data = [
  { date: '5/1/2010', close: 7.1 },
  { date: '10/1/2010', close: 10.2 },
  { date: '3/1/2011', close: 13.5 },
  { date: '8/1/2011', close: 14.3 },
  { date: '1/1/2012', close: 20.1 },
  { date: '6/1/2012', close: 23.5 },
  { date: '12/1/2012', close: 18.9 },
];

const StockDashboard = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 p-4 md:p-8 fade-in">
      {/* Chart Section */}
      <section className="bg-white/10 dark:bg-zinc-900/40 backdrop-blur-md backdrop-saturate-150 border border-white/20 dark:border-zinc-800 p-6 rounded-xl shadow-md transition">
        <h2 className="text-lg md:text-xl font-semibold text-white mb-4">
          Stock Price Over Time
        </h2>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="close"
              stroke="#60a5fa"
              strokeWidth={2}
              dot={{ r: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </section>

      {/* Info Section */}
      <section className="bg-white/10 dark:bg-zinc-900/40 backdrop-blur-md backdrop-saturate-150 border border-white/20 dark:border-zinc-800 p-6 rounded-xl shadow-md transition text-white">
        <div className="mb-4">
          <h2 className="text-lg md:text-xl font-semibold">AAPL – Summary</h2>
          <p className="text-sm text-zinc-300">As of April 29, 2025</p>
        </div>

        <div className="space-y-2 text-sm text-white/90">
          <div className="flex justify-between"><span>Open</span><span>$193.62</span></div>
          <div className="flex justify-between"><span>High</span><span>$194.85</span></div>
          <div className="flex justify-between"><span>Low</span><span>$192.43</span></div>
          <div className="flex justify-between"><span>Close</span><span>$193.58</span></div>
          <div className="flex justify-between"><span>Volume</span><span>28.3M</span></div>
          <div className="flex justify-between text-red-400">
            <span>Change</span><span>-0.04 (-0.02%)</span>
          </div>
          <div className="flex justify-between items-center">
            <span>Risk Estimate</span>
            <span className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full bg-yellow-400 animate-pulse"></span>
              Medium (86)
            </span>
          </div>
        </div>

        <div className="mt-6">
          <h3 className="text-sm font-semibold mb-2">Risk Factors</h3>
          <ul className="list-disc list-inside text-zinc-200 text-sm space-y-1">
            <li>Market volatility</li>
            <li>Upcoming earnings report</li>
            <li>Sector rotation</li>
          </ul>
        </div>
      </section>
    </div>
  );
};

export default StockDashboard;
