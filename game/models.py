
# Create your models here.
from __future__ import unicode_literals
from django.db import models
from django.core.files.storage import FileSystemStorage
fs = FileSystemStorage(location='/static')
# Create your models here.
class User(models.Model):
    user_id=models.AutoField(primary_key=True)
    user_name=models.CharField(max_length=255)
    user_password=models.CharField(max_length=200)
    user_email=models.EmailField(blank=True)
    user_category=models.CharField(max_length=2,default=2)
    user_image=models.CharField(max_length=150,blank=True,null=True)
    user_valid = models.BooleanField(default=False)
    user_dev_games=models.CharField(max_length=500,default='/',blank=True)

class Game(models.Model):
    game_id=models.AutoField(primary_key=True)
    game_name=models.CharField(max_length=255)
    game_category=models.CharField(max_length=20)
    game_price=models.DecimalField(max_digits=10,decimal_places=2)
    game_date=models.DateField(blank=True)
    game_description=models.CharField(max_length=255)
    game_sale=models.IntegerField(max_length=10,default=0)
    game_pic=models.ImageField(storage=fs,blank=True,null=True)
    game_path=models.CharField(max_length=150,blank=True,null=True)
    player=models.ManyToManyField(User,blank=True,null=True)
    #developer=models.ForeignKey(User,blank=True,null=True)

    

class Score(models.Model):
    score_id=models.AutoField(primary_key=True)
    score=models.CharField(max_length=255)
    save_score=models.CharField(max_length=255,blank=True,null=True)
    player=models.ForeignKey(User)
    game=models.ForeignKey(Game)
    

