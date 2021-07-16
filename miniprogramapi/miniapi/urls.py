#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   Scoefield 
@File    :   urls.py
@Time    :   2021/07/10 10:48:26
'''

from miniapi import views
from django.urls import path

urlpatterns = [
    path('login/', view=views.LoginView.as_view()),
    path('message/', view=views.MessageView.as_view()),
]