import React, { useEffect, useState } from 'react';
import axios from 'axios';
import CartItem from './CartItem';

const Cart = () => {
  const [cartItems, setCartItems] = useState([]);
  const [totalCost, setTotalCost] = useState(0);

  // Fetch cart items from the backend
  useEffect(() => {
    const fetchCart = async () => {
      try {
        const response = await axios.get('http://localhost:5000/cart', {
          withCredentials: true, // Include cookies for session management
        });
        setCartItems(response.data.cart_items);
        setTotalCost(response.data.total_cost);
      } catch (error) {
        console.error('Error fetching cart:', error);
      }
    };

    fetchCart();
  }, []);

  // Remove an item from the cart
  const handleRemoveFromCart = async (productId) => {
    try {
      await axios.post(
        `http://localhost:5000/remove_from_cart/${productId}`,
        {},
        { withCredentials: true }
      );
      // Update the cart items state
      setCartItems((prev) => prev.filter((item) => item._id !== productId));
    } catch (error) {
      console.error('Error removing item from cart:', error);
    }
  };

  // Update the quantity of an item in the cart
  const handleUpdateQuantity = async (productId, action) => {
    try {
      await axios.post(
        `http://localhost:5000/update_cart_quantity/${productId}/${action}`,
        {},
        { withCredentials: true }
      );
      // Refetch cart items to update the UI
      const response = await axios.get('http://localhost:5000/cart', {
        withCredentials: true,
      });
      setCartItems(response.data.cart_items);
      setTotalCost(response.data.total_cost);
    } catch (error) {
      console.error('Error updating cart quantity:', error);
    }
  };

  return (
    <div>
      <h1>Your Cart</h1>
      {cartItems.length === 0 ? (
        <p>Your cart is empty</p>
      ) : (
        <div>
          {cartItems.map((item) => (
            <CartItem
              key={item._id}
              item={item}
              onRemoveFromCart={handleRemoveFromCart}
              onUpdateQuantity={handleUpdateQuantity}
            />
          ))}
          <h3>Total Cost: {totalCost} coins</h3>
        </div>
      )}
    </div>
  );
};

export default Cart;