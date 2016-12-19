from __future__ import unicode_literals
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect

from django.db import models
import re, bcrypt
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
name_regex = re.compile(r'^[a-zA-Z]+')

class UserManager(models.Manager):
    def login(self, post):
        login_email = post['login_email']
        login_password = post['login_password']

        errors =[]

        user_list = User.objects.filter(email = login_email)

        if len(login_email) < 1:
            errors.append('Email is required')
        if len(login_password) < 1:
            errors.append('Password is required')
        if user_list:
            active_user = user_list[0]
            password = login_password.encode()
            if bcrypt.hashpw(password, active_user.pw_hash.encode()) == user_list[0].pw_hash :
                return (True, active_user)
            else:
                errors.append('Email and password do not match')
        else:
            errors.append('Email does not exist')
        return (False, errors)

    def register(self, post):
        name = post['name']
        alias = post['alias']
        email = post['email']
        password = post['password']
        confirm_password = post['confirm_password']
        birthday = post['birthday']

        errors = []
        user_list = User.objects.filter(email = email)
        alias_list = User.objects.filter(alias = alias)
        if len(name) < 1:
            errors.append('Name is required')
        if len(name) < 3:
            errors.append('Name requires more than 2 characters')
        if not name_regex.match(name):
            errors.append('Name must only contain letters')
        if len(alias) < 1:
            errors.append('Alias is required')
        if len(alias) < 3:
            errors.append('Alias requires more than 2 characters')
        if alias_list:
            errors.append('Alias already exists')
        if not EMAIL_REGEX.match(email):
            errors.append('Email is invalid!')
        if user_list:
            errors.append('Email already exists!')
        if len(password) < 1:
            errors.append('Password is required')
        if len(password) < 8:
            errors.append('Password should be at least 8 characters')
        if password != confirm_password:
            errors.append('Passwords do not match!')
        if not birthday:
            errors.append('Birthday is required')
        if len(errors) > 0:
            return (False, errors)
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        user = self.create(name=name, alias=alias, email=email, pw_hash=pw_hash, birthday=birthday)
        return (True, user)

class User(models.Model):
    name = models.CharField(max_length=45)
    alias = models.CharField(max_length=45)
    email = models.CharField(max_length=100)
    pw_hash = models.CharField(max_length=255)
    birthday = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()


class PokeManager(models.Manager):
    def add_poke(self, user_id, friend_id):
        user = User.objects.get(id=user_id)
        friend = User.objects.get(id=friend_id)
        new_poke = self.create(user=user, friend=friend)
        print new_poke
        return (True, new_poke)

class Poke(models.Model):
    user = models.ForeignKey(User, related_name='poking_user')
    friend = models.ForeignKey(User, related_name='poked_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = PokeManager()
