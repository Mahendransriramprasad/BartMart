import axios from 'axios';

const API_URL = "http://127.0.0.1:5000"; // Adjust to match your Flask server URL

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Fetch all products (home page)
export const getAllProducts = async () => {
  try {
    const response = await api.get("/");
    return response.data;
  } catch (error) {
    console.error("Error fetching products:", error);
    return null;
  }
};

// Register user
export const registerUser = async (username, password, dob) => {
  try {
    const response = await api.post("/register", { username, password, dob });
    return response.data;
  } catch (error) {
    console.error("Error registering user:", error);
    return null;
  }
};

// Login user
export const loginUser = async (username, password) => {
  try {
    const response = await api.post("/login", { username, password });
    return response.data;
  } catch (error) {
    console.error("Error logging in:", error);
    return null;
  }
};

// Logout user
export const logoutUser = async () => {
  try {
    const response = await api.get("/logout");
    return response.data;
  } catch (error) {
    console.error("Error logging out:", error);
    return null;
  }
};

// Add a product to cart
export const addToCart = async (productId) => {
  try {
    const response = await api.get(`/add_to_cart/${productId}`);
    return response.data;
  } catch (error) {
    console.error("Error adding product to cart:", error);
    return null;
  }
};

// View user's cart
export const viewCart = async () => {
  try {
    const response = await api.get("/cart");
    return response.data;
  } catch (error) {
    console.error("Error viewing cart:", error);
    return null;
  }
};

// Update cart quantity (increase or decrease)
export const updateCartQuantity = async (productId, action) => {
  try {
    const response = await api.get(`/update_cart_quantity/${productId}/${action}`);
    return response.data;
  } catch (error) {
    console.error("Error updating cart quantity:", error);
    return null;
  }
};

// Remove item from cart
export const removeFromCart = async (productId) => {
  try {
    const response = await api.get(`/remove_from_cart/${productId}`);
    return response.data;
  } catch (error) {
    console.error("Error removing item from cart:", error);
    return null;
  }
};

// Checkout (purchase the items in the cart)
export const checkout = async () => {
  try {
    const response = await api.post("/checkout");
    return response.data;
  } catch (error) {
    console.error("Error during checkout:", error);
    return null;
  }
};

// Checkout success (after successful checkout)
export const checkoutSuccess = async () => {
  try {
    const response = await api.get("/checkout_success");
    return response.data;
  } catch (error) {
    console.error("Error getting checkout success:", error);
    return null;
  }
};

// Sell product (submit for review)
export const sellProduct = async (name, category, image, price, ageGroup) => {
  try {
    const response = await api.post("/sell", { name, category, image, price, age_group: ageGroup });
    return response.data;
  } catch (error) {
    console.error("Error submitting product for sale:", error);
    return null;
  }
};

// Admin approve product
export const approveProduct = async (requestId) => {
  try {
    const response = await api.get(`/admin/approve_product/${requestId}`);
    return response.data;
  } catch (error) {
    console.error("Error approving product:", error);
    return null;
  }
};

// Admin reject product
export const rejectProduct = async (requestId) => {
  try {
    const response = await api.get(`/admin/reject_product/${requestId}`);
    return response.data;
  } catch (error) {
    console.error("Error rejecting product:", error);
    return null;
  }
};

// Admin delete product
export const deleteProduct = async (productId) => {
  try {
    const response = await api.get(`/admin/delete_product/${productId}`);
    return response.data;
  } catch (error) {
    console.error("Error deleting product:", error);
    return null;
  }
};

// Admin add product (direct product addition without approval)
export const addProductAdmin = async (name, category, image, price, ageGroup) => {
  try {
    const response = await api.post("/admin/dashboard", { name, category, image, price, age_group: ageGroup });
    return response.data;
  } catch (error) {
    console.error("Error adding product:", error);
    return null;
  }
};