import React from 'react';
import ReactDOM from 'react-dom/client';
import {BrowserRouter as Router,  Routes, Route} from 'react-router-dom'
import './index.css';
import Dashboard from './dashboard/Dashboard';
import Camera from './dashboard/Camera';
import Header from './dashboard/Header';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <Router>
      <Header/>
      <Routes>
        <Route
            exact
            path="/dashboard"
            element={<Dashboard />}
        >
        </Route>
        <Route
            exact
            path="/camera"
            element={<Camera />}
        >
        </Route>
      </Routes>
    </Router>
  </React.StrictMode>
);

