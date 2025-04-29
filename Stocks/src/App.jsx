import React from 'react';
import HeroSection from '../components/HeroSection';
import InsightsDashboard from '../components/Insights';
import StockDashboard from '../components/StockDashboard';
import logo from './assets/Stock.png';
import './App.css';

const App = () => {
  return (
    <div className="w-full min-h-screen bg-neutral-900 text-white relative overflow-hidden">
      {/* Glass animated background grid */}
      <div className="absolute inset-0 bg-[radial-gradient(#00ffff10_1px,transparent_1px)] bg-[size:40px_40px] animate-pan z-0" />

      <div className="relative z-10">
        {/* Header with glass effect */}
        <header className="w-full flex flex-col md:flex-row items-center justify-between px-4 sm:px-6 lg:px-12 py-4 bg-white/5 border-b border-white/10 backdrop-blur-md shadow-md">
          <div className="flex items-center gap-3 mb-4 md:mb-0">
            <img
              src={logo}
              alt="StockTracker Logo"
              className="w-10 h-10 object-contain animate-float"
            />
            <h1 className="text-2xl sm:text-3xl font-bold tracking-wide glow-text">StockTracker</h1>
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-2">
            <input
              className="w-full sm:w-auto px-4 py-2 rounded-md text-gray-200 outline-none focus:ring-2 ring-cyan-400 bg-black/20 placeholder-gray-400"
              type="text"
              placeholder="Search Stock..."
            />
            <button className="w-full sm:w-auto px-4 py-2 bg-cyan-600 hover:bg-cyan-700 transition rounded-md">
              Search
            </button>
          </div>

          <div className="flex gap-4 mt-4 md:mt-0">
            <a href="#" className="hover:underline text-cyan-300">Login</a>
            <a href="#" className="hover:underline text-cyan-300">Sign Up</a>
          </div>
        </header>

        {/* Hero Section with glass card */}
        <section className="w-full px-4 sm:px-6 lg:px-12 py-6 flex flex-col items-center text-center">
          <div className="w-full max-w-5xl bg-white/5 border border-white/10 backdrop-blur-md rounded-xl shadow p-6 animate-float">
            <HeroSection />
          </div>
        </section>

        {/* Dashboard Sections */}
        <main className="w-full px-4 sm:px-6 lg:px-12 pb-12 space-y-6">
          <div className="bg-white/5 border border-white/10 rounded-xl p-4 sm:p-6 shadow backdrop-blur-md hover:shadow-cyan-400/30 transition">
            <StockDashboard />
          </div>

          <div className="bg-white/5 border border-white/10 rounded-xl p-4 sm:p-6 shadow backdrop-blur-md hover:shadow-cyan-400/30 transition">
            <InsightsDashboard />
          </div>
        </main>
      </div>
    </div>
  );

  
};

export default App;
