# 🚗 ParkIQ – Smart Parking System

A smart parking web application that allows users to find, book, and manage parking slots efficiently with integrated payments, pass system, and intelligent availability prediction.

---

## 📌 Features

* 🔐 User Authentication (Register/Login)
* 🅿️ Real-time Parking Slot Booking
* 🤖 AI-based Parking Availability Prediction
* 💳 Online Payment Integration (Razorpay)
* 🎫 Monthly Parking Pass System
* 💰 Wallet Balance Display & Deduction
* ⏱ Parking Timer with Expiry Alert (SMS)
* 📄 Booking History & Receipt Download
* 📊 Admin Panel for Slot Management

---

## 🛠 Tech Stack

* **Frontend:** HTML, CSS, JavaScript
* **Backend:** Python (Flask)
* **Database:** SQLite
* **Payment Gateway:** Razorpay API
* **SMS Service:** Fast2SMS API

---

## ⚙️ Installation & Setup

1. Clone the repository:

```
git clone https://github.com/shreeyadhanmeher24-oss/your-repo-name.git
```

2. Navigate to the project folder:


cd smart_parking_system
```

3. Install dependencies:


pip install flask razorpay reportlab requests
```

4. Run the application:

```
python app.py
```

5. Open in browser:

```
http://127.0.0.1:5000/
```

---

## 💡 How It Works

### 👤 User with Pass

* Purchases monthly pass via Razorpay
* Wallet is credited with pass amount
* Books parking without payment gateway
* Amount deducted directly from wallet

### 👤 Normal User

* Books parking slot
* Redirected to Razorpay
* Completes payment
* Parking confirmed

---

## 🤖 AI-Based Parking Prediction

The system includes a smart logic to predict parking availability based on real-time conditions.

### 🔍 How it works:

* Uses current available slots
* Considers time of the day (peak vs non-peak hours)
* Generates predictions like:

  * "High demand expected"
  * "Slots may fill soon"
  * "Good availability in next 30 minutes"

### 💡 Purpose:

Helps users make better decisions by:

* Booking early during peak hours
* Avoiding unnecessary waiting

---

## 🔐 API Keys Note

* Razorpay is used in **Test Mode**
* No real money is deducted
* Replace API keys with your own for production use

---


## 🚀 Future Improvements


* 🤖 Advanced ML-based prediction using real datasets
* 📱 Mobile app version
* 🔔 Push notifications

---

## 👩‍💻 Author

**Shreeya Dhanmeher**
GitHub: https://github.com/shreeyadhanmeher24-oss

---

