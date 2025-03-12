import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Cart = () => {
  const [cartItems, setCartItems] = useState([]);
  const [totalCost, setTotalCost] = useState(0);

  useEffect(() => {
    axios.get("http://localhost:5000/cart")
      .then(response => {
        setCartItems(response.data.cart_items);
        setTotalCost(response.data.total_cost);
      })
      .catch(error => {
        console.error("There was an error fetching the cart items!", error);
      });
  }, []);

  return (
    <div>
      <h1>Your Cart</h1>
      {cartItems.length === 0 ? (
        <p>Your cart is empty</p>
      ) : (
        <div>
          {cartItems.map(item => (
            <div key={item._id}>
              <h3>{item.name}</h3>
              <p>{item.price} coins</p>
              <p>Quantity: {item.quantity}</p>
            </div>
          ))}
          <h3>Total Cost: {totalCost} coins</h3>
        </div>
      )}
    </div>
  );
}

export default Cart;
