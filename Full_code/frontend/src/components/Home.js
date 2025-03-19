import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../css/Home.css";

const Home = () => {
  const [products, setProducts] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    axios
      .get("http://localhost:5000/")
      .then((response) => {
        // Ensure _id is converted to a string for each product
        const formattedProducts = response.data.all_products.map(product => ({
          ...product,
          _id: product._id.toString(), // Convert ObjectId to string
        }));
        setProducts(formattedProducts);
      })
      .catch((error) => console.error("Error fetching products:", error));
  }, []);

  return (
    <div>
      <h1>All Products</h1>
      <div className="product-list">
        {products.map((product) => (
          <div
            key={product._id}
            className="product"
            onClick={() => {
              console.log("Product ID:", product._id); // Debugging
              navigate(`/product/${product._id}`);
            }}
          >
            <img 
              src={product.image1} 
              alt={product.name} 
              className="product-image"
              onError={(e) => e.target.src = "/fallback.jpg"} 
            />
            <h2>{product.name}</h2>
            <p>{product.category}</p>
            <p>{product.price} coins</p>
            <button>View Details</button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Home;