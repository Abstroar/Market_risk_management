import React from "react";

const InsightsDashboard = () => {
  const trendingStocks = [
    { name: "Reliance", price: "₹2456.75", change: "+2.5%", risk: 70, volume: "2.5M" },
    { name: "TCS", price: "₹3567.8", change: "-1.2%", risk: 45, volume: "1.8M" },
    { name: "HDFC", price: "₹1678.9", change: "+0.8%", risk: 65, volume: "3.2M" },
    { name: "INFY", price: "₹1456.3", change: "-0.5%", risk: 50, volume: "2.1M" },
    { name: "WIPRO", price: "₹789.45", change: "+1.7%", risk: 40, volume: "1.5M" },
  ];

  return (
    <div className="space-y-12 p-6">
            <section className="bg-white/10 backdrop-blur-md p-6 rounded-xl shadow-md">
        <h2 className="text-xl font-semibold text-white mb-4">Trending Stocks</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left text-white/90">
            <thead className="text-xs text-white/60 border-b border-white/10">
              <tr>
                <th className="py-2 px-4">Stock</th>
                <th className="py-2 px-4">Price</th>
                <th className="py-2 px-4">Change</th>
                <th className="py-2 px-4">Risk Score</th>
                <th className="py-2 px-4">Volume</th>
                <th className="py-2 px-4">Action</th>
              </tr>
            </thead>
            <tbody>
              {trendingStocks.map((stock, i) => (
                <tr key={i} className="border-b border-white/10">
                  <td className="py-2 px-4 font-medium">{stock.name}</td>
                  <td className="py-2 px-4">{stock.price}</td>
                  <td
                    className={`py-2 px-4 ${stock.change.startsWith("-") ? "text-red-400" : "text-green-400"}`}
                  >
                    {stock.change}
                  </td>
                  <td className="py-2 px-4">
                    <div className="w-24 bg-white/20 rounded-full h-2 overflow-hidden">
                      <div
                        className="bg-blue-400 h-2"
                        style={{ width: `${stock.risk}%` }}
                      ></div>
                    </div>
                  </td>
                  <td className="py-2 px-4">{stock.volume}</td>
                  <td className="py-2 px-4">
                    <button className="px-3 py-1 border border-blue-400 text-blue-400 rounded hover:bg-blue-500 hover:text-white transition text-xs">
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
  {/* Predictions + Risk Alerts */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-4 bg-white/10 border border-white/10 backdrop-blur-md rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-2 text-white">Market Prediction</h3>
          <div className="h-32 bg-blue-200/30 rounded-md animate-pulse" />
          <p className="mt-2 text-green-400 text-sm">Confidence: 92%</p>
        </div>
        <div className="p-4 bg-white/10 border border-white/10 backdrop-blur-md rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4 text-white">Risk Alerts</h3>
          <ul className="space-y-3 text-sm text-white/90">
            <li className="flex justify-between items-center bg-red-400/10 p-2 rounded-md">
              <div>
                <p className="font-semibold text-red-300">Reliance Industries</p>
                <p className="text-xs">Unusual volume spike detected</p>
              </div>
              <span className="text-xs text-white/60">10 mins ago</span>
            </li>
            <li className="flex justify-between items-center bg-yellow-300/10 p-2 rounded-md">
              <div>
                <p className="font-semibold text-yellow-200">HDFC Bank</p>
                <p className="text-xs">Volatility above average</p>
              </div>
              <span className="text-xs text-white/60">25 mins ago</span>
            </li>
            <li className="flex justify-between items-center bg-green-300/10 p-2 rounded-md">
              <div>
                <p className="font-semibold text-green-200">TCS</p>
                <p className="text-xs">Support level reached</p>
              </div>
              <span className="text-xs text-white/60">45 mins ago</span>
            </li>
          </ul>
        </div>
      </section>

      {/* Trending Stocks Table */}

    </div>
  );
};

export default InsightsDashboard;
