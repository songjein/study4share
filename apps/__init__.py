# -*- coding: utf-8 -*-
"""
Initialize Flask app

"""
import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager


app = Flask(__name__)
app.config.from_object('apps.settings.Production')

if not app.debug:
	import logging
	# logging.FileHandler(filename, mode='a', encoding=None, delay=False)	
	file_handler = logging.FileHandler(os.path.join(app.root_path, "./log/", "log.txt"))
	#file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
	file_handler.setLevel(logging.ERROR)
	app.logger.addHandler(file_handler)

db = SQLAlchemy(app)
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


import controllers, models


