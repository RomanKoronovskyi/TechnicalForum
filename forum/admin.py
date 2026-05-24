from django.contrib import admin
from .models import Tag, Question, Answer

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Question)
admin.site.register(Answer)