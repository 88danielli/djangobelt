from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.db.models import Count
from . import models
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
name_regex = re.compile(r'^[a-zA-Z]+')

def index(request):
    if not 'active_user' in request.session:
        request.session['active_user'] = ""
    return render(request, 'djangobelt_app/index.html')

def pokes(request):
    if request.session['active_user'] == "" or not 'active_user' in request.session:
        messages.add_message(request, messages.ERROR, "Please Login to Continue")
        return redirect('/')
    else:
        user_list = models.User.objects.exclude(id=request.session['active_user']['id'])
        unique_user_list = models.Poke.objects.filter(friend_id=request.session['active_user']['id']).values('user__alias').annotate(Count('user__alias')).order_by('-user__alias__count')
        count_of_unique_user_list = unique_user_list.count()
        active_user_pokes = models.Poke.objects.filter(user_id=request.session['active_user']['id']).values('friend_id').annotate(Count('friend_id'))
        print unique_user_list

        context = {
            'user_list': user_list,
            'unique_user_list': unique_user_list,
            'count_of_unique_user_list': count_of_unique_user_list,
            'active_user_pokes': active_user_pokes
        }
        return render(request, 'djangobelt_app/pokes.html', context)

def add_user(request):
    result = models.User.objects.register(request.POST)
    if result[0] == False:
        for i in result[1]:
            messages.add_message(request, messages.ERROR, i)
        return redirect('/')
    else:
        return log_user_in(request, result[1])

def login(request):
    result = models.User.objects.login(request.POST)
    if result[0] == False:
        for i in result[1]:
            messages.add_message(request, messages.ERROR, i)
        return redirect('/')
    else:
        return log_user_in(request, result[1])

def log_user_in(request, user):
    request.session['active_user'] = {
        'id' : user.id,
        'name' : user.name,
        'alias' : user.alias,
        'email' : user.email,
    }
    return redirect ('/pokes')

def logout(request):
    del request.session['active_user']
    return redirect('/')

def add_poke(request, id):
    result = models.Poke.objects.add_poke(request.session['active_user']['id'],id)
    return redirect ('/pokes')
