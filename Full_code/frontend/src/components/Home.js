import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Home = () => {
  const [products, setProducts] = useState([]);
  
  useEffect(() => {
    axios.get("http://localhost:5000/")
      .then(response => {
        setProducts(response.data.all_products);
      })
      .catch(error => {
        console.error("There was an error fetching the products!", error);
      });
  }, []);

  return (
    <div>
      <h1>All Products</h1>
      <div className="product-list">
        {products.map(product => (
          <div key={product._id} className="product">
            <img src={product.image} alt={product.name} />
            <h2>{product.name}</h2>
            <p>{product.category}</p>
            <p>{product.price} coins</p>
            <button>Add to Cart</button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Home;
