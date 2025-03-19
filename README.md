# BartMart

## Overview
BartMart is a barter-based marketplace built using Flask and MongoDB. Users earn points by selling products and use those points to buy products from others. The platform includes features like bargaining, chat for negotiations, and an admin panel for managing the marketplace.

## Features
- **User System**: New users must sell an item first to earn points before making a purchase.
- **Bargaining & Chat**: Users can negotiate prices within a fixed range through a dedicated chat system.
- **Product Listing**: Each product is unique, with no duplicate listings from the same seller.
- **Cart Logic**:
  - Users can only barter one product at a time.
  - Quantity cannot be increased since it's a one-to-one product exchange.
  - Sold products are removed from availability.
  - Prevents adding the same product multiple times to the cart.
- **Profile Management**: Users can view their points balance and trade history.
- **Secure Authentication**: Users log in via a simple authentication system using Flask-Bcrypt for password hashing.
- **Admin Panel**: Allows managing product listings, user activities, and reviews.
- **Image Uploads**: Images are uploaded and managed efficiently.

## Tech Stack
- **Backend**: Flask (Python), Flask-PyMongo for database interactions
- **Frontend**: HTML, CSS, JavaScript (templates stored in `templates/` folder)
- **Database**: MongoDB
- **Authentication**: Flask-Bcrypt for secure password management

## Folder Structure
```
BartMart/
│-- app.py               # Main application file
│-- config.py            # Configuration settings
│-- .gitignore           # Git ignore file
│-- package-lock.json    # Dependency lock file (if using npm)
│-- package.json         # Dependency file (if using npm)
│-- yarn.lock            # Dependency lock file (if using yarn)
│-- README.md            # Project documentation
│-- 25CS49[1].pptx       # Presentation file
│-- Future plans.txt     # Future improvements & roadmap
│
├── templates/           # Contains HTML templates
│   ├── admin_dashboard.html
│   ├── cart.html
│   ├── checkout.html
│   ├── login.html
│   ├── my_products.html
│   ├── (other HTML files)
│
├── static/              # Contains static assets (CSS, JS, Images)
```

## Installation & Setup
### Prerequisites
- Python installed
- MongoDB set up
- Virtual environment (optional but recommended)

### Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/Mahendransriramprasad/BartMart.git
   cd BartMart
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up environment variables (create a `.env` file and configure MongoDB URI, Flask secret key, etc.).
5. Start the Flask application:
   ```sh
   python app.py
   ```
6. Open the application in your browser at `http://localhost:5000`or `http://127.0.0.1:5000`.

## Future Plans
See `Future plans.txt` for upcoming features and improvements.

## Contributing
Contributions are welcome! Feel free to fork the repo and submit pull requests.

## License
This project is licensed under the MIT License.

## Contact
For any issues or suggestions, reach out at `mahendransriramprasad@gmail.com`.

