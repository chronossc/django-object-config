from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from object_config.models import Option

# Create your models here.
class Member(models.Model):
    user = models.OneToOneField(User)
    options = generic.GenericRelation(Option)

    def __unicode__(self):
        return self.user.email

