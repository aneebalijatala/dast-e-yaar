from flask import Flask, render_template, request, redirect, Response, send_from_directory, url_for
from models import db, Admin, Case, Document
from config import Config
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
import pdfkit
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# =========================
# LOGIN MANAGER
# =========================
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.session_protection = "strong"


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


# =========================
# 🔐 FIXED GLOBAL SECURITY (100% SAFE)
# =========================
@app.before_request
def secure_app():
    # endpoint safety check
    if request.endpoint is None:
        return

    # allow safe endpoints
    allowed = ['login', 'static']

    if request.endpoint in allowed:
        return

    # block everything else if not logged in
    if not current_user.is_authenticated:
        return redirect(url_for('login'))


# =========================
# ROOT
# =========================
@app.route('/')
def home():
    return redirect('/login')


# =========================
# LOGIN
# =========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/home')

    if request.method == 'POST':
        user = Admin.query.filter_by(username=request.form['username']).first()

        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/home')

    return render_template('login.html')


# =========================
# MAIN MENU
# =========================
@app.route('/home')
@login_required
def home_page():
    return render_template('home.html')


# =========================
# LOGOUT
# =========================
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


# =========================
# FORM
# =========================
@app.route('/form', methods=['GET', 'POST'])
@login_required
def form():
    if request.method == 'POST':

        case = Case(
            name=request.form.get('name'),
            address=request.form.get('address'),
            dob=request.form.get('dob'),
            cnic=request.form.get('cnic'),
            religion=request.form.get('religion'),
            phone=request.form.get('phone'),
            gender=request.form.get('gender'),

            marital_status=request.form.get('marital_status'),
            dependents=request.form.get('dependents'),
            family_members=request.form.get('family_members'),
            income=request.form.get('income'),
            expenses=request.form.get('expenses'),

            case_type=request.form.get('case_type'),
            description=request.form.get('description'),
            amount=request.form.get('amount'),
            previous_help=request.form.get('previous_help'),

            account_type=request.form.get('account_type'),
            account_number=request.form.get('account_number'),
            account_holder=request.form.get('account_holder'),
            relation=request.form.get('relation'),

            status="Pending"
        )

        db.session.add(case)
        db.session.commit()

        # FILE UPLOAD
        files = request.files.getlist('files')

        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                doc = Document(filename=filename, case_id=case.id)
                db.session.add(doc)

        db.session.commit()

        return redirect('/dashboard')

    return render_template('form.html')


# =========================
# DASHBOARD
# =========================
@app.route('/dashboard')
@login_required
def dashboard():
    status = request.args.get('status')

    if status:
        cases = Case.query.filter_by(status=status).all()
    else:
        cases = Case.query.all()

    return render_template('dashboard.html', cases=cases)


# =========================
# CASE DETAIL
# =========================
@app.route('/case/<int:id>', methods=['GET', 'POST'])
@login_required
def case_detail(id):
    case = Case.query.get_or_404(id)
    docs = Document.query.filter_by(case_id=id).all()

    if request.method == 'POST':
        if current_user.role == 'admin':
            case.status = request.form.get('status')

        case.comments = request.form.get('comments')
        db.session.commit()

    return render_template('case_detail.html', case=case, docs=docs)


# =========================
# FILE ACCESS
# =========================
@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# =========================
# PDF GENERATION
# =========================
@app.route('/case/<int:id>/pdf')
@login_required
def generate_pdf(id):
    case = Case.query.get_or_404(id)
    docs = Document.query.filter_by(case_id=id).all()

    html = render_template(
        'case_pdf.html',
        case=case,
        docs=docs
    )

    options = {
        'enable-local-file-access': None,
        'page-size': 'A4',
        'encoding': 'UTF-8'
    }

    pdf = pdfkit.from_string(html, False, options=options)

    return Response(
        pdf,
        content_type='application/pdf',
        headers={
            "Content-Disposition": f"attachment; filename=case_{id}.pdf"
        }
    )


# =========================
# INIT DB + RUN
# =========================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        if not Admin.query.filter_by(username='admin').first():
            admin = Admin(username='admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

# routes above...

if __name__ == "__main__":
    app.run()