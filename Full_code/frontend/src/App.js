import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './components/Home';
import Login from './components/Login';
import Register from './components/Register';
import Cart from './components/Cart';
import Sell from './components/SellProduct';
import Checkout from './components/Checkout';
import Navbar from './components/Navbar';
import ProductDetails from './pages/ProductDetails';
function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/cart" element={<Cart />} />
        <Route path="/sell" element={<Sell />} />
        <Route path="/checkout" element={<Checkout />} />
        <Route path="/product/:productId" element={<ProductDetails />} />
      </Routes>
    </Router>
  );
}

export default App;
