import React from 'react';

const ProductCard = ({ product, onAddToCart }) => {
  return (
    <div className="product-card">
      <img src={product.image} alt={product.name} />
      <h3>{product.name}</h3>
      <p>{product.category}</p>
      <p>{product.price} Coins</p>
      <button onClick={() => onAddToCart(product._id)}>Add to Cart</button>
    </div>
  );
};

export default ProductCard;
