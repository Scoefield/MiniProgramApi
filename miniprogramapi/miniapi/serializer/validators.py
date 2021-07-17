#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   Scoefield 
@File    :   validators.py
@Time    :   2021/07/17 13:13:32
'''

import re
from rest_framework.exceptions import ValidationError


def phone_validator(value):
    if not re.match(r"^(1[3|4|5|6|7|8|9])\d{9}$", value):
        raise ValidationError("手机号格式错误！")

def code_validator(code):
    if not re.match(r"\d{4}", code):
        raise ValidationError("验证码格式错误！")
