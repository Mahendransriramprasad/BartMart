import React, { useState, useEffect } from 'react';
import { getAllProducts, approveProduct, rejectProduct } from '../services/api';
import AdminProductCard from '../components/AdminProductCard';

const AdminDashboard = () => {
  const [products, setProducts] = useState([]);
  const [pendingProducts, setPendingProducts] = useState([]);

  useEffect(() => {
    const fetchProducts = async () => {
      const data = await getAllProducts();
      setProducts(data.all_products);
      setPendingProducts(data.sell_requests);
    };

    fetchProducts();
  }, []);

  const handleApprove = (productId) => {
    setPendingProducts(prev => prev.filter(product => product._id !== productId));
  };

  const handleReject = (productId) => {
    setPendingProducts(prev => prev.filter(product => product._id !== productId));
  };

  return (
    <div>
      <h1>Admin Dashboard</h1>
      <h2>Pending Products</h2>
      <div>
        {pendingProducts.map(product => (
          <AdminProductCard key={product._id} product={product} onApprove={handleApprove} onReject={handleReject} />
        ))}
      </div>
    </div>
  );
};

export default AdminDashboard;
