#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author  :   Scoefield 
@File    :   utils.py
@Time    :   2021/07/16 17:36:24
'''

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
# 导入对应产品模块的client models。
from tencentcloud.sms.v20190711 import sms_client, models
# 导入可选配置类
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile

from django.conf import settings


def send_massage(phone, random_code, template_id="1031737", second_param="1"):
    '''
    4. 验证码发送到手机，购买服务器进行发送短信：阿里云/腾讯云
    # 4.1 注册腾讯云，开通短信云服务
    # 4.2 创建应用，SDK appid: 1400545038
    # 4.3 申请短信签名，个人：用公众号来申请，ID：387322，名称：Go键盘侠
    # 4.4 申请短信模板，ID：1031737	名称：miniprogram
    # 4.5 申请密钥：https://console.cloud.tencent.com/cam/capi，
    #   SecretId：AKIDykGXZLq41i8H9k35rMaYFemeFvKSJtCD，SecretKey：lFSO3SaQzIK5ZmiNlsiGXXGitnQmrfCS
    # 4.6 调用接口发送短信，SDK，写好的工具：
    #   https://github.com/TencentCloud/tencentcloud-sdk-python/blob/master/examples/sms/v20190711/SendSms.py
    #   pip install tencentcloud-sdk-python
    '''

    secretId = settings.MSG_CONFIG.get("SECRET_ID")
    secretKey = settings.MSG_CONFIG.get("SECRET_KEY")
    city = settings.MSG_CONFIG.get("CITY")
    sdkAppId = settings.MSG_CONFIG.get("SDKAPP_ID")
    sign = settings.MSG_CONFIG.get("SING")

    phone = "{}{}".format("+86", phone)

    try:
        cred = credential.Credential(secretId, secretKey)
        # 实例化一个http选项，可选的，没有特殊需求可以跳过。
        httpProfile = HttpProfile()
        httpProfile.reqMethod = "POST"  # post请求(默认为post请求)
        httpProfile.reqTimeout = 30    # 请求超时时间，单位为秒(默认60秒)
        httpProfile.endpoint = "sms.tencentcloudapi.com"  # 指定接入地域域名(默认就近接入)

        # 非必要步骤:
        # 实例化一个客户端配置对象，可以指定超时时间等配置
        clientProfile = ClientProfile()
        clientProfile.signMethod = "TC3-HMAC-SHA256"  # 指定签名算法
        clientProfile.language = "en-US"
        clientProfile.httpProfile = httpProfile
        client = sms_client.SmsClient(cred, city, clientProfile)
        req = models.SendSmsRequest()

        # 短信应用ID: 短信SdkAppid在 [短信控制台] 添加应用后生成的实际SdkAppid，示例如1400006666
        req.SmsSdkAppid = sdkAppId
        # 短信签名内容: 使用 UTF-8 编码，必须填写已审核通过的签名，签名信息可登录 [短信控制台] 查看
        req.Sign = sign
        
        # 下发手机号码，采用 e.164 标准，+[国家或地区码][手机号]
        # 示例如：+8613711112222， 其中前面有一个+号 ，86为国家码，13711112222为手机号，最多不要超过200个手机号
        req.PhoneNumberSet = [phone]
        # 模板 ID: 必须填写已审核通过的模板 ID。模板ID可登录 [短信控制台] 查看
        req.TemplateID = template_id
        # 模板参数: 若无模板参数，则设置为空
        req.TemplateParamSet = [str(random_code), second_param]

        # 通过client对象调用DescribeInstances方法发起请求。注意请求方法名与请求对象是对应的。
        # 返回的resp是一个DescribeInstancesResponse类的实例，与请求对象对应。
        resp = client.SendSms(req)

        if resp.SendStatusSet[0].Code == "Ok":
            # 输出json格式的字符串回包
            print(resp.to_json_string(indent=2))
            return {"status": True, "message": resp.SendStatusSet[0]}
        else:
            print(resp.to_json_string(indent=2))
            return {"status": False, "message": resp.SendStatusSet[0]}

    except TencentCloudSDKException as err:
        print(err)
        return {"status": False, "message": err}
