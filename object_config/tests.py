# coding: utf-8
"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
from django.contrib.contenttypes import generic
from django.core.cache import cache
from django.db import models, IntegrityError
from django.db.models import ObjectDoesNotExist
from django.test import TestCase
from object_config.models import Option, OPT_TYPES
from decimal import Decimal
import simplejson
import datetime

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

class MyModel(models.Model):
    name = models.CharField(max_length=10)
    options = generic.GenericRelation(Option,related_name='options')

class OptionsTest(TestCase):

    def setUp(self):

        self.model = MyModel.objects.create(name='test 1')

        # Option schema
        # {
        #     'name':'',
        #     'verbose_name':'',
        #     'help_text':'', # optional field
        #     'type': -1,
        #     'default_value':'', # optional field
        # }
        self.options = [
            {
                'name':'items_per_page',
                'verbose_name':'Number of items per page',
                'help_text':'Number of items showed per page.',
                'type': 0, # integer
                'default_value': 50
            },
            {
                'name':'base_percentage_for_bonus',
                'verbose_name':'Percentage to caculate bonus',
                'help_text':'This value is a percentage that applyed to bonus give your final value.',
                'type': 1, # float
                'default_value': 0.45
            },
            {
                'name':'pi_number',
                'verbose_name':'PI Number',
                'help_text':'Value of PI number. If you want more precision, use more decimal places.',
                'type': 2, # float
                'default_value': Decimal('3.1415927')
            },
            {
                'name':'email_signature',
                'verbose_name':'Your signature',
                'help_text':'HTML accepted, use remote images if needed. You can use Django template language. request and user are in Context.',
                'type': 3, # string
                'default_value': "{{ user.get_full_name }}\n{{ user.get_profile.company }} - {{ user.get_profile.departament }}"
            },
            {
                'name':'base_data_for_user_ajax_call',
                'verbose_name':'Default JSON for user api call',
                'help_text':'This json will be expanded to custom user data in response of user ajax api. Accept Django template language in values. request and user ar in Context.',
                'type': 4, # json
                'default_value':simplejson.dumps({'allowed_apps':['djangoool','webmail','tickets','bike shop']})
            },
            {
                'name':'allow_new_docs',
                'verbose_name':'Allow new documents',
                'help_text':'If checked allow you add new documents.',
                'type': 5, # bool
                'default_value': '0'
            },
        ]

    def test_option_creation_int(self):
        """ Test creation of one option and duplicate key rule for integers """
        opts = self.options[0].copy()
        option = self.model.options.create(**opts)
        self.assertEquals(50,option.value)
        option.value = 100
        self.assertEquals(100,option.value)
        self.assertEquals('100',option.opt_value)

    def test_option_creation_float(self):
        """ Test creation of one option for float """
        opts = self.options[1].copy()
        option = self.model.options.create(**opts)
        self.assertEquals(0.45,option.value)
        option.value = 0.6555559
        self.assertEquals(0.6555559,option.value)
        self.assertEquals('0.6555559',option.opt_value)

    def test_option_creation_decimals(self):
        """ Test creation of one option for decimals """
        opts = self.options[2].copy()
        option = self.model.options.create(**opts)
        self.assertEquals(Decimal('3.1415927'),option.value)
        option.value = 3.141592653
        self.assertEquals(Decimal('3.141592653'),option.value)
        self.assertEquals('3.141592653',option.opt_value)

    def test_option_creation_string(self):
        """ Test creation of one option for integers """
        opts = self.options[3].copy()
        option = self.model.options.create(**opts)
        self.assertEquals("{{ user.get_full_name }}\n{{ user.get_profile.company }} - {{ user.get_profile.departament }}",option.value)
        option.value = "{{ user.get_full_name }}\n{{ user.get_profile.company }} - {{ user.get_profile.departament }}\nMobile: {{ user.get_profile.mobile }}"
        self.assertEquals("{{ user.get_full_name }}\n{{ user.get_profile.company }} - {{ user.get_profile.departament }}\nMobile: {{ user.get_profile.mobile }}",option.value)
        self.assertEquals("{{ user.get_full_name }}\n{{ user.get_profile.company }} - {{ user.get_profile.departament }}\nMobile: {{ user.get_profile.mobile }}",option.opt_value)

    def test_option_creation_json(self):
        """ Test creation of one option for json """
        opts = self.options[4].copy()
        option = self.model.options.create(**opts)
        self.assertEquals({'allowed_apps':['djangoool','webmail','tickets','bike shop']},option.value)
        option.value = {'allowed_apps':['djangoool','webmail','tickets','bike shop'],'last_login':str(datetime.datetime(2012,3,8,13,21))}
        self.assertEquals({'allowed_apps':['djangoool','webmail','tickets','bike shop'],'last_login':str(datetime.datetime(2012,3,8,13,21))},option.value)
        self.assertEquals('{"allowed_apps": ["djangoool", "webmail", "tickets", "bike shop"], "last_login": "2012-03-08 13:21:00"}',option.opt_value)

    def test_option_creation_bool(self):
        """ Test creation of one option for booleans """
        opts = self.options[5].copy()
        option = self.model.options.create(**opts)
        self.assertEquals(False,option.value)
        self.assertEquals('0',option.opt_value)
        option.value = True
        self.assertEquals(True,option.value)
        self.assertEquals('1',option.opt_value)

    def test_option_duplicate_key(self):
        """ Test duplicate key creation """
        opts = self.options[0].copy()
        self.model.options.create(**opts)
        self.assertRaises(IntegrityError,self.model.options.create,**opts)

    def test_option_create_many(self):
        """ Test many items creation """

        created = self.model.options.create_many(self.options)
        self.assertEquals(len(created),self.model.options.count())

        #  check each instance
        self.assertEquals(50,
            self.model.options.get(name=self.options[0]['name']).value)
        self.assertEquals(0.45,
            self.model.options.get(name=self.options[1]['name']).value)
        self.assertEquals(Decimal('3.1415927'),
            self.model.options.get(name=self.options[2]['name']).value)
        self.assertEquals("{{ user.get_full_name }}\n{{ user.get_profile.company }} - {{ user.get_profile.departament }}",
            self.model.options.get(name=self.options[3]['name']).value)
        self.assertEquals({'allowed_apps':['djangoool','webmail','tickets','bike shop']},
            self.model.options.get(name=self.options[4]['name']).value)
        self.assertEquals(False,self.model.options.get(name=self.options[5]['name']).value)

    def test_option_create_many_failed(self):
        """ Test create_maby failure. Any entrie of options dict that is sent should be in database. """
        options = list(self.options)
        options.append(options[0])

        self.assertRaises(IntegrityError,self.model.options.create_many,options)

        for opt in options:
            self.assertRaises(Option.DoesNotExist,self.model.options.get,name=opt['name'])

    def test_options_cache(self):

        created = self.model.options.create_many(self.options)
        keys = [i.cache_key for i in created]

        # it should not be cached yet
        for key in keys:
            self.assertEquals(False,cache.has_key(key))

        for opt in created:
            opt.value
            self.assertEquals(True,cache.has_key(opt.cache_key))
            self.assertEquals(opt.value,cache.get(opt.cache_key))

    def test_options_get_all_cached(self):

        created = self.model.options.create_many(self.options)
        keys = [i.cache_key for i in created]

        # it should not be cached yet
        for key in keys:
            self.assertEquals(False,cache.has_key(key))

        self.assertRaises(AttributeError,Option.objects.get_all_cached)

        opt_dict = self.model.options.get_all_cached()

        for key in keys:
            self.assertEquals(True,cache.has_key(key))
            self.assertEquals(opt_dict[key.split('-')[-1]],cache.get(key))

    def test_options_set_val(self):
        self.model.options.create(**self.options[0])
        self.assertEquals(50,self.model.options.get(name=self.options[0]['name']).value)
        self.model.options.set_val(self.options[0]['name'],100)
        self.assertEquals(100,self.model.options.get(name=self.options[0]['name']).value)

    def test_options_set_val_many(self):

        created = self.model.options.create_many(self.options)

        # check original values
        self.assertEquals(50,
            self.model.options.get(name=self.options[0]['name']).value)
        self.assertEquals(0.45,
            self.model.options.get(name=self.options[1]['name']).value)
        self.assertEquals(Decimal('3.1415927'),
            self.model.options.get(name=self.options[2]['name']).value)
        self.assertEquals("{{ user.get_full_name }}\n{{ user.get_profile.company }} - {{ user.get_profile.departament }}",
            self.model.options.get(name=self.options[3]['name']).value)
        self.assertEquals({'allowed_apps':['djangoool','webmail','tickets','bike shop']},
            self.model.options.get(name=self.options[4]['name']).value)
        self.assertEquals(False,self.model.options.get(name=self.options[5]['name']).value)

        # update values
        self.model.options.set_val_many([
            (self.options[0]['name'],100),
            (self.options[1]['name'],1.45),
            (self.options[2]['name'],Decimal('3.1415927543235')),
            (self.options[3]['name'],"{{ user.first_name }}\n{{ user.get_profile.company }} - {{ user.get_profile.departament }}"),
            (self.options[4]['name'],{'allowed_apps':['djangoool','webmail','tickets']}),
            (self.options[5]['name'],True),
        ])

        # check new values
        self.assertEquals(100,
            self.model.options.get(name=self.options[0]['name']).value)
        self.assertEquals(1.45,
            self.model.options.get(name=self.options[1]['name']).value)
        self.assertEquals(Decimal('3.1415927543235'),
            self.model.options.get(name=self.options[2]['name']).value)
        self.assertEquals("{{ user.first_name }}\n{{ user.get_profile.company }} - {{ user.get_profile.departament }}",
            self.model.options.get(name=self.options[3]['name']).value)
        self.assertEquals({'allowed_apps':['djangoool','webmail','tickets']},
            self.model.options.get(name=self.options[4]['name']).value)
        self.assertEquals(True,
            self.model.options.get(name=self.options[5]['name']).value)


    def tearDown(self):
        cache.clear()