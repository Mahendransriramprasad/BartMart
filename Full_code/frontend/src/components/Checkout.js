import React, { useState } from 'react';
import axios from 'axios';

const Checkout = () => {
  const [message, setMessage] = useState('');

  const handleCheckout = () => {
    axios.post("http://localhost:5000/checkout")
      .then(response => {
        setMessage(response.data.message);
      })
      .catch(error => {
        setMessage(error.response.data.error);
      });
  };

  return (
    <div>
      <h1>Checkout</h1>
      <button onClick={handleCheckout}>Proceed to Checkout</button>
      {message && <p>{message}</p>}
    </div>
  );
}

export default Checkout;
