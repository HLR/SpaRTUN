from glob import glob
import random
import re
from Creating_story_v2 import edit_text_form, choose_identifier, select_vocab, check_verb, defined_obj_create_name, generate_relation, prepositions_relations, start_word, verb_relations, num_to_word
from Vocabulary import vocabulary, relation_vocabulary
from Generate_graph import prolog, find_all_relations_exists_between_args , prolog_retract_all_facts, convert_relations_prolog, relation_formalism


story_f,scn_scn,obj_attr,obj_obj,_num_scenes = '',[] ,[],[] ,-1
step_reasoning, step_r = 2, 0
pre_question_forbiden = []
steps_of_reasoning = 0
annotations = []
treshhold, max_tresh, min_tresh = 0, 2, 2
trajector, landmark, spatial_ind, _traj_or_land, _phrase = [], [], [], '',[]
traj, land, sp_ind, sp_type, land_obj_id, traj_obj_id = [], [], [], [], [], []
global retract_rel

story_triplets, query, all_objects_data, query_key = [],[],[], []

def creating_questions(_query_key, _query_triplet ,_story_triplets, _all_objects_data, q_type, _vocab_selection, _relation_vocab_selection ,):
    
    global story_f, scn_scn, obj_attr, obj_obj, _num_scenes,treshhold, max_tresh, min_tresh,step_reasoning, step_r, pre_question_forbiden, annotations, trajector, landmark, spatial_ind, main, _traj_or_land
    global story_triplets, query, all_objects_data, query_key
    global traj, land, sp_ind, sp_type, land_obj_id, traj_obj_id 
    story_triplets, query, all_objects_data, query_key = _story_triplets, _query_triplet, _all_objects_data , _query_key
    traj, land, sp_ind, sp_type, land_obj_id, traj_obj_id = [], [], [], [], [], []
    # story_f,scn_scn,obj_attr,obj_obj,_num_scenes = '',[] ,[],[] ,-1
    # step_reasoning, step_r = 2, 0
    # steps_of_reasoning = 0
    # treshhold, max_tresh, min_tresh = 0, 2, 2
    # question, answer, start_end_c, candidate_answer, consistency, contrast, annotations, reasoning_type, indifinite = '', '',[],[] ,[], [],[], '', False
    
    # story_f = final_story
    # scn_scn = scn_scn1
    # obj_attr = obj_attr1
    # obj_obj = obj_obj1
    # _num_scenes = num_scenes
    # pre_question_forbiden = forbiden_from_pre_Q

    add_story_triplets()

    q_func_name = q_type+'_create_question'
    x, x_tresh = 0, 20
        
    annotations =[] # , trajector, landmark, spatial_ind, main, _traj_or_land= [], [], [], [], [], []
    try: 
        _temp = globals()[q_func_name]()
        if _temp == -1: return None
        else: question, answer = _temp #, start_end_c, candidate_answer, consistency, contrast, reasoning_type, indifinite = _temp
    except:
        raise
        pass
        
    
    question = edit_text_form(question)

    prolog_retract_all_facts(retract_rel, prolog)
#     print(annotations)
    return [question, answer, annotations] #, start_end_c, candidate_answer, consistency, contrast, annotations, reasoning_type, indifinite, pre_question_forbiden]


temporary_objs, first_temp = [], 1

    
#**************************************
#***********Question part**************
#**************************************
def YN_create_question():

    """
        question can be with does or is/are
        we need two obejcts description with a relation text
        the relation_type is provided we need to generate the relation text
        The object id's are provided we need to generate a mention for that.
            - general mentions
            - unique mentions
            - some part of the features and then compute the whole answer for all similar objects
            - we need a function to find all similar objects
            - we need to import the prolog reasoner here too. 

            TODO: have consistancy and contrast. 

    """

    global traj, land, sp_ind, sp_type, land_obj_id, traj_obj_id
    
    sen1, answer1 = '', ''

    #each obj_description can have "the" , "a/any", "all"
    obj1_select = random.choice(["the","a/any", "all"]) 
    obj2_select = random.choice(["the","a/any", "all"])

    #obj1 and its similars
    obj1_def, obj1_sim_objects, changed_select = describe_object_for_YN(obj1_select, query_key[0])
    if changed_select: obj1_select = changed_select
    #obj2 and its similars
    obj2_def, obj2_sim_objects, changed_select = describe_object_for_YN(obj2_select, query_key[1])
    if changed_select: obj2_select = changed_select
    

    # obj1_def = all_objects_data[query_key[0]]["full_name"]
    # obj2_def = all_objects_data[query_key[1]]["full_name"]
    asked_in_query = query["asked_relation"] if type(query["asked_relation"]) == str else query["asked_relation"][0]
    asked_relation = check_verb(select_vocab("relation_in_text", key= asked_in_query.upper()), is_singular= False)


    sp_ind += [[asked_relation]]
    sp_type += [[asked_in_query.upper()]]
    traj += [[obj1_def]]
    
    land += [[obj2_def]]
    
    sen1 += start_word(select_verb(obj1_select, asked_in_query))+" "+obj1_def+" "+asked_relation+" "+obj2_def+"?"


    ####finding answer
    #### check answer for obj1, and obj2 and all of their similar objects
    _obj1_sim_objects = [query_key[0]] + obj1_sim_objects
    _obj2_sim_objects = [query_key[1]] + obj2_sim_objects

    traj_obj_id += [_obj1_sim_objects]
    land_obj_id += [_obj2_sim_objects]
    #We are using CWA so if the answer not find it is False 
    """
        If all - all : check all relation and get True from all
        If all/the - any/a or any/a - all/the
        If the - the : like all - all
        If the - any/a, any/ 
    """
    _answer = True
    
    if obj1_select in ["all", "the"] and obj2_select in ["all", "the"]:
        if all(asked_in_query.lower() in find_all_relations_exists_between_args(obj1, obj2, prolog) for obj1 in _obj1_sim_objects for obj2 in _obj2_sim_objects):
            _answer = ['Yes']
        else: _answer = ['No']
            
    elif obj1_select in ["a/any"] and obj2_select in ["a/any"]:
        if any(asked_in_query.lower() in find_all_relations_exists_between_args(obj1, obj2, prolog) for obj1 in _obj1_sim_objects for obj2 in _obj2_sim_objects):
            _answer = ['Yes']
        else: _answer = ['No']
        
    elif obj1_select in ["all","the"]:
        if all( any(asked_in_query.lower() in find_all_relations_exists_between_args(obj1, obj2, prolog) for obj2 in _obj2_sim_objects ) for obj1 in _obj1_sim_objects ):
            _answer = ["Yes"]
        else:
            _answer = ["No"]
        
    else: # obj2_select is in ["all", "the"]
        if any( all(asked_in_query.lower() in find_all_relations_exists_between_args(obj1, obj2, prolog) for obj2 in _obj2_sim_objects ) for obj1 in _obj1_sim_objects ):
            _answer = ["Yes"]
        else:
            _answer = ["No"]

            
    answer1 = _answer
    create_annotation(sen1)
    return sen1, answer1

def FR_create_question():

    global traj, land, sp_ind, sp_type, land_obj_id, traj_obj_id
    #describe obj1
    obj1_desc, selected_features = predifined_description_of_objects(query_key[0])
    obj1_sim_objects = find_similar_objects_based_on_description(query_key[0], selected_features)
    if obj1_sim_objects and query_key[1] == query_key[0][0]:
        return "", ""
    elif obj1_sim_objects:
        #if there is any similar objects we add the name of block
        _block = predifined_description_of_objects(query_key[0][0])[0]
        obj1_def = choose_identifier(query_key[0], text = obj1_desc)+obj1_desc+" in "+_block
        
        traj += [[choose_identifier(query_key[0], text = obj1_desc)+obj1_desc]]
        land += [[_block]]
        sp_ind += [["in"]]
        sp_type += [["NTPP"]]
        traj_obj_id += [[query_key[0]]]
        land_obj_id += [[query_key[0][0]]]

    else: # if there isn't any similar object
        obj1_def = choose_identifier(query_key[0], text = obj1_desc)+obj1_desc
    
    #describe obj2
    obj2_desc, selected_features = predifined_description_of_objects(query_key[1])
    obj2_sim_objects = find_similar_objects_based_on_description(query_key[1], selected_features)
    if obj2_sim_objects and query_key[0] == query_key[1][0]:
        traj, land, sp_ind, sp_type, land_obj_id, traj_obj_id = [], [], [], [], [], []
        return '',''
    elif obj2_sim_objects:
        _block = predifined_description_of_objects(query_key[1][0])[0]
        obj2_def = choose_identifier(query_key[1], text = obj2_desc)+obj2_desc+" in "+_block
        
        traj += [[choose_identifier(query_key[1], text = obj2_desc)+obj2_desc]]
        land += [[_block]]
        sp_ind += [["in"]]
        sp_type += [["NTPP"]]
        traj_obj_id += [[query_key[1]]]
        land_obj_id += [[query_key[1][0]]]
    else:
        obj2_def = choose_identifier(query_key[1], text = obj2_desc)+obj2_desc
    
    # if obj1_desc== obj2_desc:
    #     obj1_desc

    sen1 = ''

    # if random.choice([0,1, 3]):
    #     sen1 += "What are the relations between "+obj1_def+" and "+obj2_def+"?"
    # else:
    #     sen1 += "Where is "+obj1_def+(" regarding " if random.choice([0,1]) else " relative to ")+ obj2_def+"?"

    m = random.choice([0,1, 3])
    if m == 2:
        sen1 += "What are the relations between "+obj1_def+" and "+obj2_def+"?"
        sp_ind += [["What are the relations"]]
    elif m == 1:
        sen1 += "What is the position of "+obj1_def+(" regarding " if random.choice([0,1]) else " relative to ")+ obj2_def+"?"
        sp_ind += [["What is the position of"]]
    else:
        sen1 += "Where is "+obj1_def+(" regarding " if random.choice([0,1]) else " relative to ")+ obj2_def+"?"
        sp_ind += [["Where is"]]
    
    
    sp_type += [["Nan"]]
    traj += [[choose_identifier(query_key[0], text = obj1_desc)+obj1_desc]]
    traj_obj_id += [[query_key[0]]]
    land += [[choose_identifier(query_key[1], text = obj2_desc)+obj2_desc]]
    land_obj_id += [[query_key[1]]]
    
    answer1 = [rel.upper() for rel in query["all_relations"]]

    create_annotation(sen1)
    return sen1, answer1

def describe_object_for_YN(quantifier, obj_id):

    change_select = None
    if quantifier == "the" :
        obj_desc, selected_features = predifined_description_of_objects(obj_id)
        obj_sim_objects = find_similar_objects_based_on_description(obj_id, selected_features)
        if len(obj_sim_objects) > 0: 
            change_select = "a/any"
            _identifier = "a" if obj_desc[0] not in ['a', 'e', 'i', 'o', 'u'] else "an"
        obj_def = choose_identifier(query_key[1], text = obj_desc)+obj_desc if change_select == None else _identifier+" " +obj_desc

    else:
        h = random.choice([0,1,1,1]) if len(obj_id) != 1 else 1
        if h:
            random_select = True
            general_desc = False
        else:
            random_select = False
            general_desc = True
        obj_desc, selected_features = predifined_description_of_objects(obj_id, use_general = general_desc, random_feature = random_select, unique= False)
        obj_sim_objects = find_similar_objects_based_on_description(obj_id, selected_features)
        if quantifier == "all":
            obj_def = "all "+obj_desc+"s"
        else:
            _identifier = "a" if obj_desc[0] not in ['a', 'e', 'i', 'o', 'u'] else "an"
            obj_def = random.choice([_identifier, "any"])+" "+obj_desc
    
    return obj_def, obj_sim_objects, change_select

def select_verb(obj1_select, asked_relation_type):

    if asked_relation_type.upper() in prepositions_relations: # we add is/are
        return check_verb('[is/are]', is_singular= False if obj1_select == "all" else True )
    else: #relation is verb
        return check_verb('[does/do]', is_singular= False if obj1_select == "all" else True )

def find_similar_objects_based_on_description(obj_id, selected_features):
    
    similar_objects = []

    if selected_features == []:
        for obj in all_objects_data:
            if obj != obj_id:
                if (len(obj_id) == 1 and len(obj) == 1) or (len(obj_id) != 1 and len(obj) != 1): #block
                    similar_objects += [obj]
        return similar_objects

    for obj in all_objects_data:
        if obj != obj_id:
            found = True
            for feature in selected_features:
                if feature not in all_objects_data[obj] :
                    found = False
                    break

                elif all_objects_data[obj][feature] != all_objects_data[obj_id][feature]:
                    found = False
                    break
            if found and obj not in similar_objects: similar_objects += [obj]

    return similar_objects


def predifined_description_of_objects(obj_id, no_nesting = True, use_general = False, unique = True, random_feature = False):

    """
        We can describe a pre-defined objects in several ways:
        unique name:
            1) With full name
            2) With unique feature
        
        general name:
            3) maybe unique maybe not
        
        shared features:
            4) use random features not in unique 
        choose_identifier(text = None,another = False, use_general = False)

        TODO nesting?
        With relation to another object but it should be unique. (also add the annotation)

    """
    obj_description = ""
    rel_annotation = {}
    unique_described_relation = find_unique_described_relation(obj_id) if not no_nesting else []

    if unique_described_relation != [] and not no_nesting: x = 0
    elif unique: x = random.choice([1, 1,2])  if all_objects_data[obj_id]["unique_features"] else 2
    elif random_feature:  x = 4
    else: x = 3 # general
    selected_features = []

    if x == 4:
        all_features = [feature for feature in  all_objects_data[obj_id] if feature not in ["general_name", "full_name", "similar_objects", "unique_features", "name", "number"] and feature not in all_objects_data[obj_id]["unique_features"]]
        random_features = random.sample(all_features, random.choice(range(len(all_features)+1)))
        obj_description = defined_obj_create_name(obj_id,  all_objects_data, list_of_features= random_features)
        rel_annotation["traj"] = obj_description
        selected_features = random_features

    elif x == 3: #use general name
        obj_description = all_objects_data[obj_id]["general_name"]
        rel_annotation["traj"] = obj_description
        selected_features = [feature for feature in  all_objects_data[obj_id] if feature not in ["general_name", "full_name", "similar_objects", "unique_features", "number"]]
    
    elif x == 2: #use full_name
        obj_description = all_objects_data[obj_id]["full_name"]
        rel_annotation["traj"] = obj_description
        selected_features = [feature for feature in  all_objects_data[obj_id] if feature not in ["general_name", "full_name", "similar_objects", "unique_features"]]
    
    elif x == 1: #use unique name
        feature = random.choice(all_objects_data[obj_id]["unique_features"])
        # unique_feature = select_vocab(feature, key = all_objects_data[obj_id][feature])
        list_of_features = [feature]
        obj_description = defined_obj_create_name(obj_id,  all_objects_data, list_of_features= list_of_features)
        # obj_description = unique_feature+ (" " + select_vocab("object_general_name") if feature != "type" else "")
        rel_annotation["traj"] = obj_description
        selected_features = feature

    # else: # use obj_obj rels
    #     selected_relation = random.choice(unique_described_relation)
    #     G_name = select_vocab("object_general_name")
    #     traj_description =  G_name
    #     relation_text, _sp_ind, need_verb = generate_relation(selected_relation[1], return_spatial_indicator = True, return_if_need_verb = True)
    #     land_description, _ = predifined_description_of_objects(selected_relation[0][1], no_nesting = True)
    #     obj_description = (
    #         traj_description
    #         +" "
    #         +wh_th()
    #         +" "
    #         +(check_verb("[was/were]", is_singular=True)+" " if need_verb else " ")
    #         + check_verb(relation_text)
    #         + " "
    #         +land_description
    #         )
    #     rel_annotation["traj"] = traj_description
    #     rel_annotation["land"] = land_description
    #     rel_annotation["sp_ind"] = check_verb(_sp_ind)
    #     rel_annotation["land_id"] = selected_relation[0][1]
    #     rel_annotation["sp_type"] = selected_relation[1][0]["relation_type"]

        selected_features = []
            
    return obj_description, selected_features #, rel_annotation

def find_unique_described_relation(obj_id):

    possible_options = [] #((key), rel)
    for key in story_triplets:
        if obj_id == key[0] and (len(key[0]) != 1 and len(key[1])!= 1): #don't consider relation with blocks
            for rel in story_triplets[key]:
                # if cannot find any other key that the land are similar and the relation are similar we can choose this.
                if not any(_key[1] == key[1] and  rel in story_triplets[_key]  for _key in story_triplets if _key != key):
                    possible_options += [(key, [rel])]
    return possible_options

def add_story_triplets():

    global retract_rel
    retract_rel = []
    # assertz all facts
    for key in story_triplets:
        for rel in story_triplets[key]:
            relation_prolog= convert_relations_prolog[rel["relation_type"].lower()]
            f = f"{relation_prolog}('{key[0]}','{key[1]}')" #relation_prolog+'("'+key[0]+'","'+key[1]+'")'
            prolog.assertz(f)
            retract_rel += [relation_prolog]

# def find_answer(obj1, obj2):

#     '''
#         1) Pass all stories triplet as fact and save the retract_rel.
#         2) Ask each query with the target answer to see if it is true or not.
#         3) Select asked_relation in a way that we have balance data based on the total number of positive and negative variable

#     '''
#     retract_rel = []
#     # assertz all facts
#     for key in story_triplets:
#         for rel in story_triplets[key]:
#             relation_prolog= convert_relations_prolog[rel["relation_type"].lower()]
#             f = relation_prolog+'("'+key[0]+'","'+key[1]+'")'
#             prolog.assertz(f)
#             retract_rel += [relation_prolog]
    
#     #find valid relations between obj1 and obj2
#     # key = query_key
#     all_correct_rels = 
#     #retract_asserted_facts
#     prolog_retract_all_facts(retract_rel)
       
    
    
#     return all_correct_rels

    
#**************************************
#*********Consistency part*************
#**************************************

def consistency_check(q_type, q_data, obj_data):
   
    consistency_list = [] # list of consistency questions and answers
    
    FR, FO, CO, YN = False, False, False, False
    if q_type == "FR": FO= True; CO= True; YN= True
    elif q_type == "FO": FR= True; CO= True; YN= True
    elif q_type == "CO": FO= True; FR= True; YN= True
    elif q_type == "YN": FO= True; CO= True; FR= True

    if FR: # create FR based on the object that are passed
        if q_type == "YN":
            if q_data["obj1_uniq"] and q_data["obj2_uniq"]: # FR can only accept unique object definition

                answer = ''
                if q_data["answer"] == ['Yes']: answer = q_data["relation"]
                elif q_data["answer"] == ['No']: answer = reverse(q_data["relation"])
                else: answer = 'DK' 
                consistency_list += FR_consis(q_data["obj1_def"], q_data["obj2_def"],answer)
                consistency_list[-1].append("FR")
        elif q_type == "CO":
            if q_data["answer"] == 0 and q_data["obj_uniq"] and q_data["obj1_uniq"]:
                answer = q_data["relation"]
                consistency_list += FR_consis(q_data["obj1_def"], q_data["obj_def"],answer)
                consistency_list[-1].append("FR")
            elif q_data["answer"] == 1 and q_data["obj_uniq"] and q_data["obj2_uniq"]:   
                answer = q_data["relation"]
                consistency_list += FR_consis(q_data["obj2_def"], q_data["obj_def"],answer)
                consistency_list[-1].append("FR")
            elif q_data["answer"] == 2 and q_data["obj_uniq"] and q_data["obj2_uniq"] and q_data["obj1_uniq"]:
                answer = q_data["relation"]
                consistency_list += FR_consis(q_data["obj1_def"], q_data["obj_def"],answer)
                consistency_list[-1].append("FR")
                consistency_list += FR_consis(q_data["obj2_def"], q_data["obj_def"],answer)
                consistency_list[-1].append("FR")
        else: # q_type == "FO"
            answer = q_data["relation"]
            if q_data["obj2_uniq"]:
                obj1_list = random.sample(q_data["obj1_def"], 3) if len(q_data["obj1_def"])>3 else q_data["obj1_def"]
                for obj in obj1_list:
                    consistency_list += FR_consis([obj], q_data["obj2_def"],answer)
                    consistency_list[-1].append("FR")
                
        
    if YN:
        if q_type == "FR":
            answer = 'Yes' if "DK" not in q_data["relation"] else 'DK'
            consistency_list += YN_consis(q_data["obj1_def"], q_data["obj1_uniq"], q_data["obj2_def"], q_data["obj2_uniq"],q_data["relation"], answer)
            consistency_list[-1].append("YN")
        elif q_type == "CO":
            answer = ['No','No']
            if q_data["answer"] == 0: answer[0] = 'Yes'
            elif q_data["answer"] == 1: answer[1] = 'Yes'
            elif q_data["answer"] == 2: answer = ['Yes','Yes']
            consistency_list += YN_consis(q_data["obj1_def"], q_data["obj1_uniq"], q_data["obj_def"], q_data["obj_uniq"],q_data["relation"], answer[0])
            consistency_list[-1].append("YN")
            consistency_list += YN_consis(q_data["obj2_def"], q_data["obj2_uniq"], q_data["obj_def"], q_data["obj_uniq"],q_data["relation"], answer[1])
            consistency_list[-1].append("YN")
        else: 
            
            if q_data["obj1_def"] != ['None']:
                obj1_list = random.sample(q_data["obj1_def"], 3) if len(q_data["obj1_def"])>3 else q_data["obj1_def"]
                for obj in obj1_list:
                    consistency_list += YN_consis([obj], q_data["obj1_uniq"], q_data["obj2_def"], q_data["obj2_uniq"],q_data["relation"], 'Yes')
                    consistency_list[-1].append("YN")
    if CO:
        if q_type == "FR":
            if "DK" not in q_data["relation"]:
                try:
                    consistency_list += CO_consis(q_data["obj1_def"], q_data["obj1_uniq"], q_data["obj2_def"], q_data["obj2_uniq"],q_data["relation"], obj_data["obj1"], obj_data["scn1"],obj_data["obj2"], obj_data["scn2"], obj_data["obj2s_temp"])
                    consistency_list[-1].append("CO")
                except:
                    raise
                    pass
        
        elif q_type == "YN":
            if q_data["obj1_uniq"] and q_data["obj2_uniq"] and q_data["answer"] == ["Yes"]: 
                try:
                    consistency_list += CO_consis(q_data["obj1_def"], q_data["obj1_uniq"], q_data["obj2_def"], q_data["obj2_uniq"],q_data["relation"], obj_data["obj1"], obj_data["scn1"],obj_data["obj2"], obj_data["scn2"], obj_data["obj2s_temp"])
                    consistency_list[-1].append("CO")
                except:
                    raise
                    pass
        
        elif q_type == "FO":
            if q_data["obj1_def"] != ['None']: 
                try:
                    obj = random.choice(q_data["obj1_def"])
                    consistency_list += CO_consis([obj], q_data["obj1_uniq"], q_data["obj2_def"], q_data["obj2_uniq"],q_data["relation"], -1, -1, obj_data["obj"], obj_data["scn"], obj_data["objs_temp"])
                    consistency_list[-1].append("CO")
                except:
                    raise
                    pass
 
    return consistency_list    

def YN_consis(obj1_def, obj1_uniq, obj2_def, obj2_uniq, rel, ans):
    
    sen, relation = '',''
    answer = [ans]
    
    if rel != "DK": relation = rel
    else: relation = random.choice(['left','right','above','below','near to', 'far from', 'touching'])
    obj1_defined = obj1_def
    obj1s_uniq = obj1_uniq
    obj2_defined = obj2_def
    obj2s_uniq = obj2_uniq
        
    if obj1s_uniq and obj2s_uniq: # when the objects are unique by their definition
        z = random.choice([0,1])
        if z: sen += 'Is the '+obj1_defined[0]+' '+R(relation)+' the '+obj2_defined[0]+'?'
        else: sen += 'Is there a '+obj1_defined[0]+' '+R(relation)+' a '+obj2_defined[0]+'?'
    elif obj1s_uniq or obj2s_uniq: 
        if obj1s_uniq: 
            z = random.choice([0,1])
            if z == 1: sen += 'Is the '+obj1_defined[0]+' '+R(relation)+' a '+obj2_defined[0]+'?'
            else: sen += 'Is the '+obj1_defined[0]+' '+R(relation)+'  any '+ make_plural(obj2_defined[0])+'?'
        else:
            z = random.choice([0,1])
            if z == 1: sen += 'Is there a '+obj1_defined[0]+' '+R(relation)+' the '+obj2_defined[0]+'?'
            else: sen += 'Is there any '+make_plural(obj1_defined[0])+' '+R(relation)+' the '+obj2_defined[0]+'?'
    else: 
        sen += 'Is there any '+make_plural(obj1_defined[0])+' '+R(relation)+' a '+obj2_defined[0]+'?'
    
    sen = edit_text_form(sen)
    return [[sen, answer, [], []]]
    
def CO_consis(obj1_def, obj1_uniq, obj2_def, obj2_uniq,rel, _obj1, _scn1,_obj2, _scn2, _obj2s_temp):
    
    global treshhold, temporary_objs, min_tresh, max_tresh, first_temp
    sen, answer = '',''
    start_end_c, candidate_answer = [], []
    obj, scn, objs_temp = _obj2, _scn2, _obj2s_temp
    obj1, scn1 = '','' 
    if _obj1 != -1: obj1 = _obj1; scn1 = _scn1 
    unique_obj = False #if we have a unique obj then we can ask question in two form. what is below the ob? which obj is below a obj? 
    unique_obj1_2 = False
    x = -1 #  0 for what is below the obj? 1 for which obj is below a obj? 
    relation = rel
    #defining object in the question
    obj_defined = obj2_def
    obj_unique = unique_obj = obj2_uniq
    obj1_defined = obj1_def
    obj1_unique = obj1_uniq
    x, x_tresh = 0, 10
    while 1:
        obj2, scn2 = one_obj_restricted(obj, scn,obj1, scn1)
        rel = FR_correct(obj, scn, obj2, scn2)
        if relation not in rel: break
        x+=1
        if x > x_tresh: return -1
    
    forbiden_list = []
    if scn == scn2: forbiden_list.append(obj)
    if scn1 == scn2: forbiden_list.append(obj1)
    max_tresh = 1
    min_treshhold = 1  
    obj2_defined = obj_def_q(obj2, scn2, forbiden_list=forbiden_list, min_treshhold = min_treshhold)
    treshhold = 0
    obj2s_temp = temporary_objs
    temporary_objs, first_temp = [], 1
    
    obj2_unique = True if len(obj2s_temp) == 1 else False
    
    if obj1_unique and obj2_unique:
        unique_obj1_2 = True
        x = random.choice([0,1]) if unique_obj else 1
    elif unique_obj: x = 0
    else: return -1
            
    max_tresh = 2
    if x == 1:
        sen += 'Which object is '+ R(relation)+' a '+obj_defined[0] +'? '
        if random.choice([0,1]):
            sen += 'the '+obj1_defined[0]+' or the '+obj2_defined+'?'  
            candidate_answer = [obj1_defined[0], obj2_defined, "both of them", "none of them"]
            answer = [0]
        else:
            sen += 'the '+obj2_defined+' or the '+obj1_defined[0]+'?'
            candidate_answer = [obj2_defined, obj1_defined[0], "both of them", "none of them"]
            answer = [1]
    else:
        sen += 'What is '+ R(relation)+' the '+obj_defined[0] +'? '
        if random.choice([0,1]):
            sen += 'a '+obj1_defined[0]+' or a '+obj2_defined+'?'  
            candidate_answer = [obj1_defined[0], obj2_defined, "both of them", "none of them"]
            answer = [0]
        else:
            sen += 'a '+obj2_defined+' or a '+obj1_defined[0]+'?'
            candidate_answer = [obj2_defined, obj1_defined[0], "both of them", "none of them"]
            answer = [1]
    
    sen = edit_text_form(sen)    
    return [[sen, answer, start_end_c, candidate_answer]]

def FO_consis(obj2_def, obj1_def, rel, obj2, scn2, obj2s_temp):
    global treshhold, temporary_objs, min_tresh, first_temp
    sen, answer = '',''
    obj, scn = obj2, scn2
    relation = rel
    obj_defined = obj2_def[0]
    objs_temp = obj2s_temp

    
    sen += 'Which object is/objects are '+R(relation)+' a '+obj_defined+'?'
    answer, start_end_c = answer_FO(obj,scn,objs_temp, relation)
    sen = edit_text_form(sen)
    return [[sen, answer, start_end_c, '']]
    

def FR_consis(obj1_def, obj2_def, ans):
    
    sen, answer = '',''
    
    obj1_defined = obj1_def
    obj2_defined = obj2_def

    sen += 'What is the relation between the '+obj1_defined[0]+' and the '+obj2_defined[0]+'?'
    
    candidate_answer = ["left", "right", "above", "below", "near to", "far from", "touching", "DK"]
    answer = [candidate_answer.index(ans)]
    sen = edit_text_form(sen)
    return [[sen, answer, [], candidate_answer]]




#**********************************************************
#******************Annotation functions********************
#**********************************************************


def create_annotation(sen):
    
    global annotations, land, traj, sp_ind, traj_obj_id, land_obj_id, sp_type
    # land, traj, sp_ind, sp_type = [], [], [], []
    # traj_obj_id, land_obj_id = [], []
    # return
    # TODO add spatial value passed by triplet
    #     print('sentence: ', sen)
    #     print('trajector:', traj, '\n Lnadmark', land,'\nSp-ind', sp_ind)
    #     print('traj id: ', traj_obj_id)
    #     print('land id: ', land_obj_id)
    # check_edge_exist()
    if traj == [[]]:
        print("!!! ERROR empty traj", sen)
    if land == [[]]:
        print("!!! ERROR empty land", sen)
    if sp_ind == [[]]:
        print("!!! ERROR empty sp_ind", sen)

    sen = edit_text_form(sen)
    if sen[-1] != ".":
        sen += ". "

    
    ann = {"main_description": -1 ,"spatial_description" : []}

    for ind in range(len(traj)):

        # trajector
        for tr_ind, tr in enumerate(traj[ind]):

            trajector = {
                "entity_id": traj_obj_id[ind],
                "phrase": "",
                "head": "",
                "properties": {},
                "spatial_property": "",
                "SOT_text": {"start": "", "end": ""},
                "SOT_sentence": {"start": "", "end": ""},
            }
            _traj = edit_text_form(tr)
            trajector["phrase"] = _traj
            (
                trajector["head"],
                trajector["properties"],
                trajector["spatial_property"],
            ) = extract_properties(traj_obj_id[ind], _traj)

            # landmark
            for ld_ind, ld in enumerate(land[ind]):
                landmark = {
                    "entity_id": land_obj_id[ind],
                    # "block_id": 100 + block_id
                    # if land_obj_id[ind][ld_ind] not in [100, 101, 102]
                    # else land_obj_id[ind][ld_ind],
                    "phrase": "",
                    "head": "",
                    "properties": [],
                    "spatial_property": "",
                    "SOT_text": {"start": "", "end": ""},
                    "SOT_sentence": {"start": "", "end": ""},
                }
                _land = edit_text_form(ld)
                landmark["phrase"] = _land
                (
                    landmark["head"],
                    landmark["properties"],
                    landmark["spatial_property"],
                ) = extract_properties(land_obj_id[ind], _land)

                for sp_ind_id, sp in enumerate(sp_ind[ind]):
                    spatial_ind = {
                        "phrase": "",
                        "SOT_text": {"start": "", "end": ""},
                        "SOT_sentence": {"start": "", "end": ""},
                    }
                    spatial_ind["phrase"] = sp

                    g_type, s_type = spatial_indicator(sp_type[ind][sp_ind_id])

                    # add
                    ann["spatial_description"].append(
                        {
                            "spatial_value": sp_type[ind][sp_ind_id],
                            "g_type": g_type,
                            "s_type": s_type,
                            "negative": False,
                            "FoR": "Relative",
                            "trajector": trajector,
                            "landmark": landmark,
                            "spatial_indicator": spatial_ind,
                        }
                    )

    annotations.append(ann)
    SOT(sen)
    land, traj, sp_ind, sp_type = [], [], [], []
    traj_obj_id, land_obj_id = [], []


def spatial_indicator(sp_type):

    g_type, s_type = "", ""

    # val1 = ["left", "right", "above", "below"]
    # val2 = ["far from", "near to"]
    # val3 = ["touching"]
    # val4 = ["in", "has", "contains", "have", "contain"]  # edge for touching edge

    if sp_type == "Nan":
        g_type = "Nan"
        s_type = "Nan"

    elif relation_formalism[sp_type.lower()] in ["dir", "dir_"]:
        g_type = "Direction"
        s_type = "Relative"

    elif relation_formalism[sp_type.lower()] in ["distance"]:
        g_type = "Distance"
        s_type = "Qualitative"


    elif relation_formalism[sp_type.lower()] in ["rcc8"]:
        g_type = "Region"
        s_type = "RCC8"

    
    return g_type, s_type


def extract_properties(obj_id, obj_desc):

    # obj_desc = obj_desc.copy()
    properties = {"color": "", "size": "", "type": "", "name": "", "number": ""}
    spatial_property = ""
    head = ""

    """
        for color, size, number, name (general and specific) we search the vocabulary in the name 
        if it is found consider it as the property. Remove them from the name and the remaining is head
    """

    if obj_id != ["-1"]:
        _obj_ids = obj_id
        obj_id = obj_id[0]
        #color
        if "color" in all_objects_data[obj_id]:
            _temp = select_vocab("color", key = all_objects_data[obj_id]["color"])
            if _temp in obj_desc:
                properties["color"] = _temp
                obj_desc = obj_desc.replace(_temp, "")
        
        #color
        if "size" in all_objects_data[obj_id]:
            _temp = select_vocab("size", key = all_objects_data[obj_id]["size"])
            if _temp in obj_desc:
                properties["size"] =  _temp
                obj_desc = obj_desc.replace(_temp, "")
        
        # if it is not a group of objects description
        if len(_obj_ids)  == 1:
            #name for blocks
            if "name" in all_objects_data[obj_id]:
                _temp = all_objects_data[obj_id]["name"]
                if _temp in obj_desc:
                    properties["name"] = _temp
                    obj_desc = obj_desc.replace(_temp, "")

            #name as number         
            if "number" in all_objects_data[obj_id]:
                _temp = "number "+num_to_word(all_objects_data[obj_id]["number"])
                if _temp in obj_desc:
                    properties["name"] = _temp
                    obj_desc = obj_desc.replace(_temp, "")
            
            #type
            # should also check the plural situation
            if "type" in all_objects_data[obj_id]: 
                _temp = select_vocab("type", key = all_objects_data[obj_id]["type"]) if len(obj_id)!= 1 else all_objects_data[obj_id]["type"]
                if _temp in obj_desc:
                    properties["type"] =  _temp
                    head = _temp
                    obj_desc = obj_desc.replace(_temp, "")
            
            #number
            for num in ["a", "an", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]:
                if obj_desc.startswith(num+" "):
                    properties["number"] = num
                    obj_desc = obj_desc.replace(num+" ", "")
                    break
            
            if obj_desc.startswith("the "):
                obj_desc = obj_desc.replace("the ","")
            if obj_desc.startswith("another "):
                obj_desc = obj_desc.replace("another ","")

            # check general names
            obj_desc = obj_desc.replace(" ", "")
            if obj_desc and head == "": head = obj_desc

        # if it is describing a group of objects
        else:
            # if is about objects
            if len(obj_id) != 1:
                if "type" in all_objects_data[obj_id]:
                    _temp = select_vocab("types", key = all_objects_data[obj_id]["type"])
                    if _temp in obj_desc:
                        properties["type"] =  _temp
                        head = _temp
                        obj_desc= obj_desc.replace(_temp, "")
                if head == "":
                    for g_name in select_vocab("objects_general_name", return_list=True):
                        if g_name in obj_desc:
                            head = g_name
                            obj_desc= obj_desc.replace(g_name, "")
                            break
            # it is block
            else:
                if "type" in all_objects_data[obj_id]:
                    _temp = select_vocab("blocks")
                    if _temp in obj_desc:
                        properties["type"] =  _temp
                        head = _temp
                        obj_desc= obj_desc.replace(_temp, "")

                if head == "":
                    for g_name in select_vocab("blocks", return_list=True):
                        if g_name in obj_desc:
                            head = g_name
                            obj_desc= obj_desc.replace(g_name, "")
                            break
    #if obj_desc is -1
    # an image, there, empty, 
    else:
        for num in ["a", "an", "one"]:#, "two", "three", "four", "five", "six", "seven", "eight", "nine"]:
            if obj_desc.startswith(num+" "):
                properties["number"] = num
                obj_desc = obj_desc.replace(num, "")
                break
        
        if obj_desc.startswith("the "):
            obj_desc = obj_desc.replace("the ","")
        if obj_desc.startswith("another "):
            obj_desc = obj_desc.replace("another ","")
        
        head = obj_desc
        

    return head, properties, spatial_property


def SOT(sen):

    global annotations, entity_phrases
    sum_char = 0

    # _file = open("repeated_annot.txt", "a+")

    for ann in annotations:
        sum_char = 0#story.find(ann["sentence"])
        if sum_char == -1:
            print("!!! ERROR sum char")
        _annot = sen.lower() #ann["sentence"].lower()
        # _annot = ann["sentence"][0].lower() + ann["sentence"][1:]
        all_double_found = {}
        _temp_ind = {}
        land_cannot_repeat = []
        for ind, sp_desc in enumerate(ann["spatial_description"]):

            # trajector
            traj_phrase = sp_desc["trajector"]["phrase"].lower()
            if traj_phrase not in ["", []] :
                start = [
                    m.start() for m in re.finditer(traj_phrase, _annot)
                ]
                if start == []:
                    print("!!! ERROR traj", _annot, traj_phrase)
                elif len(start) == 1:
                    _start = start[0]
                else:
                    start1 = start
                    # first remove the same found object which is part of another one.
                    for j in start1:
                        if _annot[j - 1] and (
                            _annot[j - 1].isalpha()
                            or _annot[j + len(traj_phrase)].isalpha()
                        ):
                            start.remove(j)
                        if (
                            "lock" not in traj_phrase
                            and _annot[j - 5 : j - 1]
                            and _annot[j - 5 : j - 1] == "lock"
                        ):
                            start.remove(j)  # e.g, remove block C from all C find

                    if len(start) == 1:
                        _start = start[0]
                    else:
                        """
                            if the phrase exists in all_double_found we choose the id after the chose one if not choose the 0 and
                            add it to all_double_found
                        """
                        _start = None
                        if traj_phrase in all_double_found:
                            for j in all_double_found[traj_phrase]:
                                if sp_desc["trajector"]["entity_id"] in all_double_found[traj_phrase][j]:
                                    _start = j
                                    break
                            if _start == None:
                                for i in range(len(start)):
                                    if start[i] not in all_double_found[traj_phrase]:
                                        
                                        all_double_found[traj_phrase][start[i]] = [sp_desc["trajector"]["entity_id"]]

                                        _start = start[i]
                                        break
                        else:
                            all_double_found[traj_phrase] = {start[0]: [sp_desc["trajector"]["entity_id"]]}
                            _start = start[0]
                        # if traj_phrase == "it":
                        #     start = start[0]
                        # else:
                        #     if "another" not in traj_phrase:
                        #         print(
                        #             "ERROR more than one phrase in TRAJ | ",
                        #             traj_phrase,
                        #             " | ",
                        #             _annot,
                        #             " | ",
                        #             sp_desc,
                        #             file = _file
                        #         )
                        #     start = start[0]
                        # print(
                        #             "ERROR more than one phrase in TRAJ | ",
                        #             traj_phrase,
                        #             " | ",
                        #             _annot,
                        #             " | ",
                        #             _start,
                        #             file = _file
                        #         )


                end = _start + len(traj_phrase)  # - 1
            else:
                _start, end, sum_char = -1, -1, 0
            (
                sp_desc["trajector"]["SOT_sentence"]["start"],
                sp_desc["trajector"]["SOT_sentence"]["end"],
            ) = (_start, end)
            (
                sp_desc["trajector"]["SOT_text"]["start"],
                sp_desc["trajector"]["SOT_text"]["end"],
            ) = (_start + sum_char, end + sum_char)

            traj_end = end

            # landmark
            land_phrase = sp_desc["landmark"]["phrase"].lower()
            if land_phrase not in ["", []]:

                start = [
                    m.start() for m in re.finditer(land_phrase, _annot)
                ]
                if start == []:
                    print("!!! ERROR land", _annot, land_phrase)
                elif len(start) == 1:
                    _start = start[0]
                elif _annot[traj_end+1: traj_end+5] in ["that","whic"]:
                    for i in start:
                        if i> traj_end:
                            land_cannot_repeat += [i]
                            _start = i
                else:

                    start1 = start
                    for j in start1:
                        if _annot[j - 1] and (
                            _annot[j - 1].isalpha()
                            or _annot[j + len(land_phrase)].isalpha()
                        ):
                            start.remove(j)
                        if (
                            "lock" not in land_phrase
                            and _annot[j - 5 : j - 1]
                            and _annot[j - 5 : j - 1] == "lock"
                        ):
                            start.remove(j)  # e.g, remove block C from all C find

                    if len(start) == 1:
                        _start = start[0]
                    else:

                        """
                            if the phrase exists in all_double_found we choose the id after the chose one if not choose the 0 and
                            add it to 
                            
                        """

                        _start = None
                        if land_phrase in all_double_found:
                            for j in all_double_found[land_phrase]:
                                if sp_desc["landmark"]["entity_id"] in all_double_found[land_phrase][j] and j not in land_cannot_repeat:
                                    _start = j
                                    break
                            if _start == None:
                                for i in range(len(start)):
                                    if start[i] not in all_double_found[land_phrase]:
                                        
                                        all_double_found[land_phrase][start[i]] = [sp_desc["landmark"]["entity_id"]]
                                        if _annot[traj_end+1: traj_end+5] in ["that","whic"]:
                                            land_cannot_repeat += [start[i]]
                                        _start = start[i]
                                        break
                        else:
                            all_double_found[land_phrase] = {start[0]: [sp_desc["landmark"]["entity_id"]]}
                            if _annot[traj_end+1: traj_end+5] in ["that","whic"]:
                                land_cannot_repeat += [start[i]]
                            _start = start[0]

                        # if land_phrase in all_double_found:
                        #     for i in range(len(start)):
                        #         if start[i] not in all_double_found[land_phrase]:
                        #             all_double_found[land_phrase] += [start[i]]
                        #             _start = start[i]
                        #             break
                        # else:
                        #     all_double_found[land_phrase] = [start[0]]
                        #     _start = start[0]

                        # if land_phrase == "it":
                        #     start = start[-1]
                        # else:
                        #     if "another" not in land_phrase:
                        # print(
                        #     "ERROR more than one phrase in LAND | ",
                        #     land_phrase,
                        #     "|",
                        #     _annot,
                        #     " | ",
                        #     _start,
                        #     file = _file
                        # )
                        #     start = start[0]

                end = _start + len(land_phrase)  # - 1
            else:
                _start, end, sum_char = -1, -1, 0
            (
                sp_desc["landmark"]["SOT_sentence"]["start"],
                sp_desc["landmark"]["SOT_sentence"]["end"],
            ) = (_start, end)
            (
                sp_desc["landmark"]["SOT_text"]["start"],
                sp_desc["landmark"]["SOT_text"]["end"],
            ) = (_start + sum_char, end + sum_char)

            land_end = end

            # spatial_indicator
            sp_ind_phrase = sp_desc["spatial_indicator"]["phrase"].lower()
            start = [
                m.start()
                for m in re.finditer(sp_ind_phrase, _annot)
            ]
            # if len(start) > 1:
            #     if sp_ind_phrase not in _temp_ind:
            #         _temp_ind[sp_ind_phrase] = -1

            if start == []:
                print("!!! ERROR sp")

            elif len(start) == 1:
                _start = start[0]
            elif _annot[traj_end+1: traj_end+5] in ["that","whic"]:
                for j in start:
                    if j > traj_end: 
                        _start = j
            else:

                start2 = start
                for j in start2:
                    if _annot[j - 1] and (
                        _annot[j - 1].isalpha()
                        or _annot[j + len(sp_ind_phrase)].isalpha()
                    ):
                        start.remove(j)

                start2 = start
                # if (
                #     _annot[traj_end + 1 : traj_end + 6] == "which"
                #     or _annot[traj_end + 1 : traj_end + 5] == "that"
                # ):

                for j in start2:
                    if (j < traj_end or j > land_end) and land_end > traj_end:
                        start.remove(j)
                    elif land_end < traj_end and (j > traj_end or j > land_end):
                        start.remove(j)

                if len(start) == 1:
                    _start = start[0]

                if len(start) > 1:
                    
                    if sp_ind_phrase in all_double_found:
                        for i in range(len(start)):
                            if start[i] not in all_double_found[sp_ind_phrase]:
                                all_double_found[sp_ind_phrase] += [start[i]]
                                _start = start[i]
                                break
                    else:
                        all_double_found[sp_ind_phrase] = [start[0]]
                        _start = start[0]


                    # print(
                    #         "ERROR more than one phrase in Spin | ",
                    #         sp_ind_phrase,
                    #         "|",
                    #         _annot,
                    #         " | ",
                    #         _start, 
                    #         " traj: ", traj_end,
                    #         " land: ", land_end,
                    #         file = _file
                    # )
                    # if (
                    #     "which" in _annot or "and" in _annot
                    # ):  # start1 = start[0]
                #         start1 = start[
                #             _temp_ind[sp_ind_phrase]
                #         ]
                #         _temp_ind[sp_ind_phrase] -= 1
                # else:
                #     start1 = start[-1]

            end = _start + len(sp_ind_phrase)  # - 1
            (
                sp_desc["spatial_indicator"]["SOT_sentence"]["start"],
                sp_desc["spatial_indicator"]["SOT_sentence"]["end"],
            ) = (_start, end)
            (
                sp_desc["spatial_indicator"]["SOT_text"]["start"],
                sp_desc["spatial_indicator"]["SOT_text"]["end"],
            ) = (_start + sum_char, end + sum_char)

        # _temp_ind = {}
        all_double_found = {}
        land_cannot_repeat = []
        sum_char = 0


def check_edge_exist():

    global sp_ind, land
    _temp = sp_ind
    for ind, i in enumerate(_temp):
        if "edge" in sp_ind[ind][0]:
            for j in range(len(land[ind])):
                start = sp_ind[ind][j].find("the")
                land[ind][j] = sp_ind[ind][j][start:] + " " + land[ind][j]
                sp_ind[ind][j] = "touching"
