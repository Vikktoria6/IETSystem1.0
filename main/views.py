from django.shortcuts import render, redirect
from .models import Electives, Group, Jobs
from .forms import ChoiceForm
from . import ont_function

selected_group = ''
selected_job = ''
number = 0
iot = False
itog_elec = []


def index(request):
    global selected_group
    global selected_job
    global number
    global iot 
    
    jobs = Jobs.objects.all()
    ont_function.read_file()

    if request.method == 'POST':
        iot = False
        form = ChoiceForm(request.POST)
        if (form.is_valid() and request.POST.get('combobox_group')!='1' and 
            request.POST.get('combobox_job')!='1' and request.POST.get('combobox_number')!='1'):
            number = int(request.POST.get('combobox_number')) - 1
            groups = ont_function.groups
            groups = [gr['name'] for gr in groups]
            selected_group = groups[int(request.POST.get('combobox_group')) - 2]

            jobs = Jobs.objects.all()
            selected_job = jobs[int(request.POST.get('combobox_job')) - 2].job_name
            return redirect('trajectory')
        else: 
            form = ChoiceForm()
            
    else:
        form = ChoiceForm()

    context = {
        'form': form
    }

    return render(request, 'main/index.html', context)

def electives(request):
    elec = Electives.objects.all()
    return render(request, 'main/electives.html', {'elec': elec})



def create_trajectory(selected_elec): 
    track_elec = []
    for sel_elec in selected_elec: 
      for elec in ont_function.elective:
         if elec['name'] == sel_elec:
            track_elec.append(elec['id'])
            break
         
    for value in ont_function.groups:
      if (value['name'] == selected_group):
        group_node = value
        break
    
    study_rank = ont_function.readiness_to_study(group_node, track_elec)


    return study_rank
    





def trajectory(request):
    global iot
    global itog_elec
    if (selected_group == '' or selected_job == ''):
        return redirect('main')
    rank = ont_function.rank_of_electives(selected_group, selected_job)
    rank_list = []
    for key, value in rank.items():
        s = (str(int(value * 100)) + '% ', str(key))
        rank_list.append(s)


    if request.method == 'POST':
        iot = False
        selected_elec = request.POST.getlist('selected_elec')

        if (len(selected_elec) == number): 
            iot = True
            itog_elec = create_trajectory(selected_elec)
            return redirect('trajectory')
        else: 
            iot = False


        

    context = {
        'rank_list': rank_list,
        'number': number,
        'iot': iot,
        'itog_elec': itog_elec
    }
    return render(request, 'main/trajectory.html', context)

