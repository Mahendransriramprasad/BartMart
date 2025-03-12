import React from 'react';
import { approveProduct, rejectProduct } from '../services/api';

const AdminProductCard = ({ product, onApprove, onReject }) => {
  const handleApprove = async () => {
    await approveProduct(product._id);
    onApprove(product._id);
  };

  const handleReject = async () => {
    await rejectProduct(product._id);
    onReject(product._id);
  };

  return (
    <div className="admin-product-card">
      <img src={product.image} alt={product.name} />
      <h3>{product.name}</h3>
      <p>Category: {product.category}</p>
      <p>Price: ${product.price}</p>
      <div>
        <button onClick={handleApprove}>Approve</button>
        <button onClick={handleReject}>Reject</button>
      </div>
    </div>
  );
};

export default AdminProductCard;
