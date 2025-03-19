import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import "../css/Navbar.css";

const Navbar = () => {
  const navigate = useNavigate();
  const isAuthenticated = localStorage.getItem("isAuthenticated") === "true";

  const handleLogout = () => {
    localStorage.removeItem("isAuthenticated"); // Remove login state
    navigate("/login"); // Redirect to login page
    window.location.reload(); // Refresh to update Navbar
  };

  return (
    <nav>
      <ul>
        <li><Link to="/">Home</Link></li>
        
        <li><Link to="/cart">Cart</Link></li>
        <li><Link to="/admin/dashboard">Admin Dashboard</Link></li>
        {!isAuthenticated ? (
          <>
            <li><Link to="/login">Login</Link></li>
            <li><Link to="/register">Register</Link></li>
          </>
        ) : (
          <li><button onClick={handleLogout}>Logout</button></li>
        )}
      </ul>
    </nav>
  );
}

export default Navbar;
