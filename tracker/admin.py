from django.contrib import admin
from .models import TestResult, SuggestionItem, ListingItem, ConsoleLog, NetworkLog

admin.site.register(TestResult)
admin.site.register(SuggestionItem)
admin.site.register(ListingItem)
admin.site.register(ConsoleLog)
admin.site.register(NetworkLog)