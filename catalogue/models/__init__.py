from .bible_book import Bible_Book
from .channel import Channel
from .demograpic import Demographic
from .enrichment import VideoEnrichment
from .label import Label
from .live_stream import LiveStream
from .ministry import Ministry
from .related_resource import RelatedResource
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
    "LiveStream",
    "Ministry",
    "RelatedResource",
    "Series",
    "Speaker",
    "Topic",
    "Video",
    "VideoEnrichment",
]

# NB will need to import models from the other tables
# when the classes for these have been created
