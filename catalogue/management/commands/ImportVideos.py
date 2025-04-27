import csv
import string

from django.core.management.base import BaseCommand, CommandError
from catalogue.models.video  import Video
from datetime import datetime


class Command(BaseCommand):
    help = "Imports data from a CSV"

    def add_arguments(self, parser): #This adds a debug coption to the command
        parser.add_argument(
            "--DEBUG", # This is the option.
            action="store_true", ## In this case it stores that the whether this option has been called or not, if it has it will return true when queried.
            help="Runs the command with Debug on", # Help text for helpful helpers.
        )

    def handle(self, *args, **options):
        self.imp_videos("CSV/Videos.csv",options["DEBUG"]) #calls the function that imports the CSV at the file path into the Bible_Book data table. It also passes the result of options["DEBUG"] which checks if the debug command has been called.

    def parse_video_date(self,DateString,ID,AltString):
        print(DateString)
        print(AltString)
        print(ID)
        try:
            DateOut = datetime.strptime(DateString,"%d/%m/%Y")
        except ValueError:
            if self.ID_has_date(ID):
                DateOut = datetime.strptime(self.get_ID_date(ID) , "%d/%m/%Y")
            else:
                DateOut = datetime.strptime(AltString, "%d/%m/%Y")
        return(DateOut)

    def ID_has_date(self,ID):

        for i in range(0,len(ID)):
            if ID[i] == '.':
                if i+3 < len(ID):
                    if ID[i+3] == '.':
                        return True

        return False

    def get_ID_date(self,ID):

        for i in range(0,len(ID)):
            if ID[i] == '.':
                Anchor = i
                break

        Day = ID[i - 2 : i ]
        Month = ID[i + 1 : i + 3 ]
        Year = ID[i + 4 : i + 6 ]

        Date = Day+'/'+Month+'/'+'20'+Year
        Date.replace(string.ascii_letters,'0')
        print(Date)
        return Date

    def imp_videos(self,filepath,Debug):
        if Debug:
            print("The command ran and:") # Debug Text
        Video.objects.all().delete() # Clears all the existing data before reimporting, a useful but dangerous commands.
        with open(filepath, 'r', encoding='utf-8-sig') as file: # Opens the file path at "filepath" readonly as the variable "file".
            reader = csv.DictReader(file) #opens file with using the CSV's library Dictreader which converts it into a dictionary, the headers are the key for each row.
            for row in reader: # cycles through the row of the dictionary previously created.
                if Debug: # Debug Text
                    print(row) # Debug Text
                    print("Imported " + row['Name'])# Debug Text, note that the rows are reffered to by the column headers in the dict
                Video.objects.create(
                    id = row['ID'],
                    id_number=row['ID Number'],
                    #bible_book=row['bible_book'],
                    description=row['Description'],
                    url = row['URL'],
                    #ministry = row['ministry'],
                    #number_in_series = row['number_in_series'],
                    name = row['Name'],
                    #speaker = row['speaker'],
                    #is_livestream = row['IsLivestream'],
                    #topic = row['topic']

                    thumbnail = row['Thumbnail'],

                    date_recorded = self.parse_video_date(row['DateRecorded'],row['ID Number'],row['DateCreated']),
                    date_created = datetime.utcnow().strftime('%Y-%m-%d'),
                    date_modified = datetime.utcnow().strftime('%Y-%m-%d'),

                    #labels = somelabel this will probably be created at the same time in this script
                    #channel = row["Channel"],
                    #series = row[series],

                )
