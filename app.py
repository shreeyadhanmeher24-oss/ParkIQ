from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
import sqlite3
import razorpay
import random
from reportlab.pdfgen import canvas
import io
import requests
from datetime import datetime
app = Flask(__name__)
app.secret_key = "parkiq_secret_key"

# Razorpay Client
client = razorpay.Client(
    auth=("rzp_test_SdKPQQ7qGLvELC", "CbrtZnClD3T2ugYDnqd68H0l")
)

# ---------------- HOME PAGE ----------------
@app.route("/")
def home():
    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM parking_slots")
    parking_slots = cursor.fetchall()
    conn.close()

    reviews = [
        {"name": "Rahul Sharma", "review": "Very easy to use and saved my time finding parking!"},
        {"name": "Priya Mehta", "review": "Payment and booking process is smooth and quick."},
        {"name": "Aman Verma", "review": "Best parking solution in crowded areas."}
    ]

    username = session.get("username")

    return render_template(
        "index.html",
        parking_slots=parking_slots,
        reviews=reviews,
        username=username
    )


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("parking.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("parking.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session["username"] = username
            return redirect(url_for("home"))

    return render_template("login.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    return render_template("dashboard.html", username=username)


# ---------------- SEARCH LOCATION ----------------
@app.route("/search_location")
def search_location():
    return render_template("search_location.html")


# ---------------- AREA SLOT DISPLAY ----------------
@app.route("/area_slots")
def area_slots():
    location = request.args.get("location")

    total_slots = random.randint(10, 30)
    available = random.randint(3, total_slots)
    occupied = total_slots - available

    current_hour = datetime.now().hour

    # AI Prediction Logic
    if 17 <= current_hour <= 21:
        # Peak evening traffic
        if available <= 5:
            prediction = "High demand expected. Slots may fill soon."
        else:
            prediction = "Moderate availability expected."
    else:
        if available > 5:
            prediction = "High chance slots available in next 30 minutes."
        else:
            prediction = "Limited slots likely. Recommended to book now."

    return render_template(
        "area_slots.html",
        area=location,
        total=total_slots,
        available=available,
        occupied=occupied,
        prediction=prediction
    )

# ---------------- BOOK SLOT ----------------
@app.route("/book/<int:id>")
def book_slot(id):
    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()

    # Get selected slot number
    cursor.execute("SELECT slot_number FROM parking_slots WHERE id=?", (id,))
    slot = cursor.fetchone()

    if slot:
        session["booked_slot"] = slot[0]

        # Mark slot occupied
        cursor.execute(
            "UPDATE parking_slots SET status='Occupied' WHERE id=?",
            (id,)
        )
        conn.commit()

    conn.close()

    # FIXED REDIRECT TO BOOKING FORM
    return redirect("/booking_form")


# ---------------- BOOKING FORM ----------------
@app.route("/booking_form")
def booking_form():
    return render_template("booking_form.html")


# ---------------- CONFIRM BOOKING ----------------
@app.route("/confirm_booking", methods=["POST"])
def confirm_booking():
    vehicle_number = request.form["vehicle_number"]
    vehicle_type = request.form["vehicle_type"]
    duration = request.form["duration"]
    price = request.form["price"]

    session["vehicle_number"] = vehicle_number
    session["vehicle_type"] = vehicle_type
    session["duration"] = duration
    session["payment_amount"] = int(price) * 100

    return redirect("/payment")


# ---------------- PAYMENT ----------------
@app.route("/payment")
def payment():
    amount = session.get("payment_amount", 5000)

    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    return render_template(
        "payment.html",
        order_id=order["id"],
        amount=amount,
        key_id="rzp_test_SdKPQQ7qGLvELC"
    )

@app.route("/extend_payment")
def extend_payment():
    session["payment_amount"] = 2000  # ₹20 extension fee
    return redirect(url_for("payment"))


# ---------------- PAYMENT SUCCESS ----------------
@app.route("/success")
def success():
    payment_id = request.args.get("payment_id")
    slot_number = session.get("booked_slot")
    username = session.get("username")

    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO bookings (username, slot_number, payment_id) VALUES (?, ?, ?)",
        (username, slot_number, payment_id)
    )

    conn.commit()
    conn.close()

    duration_units = int(session.get("duration", 1))
    seconds = duration_units * 30 * 60

    return render_template("timer.html", seconds=seconds)


# ---------------- DOWNLOAD RECEIPT ----------------
@app.route("/download_receipt/<payment_id>")
def download_receipt(payment_id):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    p.setFont("Helvetica-Bold", 18)
    p.drawString(180, 800, "ParkIQ Payment Receipt")

    p.setFont("Helvetica", 14)
    p.drawString(100, 740, f"Payment ID: {payment_id}")
    p.drawString(100, 710, f"Amount Paid: ₹{session.get('payment_amount',5000)//100}")
    p.drawString(100, 680, f"Vehicle Number: {session.get('vehicle_number','-')}")
    p.drawString(100, 650, f"Vehicle Type: {session.get('vehicle_type','-')}-Wheeler")
    p.drawString(100, 620, f"Duration: {session.get('duration','-')}")
    p.drawString(100, 590, "Parking Slot Booking Confirmed")
    p.drawString(100, 560, "Status: Successful")
    p.drawString(100, 520, "Thank you for using ParkIQ!")

    p.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"receipt_{payment_id}.pdf",
        mimetype="application/pdf"
    )


# ---------------- BOOKING HISTORY ----------------
@app.route("/history")
def history():
    username = session.get("username")

    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT slot_number, payment_id FROM bookings WHERE username=?",
        (username,)
    )

    bookings = cursor.fetchall()
    conn.close()

    return render_template("history.html", bookings=bookings)


# ---------------- LIVE SLOT API ----------------
@app.route("/get_slots")
def get_slots():
    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, slot_number, status FROM parking_slots")
    slots = cursor.fetchall()
    conn.close()

    slot_list = []
    for slot in slots:
        slot_list.append({
            "id": slot[0],
            "slot_number": slot[1],
            "status": slot[2]
        })

    return jsonify(slot_list)


# ---------------- SEND EXPIRY SMS ----------------

@app.route("/send_expiry_sms")
def send_expiry_sms():
    url = "https://www.fast2sms.com/dev/bulkV2"

    querystring = {
        "authorization": "sUmNEMI8VCSD4hkxrbgP5yK6lLu3cd9HR7wWeYojfGFZvq1p2z1SJGd38IUirBVHhYoLPDW2TAkgy7CX",
        "message": "Your parking time is over. Please extend parking now.",
        "language": "english",
        "route": "q",
        "numbers": "8104816148"
    }

    headers = {
        'cache-control': "no-cache"
    }

    response = requests.get(url, headers=headers, params=querystring)

    print(response.text)

    return "SMS Sent Successfully"






# ---------------- ADMIN PANEL ----------------
@app.route("/admin")
def admin():
    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM parking_slots")
    slots = cursor.fetchall()
    conn.close()

    return render_template("admin.html", slots=slots)


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)