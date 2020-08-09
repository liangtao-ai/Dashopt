from django.db import models
import random
from django.utils import timezone


# Create your models here.
def default_sign():
    signs = ['Come on~~', 'I am very happy!']
    return random.choice(signs)



class UserProfile(models.Model):

    #avatar 可以为空
    #表名 user_user_profile
    username = models.CharField(max_length=11,verbose_name='用户名', primary_key=True)
    nickname = models.CharField(max_length=50,verbose_name='昵称',)
    email = models.EmailField()
    password = models.CharField(max_length=32)
    sign = models.CharField(max_length=50, verbose_name='个人签名', default=default_sign)
    info = models.CharField(max_length=150, verbose_name='个人简介', default='')
    avatar = models.ImageField(upload_to='avatar', null=True)
    #from django.utils import timezone
    #新增datetime字段时,给defualt=timezone.now
    #migrate成功后,改回auto_now等参数,make&migrate
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    phone = models.CharField(max_length=11, default='')







    class Meta:
        db_table = 'user_user_profile'













