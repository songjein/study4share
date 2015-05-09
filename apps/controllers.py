# -*- coding: utf-8 -*-
import os, random

from flask import send_from_directory, render_template, request, redirect, url_for, flash, session, g, jsonify, send_from_directory,Markup

import json

from werkzeug import secure_filename
from werkzeug.exceptions import default_exceptions
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import desc

from apps import app, db

from apps.models import (User, Tag, Problem, Solution)
from apps.models import UserMirror

from apps.forms import (JoinForm, LoginForm, ProblemForm, SolutionForm)

from flask.ext.login import login_required, login_user, logout_user, current_user
from apps import login_manager

#UPLOAD_FOLDER = './uploads/'
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


@app.route("/")
def index():
@app.route("/main")
@login_required
def main():
	tags = Tag.query.all()
	form = ProblemForm()
	textcolor = ['muted', 'primary', 'success', 'info', 'warning', 'danger']
	random.shuffle(tags)
	random.shuffle(textcolor) 
	return render_template('main.html', tags=tags, form=form, textcolor=textcolor)

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



# menu functions (make_problem - pencil icon, favorite_list - start icon
##############################################################################################################
@app.route('/make_problem', methods=["GET", "POST"])
@login_required
def make_problem():
	
	tags = Tag.query.all()
	textcolor = ['muted', 'primary', 'success', 'info', 'warning', 'danger']
	random.shuffle(tags)
	random.shuffle(textcolor) 
	form = ProblemForm()

	if form.validate_on_submit():
		tag =  Tag.query.get(form.tag.data)
		if tag is None:
			tag = Tag(id=form.tag.data.strip())
			db.session.add(tag)
			db.session.commit()
		
		user = User.query.get(g.user.id)
		
		problem = Problem(
			title = form.title.data.strip(), 
			content = form.content.data,
			user_id = g.user.id,
			user = user,
			tag_id = tag.id,
			tag = tag
		)
		db.session.add(problem)

		solution = Solution(
			prob_id = problem.id,
			problem = problem,
			content = u"답을 입력해 주세요^^"
		)
		db.session.add(solution)
		db.session.commit()	
		return redirect(url_for('main'))

	elif request.method == "POST" :	
		# form에 설정했던게 안먹혀서 예외처리함
		if form.content.data == "<p><br></p>":
			form.content.errors.append(u"내용을 입력해주세요~")	
		errors = []
		errors += form.title.errors +  form.content.errors + form.tag.errors + form.newtag.errors
		for e in errors:
			flash(e)
		return render_template('main.html', form=form, tags=tags, mpmodal_open=True, textcolor=textcolor)
	
	return render_template('main.html', form=form, tags=tags, mpmodal_open=False, textcolor=textcolor)
   

@app.route('/make_problem_in_listpage/<tag_id>', methods=["GET", "POST"])
@login_required
def make_problem_in_listpage(tag_id):
	probForm = ProblemForm()
	solForm = SolutionForm()

	tag = Tag.query.get(tag_id)
	problems = tag.problems
	

	if probForm.validate_on_submit():
		tag =  Tag.query.get(probForm.tag.data)
		if tag is None:
			tag = Tag(id=probForm.tag.data.strip())
			db.session.add(tag)
			db.session.commit()
		
		user = User.query.get(g.user.id)
		
		problem = Problem(
			title = probForm.title.data.strip(), 
			content = probForm.content.data,
			user_id = g.user.id,
			user = user,
			tag_id = tag.id,
			tag = tag
		)
		db.session.add(problem)

		solution = Solution(
			prob_id = problem.id,
			problem = problem,
			content = u""
		)
		db.session.add(solution)
		db.session.commit()	
		return redirect(url_for('problem_list', tag_id=tag_id))
	# form error일 경우
	elif request.method == "POST" :	
		# form에 설정했던게 안먹혀서 예외처리함
		if probForm.content.data == "<p><br></p>":
			probForm.content.errors.append(u"내용을 입력해주세요~")	
		errors = []
		errors += probForm.title.errors +  probForm.content.errors + probForm.tag.errors + probForm.newtag.errors
		for e in errors:
			flash(e)
		return render_template('problem_list.html', tag=tag, problems=problems, solForm=solForm, probForm=probForm, mpmodal_open=True)   
	
	return render_template('problem_list.html', tag=tag, problems=problems, solForm=solForm, probForm=probForm, mpmodal_open=False)   
   


@app.route('/favorite_list')
@login_required
def favorite_list():
	return render_template('favorite_list.html')

##############################################################################################################

@app.route('/problem_list/<tag_id>')
@login_required
def problem_list(tag_id):
	probForm = ProblemForm()
	solForm = SolutionForm()

	tag = Tag.query.get(tag_id)
	problems = tag.problems
	

	# problem title을 읽으면서
	# #달린 것 중 set을 모아야 하는데..

		
	return render_template('problem_list.html', tag=tag, problems=problems, solForm=solForm, probForm=probForm, mpmodal_open=False)   


@app.route('/update_solution/<prob_id>/<tag_id>', methods=["POST"])
@login_required
def update_solution(prob_id, tag_id):
	problem = Problem.query.get(prob_id)
	solution = problem.solution[0]
	probForm = ProblemForm()
	solForm = SolutionForm(request.form, solution);
	if solForm.validate_on_submit():
		solForm.populate_obj(solution)
		db.session.commit()

	tag = Tag.query.get(tag_id)
	problems = tag.problems

	return render_template('problem_list.html', tag=tag, problems=problems, solForm=solForm, probForm=probForm, mpmodal_open=False)   

# for ajax
@app.route("/get_problem/<prob_id>")
@login_required
def get_problem(prob_id):
	problem = Problem.query.get(prob_id)
	tag = problem.tag
	# [0]안적어서 3시간 낭비함
	solution = problem.solution[0]
	return jsonify(prob_id=prob_id, tag_id=tag.id, prob_title=problem.title, prob_content=problem.content, sol_content=solution.content)

	
	


# file upload and download module
##############################################################################################################
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

##############################################################################################################

@app.route('/add/<phone>/<score>')
def upload_db(phone, score):
	if UserMirror.query.get(phone) == None:
		user = UserMirror(phone=phone, score=score)
		db.session.add(user)
		db.session.commit()
		return "add success"
	else :
		user = UserMirror.query.get(phone)
		user.score = int(score)
		db.session.commit()
		return "modify success"



@app.route('/show_rank')
def show_rank():
	# users = [ {'phone':'0909' , 'score':30}, {'phone':'0909' , 'score':30}, {'phone':'0909' , 'score':30}...]
	users = UserMirror.query.order_by(UserMirror.score).all()

	tmp = []
	for user in users:
		t = {}
		t['phone'] = user.phone
		t['score'] = user.score
		tmp.append(t)

	# json.dumps([{"jein":1},{"jein":1}])

	return json.dumps(tmp)
