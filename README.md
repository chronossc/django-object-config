# Django Object Config

### Intro

Object Config was create with clear intention of store settings per object in database, dinamically.

With settings per object I mean that that **to store user settings on Django User Profile you don't need to add N fields to this model, only Options**.

With dinamically I mean that you don't need to have all settings in all objects of same type if you prefer, only the ones you need.

The aim of Object Config app is be plugable, and not offer only a model to store options (that's easy part), but also shortcuts to manage options and  form fields to allow you (or your user) edit each option... So help is always welcome.

### How store so many options for a object?

Many Django devs already know answer for that, but some new devs may not know.

Django offers the [contenttypes framework](https://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/), that, in short, allow us to play with apps that use your models, but not depend of as explicit model, better, allow applicatiosn to plug to your models dinamically.

### What Object Config offers for now?
 T
Object Config allow you to set options for your object with many types of values. Object Config it self store all options as text, but know when a option is integer, string, boolean, or else a JSON. Object Config do it on get/set of Option Value.

You have at your disposal some good shortcuts in Option Manager, IE, the one that returns all object options in a dict format.

## Options are cached!

Object Config have full support to Django Cache framework, so when you get options, will not hit DB every time.

The cache key/value is set when you get Option Value, and is updated when you set the value, so you 'always' have last value cached.

The cache key template is "option__<content_type_id>-<object_id>-<opt_name>", so app don't overwrite keys.
Off course that if you have many 'projects' you probably don't share same contenttype table, and to avoid overwrite you should:

### If I'm using Django >= 1.3

Use [KEY\_PREFIX Django Setting](https://docs.djangoproject.com/en/dev/ref/settings/#key-prefix), also check [Cache Key Prefixing](https://docs.djangoproject.com/en/dev/topics/cache/#cache-key-prefixing) on docs.

### If I'm using Django < 1.3

This app support a setting called OBJECT\_CONFIG\_CACHE\_KEY\_TEMPLATE where you can add your own key template. Ex:

```python
# Object Config custom cache key.
OBJECT_CONFIG_CACHE_KEY_TEMPLATE = "myamazingapp_option__%s-%s-%s"

```

I'll not support a callable for this because I don´t see any reason to it. Show me one and I can add support.

### If I'm not happy with that and need to do something more

You can overwrite Options.\_get\_cache\_key\_template method, but think twice if is necessary.


## How use Options in code (finally!)?

### The Options model

Hehe, not yet. Let me show the Option model, so you can know the fields. You need to know that because you will define options at least once.

The following fields are revelant to one Option:

* **name**: A slug field containing the option name. Required, off course.
* **type**: Type is a positive integer field that stores the type choose. Types are (for now) 0-Integer, 1-Float, 2-Decimal, 3-String, 4-JSON and 5-Boolean. It's also mandatory.
* **verbose_name**: This store the label for the option, is used in forms (not yet implemented). Also required.
* help_text: Help Text store any explanation that you have about option in 255 chars.
* opt_value: Option value. Here is set the value of the option when you set it. Field is a TextField to support all types. You will get 'unserialized' value from 'Option.value' property instead opt\_value.
* default_value: Default value for option. When option don't have a value set, if default\_value is set we use it.

Under the hood we have yet content_type_id and object_id, that you need to use if create a Option without use related manager from your model. This fields a you probably know, is used by contenttypes framework.

### Using options in your model

Use options is pretty simple. You just need to add Option model as a [Generic Relation](https://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/#reverse-generic-relations) to your model and play with options.

Consider the following models.py file with a very simple User Profile model:

```python
from django.db import models
from django.contrib.auth import User
from django.contrib.contenttypes import generic
from object_config.models import Option

class Profile(models.Model):
    user = models.OneToOneField(User)
    options = generic.GenericRelation(Option)
```

Then you can manage options in following way:

```python
from django.contrib.auth.models import User
from myprofileapp.models import Profile

# create user and profile
u1 = User.objects.create(username='chronos',email='philipe.rp@gmail.com')

Profile.objects.create(user=u1) # use a signal to do it ok?
[out:<Profile: philipe.rp@gmail.com>]

profile = u1.get_profile()

profile.options.create(name='obj_per_page',verbose_name='Objects per page',type=0,default_value='50')
[out: <Option: philipe.rp@gmail.com:obj_per_page <Integer>>]

# create a option 'obj_per_page' and query it
opt = profile.options.get(name='obj_per_page')
opt.value
[out: 50]

opt.opt_value
[out: '50']

opt.default_value
[out: '50']

# now set a value and query it
opt.value = 100
opt.value
[out: 100]
opt.opt_value
[out: '100']
opt.default_value
[out: '50']

# you don't need to get option object to set option value. It works:
profile.options.set_val('obj_per_page',150)

```


### Making your life better with shortcuts

Create each option with mymodel.options.create(..) is a pain in the ass, I know, and you will have many options to justify use this app. Query each option is another pain in the ass, but I created some shortcuts to make it easy.

* **Option.objects.create_many**: The create\_many method in OptionManager allow you to create many options based on a list of dictionaries. It is used mainly to create all default options. I'll explain that better in **Setting default options at object creation**.

* **Option.objects.set_val**: Set the value of a given option, receives the option name and the value. It pretty easy to update value of a setting. Only works from a relation manager.

* **Option.objects.set\_val_many**: Given a list with tuples like (option\_name,value) use *set_val* to update many options. Useful when you will save some option page. Only works from a relation manager.

* **Option.objects.get\_all_cached**: This method returns all options of object in a dictinary. On the process it cache all options. Useful in templates or when you just need to show all options.

### Setting default options at object creation

Personally I think that better way to work with options is create all options at post_save from (continue tomorrow...)