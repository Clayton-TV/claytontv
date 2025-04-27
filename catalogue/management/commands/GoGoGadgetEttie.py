import csv


class Command(BaseCommand):
    help = "Imports data from a CSV"

    def add_arguments(self, parser): #This adds a debug option to the command
        parser.add_argument(
            "--DEBUG", # This is the option.
            action="store_true", # In this case it stores that the whether this option has been called or not, if it has it will return true when queried.
            help="Runs the command with Debug on", # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.fix_series("CSV/Series.csv",options["DEBUG"]) #calls the function that imports the CSV at the file path into the Bible_Book data table. It also passes the result of options["DEBUG"] which checks if the debug command has been called.

    def CleanID(self, ItemIn):
        SymbolsToStrip = " '[]-—"
        ItemOut = ItemIn.Strip(SymbolsToStrip)
        return ItemOut

    def fix_series(self,filepath,Debug):
        if Debug:
            print("The command ran and:") # Debug Text

        with open(filepath, 'rw', encoding='utf-8-sig') as file: # Opens the file path at "filepath" with read write acces as the variable "file".
            reader = csv.DictReader(file) #opens file with using the CSV's' library Dictreader which converts it into a dictionary, the headers are the key for each row.
            for row in reader: # cycles through the row of the dictionary previously created.
                if Debug: # Debug Text
                    print(row) # Debug Text
                    print("Linked " + row['Name'])# Debug Text, note that the rows are referred to by the column headers in the dict


                topics = self.CleanID(row['Topic']).split(',')
                speaker = self.CleanID(row['Speaker']).split(',')
                videos = self.CleanID(row['Videos']).split(',')

                try:
                    Ser = Series.objects.get(id = row['ID'])

                except django.core.exceptions.ObjectDoesNotExist:
                    print("The entry " + row['ID'] + " does not exist" )

                except django.core.exceptions.MultipleObjectsReturned:
                    print("The entry " + row['ID'] + " returned duplicate elements" )









