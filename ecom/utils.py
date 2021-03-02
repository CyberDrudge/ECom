from django.utils.text import slugify

import random
import string
import os

'''
random_string_generator is located here:
http://joincfe.com/blog/random-string-generator-in-python/
'''


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_slug_generator(instance, new_slug=None):
    """
    This is for a Django project and it assumes your instance
    has a model with a slug field and a title character (char) field.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.title)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
                    slug=slug,
                    randstr=random_string_generator(size=4)
                )
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug
# print(random_string_generator())
# print(random_string_generator(size=50))


def unique_order_id_generator(instance):
    """
    This is for a Django project and it assumes your instance
    has a model with an id field.
    """
    new_order_id = random_string_generator()

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(order_id=new_order_id).exists()
    if qs_exists:
        return unique_order_id_generator(instance)
    return new_order_id


def unique_key_generator(instance):
    """
    This is for a Django project with an key field
    """
    size = random.randint(30, 45)
    key = random_string_generator(size=size)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(key=key).exists()
    if qs_exists:
        return unique_slug_generator(instance)
    return key


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):
    new_filename = random.randint(1, 3910209312)
    name, ext = get_filename_ext(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return "products/{new_filename}/{final_filename}".format(
            new_filename=new_filename,
            final_filename=final_filename
    )
