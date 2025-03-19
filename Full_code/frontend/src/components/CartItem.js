import React from 'react';

const CartItem = ({ item, onRemoveFromCart, onUpdateQuantity }) => {
  return (
    <div className="cart-item">
      <img src={item.image} alt={item.name} />
      <h4>{item.name}</h4>
      <p>{item.price} Coins</p>
      <p>Quantity: {item.quantity}</p>
      <button onClick={() => onRemoveFromCart(item._id)}>Remove</button>
      <button onClick={() => onUpdateQuantity(item._id, 'increase')}>Increase</button>
      <button onClick={() => onUpdateQuantity(item._id, 'decrease')}>Decrease</button>
    </div>
  );
};

export default CartItem;