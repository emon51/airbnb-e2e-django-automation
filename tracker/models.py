from django.db import models


class Result(models.Model):
    test_case = models.CharField(max_length=255)
    url = models.URLField(max_length=2000)
    passed = models.BooleanField(default=False)
    comment = models.TextField(blank=True)
    screenshot = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{'PASS' if self.passed else 'FAIL'}] {self.test_case}"

    class Meta:
        ordering = ['-created_at']