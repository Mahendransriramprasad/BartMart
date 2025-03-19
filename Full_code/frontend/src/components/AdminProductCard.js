import React from 'react';

const AdminProductCard = ({ product, onApprove, onReject }) => {
  return (
    <div className="admin-product-card">
      <img src={product.image} alt={product.name} />
      <h3>{product.name}</h3>
      <p>Category: {product.category}</p>
      <p>Price: ${product.price}</p>
      <div>
        <button onClick={() => onApprove(product._id)}>Approve</button>
        <button onClick={() => onReject(product._id)}>Reject</button>
      </div>
    </div>
  );
};

export default AdminProductCard;