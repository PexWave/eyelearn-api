from django.contrib import admin
from practices.models import *
# Register your models here.
class PracticeAdmin(admin.ModelAdmin):

    search_fields = ('title', 'correct_answer', 'category')
    
class PracticeLyrics(admin.ModelAdmin):
    
    search_fields = ('lyrics', 'timestamp', 'practice__title')
    
admin.site.register(Practice, PracticeAdmin)
admin.site.register(Practice_Image)
admin.site.register(PracticeTimestamp,PracticeLyrics)