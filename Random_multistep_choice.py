# import json
import random
import numpy as np
from Find_Relations_type import reverse_relations, scene_obj_relation, obj_obj_relation, scene_scene_relation


def total_number_func(story):
    num = 0
    for i in story['structured_rep']:
        num += len(i)
    return num

def random_choice(story, seed=0):
    
    random.seed(seed)
    front_right = random.choice([0,1,1]) # select between left/right and front/behind relations
    # front_right = 0
    # total_number = total_number_func(story)
    # if total_number < 5: return -1
    
    # Choose how many block we should consider.
    weighted_random = [1] * 5 + [2] * 9 + [3] * 6
    # Choose scenes and their relations (Randomly) 
    num_scenes = random.choice(weighted_random)

    all_objects = {}
    for i in range(num_scenes): 
        all_objects[str(i)] = {}
    #Assign relations between blocks
    rels_scenes = scene_scene_relation(story, num_scenes=num_scenes, seed=seed, right_front= front_right ) if num_scenes > 1 else []

    
    objects_in_scenes = {}
    #compute the relation between each object and its scene
    for i in range(num_scenes):  
        each_objects_in_scene = {}    
        num_obj = len(story['structured_rep'][i])
        for j in range(num_obj):
            #new version of story generation
            # all_objects[str(i)+'x'+str(j)] = {"color": color(story['structured_rep'][i][j]["color"]), "size": size(story['structured_rep'][i][j]["size"]) , "type": shape(story['structured_rep'][i][j]["type"]), "number": None}
            #old version of story generation
            all_objects[str(i)+'x'+str(j)] = story['structured_rep'][i][j]
            rels, reverse_rels = scene_obj_relation(story, i, j, seed= seed)
            each_objects_in_scene[(str(i), str(i)+'x'+str(j))] = rels
            each_objects_in_scene[(str(i)+'x'+str(j), str(i))] = reverse_rels  
        objects_in_scenes[i]= each_objects_in_scene


    #Compute relation between objects
    total_num_of_objs = 0
    objects_relations = {}

    for scene in range(num_scenes):
        num_objs = len(story['structured_rep'][scene])

        objs_relations = {}
        for i in range(num_objs):
            for j in [x for x in range(num_objs) if x != i]:
                obj_rel = obj_obj_relation(story['structured_rep'][scene], i, j, seed=seed, front_right = front_right)
                if obj_rel:
                    objs_relations[(str(scene)+'x'+str(i),str(scene)+'x'+str(j))] = obj_rel
        objects_relations[scene] = objs_relations



    return [rels_scenes, objects_in_scenes, objects_relations, all_objects]
            


def choose_between_rels(num, rels):
    
    rels_copy = rels
    num_of_rels = 0
    random_choose = []
    
    while num_of_rels < num:
        sample = rels_copy.pop(random.choice(range(len(rels_copy))))

        choosed_rels = random.sample(sample[1], random.choice(range(len(sample[1])))+1)
        if 'touching' in sample[1] and 'touching' not in choosed_rels: choosed_rels+=['touching']
        if choosed_rels:
            random_choose += [[sample[0], choosed_rels]]

            num_of_rels+= len(choosed_rels)
    return random_choose

def color(x):
    global clr
    if x == '#0099ff': x = 'blue'
    else: x = x.lower()
    clr = {'color': x}
    return x

def size(x):
    global sz
    z = ''
    i = x
    if type(i) == str : i = int(i)
    if i == 10: z= 'small'
    elif i == 20: z= 'medium'
    elif i == 30: z= 'big'
    else: z= 'unknown'
    sz = {'size': z}
    return z    

def shape(x):
    global sh
    x = x.lower()
    sh = {'type': x}
    return x