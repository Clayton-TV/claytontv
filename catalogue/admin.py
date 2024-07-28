from django.contrib import admin

# Register your models here.
from .models import Video, Bible_Book, Channel, Demographic, Label, Ministry, Series, Speaker, Topic

admin.site.register(Video)
admin.site.register(Bible_Book)
admin.site.register(Channel)
admin.site.register(Demographic)
admin.site.register(Label)
admin.site.register(Ministry)
admin.site.register(Series)
admin.site.register(Speaker)
admin.site.register(Topic)