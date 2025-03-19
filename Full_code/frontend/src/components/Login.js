import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import "../css/Login.css";

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post(
        'http://localhost:5000/login',
        { username, password },
        { headers: { 'Content-Type': 'application/json' }, withCredentials: true }
      );

      if (response.data.message === "Login successful!") {
        console.log("Login successful!");
        localStorage.setItem("isAuthenticated", "true"); // Save login state
        navigate('/'); // Redirect to home
        window.location.reload(); // Refresh navbar to update login/logout
      } else {
        setError(response.data.error || "Login failed. Please try again.");
      }
    } catch (err) {
      setError(err.response?.data?.error || "An unexpected error occurred.");
    }
  };

  return (
    <div className="login-container">
      <h1>Login</h1>
      <form onSubmit={handleSubmit}>
        <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} required />
        <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        <button type="submit">Login</button>
      </form>
      
      {error && <div className="error-message">{error}</div>}

      {/* Signup redirection */}
      <p className="signup-link">Don't have an account? <span onClick={() => navigate('/register')}>Sign up</span></p>
    </div>
  );
}

export default Login;
