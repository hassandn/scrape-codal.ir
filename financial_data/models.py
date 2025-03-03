from django.db import models


class ExtractedData(models.Model):
    data = models.CharField(max_length=75)
    row = models.CharField(max_length=50)
    col = models.CharField(max_length=50)
    datetime_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.row} - {self.col}"


class Log(models.Model):
    log_detail = models.TextField()
    datetime_created = models.DateTimeField(auto_now_add=True)
    row = models.TextField()
    col = models.TextField()

    def __str__(self):
        return f"Log: {self.log_name} ({self.row.row}, {self.col.col})"
