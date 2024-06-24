import json
from .my_stopwords import my_stopwords
import nltk
import pymorphy2
import string
from nltk import pos_tag
from nltk.corpus import stopwords
import gensim
from collections import Counter
import requests
from .models import Jobs
import os


filename = 'subject.ont'
filemodel = 'model.bin'

nodes= {}     #все узлы 
elective = []   #элективы
groups = []     #направления
knowledge = []  #знания с элективов
model: any
data_json:any



def model_load():
   global model
   model = gensim.models.KeyedVectors.load_word2vec_format(filemodel, binary=True)




def read_file():
    global data_json
    if (len(nodes) == 0):
      # nltk.download('punkt')
      # nltk.download('stopwords')
      # nltk.download('wordnet') 
      # nltk.download('averaged_perceptron_tagger')
      # nltk.download('averaged_perceptron_tagger_ru')
      model_load()
      if os.path.exists(filename):
        file = open(filename, "r", encoding='utf-8')
        data = file.read()
        clear_data = data.replace('\n', '')
        data_json = json.loads(clear_data)

        for node in data_json['nodes']:
            nodes[node['id']] = node
            if (node['attributes']['title'] == 'Электив'):
                elective.append(node)
            if (node['attributes']['title'] == 'Направление'):
                groups.append(node)

        for elec in elective:
            know = ''
            know += elec['name'] + ' '
            for rel in data_json['relations']:
                if (rel['source_node_id'] == elec['id'] and rel['name'] == 'формирует'):
                    know += (nodes[rel['destination_node_id']]['name'] + ' ')
            knowledge.append(know)




def add_tags(words):
  pos_tags = pos_tag(words, lang='rus')
  list_word = []
  for index, w in enumerate(words):
    input = w
    if (pos_tags[index][1] == 'S' or w == 'ос'):
      input += '_NOUN'
      list_word.append(input)
    elif (pos_tags[index][1] == 'A=m' or pos_tags[index][1] == 'A=f'):
      input += '_ADJ'
      list_word.append(input)
    elif (pos_tags[index][1] == 'V'):
      input += '_VERB'
      list_word.append(input)
    elif (pos_tags[index][1] == 'NONLEX'):
      input += '_PROPN'
      list_word.append(input)
    # else:
    #   print(w, pos_tags[index][1])
  return list_word




def normalize_text(text, own_stopwords):
  
  token_text = nltk.word_tokenize(text)
  morph = pymorphy2.MorphAnalyzer()
  normal_text = [(morph.parse(i)[0]).normal_form for i in token_text]

  stop_words = list(stopwords.words('russian'))
  stop_words.extend(own_stopwords)
  normal_text = [i for i in normal_text if (i not in string.punctuation and i not in stop_words)]

  normal_text = add_tags(normal_text)

  clear_words = []
  for i in normal_text:
    if (i in model.index_to_key):
      clear_words.append(i)
    # else:
    #   print(i)

  word_wight = dict(sorted(Counter(clear_words).items(), key=lambda x: x[1], reverse=True))

  return word_wight




def api_job(id):
  str_job = ''
  url = f'https://api.hh.ru/vacancies?professional_role={id}&&per_page=30'

  response = requests.get(url)
  
  if response.status_code == 200:
      vacancies = response.json()
      for vacancy in vacancies.get("items", []):
        str_job = str_job + str(vacancy['snippet']['requirement']) + ' ' + str(vacancy['snippet']['responsibility']) + ' '
  else:
      print("Ошибка при выполнении запроса:", response.status_code)
  return(str_job)




def compatibility(normalize_knowledge, requirements):
    sum_elec = {}
    ratio = 0.9

    for one_skill in normalize_knowledge:
      sum_itog = 0
      length = 0
      name = elective[normalize_knowledge.index(one_skill)]['name']
      for skill, freq_skill in one_skill.items():
          sum = 0
          length += freq_skill
          for job, freq_job in requirements.items():
              sum += (model.similarity(skill, job) * freq_skill * freq_job)
              if (model.similarity(skill, job) > ratio):
                  sum += 1 * freq_skill * freq_job
          sum_itog += sum/len(requirements)

      # if (sum_itog/length > 0.4):
      #     print(name)
      #     print(sum_itog)
      #     print('len = ', length)
      sum_elec[elective[normalize_knowledge.index(one_skill)]['id']] = sum_itog/length
    return sum_elec
    


def readiness_to_study(group_node, track_elec):
    lesson = []
    for rel in data_json['relations']:
      if (rel['source_node_id'] == group_node['id'] and rel['name'] == 'содержит'):
        lesson.append(rel['destination_node_id'])
    
    group_skills = {}
    for les in lesson:
      for rel in data_json['relations']:
        if (rel['source_node_id'] == les and rel['name'] == 'формирует'):
          group_skills[rel['destination_node_id']] = rel['source_node_id']

    itog_elec = []
    end = []
    for elec in track_elec:
      dop = []
      fl = False
      count_rel = 0
      true_rel = 0
      for rel in data_json['relations']:
        if (rel['source_node_id'] == elec and rel['name'] == 'требует'):
          count_rel = count_rel + 1
          if rel['destination_node_id'] in list(group_skills):
            true_rel = true_rel + 1
          else: 
            # if rel['destination_node_id'] in list(group_skills):
            #   if not(group_skills[rel['destination_node_id']] in dop):
            #     dop.append(group_skills[rel['destination_node_id']])
            #     print(dop)
            # else:
            #   print(rel['source_node_id'], rel['destination_node_id'])
              for rel2 in data_json['relations']:
                if (rel2['destination_node_id'] == rel['destination_node_id'] and rel2['name'] == 'формирует'):
                  d = (rel2['source_node_id'], nodes[rel2['source_node_id']]['name'])
                  if not(d in dop):
                    dop.append(d)
                    if (nodes[rel2['source_node_id']]['id'] in track_elec):
                      fl = True
                  break
      if (fl):

        end.append((nodes[elec]['id'], nodes[elec]['name'], (true_rel/count_rel), dop))
      else:
        itog_elec.append((nodes[elec]['id'], nodes[elec]['name'], int((true_rel/count_rel) * 100), dop))
    
    for i, elem in enumerate(end):
       for id in elem[3]:
          if (id[0] in track_elec):
             for i_el in itog_elec:
                if (id[0] == i_el[0]):
                  itog_elec.append((elem[0], elem[1], int(elem[2]*i_el[2]), elem[3]))
                
    return itog_elec
    
    

    


def rank_of_electives(selected_group, selected_job):
    normalize_knowledge = []
    for one_skill in knowledge:
        normalize_knowledge.append(normalize_text(one_skill, my_stopwords))
    #print(normalize_knowledge)

    job = ''
    jobs = Jobs.objects.all()
    for i in jobs:
       if (i.job_name == selected_job):
        job = api_job(i.job_id)
        break


    # if (selected_job == 'Аналитик'):
    #    job = api_job('10')
    # elif (selected_job == 'Тестировщик'):
    #    job = api_job('124')

    normal_job = normalize_text(job, my_stopwords)
    requirements = {key: value for key, value in normal_job.items() if value > 1}
    rank = compatibility(normalize_knowledge, requirements)
    rank_with_name = {}
    for key, value in rank.items():
       rank_with_name[nodes[key]['name']] = value
    sorted_rank = dict(sorted(rank_with_name.items(), key=lambda x: x[1], reverse=True))
    return sorted_rank



  
  


    