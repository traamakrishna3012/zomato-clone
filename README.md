# Zomato Clone

A food ordering web application built with Django REST Framework and Vue 3. Supports restaurant discovery, menu navigation, cart management with single-restaurant constraints, coupon discounts, test payment flow, and order tracking.

---

## 1. System Architecture

```
[ Vue 3 SPA (Vite + Pinia) ]
           │ (Axios + JWT Interceptors)
           ▼
[ Django REST Framework API ]
   ├── Authentication API (Mobile OTP + SimpleJWT)
   ├── Restaurant Discovery (django-filter + Search + Prefetch)
   ├── Cart Management (Single-restaurant conflict check)
   ├── Order Processing (Atomic checkout + Server-side pricing)
   ├── Coupon Engine (Min spend & Max cap validation)
   └── Payment Sandbox (Razorpay Order creation & verification)
           │
           ▼
[ SQLite / PostgreSQL (Supabase) Database ]
```

---

## 2. Tech Stack

- **Backend:** Python 3.10+, Django 5, Django REST Framework, SimpleJWT, django-filter, drf-spectacular, SQLite / PostgreSQL (dj-database-url)
- **Frontend:** Vue 3 (Composition API), Vite, Pinia, Vue Router 4, Axios, Tailwind CSS

---

## 3. Local Setup

### Backend Setup

```bash
cd backend
python -m venv venv

# Windows:
.\venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env

python manage.py migrate
python manage.py seed_restaurants
python manage.py runserver
```

- API Server: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/api/docs/`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

- Application: `http://localhost:5173`

---

## 4. Environment Variables

Create `.env` inside `backend/`:

```env
DATABASE_URL=sqlite:///db.sqlite3
DEBUG=True
SECRET_KEY=django-insecure-change-this-in-production-long-secure-key-50-characters
ALLOWED_HOSTS=localhost,127.0.0.1,testserver
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
RAZORPAY_KEY_ID=rzp_test_zomatoCloneDemoKey
RAZORPAY_KEY_SECRET=rzp_test_secret_demo
```

---

## 5. Core Subsystem Workflows & Design Choices

### A. Authentication Subsystem
- **Mobile-as-Username:** Uses a custom `User` model inheriting from `AbstractBaseUser` with `mobile` as the `USERNAME_FIELD`.
- **OTP Generation & Lifespan:** A cryptographically secure 6-digit random code is generated per login request and stored in the database with a 5-minute expiration timestamp.
- **Consumption Guard:** An OTP is marked `is_verified = True` immediately upon successful verification to prevent replay attacks.
- **JWT Issuance:** SimpleJWT issues an access token (7-day lifetime) and refresh token (30-day lifetime).
- **Development Convenience:** When `DEBUG=True`, generated OTPs are printed to the Django terminal console and returned under `debug_otp` for evaluator testing.

### B. Restaurant Discovery & Query Optimization
- **Filtering & Search:** Supports filtering by city, pure vegetarian flag (`is_pure_veg`), minimum rating (`min_rating`), max cost for two (`max_cost`), and debounced full-text search across dishes and cuisines.
- **N+1 Query Prevention:** Endpoints leverage `.prefetch_related('menu_items', 'reviews__user')` and `.select_related('restaurant')` to ensure constant-time database queries regardless of page size.

### C. Cart & Single-Restaurant Rule
- **Single-Restaurant Constraint:** In food delivery platforms, delivery logistics require orders to originate from a single kitchen. Attempting to add an item from a different restaurant returns `HTTP 409 Conflict`.
- **Conflict Resolution:** The client displays a confirmation dialog asking the user whether to discard existing items or cancel. Passing `clear_existing=True` atomizes cart replacement.
- **Server-Side Enforcement:** Cart ownership is strictly isolated by `request.user`. Zero or negative quantity updates automatically remove the line item.

### D. Order Creation & Financial Calculations
- **Server-Calculated Billing:** The server does not trust pricing or grand total payloads from the client. All monetary values are computed using database records and `Decimal` arithmetic:
  - $\text{Taxes} = \text{round}(\text{Subtotal} \times 0.05, 2)$ (5% GST)
  - $\text{Delivery Fee} = \text{₹40.00}$ (Flat rate)
  - $\text{Grand Total} = \max\Big(0, \, \text{Subtotal} + \text{Taxes} + \text{Delivery Fee} - \text{Discount}\Big)$
- **Transactional Atomicity:** Wrapped in `@transaction.atomic` to ensure item validation, coupon application, order creation, immutable `OrderItem` price snapshotting, and cart clearing execute as a single atomic unit.
- **Multi-Restaurant Order Prevention:** Custom item payloads containing dishes from different restaurants are rejected with `HTTP 400 Bad Request`.

### E. Simulated Razorpay Payment Sandbox
- **Workflow:**
  1. Frontend requests an order creation ticket (`/api/payments/create-razorpay-order/`).
  2. Backend validates that the order belongs to the user, is currently `PENDING`, and generates a test order token with amount calculated in paise ($\text{INR} \times 100$).
  3. Frontend triggers the simulated Razorpay checkout modal.
  4. Upon simulation completion, the client submits the transaction ID to `/api/payments/verify-razorpay-payment/`, transitioning `payment_status` to `PAID`.
- **Sandbox Boundary:** Production deployments replace the simulation endpoints with the official `razorpay` Python SDK and verify webhook signatures asynchronously.

---

## 6. API Endpoints

| Method | Endpoint | Description | Auth |
|:-------|:---------|:------------|:-----|
| `POST` | `/api/auth/send-otp/` | Request 6-digit verification code | No |
| `POST` | `/api/auth/verify-otp/` | Verify code and obtain JWT tokens | No |
| `GET`  | `/api/auth/profile/` | Fetch current authenticated user | Yes |
| `GET`  | `/api/restaurants/` | Search & filter restaurants | No |
| `GET`  | `/api/restaurants/<id>/` | Fetch restaurant details, menu & reviews | No |
| `GET`  | `/api/restaurants/top-picks/` | Fetch top-rated restaurants ($\ge 4.0\star$) | No |
| `GET`  | `/api/coupons/` | List available discount coupons | No |
| `POST` | `/api/coupons/apply/` | Validate coupon code against subtotal | No |
| `GET`  | `/api/cart/` | List cart items for active user | Yes |
| `POST` | `/api/cart/` | Add item to cart (409 on restaurant mismatch) | Yes |
| `PATCH`| `/api/cart/<id>/` | Update item quantity ($\le 0$ removes) | Yes |
| `POST` | `/api/cart/clear/` | Discard all cart items | Yes |
| `GET`  | `/api/cart/summary/` | Get breakdown (subtotal, tax, fee, total) | Yes |
| `GET`  | `/api/orders/` | List past and active orders | Yes |
| `POST` | `/api/orders/` | Atomically place an order | Yes |
| `POST` | `/api/orders/<id>/cancel/` | Cancel an order in `PLACED` state | Yes |
| `POST` | `/api/orders/<id>/progress-status/` | Advance delivery state | Yes |
| `POST` | `/api/payments/create-razorpay-order/` | Prepare payment order ticket | Yes |
| `POST` | `/api/payments/verify-razorpay-payment/` | Record verified transaction | Yes |
| `GET`  | `/api/reviews/` | List customer reviews | No |
| `POST` | `/api/reviews/` | Submit a review & update restaurant rating | Yes |

---

## 7. Testing & Verification

Run the automated backend test suite:

```bash
cd backend
python manage.py test api
```

The test suite contains 21 test cases validating:
- OTP generation, dynamic code verification, expiration rejection, consumption/reuse rejection.
- Restaurant filtering by city, pure veg, rating, cuisine, and dish search.
- Cart ownership, zero quantity removal, and cross-restaurant conflict detection.
- Transactional order placement, mixed-restaurant order rejection, and server-side pricing.
- Cancellation constraints and linear state progression.
- Razorpay payment simulation and duplicate payment guards.
- Review rating aggregation.

---

## 8. Known Limitations

- **SMS Delivery:** In local development, OTPs are printed to terminal logs and provided in `debug_otp`. Live production requires configuring an SMS gateway (e.g. Twilio, AWS SNS).
- **Payment Webhooks:** Payment verification is currently performed via synchronous client confirmation. In high-traffic production, an asynchronous Razorpay webhook listener handles webhooks and idempotency keys.
- **Real-Time Push:** Delivery stage progression is triggered via API actions. Live systems would use WebSockets (Django Channels) to stream courier location updates.