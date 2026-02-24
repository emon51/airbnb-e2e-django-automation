from django.contrib import admin
from tracker.models import Result


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('test_case', 'passed', 'url', 'screenshot', 'created_at')
    list_filter = ('passed', 'test_case')
    search_fields = ('test_case', 'comment', 'url')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)