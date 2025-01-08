from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from models import db, Todo, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SECRET_KEY'] = 'hello'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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
    todos = Todo.query.all()
    return render_template('index.html', todos=todos)

# 새로운 할 일 생성 (Create)
@app.route('/add', methods=['POST'])
@login_required
def add():
    content = request.form['content']
    if not content:
        return '살려주시오 날 집에 보내다오!!', 400
    new_todo = Todo(content=content)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for('index'))

# 할 일 삭제 (Delete)
@app.route('/delete/<int:id>')
@login_required
def delete(id):
    todo_to_delete = Todo.query.get_or_404(id)
    db.session.delete(todo_to_delete)
    db.session.commit()
    return redirect(url_for('index'))

# 회원가입 (Register)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful')
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
            flash('Invalid username or password')
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