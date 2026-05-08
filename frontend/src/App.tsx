import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import JobSearch from './pages/JobSearch';
import Trends from './pages/Trends';

const App: React.FC = () => {
  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <div className="nav-container">
            <h1 className="nav-logo">💼 IT Jobs Vietnam</h1>
            <ul className="nav-menu">
              <li><Link to="/" className="nav-link">Dashboard</Link></li>
              <li><Link to="/analytics" className="nav-link">Analytics</Link></li>
              <li><Link to="/search" className="nav-link">Job Search</Link></li>
              <li><Link to="/trends" className="nav-link">Trends</Link></li>
            </ul>
          </div>
        </nav>

        <div className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/search" element={<JobSearch />} />
            <Route path="/trends" element={<Trends />} />
          </Routes>
        </div>

        <footer className="footer">
          <p>© 2026 IT Jobs Vietnam Dashboard | Built with React + TypeScript + Flask</p>
        </footer>
      </div>
    </Router>
  );
};

export default App;
