import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../css/AdminDashboard.css";

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [products, setProducts] = useState([]); 
  const [pendingProducts, setPendingProducts] = useState([]);

  // Check admin login status
  useEffect(() => {
    const checkAdmin = async () => {
      try {
        await axios.get("http://localhost:5000/admin/dashboard", {
          withCredentials: true,
        });
      } catch (error) {
        navigate("/admin/login"); // Redirect to login if not logged in
      }
    };
    checkAdmin();
  }, [navigate]);

  // ✅ Fetch products and pending products in one request
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get("http://localhost:5000/admin/dashboard", {
          withCredentials: true,
        });
        setProducts(response.data.products);
        setPendingProducts(response.data.sell_requests);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="admin-dashboard">
      <h1>Admin Dashboard</h1>
      {/* Logout Button */}
      <button
        onClick={async () => {
          await axios.post("http://localhost:5000/admin/logout", {}, { withCredentials: true });
          navigate("/admin/login");
        }}
      >
        Logout
      </button>

      {/* ✅ Render Products Table if Data Exists */}
      <h2>All Products</h2>
      {products.length > 0 ? (
        <table>
          <thead>
            <tr>
              <th>Product Name</th>
              <th>Category</th>
              <th>Price</th>
            </tr>
          </thead>
          <tbody>
            {products.map((product) => (
              <tr key={product._id}>
                <td>{product.name}</td>
                <td>{product.category}</td>
                <td>{product.price} coins</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>No products available</p>
      )}

      {/* ✅ Render Pending Products Table if Data Exists */}
      <h2>Pending Products</h2>
      {pendingProducts.length > 0 ? (
        <ul>
          {pendingProducts.map((product) => (
            <li key={product._id}>{product.name}</li>
          ))}
        </ul>
      ) : (
        <p>No pending products</p>
      )}
    </div>
  );
};

export default AdminDashboard;
