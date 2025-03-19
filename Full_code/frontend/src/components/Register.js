import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom'; 
import "../css/Register.css"; // Import CSS

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    dob: '',
  });

  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.username || !formData.password || !formData.dob) {
      setError('All fields are required.');
      return;
    }

    try {
      const response = await axios.post(
        'http://localhost:5000/register',
        formData,
        {
          headers: { 'Content-Type': 'application/json' },
          withCredentials: true,
        }
      );

      if (response.data.message) {
        setSuccess(response.data.message);
        setError('');
        setTimeout(() => navigate('/login'), 2000);
      }
    } catch (err) {
      if (err.response) {
        setError(err.response.data.error || 'Registration failed.');
      } else if (err.request) {
        setError('Network error. Please check your connection.');
      } else {
        setError('An unexpected error occurred.');
      }
      setSuccess('');
    }
  };

  return (
    <div className="register-container"> {/* Apply the CSS class here */}
      <h1>Register</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          name="username"
          value={formData.username}
          onChange={handleChange}
          placeholder="Username"
          required
        />
        <input
          type="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          placeholder="Password"
          required
        />
        <input
          type="date"
          name="dob"
          value={formData.dob}
          onChange={handleChange}
          required
        />
        <button type="submit">Register</button>
      </form>

      {success && <div className="success-message">{success}</div>}
      {error && <div className="error-message">{error}</div>}
    </div>
  );
};

export default Register;
