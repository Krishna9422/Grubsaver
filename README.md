Here is a complete `README.md` file for your **GrubSaver** project, formatted for GitHub:

---

```markdown
# 🌍 GrubSaver

**GrubSaver** is a smart, sustainable web platform designed to reduce food waste by connecting food donors with people in need. The application enables sellers to donate excess food and allows buyers to place orders for available food near them. Expired donations are automatically filtered out and moved to a biogas resale page to promote zero waste.

## 🚀 Features

- ✅ **User Registration/Login** with OTP verification (Email & Mobile)
- 👨‍🍳 **Role-Based Access** (Seller, Buyer, Delivery Boy, Admin)
- 🍽 **Food Donation** form with images and expiration in IST
- 🔍 **Location-Based Search** for available donations
- 🧾 **Order Placement** with:
  - Email notification to the seller
  - On-page buyer receipt
  - Order management for both buyer and seller
- 🔄 **Donation Expiration Handling** with expired items moved to the Biogas page
- 📬 **Newsletter Subscription** and admin-managed transaction tracking
- 🧑‍💼 **Admin Panel** for managing users, orders, and delivery tracking
- 🚚 **Delivery Boy Portal** for viewing undelivered orders

---

## 🛠 Tech Stack

| Layer       | Technology             |
|-------------|------------------------|
| Backend     | Python Flask           |
| Database    | MongoDB (PyMongo)      |
| Frontend    | HTML, CSS, JavaScript  |
| Auth        | Email & SMS OTP (SMTP, API) |
| Timezone    | IST-aware datetime (pytz)  |

---

## 🗂 Project Structure

```

grubsaver/
├── static/              # Static files (CSS, JS, images)
├── templates/           # HTML templates
├── app.py               # Main Flask app
├── config.py            # Configuration for DB, secrets
├── utils/               # Helper functions (OTP, email, datetime, etc.)
├── requirements.txt     # Python dependencies
└── README.md

````

---

## ⚙️ Setup Instructions

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/grubsaver.git
cd grubsaver
````

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Configure environment:**
   Create a `.env` file or set the following variables:

```env
MONGO_URI=your_mongo_uri
EMAIL_USER=your_email@example.com
EMAIL_PASS=your_email_password
TWILIO_SID=your_twilio_sid
TWILIO_AUTH=your_twilio_auth_token
TWILIO_PHONE=your_twilio_phone
```

4. **Run the application:**

```bash
python app.py
```

The app will run locally at `http://127.0.0.1:5000/`.

---

## 🧪 Example Use Cases

* **Seller:** Registers, donates excess food with an expiry time, receives order alerts via email.
* **Buyer:** Logs in, searches nearby food, places an order, and receives a receipt.
* **Admin:** Manages users, deletes accounts, tracks orders and deliveries.
* **Delivery Boy:** Views undelivered orders with address and user details.

---

## 🤝 Contributing

Feel free to fork this repo, create a branch, and submit a pull request. Contributions, bug reports, and feature requests are welcome!

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 📧 Contact

For questions or support, contact: **[yourname@example.com](mailto:yourname@example.com)**

```

---

Would you like me to generate a downloadable ZIP of your entire project with this `README.md` file included? Or tailor the setup instructions to your actual file structure and hosting environment?
```
