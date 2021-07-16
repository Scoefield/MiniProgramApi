from http.client import error
from miniapi.utils.utils import send_massage
import re
from django.http import response
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django_redis import get_redis_connection
from django.conf import settings


def phone_validator(value):
    if not re.match(r"^(1[3|4|5|6|7|8|9])\d{9}$", value):
        raise ValidationError("手机号格式错误！")

class MessageSerializer(serializers.Serializer):
    # 实质的验证顺序：内部是否为空的校验，validators列表里的函数，钩子函数
    phone = serializers.CharField(label="手机号", validators=[phone_validator,])
    # 钩子函数，这里不另外写了
    # def validated_phone(self, value):
    #     pass


class MessageView(APIView):
    ''' 获取验证码 '''
    
    def __init__(self):
        self.expireTime = settings.MSG_CONFIG.get("EXPIRE_TIME", 60)

    def get(self, request, *arges, **kwargs):
        # 1. 获取手机号
        # 2. 校验手机号格式
        ser = MessageSerializer(data=request.query_params)
        if not ser.is_valid():
            return response({"status": False, "message": "手机号格式错误！"})
        phone = ser.validated_data.get("phone")
        print("phone:", phone)

        # 3. 生成随机验证码
        import random
        random_code = random.randint(1000, 9999)
        print("code", random_code)

        # 4. 验证码发送到手机，购买服务器进行发送短信：阿里云/腾讯云
        send_msg_ret = send_massage(phone, random_code)
        if not send_msg_ret.get("status"):
            return Response(send_msg_ret)
        
        # 5. 验证码 + 手机号 保留（redis 设置 30s 过期）
        # 5.1 搭建 redis 服务
        # 5.2 django 中方便使用 redis 的模块 django-redis 
        #       配置并使用
        # conn.set(key, value, expire) -> conn.set(phone, code, ex=30)
        # code = conn.get(phone)
        # 方式一（普通方式）：
        # import redis
        # pool = redis.ConnectionPool(host="localhost", port=6379)
        # conn = redis.Redis(connection_pool=pool)
        # conn.set(phone, random_code, ex=30)
        # 方式二（django-redis模块）：
        conn = get_redis_connection()
        ret = conn.set(phone, random_code, ex=self.expireTime)
        print("set redis ret: ", ret)     

        return Response({"status": True, "message": "验证码发送成功"})


class LoginView(APIView):
    '''登录'''
    def post(self, request, *args, **kwargs):
        # 获取参数
        data = request.data
        print("data=", data)

        phone = data.get("phone")
        input_code = data.get("code")
        # redis 句柄
        conn = get_redis_connection()
        redis_code = conn.get(phone)
        print("phone:{}, input_code:{}, redis_code:{}".format(phone, input_code, redis_code))

        if not redis_code:
            return Response({"status": False, "message": "输入的验证码已过期，请重新获取！"})
        
        # 校验输入和redis 的 code 是否一致
        if input_code != redis_code:
            return Response({"status": False, "message": "输入的验证码有误！"})

        return Response({"status": True, "message": "登录成功"})
