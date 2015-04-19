#-*- encoding: utf-8 -*-
"""
models.py

"""
from apps import db
from datetime import datetime
from flask.ext.login import UserMixin

# 태그는 일단 유저가 추가하는대로 생기지만, 선택당하지 못하면 바로 삭제 시킬것이다.
class Tag(db.Model):
    id = db.Column(db.String(255), primary_key=True)
    #questions


class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(255))
    content = db.Column(db.Text())

    user_id = db.Column(db.String(255), db.ForeignKey('user.id'))
    user = db.relationship('User', 
        foreign_keys=[user_id],
        primaryjoin="Problem.user_id==User.id",
        backref=db.backref('problems', cascade='all, delete-orphan', lazy='dynamic'))

    tag_id = db.Column(db.String(255), db.ForeignKey('tag.id'))
    tag = db.relationship('Tag',
        foreign_keys=[tag_id],
        primaryjoin="Problem.tag_id==Tag.id",
        backref=db.backref('problems', cascade='all, delete-orphan', lazy='dynamic'))

    # 파일 첨부? 확장자로 이미지 혹은 파일 구분하기."aaa.txt,bbb.txt,eee.jpg" 이런식으로 구분
    fkey1 = db.Column(db.String(255), default="")
    fkey2 = db.Column(db.String(255), default="")
    fkey3 = db.Column(db.String(255), default="")



class Solution(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    prob_id = db.Column(db.Integer, db.ForeignKey('problem.id'))
    problem = db.relationship('Problem',
        foreign_keys=[prob_id],
        primaryjoin="Solution.prob_id==Problem.id",
        backref=db.backref('solutions', cascade='all, delete-orphan', lazy='dynamic'))

    # 유저 아이디 입력 받은걸로 get해서 객체를 user 에 저장
    user_id = db.Column(db.String(255), db.ForeignKey('user.id'))
    user = db.relationship('User', 
        foreign_keys=[user_id],
        primaryjoin="Solution.user_id==User.id",
        backref=db.backref('solutions', cascade='all, delete-orphan', lazy='dynamic'))

    content = db.Column(db.Text(), default="")



# user...
class User(UserMixin, db.Model):

    id = db.Column(db.String(255), primary_key=True) # 중복 확인 
    pw = db.Column(db.String(255), nullable=False)
    #name = db.Column(db.String(64), default="")
    #fkey = db.Column(db.String(255), default="") # file name (picture)
    date_joined = db.Column(db.DateTime, default=db.func.now())
    
    # 즐겨찾기 태그 리스트
    favlist = db.Column(db.Text(), default="")
    def __repr__(self):
        return '<User %r>' % (self.name)


