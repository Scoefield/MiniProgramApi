import re
import uuid
from http.client import error
from miniapi.utils.utils import send_massage
from django.http import response
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from django_redis import get_redis_connection
from django.conf import settings
from miniapi import models
from .serializer.account import MessageSerializer, LoginSerializer


class MessageView(APIView):
    ''' 获取验证码 '''
    
    def __init__(self):
        self.expireTime = settings.MSG_CONFIG.get("EXPIRE_TIME", 60)

    def get(self, request, *arges, **kwargs):
        # 1. 获取手机号
        # 2. 校验手机号格式
        ser = MessageSerializer(data=request.query_params)
        if not ser.is_valid():
            return Response({"status": False, "message": "手机号格式错误！"})
        phone = ser.validated_data.get("phone")
        print("phone:", phone)

        # 3. 生成随机验证码
        import random
        random_code = random.randint(1000, 9999)
        print("code", random_code)

        # todo: 已经测试成功了，调试时注释掉第四步，发短信服务有限制
        # 4. 验证码发送到手机，购买服务器进行发送短信：阿里云/腾讯云
        # send_msg_ret = send_massage(phone, random_code)
        # if not send_msg_ret.get("status"):
        #     return Response(send_msg_ret)
        
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
        if not ret:
            Response({"status": False, "message": "验证码写入redis错误"})

        return Response({"status": True, "message": "验证码发送成功"})


class LoginView(APIView):
    '''
    登录：
        1. 无验证码
        2. 有验证码，验证码错误
        3. 验证成功
    '''
    def post(self, request, *args, **kwargs):
        # 获取参数
        # data = request.data
        # print("data=", data)
        # phone = data.get("phone")
        # input_code = data.get("code")

        ser = LoginSerializer(data=request.data)
        if not ser.is_valid():
            return Response({"status": False, "message": "验证码错误"})
        
        # 根据手机号去数据库获取用户信息
        phone = ser.validated_data.get("phone")

        # 4. 获取不到用户信息，则创建；获取到，则更新token
        # 写法一：
        # user = models.UserInfo.objects.filter(phone=phone).first()
        # if not user:
        #     models.UserInfo.objects.create(phone=phone, token=str(uuid.uuid4()))
        # else:
        #     user.token = str(uuid.uuid4())
        #     user.save()
        
        # 写法二：
        user_obj, flag = models.UserInfo.objects.get_or_create(phone=phone)
        user_obj.token = str(uuid.uuid4())
        user_obj.save()

        return Response({"status": True, "message": "登录成功", "data": {"token": user_obj.token, "phone": user_obj.phone}})
