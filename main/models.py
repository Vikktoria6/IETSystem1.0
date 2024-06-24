from django.db import models


class Electives(models.Model):
    title_elec = models.CharField('Название', max_length=100)
    description_elec = models.TextField('Описание')

    def __str__(self):
        return self.title_elec
    
    class Meta: 
        verbose_name = 'Электив'
        verbose_name_plural = 'Элективы'


class Group(models.Model):
    
    group_name = models.CharField('Направление', max_length=50)

    def __str__(self):
        return self.group_name
    
    class Meta: 
        verbose_name = 'Направление'
        verbose_name_plural = 'Направления'


class Jobs(models.Model):
    job_id = models.IntegerField('job_id')
    job_name = models.CharField('Название', max_length=50)

    def __str__(self):
        return self.job_name
    
    class Meta: 
        verbose_name = 'Профессия'
        verbose_name_plural = 'Профессии'
