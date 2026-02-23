from django.db import models


class TestResult(models.Model):
    test_case = models.CharField(max_length=255)
    url = models.URLField()
    passed = models.BooleanField(default=False)
    comment = models.TextField(blank=True)
    screenshot = models.ImageField(upload_to='screenshots/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.test_case} - {'PASS' if self.passed else 'FAIL'}"


class SuggestionItem(models.Model):
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class ListingItem(models.Model):
    title = models.CharField(max_length=255)
    price = models.CharField(max_length=100)
    image_url = models.URLField(blank=True)
    detail_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class ConsoleLog(models.Model):
    level = models.CharField(max_length=50)
    message = models.TextField()
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.level}] {self.message[:80]}"


class NetworkLog(models.Model):
    method = models.CharField(max_length=20)
    url = models.URLField(max_length=2000)
    status = models.IntegerField(null=True, blank=True)
    resource_type = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.method} {self.status} {self.url[:80]}"