import React from 'react';
import ReactDOM from 'react-dom/client';
import HotelSearch from './HotelSearch';
import HotelSearchTest from './HotelSearchTest';
import './index.css';

const testMode = new URLSearchParams(window.location.search).has('test');

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {testMode ? <HotelSearchTest /> : <HotelSearch />}
  </React.StrictMode>
);
