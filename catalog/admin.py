from django.contrib import admin
from .models import Topic, Video, Channel, Speaker, Series

# Register your models here.
admin.site.register(Topic)
admin.site.register(Channel)
admin.site.register(Speaker)
admin.site.register(Series)

class VideoAdmin(admin.ModelAdmin):
    list_display = ('title','date_created','series','speaker','display_topic')
    list_filter = ('series','channel','speaker')

admin.site.register(Video,VideoAdmin)

