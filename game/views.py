

# Create your views here.
# Create your views here.
# -*- encoding:utf-8 -*-
from django.http import HttpResponse,HttpResponseRedirect
from django.core import mail
import base64
from itsdangerous import URLSafeTimedSerializer as utsr
from django.template import context, RequestContext
from django.shortcuts import render_to_response, render, redirect
from game.models import *
from mysit.settings import SECRET_KEY
from hashlib import md5
import random

class Token:
    def __init__(self,security_key):
        self.security_key = security_key
        self.salt = base64.encodestring(security_key)

    def generate_validate_token(self,username):
        serializer = utsr(self.security_key)
        return serializer.dumps(username,self.salt)

    def confirm_validate_token(self,token,expiration=3600):
        serializer = utsr(self.security_key)
        return serializer.loads(token,salt=self.salt,max_age=expiration)

token_confirm = Token(SECRET_KEY)

def logo_login(request,user_email):
    ue=user_email.split('.com')[0]+'.com'
    ps=user_email.split('.com')[1]
    user0=User.objects.filter(user_email__exact=ue)
    if user0[0].user_password!=ps:
        return render(request,'index.html')
    else:
        games = Game.objects.all()
        categories = set()
        for game in games:
            categories.add(game.game_category)
        return render_to_response('main.html', {'user': user0[0],'games':games,'categories':categories})

def user_login(request):
    errors = []
    if request.method == "POST":
        userEmail=request.POST.get('inputEmail', '')
        inputUser = request.POST.get('inputUser', '')
        if userEmail:
            userPw = request.POST.get('inputPassword', '')
            userPw = md5(userPw).hexdigest()
            user = User.objects.filter(user_email__exact=userEmail) #icontains
            if not user or not user[0].user_valid :
                errors.append("User or Password is incorrect!")
            else:
                if user[0].user_password != userPw:
                    errors.append("User or Password is incorrect!")
                else:
                    userInfo = user[0]
                    #response=auth_views.login(request,'main.html',extra_context={'userInfo': userInfo})
                    remember_me = request.POST.get('remember_me', '')
                    
                    games=Game.objects.all()
                    categories=set()
                    for game in games:
                        categories.add(game.game_category)
                    return render_to_response('main.html', {'user': userInfo,'games':games,'categories':categories})
        elif inputUser:
            try:
                regiEmail = request.POST.get('regiEmail', '')
                user = User.objects.filter(user_email__exact=regiEmail)
                assert len(user)==0
                inputPassword = request.POST.get('inputPassword', '')
                confirmPassword = request.POST.get('confirmPassword', '')
                inputUser = request.POST.get('inputUser', '')
                agreement = request.POST.get('agreement', '')
                regiCate = request.POST.get('regiCate','')
                regiImg = request.POST.get('regiImg','')
                if inputPassword!=confirmPassword:
                    errors.append("Password is not identical!")
                elif agreement=='':
                    errors.append("Fail. You refuse to accept agreement.")
                else:
                    inputPassword = md5(inputPassword).hexdigest()
                    token = token_confirm.generate_validate_token(inputUser)
                    message = "    ".join([
                        u'{0},Welcome to game store!'.format(inputUser),
                        u'Please click link to finish registration:',
                        '/'.join(['http://gamestores.herokuapp.com', 'account/activate', token])
                    ])
                    errors.append('/'.join(['http://gamestores.herokuapp.com', 'account/activate', token]))
                    #with mail.get_connection() as connection:
                    #    mail.EmailMessage(
                    #        u'Registration Validation', message, None, [regiEmail],
                    #        connection=connection,
                    #    ).send()
                    newData = User(user_name=inputUser, user_password=inputPassword, user_email=regiEmail, user_category=regiCate,user_image=regiImg,user_valid=False)
                    newData.user_category='2'
                    newData.save()
                    errors.append("Register Successfully! Please check your email.")
            except Exception:
                errors.append("Email address had been used!")
    return render(request,'index.html', {'errors': errors})

def forget_password(request):
    find_email = request.POST.get('find_email', '')
    user = User.objects.filter(user_email__exact=find_email)
    mess=''
    if find_email:
        mess = 'E-mail has been sent to your box! Please check and reset password.'
    if len(user)!=0:
        token = token_confirm.generate_validate_token(find_email)
        message = "    ".join([
            u'Hi, {0}, You could retrieve your password here.'.format(user[0].user_name),
            u'Please click link to finish:',
            '/'.join(['http://newmysite1.herokuapp.com', 'account/password', token])
        ])
        with mail.get_connection() as connection:
            mail.EmailMessage(
                u'Retrieve password', message, None, [find_email],
                connection=connection,
            ).send()
    return render(request, 'reset_password_1.html', {'mess': mess})

def set_new_password(request,emailToken):
    mess=''
    new_pw=request.POST.get('new_pw', '')
    new_pw_2 = request.POST.get('new_pw_2', '')
    user = User.objects.filter(user_email__exact=token_confirm.confirm_validate_token(emailToken))
    if new_pw!=new_pw_2:
        mess="Passwords don't match!"
    else:
        if new_pw!='' and len(user)!=0 and new_pw_2!='':
            user[0].user_password=md5(new_pw).hexdigest()
            user[0].save()
            return render(request, 'popupInfo.html')
    return render(request, 'reset_password_2.html', {'mess': mess})

def category(request,cate,user_email):
    ue=user_email.split('.com')[0]+'.com'
    ps=user_email.split('.com')[1]
    user=User.objects.filter(user_email__exact=ue)
    if user[0].user_password!=ps:
        return render(request,'index.html')
    all_game = Game.objects.all()
    games=[]
    for item in all_game:
        if item.game_category==cate:
            games.append(item)
    return render(request, 'category.html', {'user': user[0],'games':games,'cate':cate})


def management(request,user_email):
    ue=user_email.split('.com')[0]+'.com'
    ps=user_email.split('.com')[1]
    user=User.objects.filter(user_email__exact=ue)
    all_game = Game.objects.all()
    games=[]
    for item in all_game:
        if user[0] in item.player.all():
            games.append(item)
    dev_game_name=user[0].user_dev_games.split('/')
    dev_game_name=[x for x in dev_game_name if x!='']
    dev_games=[]
    for item in dev_game_name:
        agame = Game.objects.filter(game_name__exact=item)
        dev_games.append(agame[0])
    categories=['Action','Dice','Sports','Music','Others']
    if user[0].user_password!=ps:
        return render(request,'index.html')
    inputUser = request.POST.get('inputUser', '')
    inputPassword = request.POST.get('inputPassword', '')
    confirmPassword = request.POST.get('confirmPassword', '')
    role = request.POST.get('changePermission', '')
    mess1 = ''
    mess2 = ''
    if inputUser != '':
        if role == 'on':
            s=user[0]
            s.user_category = '1'
            s.save()
        else:
            s = user[0]
            s.user_category = '2'
            s.save()
    if inputUser != '':
        if inputUser.strip():
            mess1 = 'User name has been changed successfully!'
            s = user[0]
            s.user_name = inputUser
            s.save()
        else:
            mess1 = 'User name cannot be space!'
    if inputPassword != '':
        if inputPassword == confirmPassword:
            if inputPassword.strip():
                s = user[0]
                s.user_password = md5(inputPassword).hexdigest()
                s.save()
                mess2 = 'Password has changed successfully!'
            else:
                mess2 = 'Password cannot be space!'
        else:
            mess2 = 'Passwords must be identical!'
    inputGame = request.POST.get('inputGame', '')
    price = request.POST.get('price', '')
    description = request.POST.get('description', '')
    category = request.POST.get('category', 'Action')
    new_path = request.POST.get('url', '')
    new_image=request.POST.get('image', '')
    mess3=''
    import datetime
    b = Game(game_name=inputGame, game_category=category,game_price=price,game_date=datetime.datetime.now().strftime("%Y-%m-%d"),
             game_description=description,game_pic=new_image,game_path=new_path)
    if inputGame:
        ima=request.POST.get('uploadFromPC','')
        if ima:
            with open(ima, 'rb') as f:
                data = f.read()
            with open("media/" + datetime.datetime.now().strftime("%d-%s"), 'wb') as f:
                f.write(data)
        b.save()
        s=user[0]
        s.user_dev_games += (inputGame + '/')
        s.save()
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    remove=request.POST.get('remove', '')
    gameName=request.POST.get('gameName','')
    temp = Game.objects.filter(game_name__exact=gameName)
    if remove == 'is_remove':
        if len(temp):
            s=temp[0]
            s.delete()
            allgames=user[0].user_dev_games.split('/')
            allgames = [x for x in allgames if x != '']
            allgames.pop()
            res_games='/'.join(allgames)+'/'
            u=user[0]
            u.user_dev_games=res_games
            u.save()
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
    return render(request, 'management.html', {'user': user[0],'games':games,'categories':categories,
                                               'dev_games':dev_games,'mess1':mess1,'mess2':mess2})


def contact(request,userEmail):
    ue=userEmail.split('.com')[0]+'.com'
    ps=userEmail.split('.com')[1]
    user=User.objects.filter(user_email__exact=ue)
    if user[0].user_password!=ps:
        return render(request,'index.html')
    return render(request,'contact.html',{'user':user[0]})

def usergame(request,userEmail):
    ue=userEmail.split('.com')[0]+'.com'
    ps=userEmail.split('.com')[1]
    user=User.objects.filter(user_email__exact=ue)
    if user[0].user_password!=ps:
        return render(request,'index.html')
    all_game = Game.objects.all()
    games=[]
    for item in all_game:
        if user[0] in item.player.all():
            games.append(item)
    return render(request,'userGame.html',{'user':user[0],'games':games})

def gameInfo(request,userEmail,game_name):
    ue=userEmail.split('.com')[0]+'.com'
    ps=userEmail.split('.com')[1]
    user=User.objects.filter(user_email__exact=ue)
    if user[0].user_password!=ps:
        return render(request,'index.html')
    game = Game.objects.filter(game_name__exact=game_name)
    all_players=[]
    if game[0].player:
        all_players=game[0].player.all()
    return render(request,'gamedescription.html',{'user':user[0],'game':game[0],'all_players':all_players})


#@receiver(user_logged_in)
#def after_user_logged_in(request, user):
#    print user.username
#def do_stuff(sender, user, request, **kwargs):
#    print user.username
#user_logged_in.connect(do_stuff)
#def after_user_logged_in(request):
#    return render(request, 'index.html')


def active_user(request, token):
    try:
        username = token_confirm.confirm_validate_token(token)
    except:
        return HttpResponse(u'Sorry, it is expired!')
    try:
        user = User.objects.get(user_name=username)
    except User.DoesNotExist:
        return HttpResponse(u'Sorry, user is not exist, please try again!')
    user.user_valid = True
    user.save()
    return redirect("/login/")

def payment(request, userEmail,game_name):
    ue=userEmail.split('.com')[0]+'.com'
    ps=userEmail.split('.com')[1]
    user=User.objects.filter(user_email__exact=ue)
    if user[0].user_password!=ps:
        return render(request,'index.html')
    game=Game.objects.filter(game_name__exact=game_name)
    password = request.POST.get('password', '')
    mess=''
    our_sid='chinawsd2017'
    our_pid=userEmail+'.com'+game_name
    amount=game[0].game_price
    secret_key='27bf3942470d953181b397e8a92a8b42'
    checksumstr="pid={}&sid={}&amount={}&token={}".format(our_pid, our_sid, amount, secret_key)
    from hashlib import md5
    m = md5(checksumstr.encode("ascii"))
    checksum = m.hexdigest()
    return render(request,'payment.html', {'user':user[0],'game':game[0],'amount':amount,
                                           'our_sid':our_sid,'our_pid':our_pid,'our_checksum':checksum,'mess':mess})

def play(request, userEmail,game_name):
    ue=userEmail.split('.com')[0]+'.com'
    ps=userEmail.split('.com')[1]
    user=User.objects.filter(user_email__exact=ue)
    if user[0].user_password!=ps:
        return render(request,'index.html')
    game=Game.objects.filter(game_name__exact=game_name)

    max_score_wrap=''
    if len(Score.objects.filter(game_id__exact=game[0].game_id))!=0:
        max_score=-1
        for item in Score.objects.filter(game_id__exact=game[0].game_id):
            if int(item.score)>max_score:
                max_score=int(item.score)
                max_score_wrap=item

    dis_score = request.POST.get('score', '')
    temp_score=''
    all_scores = Score.objects.filter(player__exact=user[0].user_id).filter(game__exact=game[0].game_id)
    if len(all_scores)!=0:
        temp_score = all_scores[0]
    if dis_score:
        if len(all_scores)==0:
            s=Score(score=dis_score,player=user[0],game=game[0])
            s.save()
        else:
            if dis_score>temp_score.score:
                temp_score.score=dis_score
                temp_score.save()
    return render(request, 'playgame.html',{'user':user[0],'game':game[0],'max_score_wrap':max_score_wrap,'dis_score':dis_score,'yourscore':temp_score})

def game_edit(request, userEmail,game_name):
    ue=userEmail.split('.com')[0]+'.com'
    ps=userEmail.split('.com')[1]
    user=User.objects.filter(user_email__exact=ue)
    game=Game.objects.filter(game_name__exact=game_name)
    if user[0].user_password!=ps:
        return render(request,'index.html')
    inputGame = request.POST.get('inputGame', '')
    price = request.POST.get('price', '')
    description = request.POST.get('description', '')
    catergory = request.POST.get('catergory', '')
    new_path = request.POST.get('url', '')
    new_image=request.POST.get('image', '')
    s=game[0]
    #s.game_name=inputGame
    if catergory:
        s.game_category=catergory
    if price:
        s.game_price=price
    if description:
        s.game_description=description
    if new_image:
        s.game_pic=new_image
    mess=''
    if new_path or catergory or price or description or new_image:
        s.game_path=new_path
        mess = 'Changed Successfully!'
    s.save()
    categories = ['Action', 'Dice', 'Sports', 'Music', 'Others']
    return render(request, 'editGame.html',{'user':user[0],'game':game[0],'categories':categories,'mess':mess})


def search_game(request,userEmail):
    ue=userEmail.split('.com')[0]+'.com'
    ps=userEmail.split('.com')[1]
    user=User.objects.filter(user_email__exact=ue)
    #game=Game.objects.filter(game_name__exact=game_name)
    if user[0].user_password!=ps:
        return render(request,'index.html')
    search_words = request.GET.get('search_words', 'nono')
    #search_words='1234'
    search_games=Game.objects.filter(game_name__contains=search_words)
    yes_game=False
    if len(search_games)!=0:
        yes_game=True
    return render(request,'result.html',{'search_games':search_games,'yes_game':yes_game,'user':user[0]})

def payment_success(request,status):
    user_game = request.GET['pid']
    game_name = user_game.split('.com')[2]
    user_email = user_game.split('.com')[0] + '.com'
    user_pw=user_game.split('.com')[1]
    user = User.objects.filter(user_email__exact=user_email)
    game = Game.objects.filter(game_name__exact=game_name)
    if user[0].user_password!=user_pw:
        return render(request,'index.html')
    response_url = '/login'
    if status=='success':
        secret_key = '27bf3942470d953181b397e8a92a8b42'
        checksumstr="pid={}&ref={}&result={}&token={}".format(request.GET['pid'],request.GET['ref'],
                                                     request.GET['result'], secret_key)
        from hashlib import md5
        m = md5(checksumstr.encode("ascii"))
        checksum = m.hexdigest()
        real_checksum=request.GET['checksum']
        if checksum==real_checksum:
            game[0].player.add(user[0])
            game[0].game_sale+=1
            game[0].save()
            return render(request,'paymentResponse.html',{'url_status':status,'response_url':response_url,'game':game[0],'user':user[0]})
    else:
        return render(request, 'paymentResponse.html', {'url_status': 'failed', 'response_url': response_url,'game':game[0],'user':user[0]})
