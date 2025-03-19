import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

const ProductDetails = () => {
  const { productId } = useParams(); // Get product ID from URL
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [mainImage, setMainImage] = useState(""); // State for the main image
  const navigate = useNavigate();

  useEffect(() => {
    fetch(`http://localhost:5000/product/${productId}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          console.error("Error:", data.error);
          setProduct(null);
        } else {
          setProduct(data);
          setMainImage(data.image1); // Set the main image to the first image
        }
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching product:", error);
        setLoading(false);
      });
  }, [productId]);

  // Function to change the main image when a thumbnail is clicked
  const changeImage = (image) => {
    setMainImage(image);
  };

  // Function to handle "Add to Cart" button click
  const handleAddToCart = () => {
    fetch(`http://localhost:5000/add_to_cart/${productId}`, {
      method: "POST",
      credentials: "include", // Include cookies for session handling
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          alert(data.error);
        } else {
          alert("Product added to cart!");
        }
      })
      .catch((error) => {
        console.error("Error adding to cart:", error);
      });
  };

  // Function to handle "Negotiate" button click
  const handleNegotiate = () => {
    navigate(`/negotiate/${productId}`); // Navigate to the negotiate page
  };

  if (loading) return <h2>Loading...</h2>;
  if (!product) return <h2>Product not found</h2>;

  return (
    <div style={styles.container}>
      {/* Image Gallery */}
      <div style={styles.imageGallery}>
        {/* Main Image */}
        <div style={styles.mainImageContainer}>
          <img
            src={mainImage}
            alt={product.name}
            style={styles.mainImage}
          />
        </div>

        {/* Thumbnails */}
        <div style={styles.thumbnailsContainer}>
          {[product.image1, product.image2, product.image3, product.image4].map(
            (image, index) =>
              image && (
                <img
                  key={index}
                  src={image}
                  alt={`Thumbnail ${index + 1}`}
                  style={styles.thumbnail}
                  onClick={() => changeImage(image)}
                />
              )
          )}
        </div>
      </div>

      {/* Product Details */}
      <div style={styles.detailsContainer}>
        <h1 style={styles.productName}>{product.name}</h1>
        <p>
          <strong>Category:</strong> {product.category}
        </p>
        <p>
          <strong>Description:</strong> {product.description}
        </p>
        <p>
          <strong>Price:</strong> {product.price} coins
        </p>

        {/* Action Buttons */}
        <div style={styles.actionButtons}>
          <button style={styles.addToCartButton} onClick={handleAddToCart}>
            🛒 Add to Cart
          </button>
          <button style={styles.negotiateButton} onClick={handleNegotiate}>
            💬 Negotiate
          </button>
        </div>

        {/* Seller Information */}
        <div style={styles.sellerInfo}>
          <h2 style={styles.sellerHeader}>🛍️ Seller Information</h2>
          <p>
            <strong>Username:</strong>{" "}
            <a
              href={`/profile/${product.username}`}
              style={styles.sellerLink}
            >
              {product.username}
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

// Styles
const styles = {
  container: {
    maxWidth: "1200px",
    margin: "auto",
    padding: "20px",
    display: "flex",
    flexDirection: "row",
    gap: "20px",
  },
  imageGallery: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    gap: "10px",
  },
  mainImageContainer: {
    width: "100%",
    height: "400px",
    overflow: "hidden",
    borderRadius: "10px",
    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
  },
  mainImage: {
    width: "100%",
    height: "100%",
    objectFit: "cover",
  },
  thumbnailsContainer: {
    display: "flex",
    gap: "10px",
    overflowX: "auto",
    padding: "10px 0",
  },
  thumbnail: {
    width: "80px",
    height: "80px",
    objectFit: "cover",
    borderRadius: "8px",
    cursor: "pointer",
    border: "2px solid transparent",
    transition: "border 0.3s, transform 0.3s",
  },
  detailsContainer: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    gap: "20px",
  },
  productName: {
    fontSize: "2rem",
    fontWeight: "bold",
    color: "#333",
  },
  actionButtons: {
    display: "flex",
    gap: "10px",
  },
  addToCartButton: {
    flex: 1,
    padding: "10px",
    backgroundColor: "#f472b6",
    color: "white",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "1rem",
    fontWeight: "bold",
    transition: "background-color 0.3s",
  },
  negotiateButton: {
    flex: 1,
    padding: "10px",
    backgroundColor: "#3b82f6",
    color: "white",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "1rem",
    fontWeight: "bold",
    transition: "background-color 0.3s",
  },
  sellerInfo: {
    padding: "20px",
    backgroundColor: "#f9f9f9",
    borderRadius: "10px",
    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
  },
  sellerHeader: {
    fontSize: "1.5rem",
    fontWeight: "bold",
    color: "#333",
    marginBottom: "10px",
  },
  sellerLink: {
    color: "#f472b6",
    textDecoration: "none",
    fontWeight: "bold",
  },
};

export default ProductDetails;