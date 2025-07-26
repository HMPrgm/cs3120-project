from django.contrib import admin
from .models import Class, Textbook, TextbookPhoto, Collection, TextbookRequest, CollectionRequests

admin.site.register(Class)
admin.site.register(Textbook)


admin.site.register(TextbookPhoto)
admin.site.register(Collection)
admin.site.register(CollectionRequests)
admin.site.register(TextbookRequest)