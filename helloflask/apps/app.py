from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Todo  # models.py에서 모델 가져오기

app = Flask(__name__)
app.config['SECRET_KEY'] = 'helloolleh'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

# todo 모델 추가해야함




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 데이터베이스 테이블 생성
with app.app_context():
    db.create_all()

# 모든 할 일 목록 보기 (Read)
@app.route('/')
@login_required
def index():
    todos = Todo.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', todos=todos)

# 새로운 할 일 생성 (Create)
@app.route('/add', methods=['POST'])
@login_required
def add():
    content = request.form['content']
    if not content:
        return '살려주시오 날 집에 보내다오!!', 400
    new_todo = Todo(content=content, user_id=current_user.id)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for('index'))

# 할 일 삭제 (Delete)
@app.route('/delete/<int:id>')
@login_required
def delete(id):
    todo_to_delete = Todo.query.get_or_404(id)
    if todo_to_delete.user_id != current_user.id:
        return '권한이 없습니다.', 403
    db.session.delete(todo_to_delete)
    db.session.commit()
    return redirect(url_for('index'))

# 회원가입 (Register)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# 로그인 (Login)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('이름이나 비밀번호가 존재하지 않습니다!')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html')

# 로그아웃 (Logout)
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)