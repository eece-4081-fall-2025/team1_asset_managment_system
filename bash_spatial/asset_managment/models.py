import uuid
from time import timezone
from django.db import models
from django.conf import settings


class Attribute(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=1023)
    asset = models.ForeignKey(
        "Asset",
        on_delete=models.CASCADE,
        related_name="attributes_set",
    )

    def __str__(self):
        return f"{self.name}: {self.value}"


class Asset(models.Model):
    STATUS_CHOICES = [
        ("out_for_repairs", "Out for Repairs"),
        ("operational", "Operational"),
        ("checked_out", "Checked Out"),
        ("depricated", "Depricated"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(
        max_length=31, choices=STATUS_CHOICES, default="operational"
    )
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, default="General")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    depreciation = models.DateField(null=True, blank=True)
    attributes = []

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assets",
    )

    def addAttribute(self, name, value):
        self.attributes.append(Attribute(name=name, value=value))

    def assignUser(self, user):
        self.assigned_to = user
        self.save()

    @property
    def is_overdue(self):
        if self.depreciation and self.status != "out_for_repairs":
            return self.depreciation < timezone.now().date()
        return False
