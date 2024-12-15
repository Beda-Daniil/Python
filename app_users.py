from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.info("Сервер Flask запущен")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'supersecretkey'  # Измените на более надёжный ключ в боевом окружении


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
api = Api(app)

# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Модель задачи
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    done = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# # Создание всех таблиц
# with app.app_context():
#     db.create_all()

# раскомментить код, если нужно удалить все данные из БД
with app.app_context():
    db.session.query(Task).delete()  
    db.session.query(User).delete()  
    db.session.commit()
    print("База данных очищена: все пользователи и задачи удалены")

# Модели для Swagger
user_model = api.model('User', {
    'username': fields.String(required=True, description='Имя пользователя'),
    'password': fields.String(required=True, description='Пароль')
})

task_model = api.model('Task', {
    'id': fields.Integer(readonly=True, description='Идентификатор задачи'),
    'title': fields.String(required=True, description='Название задачи'),
    'description': fields.String(description='Описание задачи'),
    'done': fields.Boolean(description='Статус выполнения задачи')
})

# Регистрация
@api.route('/register')
class Register(Resource):
    @api.expect(user_model)
    def post(self):
        logger.info("Пользователь начинает регистрацию")
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if User.query.filter_by(username=username).first():
            abort(400, 'Пользователь с таким именем уже существует')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        logger.info("Пользователь завершил регистрацию")

        return {'message': 'Пользователь успешно зарегистрирован'}, 201

# Авторизация
@api.route('/login')
class Login(Resource):
    @api.expect(user_model)
    def post(self):
        data = request.json
        logger.info("Пользователь авторизовывается")
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if not user or not bcrypt.check_password_hash(user.password, password):
            abort(401, 'Неверное имя пользователя или пароль')

        access_token = create_access_token(identity=user.id)
        logger.info("Пользователь авторизовался")
        return {'access_token': access_token}, 200

# Работа с задачами
@api.route('/tasks')
class TaskList(Resource):
    
    @api.marshal_list_with(task_model)
    @jwt_required()
    # запрос на получение всех задач для конкретного пользователя
    def get(self):
        user_id = get_jwt_identity()
        tasks = Task.query.filter_by(user_id=user_id).all()
        return tasks, 200

    @api.expect(task_model)
    @jwt_required()
    # запрос на создание задачи
    def post(self): 
        user_id = get_jwt_identity()
        data = request.json
        if data['title'] is None:
            return abort(400, message = 'Не указано название задачи')
                
        new_task = Task(
            title=data['title'],
            description=data.get('description'),
            done=data.get('done', False),
            user_id=user_id
        )
        db.session.add(new_task)
        db.session.commit()
        return {
            'id': new_task.id,
            'title': new_task.title,
            'description': new_task.description,
            'done': new_task.done
        }, 201

@api.route('/tasks/<int:task_id>')
class TaskResource(Resource):
    # запрос на поиск задачи пользователя
    @api.marshal_with(task_model)
    @jwt_required()
    def get(self, task_id):
        user_id = get_jwt_identity()
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            abort(404, 'Задача не найдена')
        return task, 200
    
    # запрос на обновление задачи пользователя
    @api.expect(task_model)
    @jwt_required()
    def put(self, task_id):
        user_id = get_jwt_identity()
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            abort(404, 'Задача не найдена')

        data = request.json
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.done = data.get('done', task.done)
        db.session.commit()

        return {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'done': task.done
        }, 200
    # запрос на удаление задачи пользователя
    @jwt_required()
    def delete(self, task_id):
        user_id = get_jwt_identity()
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            abort(404, 'Задача не найдена')
        db.session.delete(task)
        db.session.commit()
        return '', 204

# запрос на вызов всех пользователей в БД
@api.route('/users')
class UserList(Resource):
    @jwt_required()
    def get(self):
        users = User.query.all()
        return [
            {'id': user.id, 'username': user.username} for user in users
        ], 200

if __name__ == '__main__':
    app.run(debug=True)