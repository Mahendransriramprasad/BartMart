import React, { useState } from 'react';
import axios from 'axios';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post(
        'http://localhost:5000/login',
        {
          username: username,
          password: password
        },
        {
          headers: {
            'Content-Type': 'application/json'  // Ensure correct Content-Type header
          }
        }
      );

      if (response.data.message) {
        // Handle successful login, for example, redirecting or showing success message
        console.log(response.data.message);
      }
    } catch (err) {
      // Handle error properly
      if (err.response) {
        console.log("Login Error:", err.response.data); // Log full error response
        setError(err.response.data.error || "An error occurred during login");
      } else {
        setError("Network Error");
      }
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit">Login</button>
      </form>
      {error && <div>{error}</div>}
    </div>
  );
}

export default Login;
