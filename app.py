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


@app.context_processor
def inject_wallet():
    try:
        user = session.get("username")

        if user:
            conn = sqlite3.connect("parking.db")
            cursor = conn.cursor()

            cursor.execute("SELECT wallet FROM users WHERE username=?", (user,))
            data = cursor.fetchone()
            conn.close()

            return dict(wallet=data[0] if data else 0)

    except:
        pass

    return dict(wallet=None)


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

    username = session.get("username")

    # ✅ GET WALLET BALANCE
    wallet = 0
    if username:
        cursor.execute("SELECT wallet FROM users WHERE username=?", (username,))
        result = cursor.fetchone()
        if result:
            wallet = result[0]

    conn.close()

    reviews = [
        {"name": "Rahul Sharma", "review": "Very easy to use and saved my time finding parking!"},
        {"name": "Priya Mehta", "review": "Payment and booking process is smooth and quick."},
        {"name": "Aman Verma", "review": "Best parking solution in crowded areas."}
    ]

    return render_template(
        "index.html",
        parking_slots=parking_slots,
        reviews=reviews,
        username=username,
        wallet=wallet   # ✅ PASS TO HTML
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
    "INSERT INTO users (username, password, wallet) VALUES (?, ?, ?)",
    (username, password, 0)
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
from datetime import datetime

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT wallet, pass_expiry FROM users WHERE username=?",
        (session["username"],)
    )

    data = cursor.fetchone()
    conn.close()

    # ✅ Safe handling (important)
    wallet = data[0] if data and data[0] else 0
    pass_expiry = data[1] if data else None

    has_pass = False

    if pass_expiry:
        try:
            expiry_date = datetime.strptime(pass_expiry, "%Y-%m-%d")
            if expiry_date >= datetime.now():
                has_pass = True
        except:
            has_pass = False

    return render_template(
        "dashboard.html",
        username=session["username"],
        wallet=wallet,
        has_pass=has_pass
    )

   
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
from datetime import datetime
import random

@app.route("/confirm_booking", methods=["POST"])
def confirm_booking():
    vehicle_number = request.form["vehicle_number"]
    vehicle_type = request.form["vehicle_type"]
    duration = request.form["duration"]
    price = int(request.form["price"])

    username = session.get("username")

    # SAVE SESSION
    session["vehicle_number"] = vehicle_number
    session["vehicle_type"] = vehicle_type
    session["duration"] = duration
    session["payment_amount"] = price * 100

    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()

    # 🔍 CHECK PASS
    cursor.execute("SELECT pass_expiry, wallet FROM users WHERE username=?", (username,))
    result = cursor.fetchone()

    if result and result[0]:
        try:
            expiry_date = datetime.strptime(result[0], "%Y-%m-%d")

            # ✅ PASS USER
            if expiry_date >= datetime.now():
                wallet = result[1]

                # 💰 CHECK WALLET
                if wallet >= price:
                    new_balance = wallet - price

                    cursor.execute(
                        "UPDATE users SET wallet=? WHERE username=?",
                        (new_balance, username)
                    )

                    conn.commit()
                    conn.close()

                    session["last_payment_id"] = "PASS_" + str(random.randint(1000, 9999))
                    return redirect("/success")

                else:
                    conn.close()
                    return "❌ Not enough balance in wallet"

        except:
            pass

    conn.close()

    # ❌ NON-PASS USER → RAZORPAY
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
    payment_id = request.args.get("payment_id") or session.get("last_payment_id")
    slot_number = session.get("booked_slot")
    username = session.get("username")

    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()

    cursor.execute(
    "INSERT INTO bookings (username, slot_number, payment_id, date, time) VALUES (?, ?, ?, ?, ?)",
    (
        session.get("username"),
        session.get("booked_slot"),
        payment_id,
        session.get("date"),
        session.get("time")
    )
)

    conn.commit()
    conn.close()

    # Save payment id for receipt + timer flow
    session["last_payment_id"] = payment_id

    # SHOW SUCCESS PAGE FIRST (not timer directly)
    return render_template("success.html", payment_id=payment_id)


# ---------------- TIMER PAGE ----------------
@app.route("/timer")
def timer():
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

    # ✅ NEW: DATE & TIME (AUTO)
    p.drawString(100, 620, f"Date: {session.get('date','-')}")
    p.drawString(100, 590, f"Time: {session.get('time','-')}")

    p.drawString(100, 560, f"Duration: {session.get('duration','-')}")
    p.drawString(100, 530, "Parking Slot Booking Confirmed")
    p.drawString(100, 500, "Status: Successful")
    p.drawString(100, 460, "Thank you for using ParkIQ!")

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

    # ✅ Fetch slot, payment, date & time
    cursor.execute(
        "SELECT slot_number, payment_id, date, time FROM bookings WHERE username=?",
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

# ---------------- ADD MONEY ----------------

@app.route("/add_money", methods=["GET", "POST"])
def add_money():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        amount = int(request.form["amount"])

        conn = sqlite3.connect("parking.db")
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET wallet = wallet + ? WHERE username=?",
            (amount, session["username"])
        )

        conn.commit()
        conn.close()

        return redirect(url_for("dashboard"))

    return render_template("add_money.html")

# BUY PASS
@app.route("/buy_pass")
def buy_pass():
    from datetime import datetime

    if "username" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT pass_expiry FROM users WHERE username=?",
        (session["username"],)
    )
    result = cursor.fetchone()

    conn.close()

    print("DEBUG PASS:", result)   # 👈 IMPORTANT (check terminal)

    # ✅ IF NO PASS → SHOW FORM
    if not result or result[0] is None:
        return render_template("buy_pass.html")

    # ✅ CHECK DATE
    try:
        expiry_date = datetime.strptime(result[0], "%Y-%m-%d")

        if expiry_date >= datetime.now():
            return f"""
            <h2>✅ Pass Active Till {result[0]}</h2>
            <a href='/view_pass'>View Pass</a>
            """

    except:
        return render_template("buy_pass.html")

    # ✅ EXPIRED → SHOW FORM
    return render_template("buy_pass.html")
  
# PASS PAYMENT

@app.route("/create_pass_payment", methods=["POST"])
def create_pass_payment():
    from datetime import datetime

    username = session.get("username")

    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT pass_expiry FROM users WHERE username=?",
        (username,)
    )
    result = cursor.fetchone()

    # ✅ CHECK IF PASS ALREADY ACTIVE
    if result and result[0]:
        try:
            expiry_date = datetime.strptime(result[0], "%Y-%m-%d")

            if expiry_date >= datetime.now():
                conn.close()
                return f"""
                <h2>⚠️ You already have an active pass till {result[0]}</h2>
                <a href='/view_pass'>View Pass</a>
                """
        except:
            pass

    conn.close()

    # CONTINUE NORMAL PAYMENT
    vehicle_number = request.form["vehicle_number"]
    vehicle_type = request.form["vehicle_type"]

    session["pass_vehicle"] = vehicle_number
    session["pass_type"] = vehicle_type

    amount = 50000

    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    return render_template(
        "pass_payment.html",
        order_id=order["id"],
        amount=amount,
        key_id="rzp_test_SdKPQQ7qGLvELC"
    )

# PASS ACTIVATE 

@app.route("/pass_success")
def pass_success():
    import datetime

    if "username" not in session:
        return redirect(url_for("login"))

    user = session.get("username")

    start_date = datetime.datetime.now()
    expiry_date = start_date + datetime.timedelta(days=30)

    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()

    # ✅ ADD ₹500 TO WALLET
    cursor.execute("UPDATE users SET wallet = wallet + 500 WHERE username=?", (user,))

    # ✅ STORE PASS ALSO (optional)
    cursor.execute("""
        UPDATE users 
        SET pass_expiry=?, vehicle_number=?, vehicle_type=? 
        WHERE username=?
    """, (
        expiry_date.strftime("%Y-%m-%d"),
        session.get("pass_vehicle"),
        session.get("pass_type"),
        user
    ))

    conn.commit()
    conn.close()

    return render_template("pass_success.html", expiry=expiry_date.strftime("%Y-%m-%d"))
# VIEW PASS 
@app.route("/view_pass")
def view_pass():
    if "username" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT vehicle_number, vehicle_type, pass_expiry 
        FROM users WHERE username=?
    """, (session["username"],))

    data = cursor.fetchone()
    conn.close()

    if not data:
        return "No pass found"

    vehicle_number, vehicle_type, expiry = data

    # check status
    from datetime import datetime
    status = "Active"
    if expiry:
        if datetime.strptime(expiry, "%Y-%m-%d") < datetime.now():
            status = "Expired"

    return render_template(
        "view_pass.html",
        username=session["username"],
        vehicle_number=vehicle_number,
        vehicle_type=vehicle_type,
        expiry=expiry,
        status=status
    )




# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)