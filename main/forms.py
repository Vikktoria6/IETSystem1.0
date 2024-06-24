from django import forms
from . import ont_function
from .models import Jobs
from django.core.exceptions import ValidationError



class ChoiceForm(forms.Form):
    ont_function.read_file()
    groups = ont_function.groups
    groups = [gr['name'] for gr in groups]
    choices_gr = [(1, 'Выберите направление')]
    for i in range(len(groups)):
        choices_gr.append((i + 2, groups[i]))

    choices_jobs = [(1, 'Выберите профессию')]
    jobs = Jobs.objects.all()
    for i in range(len(jobs)):
        choices_jobs.append((i + 2, jobs[i].job_name))

    choices_number = [(1, 'Выберите количество'), (2, '1'), (3, '2'), (4, '3'), (5, '4'), (6, '5')]

    combobox_group = forms.ChoiceField(choices=choices_gr,
                                  widget=forms.Select(attrs={'class': "form-select"}))
    combobox_job = forms.ChoiceField(choices=choices_jobs,
                                  widget=forms.Select(attrs={'class': "form-select"}))
    combobox_number = forms.ChoiceField(choices=choices_number,
                                  widget=forms.Select(attrs={'class': "form-select"}))

