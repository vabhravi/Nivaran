/**
 * NIVARAN — App Root Component
 * Single-page app with React Router for navigation between modules.
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Home from './pages/Home';
import CivicEase from './pages/CivicEase';
import RentRight from './pages/RentRight';

function Navbar() {
  const location = useLocation();

  return (
    <nav className="navbar" id="main-navbar">
      <Link to="/" className="navbar-brand">NIVARAN</Link>
      <ul className="navbar-links">
        <li>
          <Link
            to="/"
            className={location.pathname === '/' ? 'active' : ''}
            id="nav-home"
          >
            Home
          </Link>
        </li>
        <li>
          <Link
            to="/civic-ease"
            className={location.pathname === '/civic-ease' ? 'active' : ''}
            id="nav-civic-ease"
          >
            🏛️ Civic-Ease
          </Link>
        </li>
        <li>
          <Link
            to="/rent-right"
            className={location.pathname === '/rent-right' ? 'active' : ''}
            id="nav-rent-right"
          >
            🏠 Rent-Right
          </Link>
        </li>
      </ul>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/civic-ease" element={<CivicEase />} />
        <Route path="/rent-right" element={<RentRight />} />
      </Routes>
      <footer className="footer">
        <p>NIVARAN © 2025 — AI-Powered Civic & Legal Companion for Digital Inclusion</p>
        <p style={{ marginTop: '4px', fontSize: '0.8rem' }}>
          This tool provides information, not legal advice. Consult a qualified lawyer for legal decisions.
        </p>
      </footer>
    </Router>
  );
}

export default App;
