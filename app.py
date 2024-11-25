from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import User, db
from forms import RegistrationForm, LoginForm, TwoFactorForm, SupportForm
from ai_module import AdvancedAI
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp
import qrcode
import io
from base64 import b64encode

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456789'  # Replace with a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize the AI
ai = AdvancedAI()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Hash the password
        hashed_password = generate_password_hash(form.password.data)
        # Create new user
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            consent=form.consent.data
        )
        db.session.add(new_user)
        db.session.commit()
        # Generate 2FA secret
        new_user.otp_secret = pyotp.random_base32()
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Check if user exists
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            # User exists and password matches
            session['pre_2fa_userid'] = user.id
            return redirect(url_for('verify_2fa'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)

# 2FA Verification Route
@app.route('/verify_2fa', methods=['GET', 'POST'])
def verify_2fa():
    form = TwoFactorForm()
    user = User.query.get(session['pre_2fa_userid'])
    if user.otp_secret is None:
        # Generate OTP secret and QR code
        user.otp_secret = pyotp.random_base32()
        db.session.commit()
    otp_secret = user.otp_secret
    totp = pyotp.TOTP(otp_secret)
    qr_uri = totp.provisioning_uri(name=user.username, issuer_name="AI_Assistant")
    # Generate QR code
    qr = qrcode.QRCode()
    qr.add_data(qr_uri)
    qr.make()
    img = qr.make_image(fill='black', back_color='white')
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_img_str = b64encode(buffered.getvalue()).decode('utf-8')

    if form.validate_on_submit():
        token = form.token.data
        if totp.verify(token):
            login_user(user)
            session.pop('pre_2fa_userid', None)
            flash('Login successful.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid authentication token.', 'danger')
    return render_template('verify_2fa.html', form=form, qr_img_str=qr_img_str)

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

# AI Processing Route
@app.route('/process', methods=['POST'])
@login_required
def process():
    data = request.get_json()
    user_input = data.get('message')
    mode = data.get('mode')  # 'emotion' or 'logic'
    consent = current_user.consent
    response = ai.handle_user_input(user_input, consent, mode)
    return jsonify(response)

# Customer Support Route
@app.route('/support', methods=['GET', 'POST'])
def support():
    form = SupportForm()
    if form.validate_on_submit():
        # Handle support request
        flash('Your support request has been submitted.', 'success')
        return redirect(url_for('support'))
    return render_template('support.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
