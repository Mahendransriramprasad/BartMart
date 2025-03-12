import React, { useState } from 'react';
import axios from 'axios';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    dob: '',
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    axios.post('http://localhost:5000/register', formData)
      .then(response => {
        alert(response.data.message);
      })
      .catch(error => {
        alert(error.response.data.error);
      });
  };

  return (
    <div>
      <h1>Register</h1>
      <form onSubmit={handleSubmit}>
        <input 
          type="text" 
          name="username" 
          value={formData.username}
          onChange={handleChange} 
          placeholder="Username"
        />
        <input 
          type="password" 
          name="password" 
          value={formData.password}
          onChange={handleChange} 
          placeholder="Password"
        />
        <input 
          type="date" 
          name="dob" 
          value={formData.dob}
          onChange={handleChange}
        />
        <button type="submit">Register</button>
      </form>
    </div>
  );
}

export default Register;
