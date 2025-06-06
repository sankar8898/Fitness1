# 🧘 Fitness Studio Booking API

A simple RESTful API to manage bookings for fitness classes (Yoga, Zumba, HIIT) at a fictional studio. Built using Django and Django REST Framework.

---

## 🚀 Features

- View a list of upcoming fitness classes
- Book a class (if slots are available)
- Retrieve bookings by client email
- Timezone support (default: IST)
- Input validation and error handling
- In-memory DB (SQLite) — easy setup
- Function-based views and modular code

---

## 📦 Tech Stack

- Python 3.10+
- Django 4.x
- Django REST Framework
- SQLite (default)

---

## 📂 Project Structure

booking_api/
│
├── studio/ # App for fitness class & booking logic
│ ├── models.py
│ ├── serializers.py
│ ├── views.py
│ ├── urls.py
│ └── fixtures/
│ └── sample_classes.json
│
├── booking_api/ # Project settings
│ ├── settings.py
│ └── urls.py
│
├── manage.py
└── README.md