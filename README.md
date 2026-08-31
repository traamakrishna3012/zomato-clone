# Zomato Clone

A food ordering web application built with Django REST Framework and Vue 3. Supports restaurant discovery, menu navigation, cart management with single-restaurant constraints, coupon discounts, test payment flow, and order tracking.

## Tech Stack

- **Backend:** Python 3.10+, Django 5, Django REST Framework, SimpleJWT, django-filter, drf-spectacular, SQLite / PostgreSQL
- **Frontend:** Vue 3 (Composition API), Vite, Pinia, Vue Router 4, Axios, Tailwind CSS

## Local Setup

### 1. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux / macOS
# source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env

python manage.py migrate
python manage.py seed_restaurants
python manage.py runserver
```

- API server: `http://localhost:8000`
- Swagger documentation: `http://localhost:8000/api/docs/`

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

- Web application: `http://localhost:5173`

### 3. Database Seeding

Run the custom management command to populate sample restaurants, menus, and discount coupons:

```bash
cd backend
python manage.py seed_restaurants
```

### 4. Running Tests

```bash
cd backend
python manage.py test api
```

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|:-------|:---------|:------------|:--------------|
| `POST` | `/api/auth/send-otp/` | Send mobile OTP | No |
| `POST` | `/api/auth/verify-otp/` | Verify OTP and return JWT tokens | No |
| `GET`  | `/api/auth/profile/` | Fetch current user profile | Yes |
| `GET`  | `/api/restaurants/` | List restaurants with search and filters | No |
| `GET`  | `/api/restaurants/<id>/` | Retrieve restaurant details, menu items, and reviews | No |
| `GET`  | `/api/restaurants/top-picks/` | Retrieve top rated restaurants | No |
| `GET`  | `/api/coupons/` | List active coupons | No |
| `POST` | `/api/coupons/apply/` | Calculate discount for a coupon code | No |
| `GET`  | `/api/cart/` | List current user cart items | Yes |
| `POST` | `/api/cart/` | Add item to cart (with multi-restaurant conflict detection) | Yes |
| `PATCH`| `/api/cart/<id>/` | Update item quantity | Yes |
| `POST` | `/api/cart/clear/` | Empty cart | Yes |
| `GET`  | `/api/cart/summary/` | Get subtotal, tax (5%), and delivery fee breakdown | Yes |
| `GET`  | `/api/orders/` | List user orders | Yes |
| `POST` | `/api/orders/` | Place a new order | Yes |
| `POST` | `/api/orders/<id>/cancel/` | Cancel an order in `PLACED` state | Yes |
| `POST` | `/api/orders/<id>/progress-status/` | Advance order status stage | Yes |
| `POST` | `/api/payments/create-razorpay-order/` | Initialize Razorpay test order | Yes |
| `POST` | `/api/payments/verify-razorpay-payment/` | Verify signature and update order payment status | Yes |
| `GET`  | `/api/reviews/` | List restaurant reviews | No |
| `POST` | `/api/reviews/` | Submit a rating and review | Yes |