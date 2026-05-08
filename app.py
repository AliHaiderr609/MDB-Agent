import os
import hashlib
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

# NLP Utilities
from nlp_utils.pdf_processor import extract_text_from_pdf
from nlp_utils.academic_filter import is_academic_query
from nlp_utils.keyword_extractor import extract_keywords
from nlp_utils.semantic_search import get_best_match, chunk_text

app = Flask(__name__)
app.secret_key = 'mdb_secret_key_2024'

# Configure Database
db_path = os.path.join(os.path.dirname(__file__), 'mdb.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy(app)

# ──────────────── Models ────────────────

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student') # student, instructor, admin
    status = db.Column(db.String(20), nullable=False, default='active') # active, blocked
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Handout(db.Model):
    __tablename__ = 'handouts'
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    extracted_text = db.Column(db.Text, nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

class Query(db.Model):
    __tablename__ = 'queries'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    query_text = db.Column(db.Text, nullable=False)
    is_academic = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Response(db.Model):
    __tablename__ = 'responses'
    id = db.Column(db.Integer, primary_key=True)
    query_id = db.Column(db.Integer, db.ForeignKey('queries.id'), nullable=False)
    keywords = db.Column(db.Text)
    matched_content = db.Column(db.Text)
    generated_response = db.Column(db.Text)
    similarity_score = db.Column(db.Float)

class FilterLog(db.Model):
    __tablename__ = 'filter_logs'
    id = db.Column(db.Integer, primary_key=True)
    query_text = db.Column(db.Text, nullable=False)
    reason = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def init_db():
    with app.app_context():
        db.create_all()
        # Create default admin if not exists
        admin = User.query.filter_by(email='maryam@admin.com').first()
        if not admin:
            new_admin = User(
                name='Administrator',
                email='maryam@admin.com',
                password_hash=hash_password('admin123'),
                role='admin',
                status='active'
            )
            db.session.add(new_admin)
            db.session.commit()

# ──────────────── Auth decorators ────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if session.get('role') not in roles:
                flash('Access denied.', 'danger')
                role = session.get('role')
                if role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                elif role == 'instructor':
                    return redirect(url_for('instructor_dashboard'))
                return redirect(url_for('student_dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorator

# ──────────────── Routes ────────────────

@app.route('/')
def index():
    if 'user_id' in session:
        role = session.get('role')
        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif role == 'instructor':
            return redirect(url_for('instructor_dashboard'))
        return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET','POST'])
def register():
    if 'user_id' in session:
        role = session.get('role')
        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif role == 'instructor':
            return redirect(url_for('instructor_dashboard'))
        return redirect(url_for('student_dashboard'))
    if request.method == 'POST':
        name  = request.form.get('name','').strip()
        email = request.form.get('email','').strip().lower()
        pw    = request.form.get('password','')
        pw2   = request.form.get('confirm_password','')
        
        if not name or not email or not pw:
            flash('All fields are required.', 'danger')
            return render_template('register.html')
        if pw != pw2:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        if len(pw) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html')
            
        existing = User.query.filter_by(email=email).first()
        if existing:
            flash('Email already registered.', 'danger')
            return render_template('register.html')
            
        new_user = User(
            name=name,
            email=email,
            password_hash=hash_password(pw),
            role='student',
            status='active'
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if 'user_id' in session:
        role = session.get('role')
        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif role == 'instructor':
            return redirect(url_for('instructor_dashboard'))
        return redirect(url_for('student_dashboard'))
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower()
        pw    = request.form.get('password','')
        
        user = User.query.filter_by(email=email).first()
        if not user or user.password_hash != hash_password(pw):
            flash('Invalid email or password.', 'danger')
            return render_template('login.html')
            
        if user.status == 'blocked':
            flash('Your account has been blocked. Contact administrator.', 'danger')
            return render_template('login.html')
            
        session['user_id'] = user.id
        session['name']    = user.name
        session['role']    = user.role
        flash(f'Welcome back, {user.name}!', 'success')
        
        if user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif user.role == 'instructor':
            return redirect(url_for('instructor_dashboard'))
        return redirect(url_for('student_dashboard'))
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    role = session.get('role')
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif role == 'instructor':
        return redirect(url_for('instructor_dashboard'))
    return redirect(url_for('student_dashboard'))

@app.route('/student/dashboard')
@login_required
@role_required('student')
def student_dashboard():
    handouts = Handout.query.order_by(Handout.upload_date.desc()).all()
    return render_template('student_dashboard.html', handouts=handouts)

@app.route('/instructor/dashboard')
@login_required
@role_required('instructor')
def instructor_dashboard():
    students = User.query.filter_by(role='student').order_by(User.name).all()
    handouts = Handout.query.order_by(Handout.upload_date.desc()).all()
    return render_template('instructor_dashboard.html', students=students, handouts=handouts)

@app.route('/admin')
@login_required
@role_required('admin')
def admin_dashboard():
    users = User.query.order_by(User.role, User.name).all()
    return render_template('admin_panel.html', users=users)

@app.route('/admin/users/create', methods=['POST'])
@login_required
@role_required('admin')
def admin_create_user():
    name  = request.form.get('name','').strip()
    email = request.form.get('email','').strip().lower()
    pw    = request.form.get('password','')
    role  = request.form.get('role','student')
    
    if not name or not email or not pw or role not in ('student','instructor','admin'):
        flash('All fields required and role must be valid.', 'danger')
        return redirect(url_for('admin_dashboard'))
        
    existing = User.query.filter_by(email=email).first()
    if existing:
        flash('Email already exists.', 'danger')
        return redirect(url_for('admin_dashboard'))
        
    try:
        new_user = User(
            name=name,
            email=email,
            password_hash=hash_password(pw),
            role=role,
            status='active'
        )
        db.session.add(new_user)
        db.session.commit()
        flash(f'User {name} created successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating user: {str(e)}', 'danger')
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/users/<int:uid>/block', methods=['POST'])
@login_required
@role_required('admin')
def admin_block_user(uid):
    if uid == session['user_id']:
        flash('You cannot block yourself.', 'danger')
        return redirect(url_for('admin_dashboard'))
        
    user = User.query.get(uid)
    if user:
        user.status = 'blocked'
        db.session.commit()
        flash('User blocked.', 'warning')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/users/<int:uid>/unblock', methods=['POST'])
@login_required
@role_required('admin')
def admin_unblock_user(uid):
    user = User.query.get(uid)
    if user:
        user.status = 'active'
        db.session.commit()
        flash('User unblocked.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/users/<int:uid>/delete', methods=['POST'])
@login_required
@role_required('admin')
def admin_delete_user(uid):
    if uid == session['user_id']:
        flash('You cannot delete yourself.', 'danger')
        return redirect(url_for('admin_dashboard'))
        
    user = User.query.get(uid)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted.', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/users/<int:uid>/role', methods=['POST'])
@login_required
@role_required('admin')
def admin_change_role(uid):
    if uid == session['user_id']:
        flash('You cannot change your own role.', 'danger')
        return redirect(url_for('admin_dashboard'))
        
    new_role = request.form.get('role')
    if new_role not in ('student','instructor','admin'):
        flash('Invalid role.', 'danger')
        return redirect(url_for('admin_dashboard'))
        
    user = User.query.get(uid)
    if user:
        user.role = new_role
        db.session.commit()
        flash('Role updated.', 'success')
    return redirect(url_for('admin_dashboard'))

# ──────────────── Phase 3: Integration & AI Endpoints ────────────────

@app.route('/upload_handout', methods=['POST'])
@login_required
@role_required('instructor')
def upload_handout():
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('instructor_dashboard') if session.get('role') == 'instructor' else url_for('student_dashboard'))
        
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('instructor_dashboard') if session.get('role') == 'instructor' else url_for('student_dashboard'))
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(filepath)
        
        # Extract text using NLP utility
        extracted_text = extract_text_from_pdf(filepath)
        
        if not extracted_text:
            flash('Failed to extract text from PDF.', 'danger')
            return redirect(url_for('instructor_dashboard') if session.get('role') == 'instructor' else url_for('student_dashboard'))
            
        # Save to database
        new_handout = Handout(
            file_name=filename,
            extracted_text=extracted_text
        )
        db.session.add(new_handout)
        db.session.commit()
        
        flash(f'Handout "{filename}" uploaded and processed successfully!', 'success')
        return redirect(url_for('instructor_dashboard') if session.get('role') == 'instructor' else url_for('student_dashboard'))
        
    flash('Allowed file types: PDF only.', 'danger')
    return redirect(url_for('instructor_dashboard') if session.get('role') == 'instructor' else url_for('student_dashboard'))

@app.route('/handouts/<int:handout_id>/download')
@login_required
@role_required('student')
def download_handout(handout_id):
    handout = Handout.query.get_or_404(handout_id)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], handout.file_name)
    if not os.path.isfile(filepath):
        flash('This handout file is no longer available on the server.', 'danger')
        return redirect(url_for('student_dashboard'))
    return send_file(
        filepath,
        as_attachment=True,
        download_name=handout.file_name,
        mimetype='application/pdf',
    )

@app.route('/handouts/<int:handout_id>/delete', methods=['POST'])
@login_required
@role_required('instructor')
def delete_handout(handout_id):
    handout = Handout.query.get_or_404(handout_id)
    upload_root = os.path.realpath(app.config['UPLOAD_FOLDER'])
    filepath = os.path.realpath(os.path.join(upload_root, handout.file_name))
    if filepath.startswith(upload_root + os.sep):
        if os.path.isfile(filepath):
            try:
                os.remove(filepath)
            except OSError:
                flash(f'Could not remove file "{handout.file_name}" from disk.', 'warning')
    db.session.delete(handout)
    db.session.commit()
    flash(f'Handout "{handout.file_name}" removed.', 'success')
    return redirect(url_for('instructor_dashboard'))

@app.route('/analyze_query', methods=['POST'])
@login_required
@role_required('student')
def analyze_query():
    query_text = request.form.get('query','').strip()
    if not query_text:
        return jsonify({'error': 'Empty query'}), 400
        
    # 1. Save initial query to DB
    new_query = Query(
        user_id=session['user_id'],
        query_text=query_text
    )
    db.session.add(new_query)
    db.session.flush() # Get the ID before commit
    
    # 2. Check Academic Filter
    is_acad, reason = is_academic_query(query_text)
    
    if not is_acad:
        new_query.is_academic = False
        log = FilterLog(query_text=query_text, reason=reason)
        db.session.add(log)
        db.session.commit()
        return jsonify({
            'is_academic': False,
            'message': 'Your post was rejected as it contains non-academic content.',
            'reason': reason
        })
        
    # 3. Process Academic Query
    # Extract keywords
    keywords_list = extract_keywords(query_text)
    keywords_str = ", ".join(keywords_list)
    
    # Find best match from all handouts
    handouts = Handout.query.all()
    if not handouts:
        db.session.commit()
        return jsonify({
            'is_academic': True,
            'message': 'No handout material available yet. Please contact your instructor.',
            'response': None
        })
        
    # Combine all hand out texts for matching
    all_chunks = []
    for h in handouts:
        all_chunks.extend(chunk_text(h.extracted_text))
        
    best_chunk, score = get_best_match(query_text, all_chunks)
    
    # 4. Generate Response
    if best_chunk and score > 0.35:
        generated_resp = f"According to the handout: \"{best_chunk}\""
    else:
        generated_resp = "I couldn't find a direct answer in the handouts, but I've saved your query."
    
    # Save Response
    new_response = Response(
        query_id=new_query.id,
        keywords=keywords_str,
        matched_content=best_chunk if (best_chunk and score > 0.35) else None,
        generated_response=generated_resp,
        similarity_score=score
    )
    db.session.add(new_response)
    db.session.commit()
    
    return jsonify({
        'is_academic': True,
        'keywords': keywords_list,
        'response': generated_resp,
        'score': score
    })

@app.route('/history')
@login_required
@role_required('student')
def history():
    user_id = session['user_id']
    # Join queries and responses
    past_interactions = db.session.query(Query, Response).outerjoin(
        Response, Query.id == Response.query_id
    ).filter(Query.user_id == user_id).order_by(Query.created_at.desc()).all()
    
    # Return as JSON for now (Phase 3 focused on API)
    history_data = []
    for q, r in past_interactions:
        history_data.append({
            'query': q.query_text,
            'is_academic': q.is_academic,
            'timestamp': q.created_at.strftime('%Y-%m-%d %H:%M'),
            'response': r.generated_response if r else None,
            'keywords': r.keywords if r else None,
            'has_answer': True if (r and r.matched_content) else False
        })
    return jsonify(history_data)

@app.route('/admin/data/reset', methods=['POST'])
@login_required
@role_required('admin')
def admin_reset_data():
    """Admin tool to clear handouts and logs for testing."""
    Handout.query.delete()
    Query.query.delete()
    Response.query.delete()
    FilterLog.query.delete()
    db.session.commit()
    flash('Database tables cleared successfully.', 'info')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)
