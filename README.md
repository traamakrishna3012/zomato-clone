# Zomato Clone

A full-stack food delivery web application replicating core restaurant discovery, menu browsing, cart management with multi-restaurant conflict handling, coupon discounts, Razorpay payments, and live order tracking.

## Features

- **Authentication:** Passwordless mobile OTP login with JWT access and refresh tokens.
- **Restaurant Discovery:** Search by name/cuisine/dish, filter by rating, veg/non-veg, delivery time, and cost for two.
- **Menu & Cart:** Category-wise menu browsing with dish counters, slide-out cart drawer, and cross-restaurant conflict detection modal.
- **Coupons:** Discount code verification and dynamic bill deduction (percentage and flat discounts with minimum spend rules).
- **Payment & Checkout:** Test mode Razorpay checkout (UPI, Card, Netbanking) and Cash on Delivery.
- **Order Tracking:** 4-stage visual progress tracker (`Placed` -> `Preparing` -> `Out for Delivery` -> `Delivered`) and order cancellation support.
- **Reviews:** Rating and review submission with automated restaurant score aggregation.

## Tech Stack

- **Backend:** Django 5, Django REST Framework, SimpleJWT, django-filter, drf-spectacular, PostgreSQL (Supabase / SQLite fallback)
- **Frontend:** Vue 3 (Composition API), Vite, Pinia, Vue Router 4, Axios, Tailwind CSS

## Local Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate
# macOS/Linux
# source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env

python manage.py migrate
python manage.py seed_restaurants
python manage.py runserver
```

Backend server runs at `http://localhost:8000`.  
Swagger documentation available at `http://localhost:8000/api/docs/`.

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend app runs at `http://localhost:5173`.

### 3. Run Backend Tests

```bash
cd backend
python manage.py test api
```

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|:-------|:---------|:------------|:--------------|
| `POST` | `/api/auth/send-otp/` | Send mobile OTP | No |
| `POST` | `/api/auth/verify-otp/` | Verify OTP and return JWT tokens | No |
| `GET`  | `/api/auth/profile/` | Current user profile | Yes |
| `GET`  | `/api/restaurants/` | List restaurants (search & filters) | No |
| `GET`  | `/api/restaurants/<id>/` | Restaurant detail with menu items and reviews | No |
| `GET`  | `/api/restaurants/top-picks/` | Top rated restaurants | No |
| `GET`  | `/api/coupons/` | List active coupons | No |
| `POST` | `/api/coupons/apply/` | Calculate coupon discount | No |
| `GET`  | `/api/cart/` | Get cart items | Yes |
| `POST` | `/api/cart/` | Add item to cart | Yes |
| `PATCH`| `/api/cart/<id>/` | Update item quantity | Yes |
| `POST` | `/api/cart/clear/` | Clear cart | Yes |
| `GET`  | `/api/cart/summary/` | Bill breakdown | Yes |
| `GET`  | `/api/orders/` | List user orders | Yes |
| `POST` | `/api/orders/` | Place order | Yes |
| `POST` | `/api/orders/<id>/cancel/` | Cancel order | Yes |
| `POST` | `/api/orders/<id>/progress-status/` | Advance order status stage | Yes |
| `POST` | `/api/payments/create-razorpay-order/` | Create Razorpay order | Yes |
| `POST` | `/api/payments/verify-razorpay-payment/` | Verify payment and mark paid | Yes |
| `GET`  | `/api/reviews/` | List restaurant reviews | No |
| `POST` | `/api/reviews/` | Submit review | Yes |