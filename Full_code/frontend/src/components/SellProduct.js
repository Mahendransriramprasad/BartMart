import React, { useState } from 'react';
import { sellProduct } from '../services/api';
import { useNavigate } from 'react-router-dom';  // Use useNavigate instead of useHistory

const SellProduct = () => {
  const [name, setName] = useState('');
  const [category, setCategory] = useState('');
  const [image, setImage] = useState('');
  const [price, setPrice] = useState('');
  const [ageGroup, setAgeGroup] = useState('');
  const navigate = useNavigate();  // Initialize navigate

  const handleSubmit = async (e) => {
    e.preventDefault();
    const response = await sellProduct(name, category, image, price, ageGroup);
    if (response) {
      navigate('/');  // Use navigate instead of history.push
    }
  };

  return (
    <div>
      <h1>Sell a Product</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Product Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <input
          type="text"
          placeholder="Category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        />
        <input
          type="text"
          placeholder="Image URL"
          value={image}
          onChange={(e) => setImage(e.target.value)}
        />
        <input
          type="number"
          placeholder="Price"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
        />
        <select onChange={(e) => setAgeGroup(e.target.value)} value={ageGroup}>
          <option value="">Age Group</option>
          <option value="Kids">Kids</option>
          <option value="Teens">Teens</option>
          <option value="Adults">Adults</option>
        </select>
        <button type="submit">Submit</button>
      </form>
    </div>
  );
};

export default SellProduct;
