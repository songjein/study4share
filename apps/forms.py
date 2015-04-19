# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import (
    StringField,
    PasswordField,
    TextAreaField
)
from wtforms import validators
from wtforms.fields.html5 import EmailField


class LoginForm(Form):
    id = StringField(u'아뒤')
    password = PasswordField(u'비번')


class JoinForm(Form):
    id = StringField(
        u'아뒤',
        [validators.data_required(u'아이디 입력! 한글가능,1~16글자'),
		validators.Length(min=1, max=16, message=u'아이디는 최대 16글자입니다^^')]
        )
    password = PasswordField(
        u'비번',
        [validators.data_required(u'비밀번호를 입력해주셔야죠!'),
        validators.EqualTo('confirm', message=u'비번이 일치 하지 않아요ㅇㅅㅇ'),
	validators.Length(min=4,max=4, message=u'비밀번호는 4자리 입니다^^')]
        )
    confirm = PasswordField(
        u' ',
        [validators.data_required(u'비밀번호를 한 번더 입력해주싱')],
        )

