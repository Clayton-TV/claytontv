import csv
from django.core.management.base import BaseCommand, CommandError
import django.core.exceptions
from catalogue.models.demograpic import Demographic
from catalogue.models.topic import Topic
from catalogue.models.series import Series
from catalogue.models.video import Video


class Command(BaseCommand):
    help = "Imports data from a CSV"

    def add_arguments(self, parser): #This adds a debug option to the command
        parser.add_argument(
            "--DEBUG", # This is the option.
            action="store_true", # In this case it stores that the whether this option has been called or not, if it has it will return true when queried.
            help="Runs the command with Debug on", # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.link_demographics("CSV/Demographics.csv",options["DEBUG"]) #calls the function that imports the CSV at the file path into the Bible_Book data table. It also passes the result of options["DEBUG"] which checks if the debug command has been called.

    def link_demographics(self,filepath,Debug):
        if Debug:
            print("The command ran and:") # Debug Text

        with open(filepath, 'r', encoding='utf-8-sig') as file: # Opens the file path at "filepath" readonly as the variable "file".
            reader = csv.DictReader(file) #opens file with using the CSV's' library Dictreader which converts it into a dictionary, the headers are the key for each row.
            for row in reader: # cycles through the row of the dictionary previously created.
                if Debug: # Debug Text
                    print(row) # Debug Text
                    print("Linked " + row['Name'])# Debug Text, note that the rows are referred to by the column headers in the dict

                topics = row['Topics'].split(',')
                series = row['Series'].split(',')
                videos = row['Videos'].split(',')

                try:
                    Dem = Demographic.objects.get(name = row['Name'])


                except django.core.exceptions.ObjectDoesNotExist:
                    print("The entry " + row['Name'] + " does not exist" )
                    input("Press Enter to continue...")

                except django.core.exceptions.MultipleObjectsReturned:
                    print("The entry " + row['Name'] + " returned duplicate elements" )

                else:

                    Dem.topics.clear()
                    Dem.series.clear()
                    Dem.videos.clear()

                    for i in topics:
                        try:
                            Dem.topics.add(Topic.objects.get(id = i))

                        except django.core.exceptions.ObjectDoesNotExist:
                            print("The topic " + i + " does not exist")
                            print(Topic.objects.get(name = 'The Law').id)
                            if (i == Topic.objects.get(name = 'The Law').id):
                                print("true")
                            else:
                                print("false")
                            input("Press Enter to continue...")

                        except django.core.exceptions.MultipleObjectsReturned:
                            print("The topic " + i + " returned duplicate elements")

                    for i in series:
                        try:
                            Dem.series.add(Series.objects.get(id_number = i))

                        except django.core.exceptions.ObjectDoesNotExist:
                            print("The Series " + i + " does not exist")


                        except django.core.exceptions.MultipleObjectsReturned:
                            print("The Series " + i + " returned duplicate elements")

                    for i in videos:
                        try:
                            Dem.videos.add(Video.objects.get(id = i))

                        except django.core.exceptions.ObjectDoesNotExist:
                            print("The Video " + i + " does not exist")
                            input("Press Enter to continue...")

                        except django.core.exceptions.MultipleObjectsReturned:
                            print("The Video " + i + " returned duplicate elements")







