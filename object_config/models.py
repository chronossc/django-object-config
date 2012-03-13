# coding: utf-8

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from decimal import Decimal, DecimalException
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify

import simplejson

OPT_TYPES = (
    (0,_('Integer')),
    (1,_('Float')),
    (2,_('Decimal')),
    (3,_('String')),
    (4,_('JSON')),
    (5,_('Boolean')),
    # (5,),
    # (6,),
    # (7,),
    # (8,),
    # (9,),
)

class OptionManager(models.Manager):

    def get_option(self,name):
        return self.get(name=name)

class Option(models.Model):

    # Usage:

    # # models.py

    # from django.contrib.contenttypes import generic

    # class MyModel(models.Model):
    #     name = models.CharField(max_length=50)
    #     options = generic.GenericRelation(Option)

    # >>> from mymodel.models import MyModel
    # >>> m = MyModel.objects.create(name='test 1')
    # >>> m
    # <MyModel: MyModel object>
    # >>> m.options.all()
    # []
    # >>> m.options.create(name='option-1',verbose='Option 1',help_text='This text will help you.',type=4)
    # <Option: MyModel object:option-1 <JSON>>
    # >>>
    # >>> option_1 = m.options.get_option('option-1')
    # >>>
    # >>> print option_1.value # value is a property, it returns translated value, and also set translated value, default translated value is None
    # None
    # >>> print option_1.opt_value # opt_value is the value field itself, the default is '', not None

    # >>>
    # >>> option_1.value = {'some':'data','sub':{1:'33',3:'foo','foo':['f','o','b']}} # when set on attr value, it translate and save value
    # >>>
    # >>> print option_1.value
    # {'some': 'data', 'sub': {'1': '33', '3': 'foo', 'foo': ['f', 'o', 'b']}}
    # >>>
    # >>> print option_1.opt_value
    # {"some": "data", "sub": {"1": "33", "3": "foo", "foo": ["f", "o", "b"]}}
    # >>>
    # >>> print m.options.get_option('option-1').value
    # {u'some': u'data', u'sub': {u'1': u'33', u'3': u'foo', u'foo': [u'f', u'o', u'b']}}
    # >>>
    # >>> type(m.options.get_option('option-1').value)
    # <type 'dict'>
    # >>>
    # >>> pprint(m.options.get_option('option-1').__dict__)
    # {'_state': <django.db.models.base.ModelState object at 0x32e8d50>,
    #  'content_type_id': 120L,
    #  'help_text': u'This text will help you.',
    #  'id': 3L,
    #  'name': u'option-1',
    #  'object_id': 1L,
    #  'opt_value': u'{"some": "data", "sub": {"1": "33", "3": "foo", "foo": ["f", "o", "b"]}}',
    #  'type': 4L,
    #  'verbose': u'Option 1'}


    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type','object_id')

    name = models.SlugField(max_length=255)
    verbose_name = models.CharField(max_length=100)
    help_text = models.CharField(max_length=255,default='',blank=True)
    type = models.PositiveIntegerField(choices=OPT_TYPES)
    opt_value = models.TextField(default='',blank=True)
    default_value = models.TextField(default='',blank=True)

    objects = OptionManager()

    class Meta:
        unique_together = ('content_type','object_id','name')

    def __unicode__(self):
        return u"%s:%s <%s>" % (self.content_object,self.name,self.get_type_display())

    def _get_value(self):
        if not self.opt_value:
            return None
        f = None
        if self.type == 0:
            f = int
        if self.type == 1:
            f = float
        if self.type == 2:
            f = Decimal
        if self.type == 3:
            f = lambda s: u"%s" % s
        if self.type == 4:
            # import ipdb
            # ipdb.set_trace()
            f = lambda s:  simplejson.loads(s) if s else {}
        if self.type == 5:
            f = bool

        if f is None:
            raise TypeError,u"Unknow type set."

        return f(self.opt_value or self.default_value)

    def _set_value(self,value):
        if self.type == 4:
            self.opt_value = simplejson.dumps(value)
        elif self.type == 5:
            self.opt_value = 1 if bool(value) else 0
        else:
            self.opt_value = u"%s" % value
        self.save()

    value = property(_get_value,_set_value)

    def save(self,*args,**kwargs):
        self.name = slugify(self.name)
        if not self.opt_value:
            self.opt_value = self.default_value
        super(Option,self).save(*args,**kwargs)
