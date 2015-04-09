# -*- coding: utf-8 -*-
import os

from flask import send_from_directory, render_template, request, redirect, url_for, flash, session, g, jsonify, send_from_directory

from werkzeug import secure_filename

from sqlalchemy import desc

from apps import app, db

from apps.models import (User, Tag, Question, Answer)


UPLOAD_FOLDER = './uploads/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def main():
	return render_template('main.html')

@app.route("/join")
def join():
	return "join"

@app.route('/make_question')
def make_question():
	return render_template('make_question.html')
   

@app.route('/question_list')
def question_list():
	return render_template('question_list.html')   


@app.route('/favorite_list')
def favorite_list():
	return render_template('favorite_list.html')


















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



# @error Handlers
#
# Handle 404 errors
@app.errorhandler(404)
def page_not_found(e):
	return render_template('error/404.html'), 404


# Handle 500 errors
@app.errorhandler(500)
def server_error(e):
	return render_template('error/500.html'), 500


