import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import OrderList from './components/orders/OrderList';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<OrderList />} />
      </Routes>
    </Router>
  );
};

export default App; 