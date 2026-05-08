import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import JobSearch from './pages/JobSearch';
import Trends from './pages/Trends';

const AppContent: React.FC = () => {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Top NavBar */}
      <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-6 h-16 bg-white border-b border-gray-200 shadow-sm">
        <div className="flex items-center gap-8">
          <span className="text-lg font-bold text-blue-600">IT Jobs Vietnam</span>
          <div className="hidden md:flex items-center bg-gray-100 rounded-lg px-4 py-2 gap-2">
            <span className="material-symbols-outlined text-gray-500">search</span>
            <input 
              className="bg-transparent border-none focus:ring-0 text-sm w-64 outline-none" 
              placeholder="Global search..." 
              type="text"
            />
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex gap-2">
            <button className="p-2 rounded-full hover:bg-gray-100 transition-colors">
              <span className="material-symbols-outlined text-gray-600">notifications</span>
            </button>
            <button className="p-2 rounded-full hover:bg-gray-100 transition-colors">
              <span className="material-symbols-outlined text-gray-600">settings</span>
            </button>
          </div>
          <div className="h-8 w-8 rounded-full bg-blue-200 overflow-hidden">
            <img 
              alt="User profile" 
              className="h-full w-full object-cover" 
              src="https://ui-avatars.com/api/?name=Admin&background=3b82f6&color=fff"
            />
          </div>
        </div>
      </header>

      {/* Side NavBar */}
      <aside className="fixed left-0 top-16 h-[calc(100vh-64px)] w-[260px] bg-white border-r border-gray-200 flex flex-col py-4 overflow-y-auto">
        <div className="px-4 mb-6">
          <div className="flex items-center gap-2 mb-1">
            <span className="material-symbols-outlined text-blue-600 text-3xl" style={{ fontVariationSettings: "'FILL' 1" }}>
              work
            </span>
            <span className="text-lg font-bold text-blue-600">Recruiter Portal</span>
          </div>
          <p className="text-gray-500 text-sm opacity-70">Enterprise Edition</p>
        </div>

        <nav className="flex-grow space-y-1">
          <Link 
            to="/" 
            className={`flex items-center gap-4 px-4 py-2 transition-all ${
              isActive('/') 
                ? 'bg-blue-100 text-blue-700 border-l-4 border-blue-600' 
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <span className="material-symbols-outlined">dashboard</span>
            <span className="font-medium">Dashboard</span>
          </Link>

          <Link 
            to="/analytics" 
            className={`flex items-center gap-4 px-4 py-2 transition-all ${
              isActive('/analytics') 
                ? 'bg-blue-100 text-blue-700 border-l-4 border-blue-600' 
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <span className="material-symbols-outlined">analytics</span>
            <span className="font-medium">Analytics</span>
          </Link>

          <Link 
            to="/search" 
            className={`flex items-center gap-4 px-4 py-2 transition-all ${
              isActive('/search') 
                ? 'bg-blue-100 text-blue-700 border-l-4 border-blue-600' 
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <span className="material-symbols-outlined">search</span>
            <span className="font-medium">Job Search</span>
          </Link>

          <Link 
            to="/trends" 
            className={`flex items-center gap-4 px-4 py-2 transition-all ${
              isActive('/trends') 
                ? 'bg-blue-100 text-blue-700 border-l-4 border-blue-600' 
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <span className="material-symbols-outlined">trending_up</span>
            <span className="font-medium">Technology Trends</span>
          </Link>
        </nav>

        <div className="mt-auto border-t border-gray-200 pt-4 space-y-1">
          <a className="flex items-center gap-4 text-gray-600 px-4 py-2 hover:bg-gray-100 transition-all" href="#">
            <span className="material-symbols-outlined">help</span>
            <span className="font-medium">Support</span>
          </a>
          <a className="flex items-center gap-4 text-gray-600 px-4 py-2 hover:bg-gray-100 transition-all" href="#">
            <span className="material-symbols-outlined">settings</span>
            <span className="font-medium">Settings</span>
          </a>
        </div>
      </aside>

      {/* Main Content */}
      <main className="ml-[260px] pt-16 min-h-screen">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/search" element={<JobSearch />} />
          <Route path="/trends" element={<Trends />} />
        </Routes>
      </main>

      {/* Footer */}
      <footer className="flex justify-between items-center px-6 py-4 ml-[260px] bg-white border-t border-gray-200">
        <div className="text-gray-500 text-xs font-semibold uppercase tracking-wider">
          © 2026 IT Jobs Vietnam. Data-driven Recruitment Excellence.
        </div>
        <div className="flex gap-6">
          <a className="text-xs font-semibold uppercase tracking-wider text-gray-500 hover:text-blue-600 transition-colors" href="#">
            Crawler Status
          </a>
          <a className="text-xs font-semibold uppercase tracking-wider text-gray-500 hover:text-blue-600 transition-colors" href="#">
            React Frontend
          </a>
          <a className="text-xs font-semibold uppercase tracking-wider text-gray-500 hover:text-blue-600 transition-colors" href="#">
            Flask API
          </a>
        </div>
      </footer>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <Router>
      <AppContent />
    </Router>
  );
};

export default App;
