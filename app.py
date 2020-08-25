from SimpleTM import SimpleTM
import hashlib
import flask
from flask import request, jsonify, render_template, send_file, flash, redirect, url_for
from flask_httpauth import HTTPBasicAuth
import flask_login
from forms import RegistrationForm, NewGameForm
from config import Config

def hash(s):
    return hashlib.sha256(s.encode()).hexdigest()

app = flask.Flask(__name__)
app.secret_key = b'jasm.9d8Pd01[p]/))((*&(283972rhc&&'
auth = HTTPBasicAuth()
login_manager = flask_login.LoginManager()
login_manager.init_app(app)



@auth.verify_password
def verify_password(username, password):
    db = SimpleTM(Config.dbFileName)
    user = db.GetUser(username)
    if user and user[0] == username and user[1] == hash(password):
        return username

class User(flask_login.UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def user_loader(user_id):
    db = SimpleTM(Config.dbFileName)
    user_record = db.QueryUser(user_id)
    if not user_record:
        return
    user = User(user_id)
    return user

@login_manager.request_loader
def request_loader(request):
    db = SimpleTM(Config.dbFileName)
    user_id = request.form.get('username')
    user_record = db.QueryUser(user_id)
    if not user_record:
        return
    user = User(user_id)
    return user
    

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm(request.form)
    error = None
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        db = SimpleTM(Config.dbFileName)
        try:
            db.AddUser(username, hash(password))
            flash('注册成功', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            error = e
    
    return render_template('register.html', form=form, error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user_id = verify_password(request.form['username'], request.form['password'])
        if user_id:
            flask_login.login_user(User(user_id))
            return redirect(url_for('home'))
        else:
            flash('用户名或密码不正确', 'danger')
    return render_template('login.html')

@app.route('/home', methods=['GET','POST'])
@flask_login.login_required
def home():
    form = NewGameForm(request.form)
    user = flask_login.current_user.id
    db = SimpleTM(Config.dbFileName)
    if request.method == 'POST':
        gid = form.gid.data
        description = form.description.data
        print(gid, description)
        try:
            db.AddGameAsUser(user, gid, description)
            flash(f"项目{gid}创建成功", "success")
        except Exception as e:
            print(e)
            flash("该项目已存在，请换一个项目名", "danger")
    games = db.GetGamesByUser(user)
    return render_template('home.html', user=user, projects=games, form=form)

@app.route('/logout')
def logout():
    flask_login.logout_user()
    flash('已登出', 'primary')
    if flask_login.current_user.is_authenticated:
        print('still authed')
    return redirect(url_for('index'))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauthorized.html')

@app.route('/api/query/<string:rawWord>', methods=['GET'])
@auth.login_required
def api_query(rawWord):
    try:
        SimpleTMObj = SimpleTM(Config.dbFileName)
        ret = SimpleTMObj.Query(rawWord)
        SimpleTMObj.Close()
        json_lst = []
        for line in ret:
            tmp_json_dict = {}
            tmp_json_dict['raw'] = line[0]
            tmp_json_dict['translate'] = line[1]
            tmp_json_dict['game'] = line[2]
            json_lst.append(tmp_json_dict)
        return jsonify(json_lst)
    except Exception as e:
        return jsonify(Result='False', Message=str(e))

@app.route('/api/querybygame/<string:game>', methods=['GET'])
@auth.login_required
def api_querybygame(game):
    try:
        SimpleTMObj = SimpleTM(Config.dbFileName)
        ret = SimpleTMObj.QueryByGame(game)
        SimpleTMObj.Close()
        json_lst = []
        for line in ret:
            tmp_json_dict = {}
            tmp_json_dict['raw'] = line[0]
            tmp_json_dict['translate'] = line[1]
            json_lst.append(tmp_json_dict)
        return jsonify(json_lst)
    except Exception as e:
        return jsonify(Result='False', Message=str(e))


@app.route('/api/insert/<string:rawWord>/<string:translate>/<string:game>', methods=['GET'])
@auth.login_required
def api_insert(rawWord,translate,game):
    try:
        SimpleTMObj = SimpleTM(Config.dbFileName)
        ret = SimpleTMObj.Insert(rawWord, translate, game)
        SimpleTMObj.Close()
        if ret == True:
            return jsonify(Result='True', Message='')
        else:
            return jsonify(Result='False', Message='')
    except Exception as e:
        return jsonify(Result='False', Message=str(e))


@app.route('/api/update/<string:rawWord>/<string:translate>/<string:game>', methods=['GET'])
@auth.login_required
def api_update(rawWord,translate,game):
    try:
        SimpleTMObj = SimpleTM(Config.dbFileName)
        ret = SimpleTMObj.Update(rawWord, translate, game)
        SimpleTMObj.Close()
        if ret == True:
            return jsonify(Result='True', Message='')
        else:
            return jsonify(Result='False', Message='')
    except Exception as e:
        return jsonify(Result='False', Message=str(e))


@app.route('/maintain/upload')
@flask_login.login_required
def api_maintain_upload():
    return render_template("file_upload_form.html")


@app.route('/maintain/success', methods=['POST'])
@flask_login.login_required
def api_maintain_upload_success():
    try:
        if request.method == 'POST':
            f = request.files['file']
            f.save(Config.dbFileName)
            return render_template("success.html", name=f.filename)
        else:
            return jsonify(Result='False', Message='Not a POST action!')
    except Exception as e:
        return jsonify(Result='False', Message=str(e))


@app.route('/maintain/download')
@flask_login.login_required
def api_maintain_download():
    try:
        return send_file(Config.dbFileName, attachment_filename='TM.db')
    except Exception as e:
        return jsonify(Result='False', Message=str(e))


if __name__ == '__main__':
    app.run(host="0.0.0.0")
