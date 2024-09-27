import csv
from django.core.management.base import BaseCommand, CommandError
from catalogue.models.topic import Topic



class Command(BaseCommand):
    help = "Imports data from a CSV"

    def add_arguments(self, parser): #This adds a debug coption to the command
        parser.add_argument(
            "--DEBUG", # This is the option.
            action="store_true", ## In this case it stores that the whether this option has been called or not, if it has it will return true when queried.
            help="Runs the command with Debug on", # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.imp_topics("CSV/Topics.csv",options["DEBUG"]) #calls the function that imports the CSV at the file path into the Bible_Book data table. It also passes the result of options["DEBUG"] which checks if the debug command has been called.

    def imp_topics(self,filepath,Debug):
        if Debug:
            print("The command ran and:") # Debug Text
        Topic.objects.all().delete() # Clears all the existing data before reimporting, a useful but dangerous commands.
        with open(filepath, 'r', encoding='utf-8-sig') as file: # Opens the file path at "filepath" readonly as the variable "file".
            reader = csv.DictReader(file) #opens file with using the CSV's library Dictreader which converts it into a dictionary, the headers are the key for each row.
            for row in reader: # cycles through the row of the dictionary previously created.
                if Debug: # Debug Text
                    print(row) # Debug Text
                    print("Imported " + row['Name'])# Debug Text, note that the rows are reffered to by the column headers in the dict
                Topic.objects.create(
                    name=row['Name'],
                    summary=row['Summary'],
                    category=row['Category']
                    # videos=row['Videos'], Not added at this point
                    # series=row['Series'], Not added at this point
                )