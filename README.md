# Zomato Clone

A full-stack food delivery web application developed as an assignment project using Django REST Framework for the backend and Vue 3 (Vite) for the frontend. The system includes restaurant discovery with category/dietary filters, a cart that restricts items to a single restaurant at a time, promotional coupon application, simulated payment processing, and order status tracking.

## Tech Stack

- **Backend:** Python 3.10+, Django 5, Django REST Framework, SimpleJWT, django-filter, SQLite / PostgreSQL
- **Frontend:** Vue 3 (Composition API), Vite, Pinia, Vue Router 4, Axios, Tailwind CSS

---

## Setup Instructions

### 1. Backend Setup (Django REST Framework)

Navigate to the `backend` directory, set up a Python virtual environment, install dependencies, and run the database migrations:

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On Linux / macOS:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Run database migrations
python manage.py migrate

# Seed initial restaurant, menu, and coupon data
python manage.py seed_restaurants

# Start the development server
python manage.py runserver
```

- Backend API: `http://localhost:8000/api/`
- Interactive API Docs (Swagger): `http://localhost:8000/api/docs/`

To run backend automated tests:

```bash
python manage.py test api
```

---

### 2. Frontend Setup (Vue 3 + Vite)

Navigate to the `frontend` directory, install the required npm packages, and start the local development server:

```bash
cd frontend

# Install node dependencies
npm install

# Start Vite development server
npm run dev
```

- Frontend App: `http://localhost:5173`

> **Note on Environment Variables:** By default, the frontend connects to `http://localhost:8000/api`. If your backend runs on a different port or host, create a `.env` file in the `frontend` root with `VITE_API_BASE_URL=http://your-backend-url/api`.

---

## API Documentation

| Method | Endpoint | Description | Auth Required |
|:-------|:---------|:------------|:--------------|
| `POST` | `/api/auth/send-otp/` | Generate and send a 6-digit OTP to mobile | No |
| `POST` | `/api/auth/verify-otp/` | Verify OTP and return JWT access/refresh tokens | No |
| `GET`  | `/api/auth/profile/` | Retrieve current user profile | Yes |
| `GET`  | `/api/restaurants/` | List restaurants with search, cuisine, and veg filters | No |
| `GET`  | `/api/restaurants/<id>/` | Retrieve restaurant details, menu categories, and reviews | No |
| `GET`  | `/api/restaurants/top-picks/` | Retrieve top-rated restaurants (rating >= 4.0) | No |
| `GET`  | `/api/coupons/` | List available promo coupons | No |
| `POST` | `/api/coupons/apply/` | Validate coupon code against current subtotal | No |
| `GET`  | `/api/cart/` | List cart items for the authenticated user | Yes |
| `POST` | `/api/cart/` | Add menu item to cart (returns 409 on restaurant conflict) | Yes |
| `PATCH`| `/api/cart/<id>/` | Update item quantity (setting to 0 removes the item) | Yes |
| `POST` | `/api/cart/clear/` | Remove all items from user's cart | Yes |
| `GET`  | `/api/cart/summary/` | Get calculated subtotal, 5% GST, and delivery fee | Yes |
| `GET`  | `/api/orders/` | List user order history | Yes |
| `POST` | `/api/orders/` | Place a new order from current cart or item payload | Yes |
| `POST` | `/api/orders/<id>/cancel/` | Cancel an order (allowed only in `PLACED` status) | Yes |
| `POST` | `/api/orders/<id>/progress-status/` | Progress order status to next stage (demo action) | Yes |
| `POST` | `/api/payments/create-razorpay-order/` | Generate test payment order ID and amount in paise | Yes |
| `POST` | `/api/payments/verify-razorpay-payment/` | Mark order payment as PAID with transaction ID | Yes |
| `GET`  | `/api/reviews/` | List customer reviews for restaurants | No |
| `POST` | `/api/reviews/` | Submit a rating and review (recalculates restaurant average) | Yes |

---

## Screenshots of the UI

### 1. Home Page & Restaurant Discovery
![Home Page / Restaurant Listing](./screenshots/home_page.png)

### 2. Menu Page & Cart Drawer
![Menu & Cart Drawer](./screenshots/menu_cart_drawer.png)

### 3. Checkout & Order Status Tracker
![Checkout & Order Status Tracker](./screenshots/checkout_order_tracker.png)

---

## Deployment Links

- **Live Frontend App:** `https://your-frontend-deployment.vercel.app` *(Replace with your live frontend URL)*
- **Live Backend API:** `https://your-backend-deployment.onrender.com` *(Replace with your live API URL)*
- **API Documentation:** `https://your-backend-deployment.onrender.com/api/docs/`

### Demo Test Credentials

- **Mobile Number:** `9876543210` (or any valid 10-digit number)
- **OTP Verification:** Enter the 6-digit code displayed in the backend terminal logs (or returned in the response in debug mode).