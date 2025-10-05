import datetime
from django.db import models


class StatusCatalog(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'status_catalog'
        verbose_name = 'Категория статуса'
        verbose_name_plural = 'Категории статусов'

    def __str__(self):
        return self.name


class TypeCatalog(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'type_catalog'
        verbose_name = 'Категорию'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class CategoryCatalog(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    types = models.ForeignKey(TypeCatalog, related_name='categories', on_delete=models.CASCADE)

    class Meta:
        db_table = 'category_catalog'
        verbose_name = 'Категорию'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class SubCategoryCatalog(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(CategoryCatalog, related_name='subcategories', on_delete=models.CASCADE)

    class Meta:
        db_table = 'sub_category_catalog'


class CashFlow(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField(default=datetime.date.today)
    status = models.ForeignKey(StatusCatalog, on_delete=models.CASCADE)
    type = models.ForeignKey(TypeCatalog, on_delete=models.CASCADE)
    category = models.ForeignKey(CategoryCatalog, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategoryCatalog, on_delete=models.CASCADE, related_name='categories', null=True,
                                    blank=True)
    sum = models.FloatField(default=0)
    comment = models.TextField()
