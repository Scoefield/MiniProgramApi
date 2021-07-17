#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   Scoefield 
@File    :   account.py
@Time    :   2021/07/17 13:11:58
'''

from rest_framework import serializers
from .validators import phone_validator
from rest_framework.exceptions import ValidationError
from django_redis import get_redis_connection


class MessageSerializer(serializers.Serializer):
    '''
        发送验证码的相关参数校验的序列化器
    '''
    # 实质的验证顺序：内部是否为空的校验，validators列表里的函数，钩子函数
    phone = serializers.CharField(label="手机号", validators=[phone_validator,])
    # code = serializers.CharField(label="验证码", validators=[code_validator,])
    # 钩子函数，这里不另外写了
    # def validated_phone(self, value):
    #     pass


class LoginSerializer(serializers.Serializer):
    '''
        登录相关的参数校验的序列化器
    '''
    phone = serializers.CharField(label="手机号", validators=[phone_validator,])
    code = serializers.CharField(label="短信验证码")    # 默认校验不为空

    # 定义钩子函数校验验证码
    def validate_code(self, value):
        if len(value) != 4:
            raise ValidationError("短信验证码格式错误")

        if not value.isdecimal():
            raise ValidationError("短信验证码格式错误")

        phone = self.initial_data.get("phone")
        conn = get_redis_connection()
        code = conn.get(phone)
        print("input_code:{}, code:{}".format(value, code))
        if not code:
            raise ValidationError("验证码过期或不存在")

        if value != code:
            raise ValidationError("验证码错误")

        return value
