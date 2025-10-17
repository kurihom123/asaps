from django.db import models
from django.core.exceptions import ValidationError

class University(models.Model):
    name = models.CharField(max_length=100, unique=True)
    abbr = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = 'university'

    def __str__(self):
        return f'{self.abbr}'

class Association(models.Model):
    name = models.CharField(max_length=150)
    abbr = models.CharField(max_length=10, unique=True)
    member_number = models.IntegerField()
    logo = models.ImageField(upload_to='association_logos', default='asso.jpg')
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='association_university')

    class Meta:
        db_table = 'association'

    def __str__(self):
        return f'{self.abbr}'

class Contribution(models.Model):
    allocation = models.BigIntegerField()
    payment_date = models.DateField()
    amount_paid = models.BigIntegerField()
    balance = models.BigIntegerField()
    association = models.ForeignKey(Association, on_delete=models.CASCADE, related_name='contribution_association')
    year = models.CharField(max_length=9, default='2024-2025')

    class Meta:
        db_table = 'contribution'
        unique_together = ['association', 'year']  # Prevent duplicates

    def __str__(self):
        return f'{self.association} - {self.year}'

    def clean(self):
        if self.amount_paid is not None and self.amount_paid < 0:
            raise ValidationError("Amount paid cannot be negative.")

        if self.amount_paid is not None and self.allocation is not None:
            if self.amount_paid > self.allocation:
                raise ValidationError("Amount paid cannot exceed allocation.")
            self.balance = self.allocation - self.amount_paid

class ContributionUpload(models.Model):
    excel_file = models.FileField(upload_to='contribution_uploads/')
    year = models.CharField(max_length=9)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    class Meta:
        db_table = 'contribution_upload'

    def __str__(self):
        return f'Upload for {self.year} - {self.uploaded_at}'

class Position(models.Model):
    name = models.CharField(max_length=45, unique=True)

    class Meta:
        db_table = 'position'

    def __str__(self):
        return f'{self.name}'