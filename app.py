from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import os
import random
from datetime import datetime, timedelta
from math import radians, cos, sin, asin, sqrt
import uuid  
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import pytz
def generate_donation_id():
    return 'DON' + ''.join(random.choices(string.digits, k=6))

app = Flask(__name__)
app.secret_key = 'your-secret-key'

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

client = MongoClient("mongodb://localhost:27017")
db = client['grubsaver_db']
users = db['users']
waste_db = client["waste"]
biogas_orders = db['biogas_orders']
donations = waste_db["donations"]
subscriptions = db['subscriptions']
contact_messages = db['contact_messages']
if 'orders' not in db.list_collection_names():
    db.create_collection('orders')
orders = db['orders']

users.create_index('email', unique=True)
users.create_index('mobile', unique=True)
users.create_index('username', unique=True)

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='shrikrushnagandhewar@gmail.com',
    MAIL_PASSWORD='ktnm ilby nmbk ewwz'  # Use env vars instead in production!
)
mail = Mail(app)

def send_sms(mobile, otp):
    print(f"Simulated SMS to {mobile}: Your OTP is {otp}")

@app.route('/')
def index():
    return render_template('index.html')




@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email")
    if email:
        subscriptions.insert_one({"email": email})

        admin_msg = Message("New Newsletter Subscriber",
                            sender=app.config['MAIL_USERNAME'],
                            recipients=["kgandhewar9040@gmail.com"])
        admin_msg.body = f"A new user has subscribed with the email: {email}"
        mail.send(admin_msg)

        user_msg = Message("Welcome to GrubSaver Newsletter!",
                           sender=app.config['MAIL_USERNAME'],
                           recipients=[email])
        user_msg.body = (
            f"Hi there,\n\n"
            f"Thank you for subscribing to GrubSaver! 🎉\n\n"
            f"You'll now receive updates about food donations, buyer-seller features, and much more.\n\n"
            f"Stay connected and help reduce food waste with us!\n\n"
            f"- The GrubSaver Team"
        )
        mail.send(user_msg)

        flash("✅ Subscription successful. Check your email for confirmation.", "success")
    else:
        flash("❌ Please enter a valid email address.", "error")
    return redirect("/")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = {
            'full_name': request.form['fullName'],
            'email': request.form['email'],
            'mobile': request.form['mobile'],
            'username': request.form['username'],
            'password': request.form['password'],
            'user_type': request.form['user_type']
        }

        if data['user_type'] == 'buyer':
            buyer_type = request.form.get('buyer_type')
            data['buyer_type'] = buyer_type

            if buyer_type == 'ngo':
                data['ngo_name'] = request.form.get('ngo_name')
                data['ngo_reg'] = request.form.get('ngo_reg')
            elif buyer_type == 'biogas':
                data['biogas_name'] = request.form.get('biogas_name')
                data['biogas_capacity'] = request.form.get('biogas_capacity')

        if users.find_one({'email': data['email']}):
            flash('❌ Email is already registered.')
            return redirect('/register')
        if users.find_one({'mobile': data['mobile']}):
            flash('❌ Mobile number is already registered.')
            return redirect('/register')
        if users.find_one({'username': data['username']}):
            flash('❌ Username is already taken.')
            return redirect('/register')

        otp = str(random.randint(100000, 999999))
        session['otp'] = otp
        session['reg_data'] = data

        msg = Message('GrubSaver OTP Verification',
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[data['email']])
        msg.body = f'Your OTP for registration is: {otp}'
        mail.send(msg)

        send_sms(data['mobile'], otp)

        return redirect('/verify')

    return render_template('register.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        entered_otp = request.form['otp']
        if entered_otp == session.get('otp'):
            data = session.pop('reg_data', {})
            session.pop('otp', None)
            data['password'] = generate_password_hash(data['password'])
            users.insert_one(data)
            flash('✅ Registration successful! Please log in.')
            return redirect('/login')
        else:
            flash('❌ Incorrect OTP. Try again.')
    return render_template('verify.html')

from werkzeug.security import check_password_hash
from flask import Flask, request, session, flash, redirect, render_template

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # ✅ Hardcoded admin login (Uday / Krishna@9040)
        if username == 'Uday' and password == 'Krishna@9040':
            session['logged_in'] = True
            session['username'] = username
            session['user_type'] = 'admin'
            session['admin_logged_in'] = True
            flash('✅ Admin login successful!')
            return redirect('/admin/dashboard')

        # 🔐 Regular user login
        user = users.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            session['logged_in'] = True
            session['username'] = username
            session['user_type'] = user['user_type']

          

            # 👉 Handle buyer role specifically
            if user['user_type'] == 'buyer':
                if user.get('buyer_type') == 'biogas':
                    return redirect('/biogas')  # redirect to biogas page
                else:
                    return redirect('/buyer')  # NGO or regular buyer

            # Seller or delivery boy
            return redirect(f'/{user["user_type"]}')

        flash('❌ Invalid username or password.')

    return render_template('login.html')



@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.')
    return redirect('/')

@app.route('/about')
def about():
    return render_template('about.html')

# @app.route('/how_it_works')
# def about():
#     return render_template('how_it_works.html')

@app.route('/seller')
def seller_page():
    if session.get('logged_in') and session.get('user_type') == 'seller':
        return render_template('seller.html')
    flash('Access denied.')
    return redirect('/login')



@app.route('/biogas')
def biogas_page():
    if 'logged_in' not in session or session.get('user_type') != 'buyer':
        flash("Access denied. Please log in as a buyer.")
        return redirect('/login')

    return render_template('biogas.html')


@app.route('/buyer')
def buyer_page():
    if session.get('logged_in') and session.get('user_type') == 'buyer':
        return render_template('buyer.html')
    flash('Access denied.')
    return redirect('/login')



import uuid  # already in your code

@app.route('/donate_form', methods=['GET', 'POST'])
def donate_form():
    if 'logged_in' not in session or session.get('user_type') != 'seller':
        flash('Login as a seller to post donations.')
        return redirect('/login')

    if request.method == 'POST':
        try:
            title = request.form.get('title').strip()
            price = float(request.form.get('price'))  # ✅ New price field
            quantity = float(request.form.get('quantity'))  # Quantity field
            location = request.form.get('location').strip()
            restaurant_name = request.form.get('restaurant_name').strip()
            restaurant_address = request.form.get('restaurant_address').strip()
            description = request.form.get('description').strip()
            expire_after = int(request.form.get('expire_after'))

            image_file = request.files.get('image')
            if not image_file or not allowed_file(image_file.filename):
                flash('❌ Invalid image file.')
                return redirect('/donate_form')

            filename = f"{uuid.uuid4().hex}_{secure_filename(image_file.filename)}"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)

            # Get user info
            username = session['username']
            user_record = users.find_one({'username': username})
            mobile_number = user_record.get('mobile', 'N/A')

            # IST datetime
            utc_now = datetime.utcnow()
            ist_timezone = pytz.timezone('Asia/Kolkata')
            created_at_ist = utc_now.replace(tzinfo=pytz.utc).astimezone(ist_timezone)
            expiry_time_ist = created_at_ist + timedelta(hours=expire_after)

            # ✅ Generate unique donation_id
            donation_id = f"DN{uuid.uuid4().hex[:8].upper()}"  # example: DN7F9A12C4

            donation = {
                "donation_id": donation_id,  # ✅ unique transaction ID
                "title": title,
                "quantity": quantity,\
                "price": price,  # ✅ Storing price
                "location": location,
                "restaurant_name": restaurant_name,
                "restaurant_address": restaurant_address,
                "description": description,
                "image_filename": filename,
                "posted_by": username,
                "posted_mobile": mobile_number,
                "created_at": created_at_ist,
                "expiry_time": expiry_time_ist,
                
                "expired": False
            }

            donations.insert_one(donation)
            flash(f"✅ Donation posted successfully! ID: {donation_id}")
            return redirect('/seller')

        except Exception as e:
            print(f"[Error] Donation form: {e}")
            flash("❌ Something went wrong. Please try again.")
            return redirect('/donate_form')

    return render_template('donate_form.html')


@app.before_request
def update_expired_donations():
    ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    donations.update_many(
        {'expiry_time': {'$lt': now_ist}, 'expired': False},
        {'$set': {'expired': True}}
    )
@app.route('/my_orders')
def my_orders():
    if 'logged_in' not in session or session.get('user_type') != 'buyer':
        flash('Login as buyer.')
        return redirect('/login')

    my_orders = list(orders.find({'buyer': session['username']}))
    return render_template('my_orders.html', orders=my_orders)

@app.route('/seller_orders')
def seller_orders():
    if 'logged_in' not in session or session.get('user_type') != 'seller':
        flash('Login as seller.')
        return redirect('/login')

    my_sales = list(orders.find({
        'seller': session['username'],
        'status': {'$ne': 'delivered'}  # Exclude delivered
    }))
    return render_template('seller_orders.html', orders=my_sales)




@app.route('/my_donations')
def my_donations():
    if 'logged_in' not in session or session.get('user_type') != 'seller':
        flash('Please login as a seller to view your donations.')
        return redirect('/login')

    username = session['username']

    # Active (non-expired) donations from donations collection
    active_donations = list(donations.find({'posted_by': username}))
    for d in active_donations:
        d['image_path'] = url_for('static', filename=f'uploads/{d["image_filename"]}') if 'image_filename' in d else None
        d['created_at_str'] = str(d.get('created_at'))
        d['expiry_time_str'] = str(d.get('expiry_time'))
        d['expired_str'] = "Yes ✅" if d.get('expired') else "No ❌"
        d['type'] = 'active'

    # Ordered or delivered donations from orders collection
    ordered_donations = list(orders.find({'seller': username}))
    for o in ordered_donations:
        o['image_path'] = url_for('static', filename=f'uploads/{o["image_filename"]}') if 'image_filename' in o else None
        o['created_at_str'] = str(o.get('created_at', ''))
        o['expiry_time_str'] = 'N/A'
        o['expired_str'] = o.get('status', 'ordered').capitalize()
        o['type'] = 'ordered'

    all_donations = active_donations + ordered_donations

    return render_template('my_donations.html', donations=all_donations)


@app.route('/donate_search', methods=['GET', 'POST'])
def donate_search():
    if 'logged_in' not in session or session.get('user_type') != 'buyer':
        flash('Access denied. Only buyers can view this page.')
        return redirect('/login')

    query = {}
    search_term = ''

    if request.method == 'POST':
        search_term = request.form.get('search', '').strip()
        if search_term:
            query = {
                '$or': [
                    {'title': {'$regex': search_term, '$options': 'i'}},
                    {'location': {'$regex': search_term, '$options': 'i'}},
                    {'restaurant_name': {'$regex': search_term, '$options': 'i'}}
                ]
            }

    all_donations = list(donations.find(query).sort('created_at', -1))

    for d in all_donations:
        d['image_path'] = url_for('static', filename=f'uploads/{d["image_filename"]}') if 'image_filename' in d else None
        d['created_at_str'] = d.get('created_at', 'Unknown')

    return render_template('donate_search.html', donations=all_donations, search_term=search_term)



@app.route('/order/<donation_id>', methods=['POST'])
def place_order(donation_id):
    if 'logged_in' not in session or session.get('user_type') != 'buyer':
        flash('Only buyers can place orders.')
        return redirect('/login')

    try:
        buyer_username = session['username']
        donation = donations.find_one({'_id': ObjectId(donation_id)})

        if not donation:
            flash('Donation not found.')
            return redirect('/donate_search')

        if donation.get('expired', False):
            flash('This donation has expired.')
            return redirect('/donate_search')

        # Prevent multiple orders on same donation
        if orders.find_one({'donation_id': donation['donation_id']}):
            flash('This item has already been ordered.')
            return redirect('/donate_search')

        # Prepare order entry
        order = {
            'order_id': f"ORD{uuid.uuid4().hex[:8].upper()}",
            'donation_id': donation['donation_id'],
            'title': donation['title'],
            'quantity': donation['quantity'],
            'location': donation['location'],
            'restaurant_name': donation['restaurant_name'],
            'restaurant_address': donation['restaurant_address'],
            'description': donation['description'],
            'price': donation['price'],
            'image_filename': donation['image_filename'],
            'buyer': buyer_username,
            'seller': donation['posted_by'],
            'created_at': donation['created_at'],         # ✅ Added
            'expiry_time': donation['expiry_time'],       # ✅ Added
            'ordered_at': datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        }

        # Insert into orders and remove from donations
        orders.insert_one(order)
        donations.delete_one({'_id': donation['_id']})

        # Send email to seller
        seller = users.find_one({'username': donation['posted_by']})
        if seller:
            seller_email = seller.get('email')
            if seller_email:
                msg = Message(
                    subject='GrubSaver: Your donation has been ordered!',
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[seller_email]
                )
                msg.body = (
                    f"Hi {seller['full_name']},\n\n"
                    f"Your donation titled '{donation['title']}' has been ordered by buyer '{buyer_username}'.\n\n"
                    f"Location: {donation['location']}\n"
                    f"Restaurant: {donation['restaurant_name']}\n"
                    f"Quantity: {donation['quantity']}\n\n"
                    f"Price: {donation['price']}\n\n"
                    f"Thank you for contributing to food waste reduction!\n\n"
                    f"- GrubSaver Team"
                )
                mail.send(msg)

        # Store the order ID temporarily for receipt display
        session['last_order'] = order['order_id']

        flash('✅ Order placed successfully!')
        return redirect('/receipt')

    except Exception as e:
        print(f"[Error in placing order]: {e}")
        flash('❌ Something went wrong while placing the order.')
        return redirect('/donate_search')





@app.route('/place_order/<donation_id>', methods=['POST'])
def place_order_view(donation_id):
    if 'logged_in' not in session or session.get('user_type') != 'buyer':
        flash('Login as a buyer to place an order.')
        return redirect('/login')

    try:
        # Get donation
        donation = donations.find_one({'_id': ObjectId(donation_id)})
        if not donation:
            flash('Donation not found.')
            return redirect('/donate_search')

        # Extract buyer and seller info
        buyer_username = session['username']
        seller_username = donation['posted_by']
        seller_email = users.find_one({'username': seller_username})['email']

        # Create order record
        order = {
            'donation_id': donation.get('donation_id', str(donation_id)),
            'title': donation['title'],
            'quantity': donation['quantity'],
            'location': donation['location'],
            'description': donation['description'],
            'image_filename': donation['image_filename'],
            'restaurant_name': donation['restaurant_name'],
            'price': donation['price'],
            'restaurant_address': donation['restaurant_address'],
            'buyer': buyer_username,
            'seller': seller_username,
            'created_at': donation['created_at'],
            'order_time': datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S %Z%z'),
        }

        # Save order
        db['orders'].insert_one(order)

        # Delete the donation from listings
        donations.delete_one({'_id': ObjectId(donation_id)})

        # Send email to seller
        msg = Message("New Order Placed on GrubSaver",
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[seller_email])
        msg.body = (
            f"Hello {seller_username},\n\n"
            f"You have received a new order from {buyer_username} for:\n"
            f"Title: {donation['title']}\n"
            f"Quantity: {donation['quantity']} kg\n"
            f"Location: {donation['location']}\n\n"
            f"Please coordinate accordingly.\n\n"
            f"- GrubSaver"
        )
        mail.send(msg)

        # Show receipt page to buyer
        return render_template('receipt.html', order=order)

    except Exception as e:
        print(f"[Error] place_order_view: {e}")
        flash("❌ Something went wrong. Try again.")
        return redirect('/donate_search')


@app.route('/biogas_order/<donation_id>', methods=['POST'])
def place_biogas_order(donation_id):
    if 'logged_in' not in session:
        flash('Please log in to continue.')
        return redirect('/login')

    try:
        # Get donation from DB
        donation = donations.find_one({'_id': ObjectId(donation_id)})

        if not donation:
            flash('Donation not found.')
            return redirect('/biogas_resale')

        if not donation.get('expired', False):
            flash('Only expired donations can be ordered from this section.')
            return redirect('/biogas_resale')

        # Buyer and seller info
        buyer_username = session['username']
        seller_username = donation['posted_by']
        seller_user = users.find_one({'username': seller_username})
        seller_email = seller_user['email'] if seller_user else None

        # Order data
        order = {
            'donation_id': donation.get('donation_id', str(donation_id)),
            'title': donation['title'],
            'quantity': donation['quantity'],
            'location': donation['location'],
            'description': donation['description'],
            'image_filename': donation['image_filename'],
            'restaurant_name': donation['restaurant_name'],
            'restaurant_address': donation['restaurant_address'],
            'price':  donation['price'],
            'seller': seller_username,
            'created_at': donation['created_at'],
            'order_time': datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S %Z%z'),
            'source': 'expired',
            'status': 'pending'
             # Include price if needed
        }

        # Save order to biogas_orders
        biogas_orders.insert_one(order)

        # Delete from donation listings
        donations.delete_one({'_id': ObjectId(donation_id)})

        # Notify seller
        if seller_email:
            msg = Message("Biogas Order Placed on GrubSaver",
                          sender=app.config['MAIL_USERNAME'],
                          recipients=[seller_email])
            msg.body = (
                f"Hello {seller_username},\n\n"
                f"A biogas plant has claimed your expired donation titled '{donation['title']}'.\n"
                f"Buyer: {buyer_username}\nLocation: {donation['location']}\n\n"
                f"- GrubSaver"
            )
            mail.send(msg)

        # ✅ Save order ID for receipt display
        session['last_biogas_order'] = order['donation_id']

        flash("✅ Donation moved to biogas plant orders successfully!")
        return redirect('/biogas_receipt')

    except Exception as e:
        print(f"[ERROR - Biogas Order]: {e}")
        flash("❌ Failed to place biogas order.")
        return redirect('/biogas_resale')


@app.route('/biogas_orders')
def biogas_orders_view():
    if 'logged_in' not in session or session.get('user_type') != 'seller':
        flash("Access denied. Please login as a seller.")
        return redirect('/login')

    # Get current seller username
    seller_username = session['username']

    # Fetch only orders where this seller is involved
    seller_orders = list(biogas_orders.find({'seller': seller_username}))

    # Add image paths if needed
    for order in seller_orders:
        if 'image_filename' in order:
            order['image_path'] = url_for('static', filename=f'uploads/{order["image_filename"]}')

    return render_template('biogas_orders.html', orders=seller_orders)

@app.route('/biogas_receipt')
def biogas_receipt():
    order_id = session.pop('last_biogas_order', None)  # Use the correct session key

    if not order_id:
        flash("No recent biogas order found.")
        return redirect('/biogas_resale')

    order = biogas_orders.find_one({'donation_id': order_id})

    if not order:
        flash("Order not found.")
        return redirect('/biogas_resale')

    if 'image_filename' in order:
        order['image_path'] = url_for('static', filename=f'uploads/{order["image_filename"]}')

    return render_template('biogas_receipt.html', order=order)



@app.route('/receipt')
def receipt():
    if 'last_order' not in session:
        flash('No recent order to display.')
        return redirect('/buyer')

    order = orders.find_one({'order_id': session.pop('last_order')})
    if not order:
        flash('Order not found.')
        return redirect('/buyer')

    order['image_path'] = url_for('static', filename=f'uploads/{order["image_filename"]}') if 'image_filename' in order else None
    return render_template('receipt.html', order=order)


@app.route('/donate-results', methods=['POST'])
def donate_results():
    if 'logged_in' not in session or session.get('user_type') != 'buyer':
        flash('Login as a buyer to search donations.')
        return redirect('/login')

    location_query = request.form['location']

    # Use case-insensitive partial matching in MongoDB
    matched_donations = list(donations.find({
        'location': {'$regex': location_query, '$options': 'i'}
    }))

    # Format image paths if needed
    for d in matched_donations:
        d['image_path'] = f"uploads/{d['image_filename']}" if 'image_filename' in d else None

    return render_template('donate_search.html', cards=matched_donations)
@app.route('/biogas_resale')
def biogas_resale():
    expired_donations = list(donations.find({'expired': True}))

    for d in expired_donations:
        d['image_path'] = url_for('static', filename=f'uploads/{d["image_filename"]}')
        d['created_at_str'] = d.get('created_at', 'Unknown')

    return render_template('biogas_resale.html', donations=expired_donations)


@app.route('/delete_donation/<donation_id>', methods=['POST'])
def delete_donation(donation_id):
    if 'logged_in' not in session:
        flash('Please log in to delete your donation.')
        return redirect('/login')

    donation = donations.find_one({'_id': ObjectId(donation_id)})

    if not donation:
        flash('Donation not found.')
        return redirect('/my_donations')

    # Ensure only the owner can delete their donation
    if donation.get('posted_by') != session.get('username'):
        flash('You are not authorized to delete this donation.')
        return redirect('/my_donations')

    # Delete image file from filesystem
    if 'image_filename' in donation:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], donation['image_filename'])
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            print(f"[Error] Failed to delete image: {e}")

    # Delete the donation from the database
    donations.delete_one({'_id': ObjectId(donation_id)})

    flash('✅ Donation deleted successfully.')
    return redirect('/my_donations')




from flask import render_template, session, redirect, url_for
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client['grubsaver_db']
users = db['users']
subscriptions = db['subscriptions']
orders = db['orders']

# Connect to donations in the separate "waste" database
donations = client["waste"]["donations"]

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    # Get buyers and sellers
    buyers = list(users.find({'role': 'buyer'}))
    sellers = list(users.find({'role': 'seller'}))
    biogas_orders_list = list(biogas_orders.find()) 

    # Get orders (transactions)
    transactions = list(orders.find({}))

    # Get newsletter subscribers
    subs = list(subscriptions.find({}))

    return render_template("admin_dashboard.html",
                           buyers=users.find({'user_type': 'buyer'}),
                           sellers=users.find({'user_type': 'seller'}),
                           transactions=transactions,
                            biogas_transactions=biogas_orders_list,
                           subs=subscriptions)






@app.route('/admin/delete_user/<username>', methods=['POST'])
def admin_delete_user(username):
    if not session.get('admin_logged_in'):
        return redirect('/login')

    user = users.find_one({'username': username})
    if not user:
        flash("❌ User not found.")
        return redirect('/admin/dashboard')

    email = user.get('email')
    if email:
        try:
            msg = Message("Account Deletion - GrubSaver",
                          sender=app.config['MAIL_USERNAME'],
                          recipients=[email])
            msg.body = (
                f"Dear {user.get('full_name', 'User')},\n\n"
                f"Your account with username '{username}' has been deleted by the admin for GrubSaver.\n"
                f"If this was a mistake or you have questions, please contact support.\n\n"
                f"Regards,\nGrubSaver Team"
            )
            mail.send(msg)
        except Exception as e:
            print(f"Email send failed: {e}")

    users.delete_one({'username': username})
    flash("✅ User deleted and email sent.")
    return redirect('/admin/dashboard')


@app.route('/admin/edit_user/<username>', methods=['GET', 'POST'])
def admin_edit_user(username):
    if not session.get('admin_logged_in'):
        flash("Access denied.")
        return redirect('/login')

    user = users.find_one({'username': username})
    if not user:
        flash("User not found.")
        return redirect('/admin/dashboard')

    if request.method == 'POST':
        updated_email = request.form.get('email')
        updated_mobile = request.form.get('mobile')
        updated_buyer_type = request.form.get('buyer_type')

        users.update_one(
            {'username': username},
            {'$set': {
                'email': updated_email,
                'mobile': updated_mobile,
                'buyer_type': updated_buyer_type
            }}
        )

        # ✅ Send email to user after update
        if updated_email:
            msg = Message(
                subject='Your GrubSaver Account Information Updated',
                sender=app.config['MAIL_USERNAME'],
                recipients=[updated_email]
            )
            msg.body = (
                f"Hi {username},\n\n"
                "This is to inform you that your account details were updated by the admin.\n"
                f"Updated Mobile: {updated_mobile}\n"
                f"Updated Buyer Type: {updated_buyer_type or 'N/A'}\n\n"
                "If you didn't request or approve this change, please contact support immediately.\n\n"
                "- GrubSaver Admin"
            )
            mail.send(msg)

        flash("✅ User information updated and email notification sent.")
        return redirect('/admin/dashboard')

    return render_template('admin_edit_user.html', user=user)


@app.route('/admin/track_orders')
def admin_track_orders():
    if not session.get('admin_logged_in'):
        flash("Admin access only.")
        return redirect('/login')

    all_orders = list(orders.find())
    for order in all_orders:
        order['image_path'] = url_for('static', filename=f'uploads/{order["image_filename"]}') if 'image_filename' in order else None
        order['status'] = order.get('status', 'pending')
    return render_template('admin_track_orders.html', orders=all_orders)


from bson.objectid import ObjectId

@app.route('/send_delivery_otp/<donation_id>', methods=['POST'])
def send_delivery_otp(donation_id):
    try:
        order1 = orders.find_one({'_id': ObjectId(donation_id)})
    except Exception:
        order1 = None

    if not order1:
        flash('Order not found.')
        return redirect(url_for('orders'))

    buyer_username = order1.get('buyer')
    if not buyer_username:
        flash('Buyer information not found in order.')
        return redirect(url_for('orders'))

    # Find buyer email in users collection by username
    buyer_doc = users.find_one({'username': buyer_username})
    if not buyer_doc or 'email' not in buyer_doc:
        flash('Buyer email not found.')
        return redirect(url_for('orders'))

    buyer_email = buyer_doc['email']

    otp = str(random.randint(100000, 999999))
    session['delivery_otp'] = otp
    session['delivery_order_id'] = donation_id

    msg = Message('Delivery OTP Verification',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[buyer_email])
    msg.body = f"Your OTP to confirm delivery of '{order1.get('title', '')}' is: {otp}"
    mail.send(msg)

    flash('OTP sent to buyer email. Please enter it below.')
    return redirect(url_for('verify_delivery_otp'))


@app.route('/verify_delivery_otp', methods=['GET', 'POST'])
def verify_delivery_otp():
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        real_otp = session.get('delivery_otp')
        donation_id = session.get('delivery_order_id')

        if not donation_id or not real_otp:
            flash('Session expired or invalid. Please try again.')
            return redirect(url_for('seller_orders'))

        if entered_otp == real_otp:
            # ✅ Just update the status
            orders.update_one({'_id': ObjectId(donation_id)},
                              {'$set': {'status': 'delivered'}})

            session.pop('delivery_otp', None)
            session.pop('delivery_order_id', None)

            flash('✅ Order marked as delivered!')
            return redirect(url_for('seller_orders'))
        else:
            return render_template('verify_delivery_otp.html', error="Incorrect OTP. Please try again.")

    return render_template('verify_delivery_otp.html')



# ✅ Route for Contact Us
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        date_submitted = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # ✅ Save to MongoDB
        contact_messages.insert_one({
            'name': name,
            'email': email,
            'message': message,
            'submitted_at': date_submitted
        })

        # ✅ Send email to admin
        msg = Message("📩 New Contact Message - GrubSaver",
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[app.config['MAIL_USERNAME']])  # send to self (admin)
        msg.body = (
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Date: {date_submitted}\n\n"
            f"Message:\n{message}"
        )
        mail.send(msg)

        flash('✅ Message sent successfully!')
        return redirect('/contact')

    return render_template('contact.html')  # your contact page


@app.route('/howitworks')
def how_it_works():
    return render_template('about us.html')

@app.route('/how_its_work')
def how_its_work():
    return render_template('how_its_work.html')


if __name__ == '__main__':
    app.run(debug=True)
