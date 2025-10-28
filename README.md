# 🛒 Grocery Store Backend (Django REST Framework)

A complete **Django + Django REST Framework** backend for managing a grocery store — supporting user authentication, product inventory, cart, wishlist, discounts, and low-stock alerts for managers.

---

## 🚀 Features

* 🔐 **JWT Authentication** (Login, Register, Logout)
* 🛍️ **Product Management** (Add, Update, Delete)
* 🧺 **Cart System** (Add, Update, Checkout)
* 💖 **Wishlist System**
* 💸 **Promo Code Discount System**
* ⚠️ **Low-Stock Alerts for Store Managers**
* 📦 **Order Tracking**
* 👥 **Separate Apps:** `store`, `users`, and `customer`
* 🧑‍💼 **Role-based Permissions (Customer & Manager)**
* 📊 **Sales Report API**

---

## 🧩 Tech Stack

* **Backend:** Django, Django REST Framework
* **Database:** SQLite (default; can switch to PostgreSQL/MySQL)
* **Authentication:** JWT
* **Language:** Python 3.11+

---

## 🗂️ Project Structure

```
grocery-store-backend/
│
├── store/
│   ├── models.py          # Product, Cart, Wishlist, PromoCode models
│   ├── serializers.py     # Serializers for store data
│   ├── views.py           # All API endpoints related to store logic
│   ├── urls.py            # Store API routes
│
├── users/
│   ├── models.py          # Custom User model with role field
│   ├── serializers.py     # User-related serializers
│   ├── views.py           # Register/Login views
│
├── customer/
│   ├── models.py          # Customer profile or order history models
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│
├── grocery_store_backend/
│   ├── settings.py        # Project configuration (includes JWT setup)
│   ├── urls.py            # Global route registry
│
├── requirements.txt       # Python dependencies
├── manage.py
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/grocery-store-backend.git
cd grocery-store-backend
```

### 2. Create and activate virtual environment

```bash
python -m venv .venv
# Activate:
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create superuser

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

Now open your API in the browser:
👉 `http://127.0.0.1:8000/api/`

---

## 🧾 API Endpoints

| Feature             | Method | Endpoint                                | Description                          |
| ------------------- | ------ | --------------------------------------- | ------------------------------------ |
| **Auth**            | POST   | `/api/auth/register/`                   | Register a new user                  |
|                     | POST   | `/api/auth/login/`                      | Login & get JWT                      |
| **Products**        | GET    | `/api/store/products/`                  | View all products                    |
|                     | POST   | `/api/store/products/add/`              | Add product (Manager only)           |
| **Cart**            | GET    | `/api/store/cart/`                      | View user’s cart                     |
|                     | POST   | `/api/store/cart/add/<product_id>/`     | Add item to cart                     |
| **Wishlist**        | GET    | `/api/store/wishlist/`                  | View wishlist                        |
|                     | POST   | `/api/store/wishlist/add/<product_id>/` | Add to wishlist                      |
| **Promo Codes**     | POST   | `/api/store/promo/create/`              | Create promo (Manager only)          |
|                     | GET    | `/api/store/promo/`                     | View available promos                |
| **Low Stock Alert** | GET    | `/api/store/low-stock-alert/`           | Show products with stock ≤ threshold |              |
| **Sales Report**    | GET    | `/api/store/sales-report/`              | Generate sales summary               |

---

## 💸 Promo Code Example

### Request Body

```json
{
  "code": "DIWALI25",
  "discount_percent": 25,
  "active": true,
  "expiry_date": "2025-12-31"
}
```

### Response

```json
{
  "message": "Promo code created successfully"
}
```

---

## ⚠️ Low-Stock Alert Example

### Request

```
GET /api/store/low-stock-alert/
(Manager only)
```

### Response

```json
{
  "low_stock_count": 2,
  "products": [
    {
      "id": 5,
      "name": "Onion",
      "stock": 3,
      "low_stock_threshold": 5
    },
    {
      "id": 7,
      "name": "Milk Packet",
      "stock": 2,
      "low_stock_threshold": 4
    }
  ]
}
```

---

## 🧠 Notes

* Default database is SQLite (`db.sqlite3`).
* JWT tokens are issued via the login endpoint.
  If tokens expire quickly, check your JWT settings in `settings.py` (`ACCESS_TOKEN_LIFETIME` and `REFRESH_TOKEN_LIFETIME`).
* Only users with `role='manager'` can:

  * Add products
  * Create promo codes
  * View low-stock alerts

---

## 🧰 Troubleshooting

| Issue                               | Fix                                                            |
| ----------------------------------- | -------------------------------------------------------------- |
| `Cannot resolve keyword 'quantity'` | Replace with `stock` in filters                                |
| `PermissionDenied` for managers     | Ensure the user has `role='manager'`                           |
| Invalid token after 5 mins          | Adjust token lifetime in JWT settings                          |
| Migration errors                    | Delete `migrations/` folders and re-run makemigrations/migrate |

---

## 🧾 Requirements (from `requirements.txt`)

```
Django>=5.0
djangorestframework
djangorestframework-simplejwt
```



---

## 📜 License

This project is open-source under the **MIT License**.

---

**Developed with ❤️ using Django REST Framework**
