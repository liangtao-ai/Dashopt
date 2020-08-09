import hashlib

from django.http import HttpResponse, JsonResponse
from django.views import View
import json
from .models import UserProfile
from btoken.views import make_token
from tools.logging_dec import logging_check
from django.utils.decorators import method_decorator
import random
from django.core.cache import cache
from django.conf import settings
from tools.sms import YunTongXin

from .tasks import send_sms

# Create your views here.

#10100 - 10199 异常码


#FBV  F:function
def users_view(request):
    #/v1/users

    return HttpResponse('--user view')

#CBV C:class
#特点: 当接到未定义方法的http请求,视图类会返回405响应码
class UsersView(View):

    def get(self, request, username=None):

        if username:
            #获取指定用户的数据
            try:
                user = UserProfile.objects.get(username=username)
            except Exception as e:
                print('--get user error %s'%(e))
                result = {'code': 10104, 'error':'The username is wrong'}
                return JsonResponse(result)

            if request.GET.keys():
                #判断是否有查询字符串过来
                data = {}
                for k in request.GET.keys():
                    if k == 'password':
                        continue
                    if hasattr(user, k):
                        if k == 'avatar':
                            data[k] = str(getattr(user ,k))
                        else:
                            data[k] = getattr(user, k)
                result = {'code':200, 'username':username, 'data':data}
            else:
                #获取指定用户的全部数据
                result = {'code':200, 'username':username, 'data':{'info':user.info,'sign':user.sign, 'nickname':user.nickname, 'avatar': str(user.avatar) }}

            return JsonResponse(result)


        else:
            #获取全部用户的数据
            pass

        return HttpResponse('--user get')

    def post(self, request):

        #如何取数据
        json_str = request.body
        json_obj = json.loads(json_str)
        username = json_obj['username']
        email = json_obj['email']
        phone = json_obj['phone']
        password_1 = json_obj['password_1']
        password_2 = json_obj['password_2']
        sms_num = json_obj['sms_num']

        #校验验证码
        old_code = cache.get('sms_%s'%(phone))
        if not old_code:
            result = {'code':10113, 'error':'code is wrong!'}
            return JsonResponse(result)

        if int(sms_num) != old_code:
            result = {'code': 10114, 'error': 'code is wrong!'}
            return JsonResponse(result)

        #TODO 参数检查
        if len(username) > 11:
            result = {'code':10100, 'error':'The username is wrong~'}
            return JsonResponse(result)

        #检查用户名是否可用
        old_user = UserProfile.objects.filter(username=username)
        if old_user:
            result = {'code':10101, 'error': 'The username is already exist~'}
            return JsonResponse(result)
        #密码处理
        if password_1 != password_2:
            result = {'code':10102, 'error':'The password is error~'}
            return JsonResponse(result)
        p_m = hashlib.md5()
        p_m.update(password_1.encode())
        password_m = p_m.hexdigest()
        #插入数据
        try:
            user = UserProfile.objects.create(username=username,password=password_m,email=email,phone=phone, nickname=username)
        except Exception as e:
            print('create error is %s'%(e))
            result = {'code':10103, 'error': 'The username is already exist~'}
            return JsonResponse(result)

        #签发jwt
        token = make_token(username)
        return JsonResponse({'code': 200 , 'username':username, 'data':{'token':token.decode()}})

    @method_decorator(logging_check)
    def put(self, request, username):

        #method_decorator 将传入的 函数装饰器 转换为 方法装饰器
        json_str = request.body
        json_obj = json.loads(json_str)

        request.myuser.sign = json_obj['sign']
        request.myuser.nickname = json_obj['nickname']
        request.myuser.info = json_obj['info']
        request.myuser.save()

        result = {'code':200, 'username':request.myuser.username}
        return JsonResponse(result)









@logging_check
def user_avatar(request, username):

    #上传头像
    if request.method != 'POST':
        result = {'code':10105, 'error':'Please give me POST'}
        return JsonResponse(result)
    #/v1/users/guoxiaonao/avatar
    # if request.myuser.username != username:
    #     #别搞我
    #     pass

    #获取已登录的用户
    user = request.myuser
    user.avatar = request.FILES['avatar']
    user.save()

    result = {'code':200, 'username':user.username}
    return JsonResponse(result)




def sms_view(request):

    json_str = request.body
    json_obj = json.loads(json_str)
    phone = json_obj['phone']

    #检查 手机号是否已经注册

    #检查 当前手机号 有没有 已存在的验证码
    cache_key = 'sms_%s'%(phone)
    old_code = cache.get(cache_key)
    if old_code:
        result = {'code':10112, 'error':'qing shaohou zailai'}
        return JsonResponse(result)

    code = random.randint(1000, 9999)
    #存储验证码
    cache.set(cache_key, code, 65)
    print('---send code %s'%(code))
    #同步 - 发送
    # x = YunTongXin(settings.SMS_ACCOUNT_ID, settings.SMS_ACCOUNT_TOKEN, settings.SMS_APP_ID, settings.SMS_TEMPLATE_ID)
    # res = x.run(phone, code)
    # print('---send sms result is %s'%(res))

    #异步 - 发送 - celery
    send_sms.delay(phone, code)

    return JsonResponse({'code':200})


































