from django_seed import Seed

seeder = Seed.seeder()

from catalogue.models import bible_book
seeder.add_entity(bible_book, 5)


inserted_pks = seeder.execute()