# coding: utf-8

from django.conf import settings
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models, transaction, IntegrityError
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

    def create_many(self,items):
        """ Create many entries based on a list of dictionarys """

        # since transactions not work in MyISAM, let's do our way.
        # 'transactions' here is important because who normally wil use this
        # method is developer when create a model entry and need to setup default
        # options.
        created=[]

        for item in items:
            try:
                created.append(self.create(**item))
            except IntegrityError, err:
                [i.delete() for i in created]
                raise IntegrityError, "%s. ALL CREATED ITEMS ARE REMOVED." % err

        return self.get_query_set().filter(pk__in=[i.id for i in created])

    def get_all_cached(self):
        """ Returns a dictonary of option_name: option_value entries. Returned value is parsed and cached.
        Be smart and use it with something model.options.get_all_cached(). Use like Options.objects.get_all_cached() will raise AttributeError """

        if self.__class__.__name__ != 'GenericRelatedObjectManager':
            raise AttributeError,u"This method can't be called from a normal Manager. This method should be called from a GenericRelatedObjectManager, in other words, use mode.options.get_all_cached()"

        values = self.values_list('pk','content_type','object_id','name')

        result={}

        for pk,content_type_id,object_id,name in values:
            key = self.cache_key_template % (content_type_id,object_id,name)
            if cache.has_key(key):
                result[name]=cache.get(key)
            else:
                result[name]=Option.objects.get(pk=pk).value # this cache parsed value

        return result

    def set_val(self,name,value):
        """ Set value for a option without need to get options """

        if self.__class__.__name__ != 'GenericRelatedObjectManager':
            raise AttributeError,u"This method can't be called from a normal Manager. This method should be called from a GenericRelatedObjectManager, in other words, use mode.options.set_val(name,value)"

        self.get(name=name).value = value

    def set_val_many(self,values_list):
        """ Set values for many options without need to get options """

        if self.__class__.__name__ != 'GenericRelatedObjectManager':
            raise AttributeError,u"This method can't be called from a normal Manager. This method should be called from a GenericRelatedObjectManager, in other words, use mode.options.set_val_many([(name,val),(name,val),(name,val)])"

        for name,value in values_list:
            self.set_val(name,value)


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
    opt_value = models.TextField(default=None,null=True,blank=True)
    default_value = models.TextField(default=None,null=True,blank=True)

    objects = OptionManager()



    class Meta:
        unique_together = ('content_type','object_id','name')

    def __unicode__(self):
        return u"%s:%s <%s>" % (self.content_object,self.name,self.get_type_display())

    _key = None
    def _get_cache_key_template(self):
        """
        Returns the cache key template.
        The base template is 'option__<content_type_id>-<object_id>-<opt_name>',
        so, for your key template you should consider tree places to put 
        content_type_id, object_id and opt_name.

        To get a different cache key template you should overwrite this method
        or configure a setting called OBJECT_CONFIG_CACHE_KEY_TEMPLATE.

        It is really useful for Django < 1.3 that can't set CACHE_KEY_PREFIX
        settings (https://docs.djangoproject.com/en/1.3/ref/settings/#key-prefix).
        """
        try:
            return settings.OBJECT_CONFIG_CACHE_KEY_TEMPLATE
        except AttributeError:
            return 'option__%s-%s-%s'
    cache_key_template = property(_get_cache_key_template)


    @property
    def cache_key(self):
        if not self._key and self.content_type_id and self.object_id and self.name:
            # if change how key is made CHANGE MANAGER TOO
            self._key=self.cache_key_template % (self.content_type_id,self.object_id,self.name)

        if not self._key: return None

        return self._key

    def _get_value(self):

        if self.cache_key and cache.has_key(self.cache_key):
            return cache.get(self.cache_key)

        if self.opt_value is None:
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
            f = lambda s:  simplejson.loads(s) if s else {}
        if self.type == 5:
            f = lambda s: bool(int(s))

        if f is None:
            raise TypeError,u"Unknow type set."

        value = f(self.opt_value or self.default_value)

        cache.set(self.cache_key,value,3600)

        return value

    def _set_value(self,value):
        cache.delete(self.cache_key)
        if self.type == 4:
            self.opt_value = simplejson.dumps(value)
        elif self.type == 5:
            self.opt_value = '1' if bool(int(value)) else '0'
        else:
            self.opt_value = u"%s" % value
        self.save()
        self._get_value() # this cache value again.

    value = property(_get_value,_set_value)

    def save(self,*args,**kwargs):
        self.name = slugify(self.name)

        if self.opt_value in ('',None) and self.default_value not in ('',None):
            self.opt_value = self.default_value
        super(Option,self).save(*args,**kwargs)
