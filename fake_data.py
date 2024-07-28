import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
import django
django.setup()
from faker import factory, Faker
from catalogue.models import *
from model_bakery.recipe import Recipe

myfake = Faker()

for k in range(50):
	bible_book = Recipe(Bible_Book,
		name = myfake.name(),
		order = myfake.name(),
	    summary = myfake.name(),
        type = myfake.name(),)