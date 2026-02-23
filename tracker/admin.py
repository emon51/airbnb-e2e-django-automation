from django.contrib import admin
from .models import TestResult, SuggestionItem, ListingItem

admin.site.register(TestResult)
admin.site.register(SuggestionItem)
admin.site.register(ListingItem)