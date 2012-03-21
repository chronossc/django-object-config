# coding: utf-8
from django.db import models
from django.contrib.contenttypes import generic
from object_config.models import Option

class MyModel(models.Model):
    name = models.CharField(max_length=10)
    options = generic.GenericRelation(Option,related_name='options')

