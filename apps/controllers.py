# -*- coding: utf-8 -*-
import os

from flask import send_from_directory, render_template, request, redirect, url_for, flash, session, g, jsonify, send_from_directory,Markup

from werkzeug import secure_filename
from werkzeug.exceptions import default_exceptions
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import desc

from apps import app, db

from apps.models import (User, Tag, Problem, Solution)
from apps.forms import (JoinForm, LoginForm)

from flask.ext.login import login_required, login_user, logout_user, current_user
from apps import login_manager

#UPLOAD_FOLDER = './uploads/'
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


@app.route("/")
def index():
	return redirect(url_for('login'))


# login & join  function
##############################################################################################################
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    flash(u"로그인이 필요합니다.")
    return redirect(url_for('login'))

@app.before_request
def before_request():
    g.user = current_user



@app.route("/login", methods=['GET', 'POST'])
def login():
	loginform = LoginForm()
	joinform = JoinForm()
	#if loginform.validate_on_submit():
	if request.method=="POST":
		# 없는 회원
		if User.query.get(loginform.id.data) == None:
			flash(u'없는 ID입니다^^')
			return render_template('login.html',loginform=loginform, joinform=joinform, modal_open=False)
		else:
			user = User.query.get(loginform.id.data)
			if check_password_hash(user.pw, loginform.password.data):
				login_user(user)
				return redirect(url_for('main'))
			else :
				flash(u'비밀번호 틀림 허허')
				return render_template('login.html',loginform=loginform, joinform=joinform, modal_open=False)

		return redirect(url_for('login'))

	return render_template('login.html', loginform=loginform, joinform=joinform, modal_open=False)


@app.route('/join', methods=['POST'])
def join():
	loginform = LoginForm()
	joinform = JoinForm()
	if joinform.validate_on_submit():
		# 이미 존재하는 회원

		if User.query.get(joinform.id.data):
			# form의 errors영역에 추가할수없나. 되네?
			joinform.id.errors.append(u'이미 존재하는 회원입니다^^')
			return render_template('login.html',loginform=loginform, joinform=joinform, modal_open=True)
		new_user = User(id=joinform.id.data, pw=generate_password_hash(joinform.password.data))
		db.session.add(new_user)
		db.session.commit()
		flash(u'회원 가입 완료^^')
		return redirect(url_for('login'))
	
	# 에러 발생하면, 강제로 modal을 띄워줘야 하기에, html로 modal_open=True를
	# 전달해서 modal_open가 True면  무조건 모달창을 띄워주는 제이쿼리 코드를 삽입한다.
	return render_template('login.html',loginform=loginform, joinform=joinform, modal_open=True)


##############################################################################################################

@app.route("/main")
def main():
	return render_template('main.html')

@app.route('/make_question')
def make_question():
	return render_template('make_question.html')
   

@app.route('/question_list')
def question_list():
	return render_template('question_list.html')   


@app.route('/favorite_list')
def favorite_list():
	return render_template('favorite_list.html')


# write questions



# file upload and download module
#########################################################################################

def allowed_file(filename):
	return '.' in filename and \
			filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/file', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		file = request.files['file']
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			# 문제는 여기다.
			file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
			return  "완료"
		else:
			return "허용된 파일 형식이 아닙니다~^^"

	return '''
	<!doctype html>
	<title>Upload new File</title>
	<h1>Upload new File</h1>
	<form action="" method=post enctype=multipart/form-data>
		<p><input type=file name=file>
		<input type=submit value=Upload>
	</form>
	
	<hr><h3> uploaded files list</h3>
	<p>%s</p>
	''' % "<br>".join(os.listdir(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])))

@app.route('/download/<filename>')
def uploaded_file(filename):
	return send_from_directory(os.path.join(app.root_path, app.config['UPLOAD_FOLDER']), filename)

#########################################################################################



# Error logging module
#########################################################################################
'''def show_errormessage(error):
     desc = error.get_description(flask.request.environ)
     return render_template('error.html',
        code=error.code,
        name=error.name,
        description=Markup(desc)
    ), error.code

for _exc in default_exceptions:
    app.error_handlers[_exc] = show_errormessage
del _exc'''
#########################################################################################
