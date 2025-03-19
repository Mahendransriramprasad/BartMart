import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Checkout = () => {
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleCheckout = async () => {
    try {
      const response = await axios.post(
        'http://localhost:5000/checkout',
        {},
        { withCredentials: true }
      );
      setMessage(response.data.message);
      // Redirect to checkout success page after 2 seconds
      setTimeout(() => {
        navigate('/checkout_success');
      }, 2000);
    } catch (error) {
      setMessage(error.response?.data?.error || 'Checkout failed. Please try again.');
    }
  };

  return (
    <div>
      <h1>Checkout</h1>
      <button onClick={handleCheckout}>Proceed to Checkout</button>
      {message && <p>{message}</p>}
    </div>
  );
};

export default Checkout;