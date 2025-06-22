from .bible_book import Bible_Book
from .channel import Channel
from .demograpic import Demographic
from .label import Label
from .ministry import Ministry
from .series import Series
from .speaker import Speaker
from .topic import Topic
from .video import Video

# Define which models should be available when importing from catalogue.models
__all__ = [
    "Bible_Book",
    "Channel",
    "Demographic",
    "Label",
    "Ministry",
    "Series",
    "Speaker",
    "Topic",
    "Video",
]

# NB will need to import models from the other tables
# when the classes for these have been created
