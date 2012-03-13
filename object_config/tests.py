# coding: utf-8
"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
from django.contrib.contenttypes import generic
from django.db import models, IntegrityError
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
                'default_value': False
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
        """ Test creation of one option and duplicate key rule for float """
        opts = self.options[1].copy()
        option = self.model.options.create(**opts)
        self.assertEquals(0.45,option.value)
        option.value = 0.6555559
        self.assertEquals(0.6555559,option.value)
        self.assertEquals('0.6555559',option.opt_value)

    def test_option_creation_decimals(self):
        """ Test creation of one option and duplicate key rule for decimals """
        opts = self.options[2].copy()
        option = self.model.options.create(**opts)
        self.assertEquals(Decimal('3.1415927'),option.value)
        option.value = 3.141592653
        self.assertEquals(Decimal('3.141592653'),option.value)
        self.assertEquals('3.141592653',option.opt_value)

    def test_option_creation_string(self):
        """ Test creation of one option and duplicate key rule for integers """
        opts = self.options[3].copy()
        option = self.model.options.create(**opts)
        self.assertEquals("{{ user.get_full_name }}\n{{ user.get_profile.company }} - {{ user.get_profile.departament }}",option.value)
        option.value = "{{ user.get_full_name }}\n{{ user.get_profile.company }} - {{ user.get_profile.departament }}\nMobile: {{ user.get_profile.mobile }}"
        self.assertEquals("{{ user.get_full_name }}\n{{ user.get_profile.company }} - {{ user.get_profile.departament }}\nMobile: {{ user.get_profile.mobile }}",option.value)
        self.assertEquals("{{ user.get_full_name }}\n{{ user.get_profile.company }} - {{ user.get_profile.departament }}\nMobile: {{ user.get_profile.mobile }}",option.opt_value)

    def test_option_creation_json(self):
        """ Test creation of one option and duplicate key rule for integers """
        opts = self.options[4].copy()
        option = self.model.options.create(**opts)
        self.assertEquals({'allowed_apps':['djangoool','webmail','tickets','bike shop']},option.value)
        option.value = {'allowed_apps':['djangoool','webmail','tickets','bike shop'],'last_login':str(datetime.datetime(2012,3,8,13,21))}
        self.assertEquals({'allowed_apps':['djangoool','webmail','tickets','bike shop'],'last_login':str(datetime.datetime(2012,3,8,13,21))},option.value)
        self.assertEquals('{"allowed_apps": ["djangoool", "webmail", "tickets", "bike shop"], "last_login": "2012-03-08 13:21:00"}',option.opt_value)

    def test_option_duplicate_key(self):
        opts = self.options[0].copy()
        self.model.options.create(**opts)
        self.assertRaises(IntegrityError,self.model.options.create,**opts)