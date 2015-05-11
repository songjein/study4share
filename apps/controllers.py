# -*- coding: utf-8 -*-
import os, random

from flask import send_from_directory, render_template, request, redirect, url_for, flash, session, g, jsonify, send_from_directory,Markup

import json

from werkzeug import secure_filename
from werkzeug.exceptions import default_exceptions
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import desc

from apps import app, db, login_manager, socketio

from apps.models import (User, Tag, Problem, Solution)
from apps.models import UserMirror

from apps.forms import (JoinForm, LoginForm, ProblemForm, SolutionForm)

from flask.ext.login import login_required, login_user, logout_user, current_user



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



# menu functions (make_problem - pencil icon, favorite_list - start icon
##############################################################################################################
@app.route('/main', methods=["GET", "POST"])
@login_required
def main():
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
		
		# 이 코드는 problem_list 에도 있다.
		# 만약 problem의 제목에 새로운 해시태그가 포함되어 있다면
		# htag list업데이트 해줘야한다.
		if "#" in problem.title and problem.title.count('#') >= 2:
			key = problem.title.split('#')[1] 
			if key not in tag.sort:	
				if tag.sort=="":
					tag.sort += key
				else:
					tag.sort += "," + key

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
   



##############################################################################################################
# tag를 클릭 했을 때 나오는 problem list 조회 기능
##############################################################################################################
@app.route('/problem_list/<tag_id>/<prob_id>', methods=["GET", "POST"])
@login_required
def problem_list(tag_id, prob_id):
	probForm = ProblemForm()
	solForm = SolutionForm()

	tag = Tag.query.get(tag_id)
	problems = tag.problems
	
	#################################################################
	# problems 해시태그 이용 정렬
	#################################################################
	none_htag_list = [] # hash tag가 없는 문제를 담는다
	dict_for_flist = {} # hash tag가 있는 문제를 담는다
	if tag.sort == "":
		for prob in problems:
			if "#" in prob.title and prob.title.count('#') >= 2:
				htag = prob.title.split('#')[1] #  "[0]#[1]제인#[2] 머가머가무가머가"
					
				if htag not in dict_for_flist: # 만약 태그가 이미 dict안에없다면 
					dict_for_flist[htag] = [] # dict안에 이 hash tag를 위한 list를 만들어 준다.
				# else로 하지마!	
				if htag in dict_for_flist: # 만약 태그가 이미 dict안에 있다면
					dict_for_flist[htag].append(prob) # 이 문제를 거기에 추가한다.
						
			else :
				none_htag_list.append(prob)					
		# Tag 의 sort  값 수정 (dict의 키값들로)
		s = "" 
		for key in dict_for_flist.keys():
			if s == "":
				s += key
			else:
				s += "," + key
		tag.sort = s
		db.session.commit()

	problem_colors = []	
	none_htag_list = [] # hash tag가 없는 문제를 담는다
	dict_for_flist = {} # hash tag가 있는 문제를 담는다
	if tag.sort != "":	
		# tag.sort를 기준으로 만든다. ? 근데 나중에 새로운 태그가 들어온다면?어케해?
		# problem을 추가할때마다 모니터링 하는 수 밖에 없는듯! tag.sort에 없다면 맨뒤에 추가해주면된다.
		htags = tag.sort.split(",")
		for key in htags:
			dict_for_flist[key] = []

		for prob in problems:
			if "#" in prob.title and prob.title.count('#') >= 2:
				key = prob.title.split('#')[1] 
				dict_for_flist[key].append(prob)
						
			else :
				none_htag_list.append(prob)					
		# sort by hash tag
		tproblems = []
		s = ""	
		c = 0
		for key in htags:
			tproblems += dict_for_flist[key]	
			for t in dict_for_flist[key]:
				if c%2 == 0:
					problem_colors.append("warning")
				else:
					problem_colors.append("success")
			c += 1
		tproblems += none_htag_list
		for t in none_htag_list:
			if c%2 == 0:
				problem_colors.append("warning")
			else:
				problem_colors.append("success")
		
		problems = tproblems
	# 만약 해시태그가 하나도 없는 tag라면, problem_colors가 비어있음	

	
	# template에 전달해줘서 화면에 표시해 줄 것이다.
	tags = tag.sort.split(',')
	if tags[0] == "":
		tags = []	
	
	#################################################################

	# prob_id 에 먼가 담겨있으면 그건 solution 업데이트 할때임!~!	
	if Problem.query.get(prob_id):
		solution = Problem.query.get(prob_id).solution[0]
		solForm = SolutionForm(request.form, solution);

		if solForm.validate_on_submit():
			solForm.populate_obj(solution)
			db.session.commit()
		# 예외로 prob_id 전달하기
		return render_template('problem_list.html', tag=tag, tags=tags, problems=problems, solForm=solForm, probForm=probForm, sModal_open=True, prob_id=prob_id, problem_colors=problem_colors)   

	# prob_id가 " "이면 이건 make_problem
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
		
		# 이코드는 main에도 있다.	
		# 만약 problem의 제목에 새로운 해시태그가 포함되어 있다면
		# htag list업데이트 해줘야한다.
		if "#" in problem.title and problem.title.count('#') >= 2:
			key = problem.title.split('#')[1] 
			if key not in tag.sort:	
				if tag.sort=="":
					tag.sort += key
				else:
					tag.sort += "," + key

		solution = Solution(
			prob_id = problem.id,
			problem = problem,
			content = u"답을 입력해 주세요^^"
		)
		db.session.add(solution)
		db.session.commit()	
		return redirect(url_for('problem_list', tag_id=tag_id, prob_id=" "))
	# form error일 경우
	elif request.method == "POST" :	
		# form에 설정했던게 안먹혀서 예외처리함
		if probForm.content.data == "<p><br></p>":
			probForm.content.errors.append(u"내용을 입력해주세요~")	
		errors = []
		errors += probForm.title.errors +  probForm.content.errors + probForm.tag.errors + probForm.newtag.errors
		for e in errors:
			flash(e)
		return render_template('problem_list.html', tag=tag, tags=tags, problems=problems, solForm=solForm, probForm=probForm, mpmodal_open=True, problem_colors=problem_colors)   
	
	return render_template('problem_list.html', tag=tag, tags=tags, problems=problems, solForm=solForm, probForm=probForm, problem_colors=problem_colors)   
   



# for ajax
@app.route("/get_problem/<prob_id>")
@login_required
def get_problem(prob_id):
	problem = Problem.query.get(prob_id)
	tag = problem.tag
	# [0]안적어서 3시간 낭비함
	solution = problem.solution[0]
	return jsonify(prob_id=prob_id, tag_id=tag.id, prob_title=problem.title, prob_content=problem.content, sol_content=solution.content)


# for ajax
@app.route("/delete_problem/<prob_id>")
@login_required
def delete_problem(prob_id):
	problem = Problem.query.get(prob_id)
	tag = problem.tag
	
	htag = None	
	if "#" in problem.title and problem.title.count('#') >= 2:
		htag = problem.title.split('#')[1] 
	db.session.delete(problem)
	db.session.commit()

	#만약 마지막 태그라면.. tag의 sort_list 에서도 제외시켜야됨
	will_be_deleted = True 
	if htag != None:
		for problem in tag.problems:
			if "#" in problem.title and problem.title.count('#') >= 2:
				chtag = problem.title.split('#')[1] 
				if chtag == htag:
					will_be_deleted = False
					break
	
		# 이때 tag.sort가""일 수 없는게, htag가 None이 아니란 말이니까..					
		if will_be_deleted:
			sortlist = tag.sort.split(',')
			sortlist.remove(htag)
			tag.sort = ",".join(sortlist)
			db.session.commit()
	
	# 만약 tag에 속한 문제가 없어지게 된다면 태그 자동 삭제
	c = 0
	for prob in tag.problems:
		c += 1
	if c == 0:
		db.session.delete(tag)
		db.session.commit()
		return "tag_deleted"

	return "success"


#for ajax
@app.route('/update_htags/<tag_id>')
def update_htags(tag_id):
	listOfHtags = request.args['listOfHtags']

	tag = Tag.query.get(tag_id)
	tag.sort = listOfHtags
	db.session.commit()

	return "success" 


##############################################################################################################
# 즐겨 찾기 기능
##############################################################################################################
@app.route('/favorite_list')
@login_required
def favorite_list():

	textcolor = ['muted', 'primary', 'success', 'info', 'warning', 'danger']
	random.shuffle(textcolor) 

	user = User.query.get(g.user.id)

	tag_ids = user.favlist.split(',') # 항상 주의 아무것도 없으면 ""이 첫 원소
	tags = []
	if tag_ids[0] != "":
		for id in tag_ids:
			tags.append(Tag.query.get(id))	

	return render_template('favorite_list.html', tags=tags, textcolor=textcolor)

# for jquery
@app.route('/add_favorite/<tag_id>')
@login_required
def add_favorite(tag_id):
	user = User.query.get(g.user.id)

	if user.favlist == "":
		user.favlist += tag_id
	elif tag_id in user.favlist:
		return "already"
	else :
		user.favlist += "," + tag_id
	db.session.commit()

	return "success" 


@app.route('/delete_favorite/<tag_id>')
@login_required
def delete_favorite(tag_id):
	user = User.query.get(g.user.id)
	favlist = user.favlist.split(',')
	favlist.remove(tag_id)
	user.favlist = ",".join(favlist)
	db.session.commit()
	return "success"

##############################################################################################################
# management function
##############################################################################################################
@app.route('/clear_tags')
def clear_tags():
	tags = Tag.query.all()
	s = ""
	for tag in tags:
	#	s += tag.id + "</br>"
		c = 0
		for prob in tag.problems:	
			c += 1
		if c == 0:
			db.session.delete(tag)
	db.session.commit()

	return "useless tags are all removed"

@app.route("/test")
def test():
	tags = Tag.query.all()
	for tag in tags:
		tag.sort = ""
	db.session.commit()
	return "ok"


##############################################################################################################
# socket io 
##############################################################################################################
@socketio.on('my event', namespace='/test')
def test_message(message):
    emit('my response', {'data': message['data']})

@socketio.on('my broadcast event', namespace='/test')
def test_message(message):
    emit('my response', {'data': message['data']}, broadcast=True)

@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected'})


##############################################################################################################
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
# 지윤이네꺼!
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
##############################################################################################################
