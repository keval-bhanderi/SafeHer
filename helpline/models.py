from django.db import models

class Helpline(models.Model):
    CATEGORY_CHOICES = [
        ('women', 'Women Helpline'),
        ('police', 'Police'),
        ('medical', 'Medical'),
        ('child', 'Child Helpline'),
        ('mental', 'Mental Health'),
        ('legal', 'Legal Aid'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=200)
    number = models.CharField(max_length=20)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    available_24x7 = models.BooleanField(default=True)
    state = models.CharField(max_length=100, blank=True, help_text="Leave blank for national helpline")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} - {self.number}"
