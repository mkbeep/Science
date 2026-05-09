import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import './App.css';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import JobSearch from './pages/JobSearch';
import Trends from './pages/Trends';
import SkillNetwork from './pages/SkillNetwork';

const AppContent: React.FC = () => {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <div style={{ 
      backgroundColor: '#F8FAFC', 
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* Top NavBar - CorpScale Style */}
      <header style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        zIndex: 50,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '0 32px',
        height: '64px',
        backgroundColor: '#1E3A5F',
        borderBottom: '1px solid #162D4A',
        boxShadow: '0 1px 2px rgba(15, 23, 42, 0.04)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '32px' }}>
          <span style={{ 
            fontFamily: 'Noto Serif, serif',
            fontSize: '24px', 
            fontWeight: 'bold', 
            color: '#FFFFFF'
          }}>
            Việc Làm IT Việt Nam
          </span>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '4px',
            padding: '8px 12px',
            gap: '8px',
            border: '1px solid rgba(255, 255, 255, 0.2)'
          }}>
            <span style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '18px' }}>🔍</span>
            <input 
              style={{
                backgroundColor: 'transparent',
                border: 'none',
                outline: 'none',
                color: '#FFFFFF',
                fontSize: '13px',
                width: '240px'
              }}
              placeholder="Tìm kiếm công việc, kỹ năng, công ty..." 
              type="text"
            />
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button style={{
            padding: '8px',
            borderRadius: '4px',
            backgroundColor: 'transparent',
            border: 'none',
            color: 'rgba(255, 255, 255, 0.8)',
            cursor: 'pointer',
            transition: 'all 0.15s ease'
          }}
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.1)'}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
            <span style={{ fontSize: '20px' }}>🔔</span>
          </button>
          <button style={{
            padding: '8px',
            borderRadius: '4px',
            backgroundColor: 'transparent',
            border: 'none',
            color: 'rgba(255, 255, 255, 0.8)',
            cursor: 'pointer',
            transition: 'all 0.15s ease'
          }}
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.1)'}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
            <span style={{ fontSize: '20px' }}>⚙️</span>
          </button>
          <div style={{
            height: '32px',
            width: '32px',
            borderRadius: '9999px',
            backgroundColor: '#2563EB',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#FFFFFF',
            fontWeight: '600',
            fontSize: '14px'
          }}>
            A
          </div>
        </div>
      </header>

      {/* Side NavBar - CorpScale Style */}
      <aside style={{
        position: 'fixed',
        left: 0,
        top: '64px',
        height: 'calc(100vh - 64px)',
        width: '260px',
        backgroundColor: '#FFFFFF',
        borderRight: '1px solid #E2E8F0',
        display: 'flex',
        flexDirection: 'column',
        padding: '16px 0',
        overflowY: 'auto'
      }}>
        <div style={{ padding: '0 16px', marginBottom: '24px' }}>
          <div style={{ 
            fontFamily: 'Noto Serif, serif',
            fontSize: '18px',
            fontWeight: '600',
            color: '#1E3A5F',
            marginBottom: '4px'
          }}>
            Cổng Tuyển Dụng
          </div>
          <p style={{ 
            color: '#6B7280', 
            fontSize: '12px',
            margin: 0
          }}>
            Phiên Bản Doanh Nghiệp
          </p>
        </div>

        <nav style={{ flexGrow: 1, display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <Link 
            to="/" 
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '8px 16px',
              textDecoration: 'none',
              fontSize: '14px',
              fontWeight: '500',
              transition: 'all 0.15s ease',
              backgroundColor: isActive('/') ? '#EFF6FF' : 'transparent',
              color: isActive('/') ? '#1E3A5F' : '#6B7280',
              borderLeft: isActive('/') ? '2px solid #1E3A5F' : '2px solid transparent'
            }}
            onMouseEnter={(e) => {
              if (!isActive('/')) {
                e.currentTarget.style.backgroundColor = '#F8FAFC';
              }
            }}
            onMouseLeave={(e) => {
              if (!isActive('/')) {
                e.currentTarget.style.backgroundColor = 'transparent';
              }
            }}
          >
            <span style={{ fontSize: '20px' }}>📊</span>
            <span>Dashboard</span>
          </Link>

          <Link 
            to="/analytics" 
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '8px 16px',
              textDecoration: 'none',
              fontSize: '14px',
              fontWeight: '500',
              transition: 'all 0.15s ease',
              backgroundColor: isActive('/analytics') ? '#EFF6FF' : 'transparent',
              color: isActive('/analytics') ? '#1E3A5F' : '#6B7280',
              borderLeft: isActive('/analytics') ? '2px solid #1E3A5F' : '2px solid transparent'
            }}
            onMouseEnter={(e) => {
              if (!isActive('/analytics')) {
                e.currentTarget.style.backgroundColor = '#F8FAFC';
              }
            }}
            onMouseLeave={(e) => {
              if (!isActive('/analytics')) {
                e.currentTarget.style.backgroundColor = 'transparent';
              }
            }}
          >
            <span style={{ fontSize: '20px' }}>📈</span>
            <span>Phân Tích</span>
          </Link>

          <Link 
            to="/search" 
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '8px 16px',
              textDecoration: 'none',
              fontSize: '14px',
              fontWeight: '500',
              transition: 'all 0.15s ease',
              backgroundColor: isActive('/search') ? '#EFF6FF' : 'transparent',
              color: isActive('/search') ? '#1E3A5F' : '#6B7280',
              borderLeft: isActive('/search') ? '2px solid #1E3A5F' : '2px solid transparent'
            }}
            onMouseEnter={(e) => {
              if (!isActive('/search')) {
                e.currentTarget.style.backgroundColor = '#F8FAFC';
              }
            }}
            onMouseLeave={(e) => {
              if (!isActive('/search')) {
                e.currentTarget.style.backgroundColor = 'transparent';
              }
            }}
          >
            <span style={{ fontSize: '20px' }}>🔍</span>
            <span>Tìm Việc</span>
          </Link>

          <Link 
            to="/trends" 
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '8px 16px',
              textDecoration: 'none',
              fontSize: '14px',
              fontWeight: '500',
              transition: 'all 0.15s ease',
              backgroundColor: isActive('/trends') ? '#EFF6FF' : 'transparent',
              color: isActive('/trends') ? '#1E3A5F' : '#6B7280',
              borderLeft: isActive('/trends') ? '2px solid #1E3A5F' : '2px solid transparent'
            }}
            onMouseEnter={(e) => {
              if (!isActive('/trends')) {
                e.currentTarget.style.backgroundColor = '#F8FAFC';
              }
            }}
            onMouseLeave={(e) => {
              if (!isActive('/trends')) {
                e.currentTarget.style.backgroundColor = 'transparent';
              }
            }}
          >
            <span style={{ fontSize: '20px' }}>📉</span>
            <span>Xu Hướng Công Nghệ</span>
          </Link>

          <Link 
            to="/skill-network" 
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '8px 16px',
              textDecoration: 'none',
              fontSize: '14px',
              fontWeight: '500',
              transition: 'all 0.15s ease',
              backgroundColor: isActive('/skill-network') ? '#EFF6FF' : 'transparent',
              color: isActive('/skill-network') ? '#1E3A5F' : '#6B7280',
              borderLeft: isActive('/skill-network') ? '2px solid #1E3A5F' : '2px solid transparent'
            }}
            onMouseEnter={(e) => {
              if (!isActive('/skill-network')) {
                e.currentTarget.style.backgroundColor = '#F8FAFC';
              }
            }}
            onMouseLeave={(e) => {
              if (!isActive('/skill-network')) {
                e.currentTarget.style.backgroundColor = 'transparent';
              }
            }}
          >
            <span style={{ fontSize: '20px' }}>🔗</span>
            <span>Skill Network</span>
          </Link>
        </nav>

        <div style={{ 
          marginTop: 'auto', 
          borderTop: '1px solid #E2E8F0',
          paddingTop: '16px',
          display: 'flex',
          flexDirection: 'column',
          gap: '4px'
        }}>
          <a style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '8px 16px',
            textDecoration: 'none',
            fontSize: '14px',
            fontWeight: '500',
            color: '#6B7280',
            transition: 'all 0.15s ease'
          }}
          href="#"
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#F8FAFC'}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
            <span style={{ fontSize: '20px' }}>❓</span>
            <span>Hỗ Trợ</span>
          </a>
          <a style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '8px 16px',
            textDecoration: 'none',
            fontSize: '14px',
            fontWeight: '500',
            color: '#6B7280',
            transition: 'all 0.15s ease'
          }}
          href="#"
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#F8FAFC'}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
            <span style={{ fontSize: '20px' }}>⚙️</span>
            <span>Cài Đặt</span>
          </a>
        </div>
      </aside>

      {/* Main Content */}
      <main style={{ 
        marginLeft: '260px', 
        paddingTop: '64px',
        minHeight: '100vh'
      }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/search" element={<JobSearch />} />
          <Route path="/trends" element={<Trends />} />
          <Route path="/skill-network" element={<SkillNetwork />} />
        </Routes>
      </main>

      {/* Footer */}
      <footer style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '16px 32px',
        marginLeft: '260px',
        backgroundColor: '#FFFFFF',
        borderTop: '1px solid #E2E8F0',
        fontSize: '12px'
      }}>
        <div style={{ 
          color: '#6B7280',
          fontWeight: '600',
          textTransform: 'uppercase',
          letterSpacing: '0.05em'
        }}>
          © 2026 Việc Làm IT Việt Nam. Nền Tảng Phân Tích Doanh Nghiệp.
        </div>
        <div style={{ display: 'flex', gap: '24px' }}>
          <a style={{
            color: '#6B7280',
            textDecoration: 'none',
            fontWeight: '600',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            transition: 'color 0.15s ease'
          }}
          href="#"
          onMouseEnter={(e) => e.currentTarget.style.color = '#2563EB'}
          onMouseLeave={(e) => e.currentTarget.style.color = '#6B7280'}>
            Trạng Thái API
          </a>
          <a style={{
            color: '#6B7280',
            textDecoration: 'none',
            fontWeight: '600',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            transition: 'color 0.15s ease'
          }}
          href="#"
          onMouseEnter={(e) => e.currentTarget.style.color = '#2563EB'}
          onMouseLeave={(e) => e.currentTarget.style.color = '#6B7280'}>
            Tài Liệu
          </a>
          <a style={{
            color: '#6B7280',
            textDecoration: 'none',
            fontWeight: '600',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            transition: 'color 0.15s ease'
          }}
          href="#"
          onMouseEnter={(e) => e.currentTarget.style.color = '#2563EB'}
          onMouseLeave={(e) => e.currentTarget.style.color = '#6B7280'}>
            Hỗ Trợ
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
