from itertools import permutations
import networkx as nx
from pyswip import *
import random
from Find_Relations_type import reverse_relations

prolog = Prolog()
convert_relations_prolog = {
    "left":"left_"
    , "right":"right_"
    , "above":"above_"
    , "below":"below_"
    , "front":"front_"
    , "behind":"behind_"
    , "near":"near_"
    , "far":"far_"
    , "dc":"dc_"
    , "ec":"ec_"
    , "po":"po_"
    , "tpp":"tpp_"
    , "ntpp":"ntpp_"
    , "tppi":"tppi_"
    , "ntppi":"ntppi_"
    }

relation_formalism = {
    "left":"dir"
    , "right":"dir"
    , "above":"dir"
    , "below":"dir"
    , "behind": "dir_"
    , "front": "dir_"
    , "near":"distance"
    , "far":"distance"
    , "dc":"rcc8"
    , "ec":"rcc8"
    , "po":"rcc8"
    , "tpp":"rcc8"
    , "ntpp":"rcc8"
    , "tppi":"rcc8"
    , "ntppi":"rcc8"
    }

# relation_formalism = {
#     "left":"right", "above", "below"
#     , "right":"left, above, below"
#     , "above":"left, right, below"
#     , "below":"right, left, above"
#     , "near":"far, right, left, above, below, dc, ec"
#     , "far": "near, right, left, above, below, dc, ec"
#     , "dc":"rcc8"
#     , "ec":"rcc8"
#     , "po":"rcc8"
#     , "tpp":"rcc8"
#     , "ntpp":"rcc8"
#     , "tppi":"rcc8"
#     , "ntppi":"rcc8"
#     }


# convert_relations_prolog = {"left":"left_", "right":"right_", "above":"above_", "below":"below_", "front":"front_", "behind":"behind_", "near":"near_", "far":"far_", "dc":"dc_", "ec":"ec_", "po":"po_", "tpp":"tpp_", "ntpp":"ntpp_", "tppi":"tppi_", "ntppi":"ntppi_"}
# askde_rels = {"left":"left_", "right":"right_", "above":"above_", "below":"below_", "near":"near_", "far":"far_", "dc":"dc_", "ec":"ec_", "po":"po_", "tpp":"tpp_", "ntpp":"ntpp_", "tppi":"tppi_", "ntppi":"ntppi_"}
askde_rels = {"left":"left_", "right":"right_", "above":"above_", "below":"below_", "front":"front_", "behind":"behind_", "near":"near_", "far":"far_", "dc":"dc_", "ec":"ec_", "po":"po_", "tpp":"tpp_", "ntpp":"ntpp_", "tppi":"tppi_", "ntppi":"ntppi_"}
positive = 0
negative = 0

def example_path(path):
    import os.path
    x = os.path.normpath(os.path.join(os.path.split(os.path.abspath(__file__))[0],path)).replace("\\", "\\\\")
    # print(x)
    return x

prolog.consult(example_path("prolog/spatial_rules.pl"))

def create_scene_graph(scenes_relations , scene_objects_relations, objects_object_relations, all_objects, num_questions = 2 , seed = 0):

    random.seed(seed)
    #Creating a scene graph of all relation extracted from image
    scene_graph_no_edge_prop = nx.DiGraph()
    scene_graph = nx.MultiDiGraph()

    for tuple in scenes_relations:
        for relation in scenes_relations[tuple]:
            scene_graph.add_edge(str(tuple[0]), str(tuple[1]), relation_type=relation["relation_type"], relation_property = relation["relation_property"])
            scene_graph_no_edge_prop.add_edge(str(tuple[0]), str(tuple[1]))

    for scene in scene_objects_relations:
        for tuple in scene_objects_relations[scene]:
            for relation in scene_objects_relations[scene][tuple]:
                scene_graph.add_edge(str(tuple[0]), str(tuple[1]), relation_type=relation["relation_type"], relation_property = relation["relation_property"])
                scene_graph_no_edge_prop.add_edge(str(tuple[0]), str(tuple[1]))

    for scene in objects_object_relations:
        for tuple in objects_object_relations[scene]:
            for relation in objects_object_relations[scene][tuple]:
                scene_graph.add_edge(str(tuple[0]), str(tuple[1]), relation_type=relation["relation_type"], relation_property = relation["relation_property"])
                scene_graph_no_edge_prop.add_edge(str(tuple[0]), str(tuple[1]))

    random_objects_all_possible_queries = {}
    objs_and_blocks = list(all_objects)
    number_of_pairs = int(num_questions*2) if int(num_questions*3/2) < len(objs_and_blocks)* (len(objs_and_blocks)-1) else len(objs_and_blocks)* (len(objs_and_blocks)-1)
    all_possible_pairs = list(permutations(objs_and_blocks, 2))
    random_pairs = random_pair_selection(all_possible_pairs, number_of_pairs)
    # random_pairs = random.sample(list(permutations(list(all_objects)+[str(x) for x in scene_objects_relations], 2)), number_of_pairs)
   
    for pair in random_pairs:
        random_objects_all_possible_queries[pair] = find_possible_query(scene_graph, pair)
    
    all_pair_relation = make_single_dic(scenes_relations,  scene_objects_relations, objects_object_relations) 

    selected_story_triplets, selected_queries = choose_paths(random_objects_all_possible_queries, num_questions, all_pair_relation, all_objects)
    selected_story_triplets, updated_queries = add_extra_relation(selected_story_triplets, selected_queries,  all_pair_relation, scene_objects_relations)

    #set the answer to each query in away that we have a balance dataset
    #double check the result based on the current story triplets
    queries_triplet = queries_final_check(selected_story_triplets, updated_queries)

    # scen_scen, scene_objs, objs_objs = change_data_format(selected_story_triplets, all_objects)
    
    # print(queries_triplet, '\n\n\n',selected_story_triplets)
    return queries_triplet, selected_story_triplets#, (scen_scen, scene_objs, objs_objs)

# def change_data_format(story_triplets,all_objects):

def queries_final_check(selected_story_triplets, queries):

    '''
        1) Pass all stories triplet as fact and save the retract_rel.
        2) Ask each query with the target answer to see if it is true or not.
        3) Select asked_relation in a way that we have balance data based on the total number of positive and negative variable

    '''
    global positive, negative
    retract_rel = []
    # assertz all facts
    for key in selected_story_triplets:
        for rel in selected_story_triplets[key]:
            relation_prolog= convert_relations_prolog[rel["relation_type"].lower()]
            f = f"{relation_prolog}('{key[0]}','{key[1]}')" #relation_prolog+'("'+key[0]+'","'+key[1]+'")'
            retract_rel += [relation_prolog]
            prolog.assertz(f)
            
    

    #check all queries
    final_queries = {}
    
    for key in queries:
        all_correct_rels = find_all_relations_exists_between_args(key[0],key[1])
        queries[key]["all_relations"] = all_correct_rels

        for r in all_correct_rels:
            reverse = reverse_relations(r.upper()).lower()
            if reverse != r and reverse in all_correct_rels:
                print(all_correct_rels)
                # prolog_retract_all_facts(retract_rel)
                # return 
                # print(all_correct_rels)

        if queries[key]["target_relation"][0] in all_correct_rels: 
            #choose the label of the example
            if positive > (10 * negative): #this question should be negative
                queries[key]["asked_relation"] = random.choice([x for x in convert_relations_prolog if x not in all_correct_rels and any(relation_formalism[x] == relation_formalism[i] for i in all_correct_rels )])
                negative += 1
            elif (10 * negative) > positive: #this question should be positive
                queries[key]["asked_relation"] = queries[key]["target_relation"]
                positive += 1
            else: #equal --> random selection
                if random.choice([0,1,1]):
                    queries[key]["asked_relation"] = queries[key]["target_relation"]
                    positive += 1
                else:
                    queries[key]["asked_relation"] = random.choice([x for x in convert_relations_prolog if x not in all_correct_rels and any(relation_formalism[x] == relation_formalism[i] for i in all_correct_rels )])
                    negative += 1

            final_queries[key] = queries[key]
        #else: do nothing and ignore this query

    #retract_asserted_facts
    prolog_retract_all_facts(retract_rel)
       
    
    
    return final_queries


def add_extra_relation(selected_story_triplets, selected_queries,  all_pair_relation, scene_objects_relations):

    ''' 
        - select some random facts to make it more complex
        - double check the answer after random facts (?) 
        - select the number of extra entities and relations
        - conditions on selection 
            - it must not be in already selected triplets
            - it must not be in  queries
            - its reverse must not be in already selected triplets
            - its reverse must not be in queries
            - the reverse not in the chain of queries
    '''

    '''
        1) it is possible that both (1,0) and (0,1) where selected in the extra
        
    '''
    # max_num_entities = min(len(all_objects), 8)
    '''
        how many extra relation we want to add? 
        it can be form 1 to the subtraction of len(current triplets)  from 10 which is the highest number. 
        so we randomly select a number from these part
        
    '''

    ''' First all *PP relation for the relation between obejcts and its block'''

    
    

    # max_num_of_objs_relations = min(len(selected_story_triplets)+1,10)
    num_of_current_relation = 0
    for i in selected_story_triplets:
        num_of_current_relation += len(selected_story_triplets[i])
    if num_of_current_relation > 7: 
        selected_story_triplets = add_pp_relations_for_all_used_objects(selected_story_triplets, scene_objects_relations)
        return selected_story_triplets, selected_queries

    number_of_extra = random.choice(range(3,11 - num_of_current_relation))
    # max_num_scn_relations = len(scenes_relations)+1

    '''create a list of all relations which satisfy the mentioned conditions'''
    all_possible_extra_relations = []
    for keys in all_pair_relation:
        for rel in all_pair_relation[keys]:
            if check_if_conditions_are_satisfied(keys, rel, selected_story_triplets, selected_queries):
                all_possible_extra_relations += [ (keys[0], keys[1], rel)]

    if all_possible_extra_relations:
        '''select random triplets'''
        random_extra_selected_triplets = []
        for i in range(number_of_extra):
            _selected = random.choice(all_possible_extra_relations)
            random_extra_selected_triplets += [ _selected]
            all_possible_extra_relations = [i for i in all_possible_extra_relations if i != _selected and i != (_selected[1], _selected[0], reverse_relations_data(_selected[2]))]
            if all_possible_extra_relations == []: break


        '''add random triplets'''
        for extra in random_extra_selected_triplets:
            if (extra[0], extra[1]) in selected_story_triplets: selected_story_triplets[(extra[0], extra[1])] += [extra[2]]
            else: selected_story_triplets[(extra[0], extra[1])] = [extra[2]]
    
    selected_story_triplets = add_pp_relations_for_all_used_objects(selected_story_triplets, scene_objects_relations)

    #select all chosen entities based on the current queries.
    # all_used_objects = []
    # for y in all_fixed_relation:
    #     if y[0] not in  all_used_objects: all_used_objects += [y[0]]
    #     if y[1] not in  all_used_objects: all_used_objects += [y[1]]
    
    # # if less than maximum choose a random number obetween the current length and the maximun as a total number of entities in the story
    # random_number_of_extra_entities = random.choice(range(max_num_entities- len(all_used_objects) + 1)) if len(all_used_objects) < max_num_entities else 0
    # #select extra entities from remaining 
    # extra_entities = random.sample([entity for entity in all_objects if entity not in all_used_objects], random_number_of_extra_entities)

    # #create all final selected objetcs
    # all_final_objects = {}
    # for obj in all_objects:
    #     if obj in all_used_objects or obj in extra_entities: all_final_objects[obj] = all_objects[obj]


    #compute the total number of relation we want


    #select scene relations
    # random_list = {}
    # for i in scenes_relations:
    #     if i in all_fixed_relation:
    #         scns_scns[i]  = [all_fixed_relation[i]]
            # if len


    return selected_story_triplets, selected_queries


def check_if_conditions_are_satisfied(key, rel, selected_story_triplets, query_triplets):

    reverse_key = (key[1], key[0])
    if key in selected_story_triplets:
        for story_rel in selected_story_triplets[key]:
            if story_rel == rel: 
                return False
    
    if reverse_key in selected_story_triplets:
        for story_rel in selected_story_triplets[reverse_key]:
            if reverse_relations_data(story_rel) == rel: 
                return False
    
    

    #TODO we can also consider the relation in the query to only ignore those that have the same relation 
    if key in query_triplets:
        return False
    
    if reverse_key in query_triplets:
        return False
     
    return True

def add_pp_relations_for_all_used_objects(selected_story_triplets, scene_objects_relations):

    all_objects, all_blocks = find_all_used_objects(selected_story_triplets)

    for obj in all_objects:
        if check_pp_rel_of_object(obj, selected_story_triplets):
            continue
        else:
            selected_story_triplets = add_pp_rel_to_object(obj, scene_objects_relations, selected_story_triplets)
    
    return selected_story_triplets

def check_pp_rel_of_object(obj, selected_story_triplets):

    if (obj, obj[0]) in selected_story_triplets:
        for rel in selected_story_triplets[(obj, obj[0])]:
            if "PP" in rel["relation_type"]: return True
        return False
    elif (obj[0], obj,) in selected_story_triplets :
        for rel in selected_story_triplets[( obj[0],obj)]:
            if "PP" in rel["relation_type"]: return True
        return False
    return False


def add_pp_rel_to_object(obj, scene_objects_relations, selected_story_triplets):

    list_of_pp_rels = {}
    for key in scene_objects_relations[int(obj[0])]:
        if (obj , obj[0]) == key:
            for rel in scene_objects_relations[int(obj[0])][key]:
                if "PP" in rel["relation_type"]: list_of_pp_rels[key] = [rel]
        
        elif (obj[0] , obj) == key :
            for rel in scene_objects_relations[int(obj[0])][key]:
                if "PP" in rel["relation_type"]: list_of_pp_rels[key] = [rel]
    
    if list_of_pp_rels == {}: print("ERROR"); return selected_story_triplets
    # else:
    selected_pp_key = random.choice([key for key in list_of_pp_rels])
    if selected_pp_key not in selected_story_triplets: selected_story_triplets[selected_pp_key] = list_of_pp_rels[selected_pp_key]
    else: selected_story_triplets[selected_pp_key] += list_of_pp_rels[selected_pp_key]
    
    return selected_story_triplets


def find_all_used_objects(selected_story_triplets):

    all_objects, all_blocks = [], []
    for i in selected_story_triplets:
        if 'x' in i[0] and i[0] not in all_objects: all_objects += [i[0]]
        elif 'x' not in i[0] and i[0] not in all_blocks: all_blocks += [i[0]]

        if 'x' in i[1] and i[1] not in all_objects: all_objects += [i[1]]
        elif 'x' not in i[1] and i[1] not in all_blocks: all_blocks += [i[1]]
    return all_objects, all_blocks

def random_pair_selection(objects_list, number_of_pairs):

    random_pairs = []
    while number_of_pairs and objects_list:
        random_pair = random.choice(objects_list)
        random_pairs += [random_pair]

        #update list by removing the selected pair and its reverse vewrsion
        objects_list = [obj for obj in objects_list if obj != random_pair and obj != (random_pair[1], random_pair[0])]
        number_of_pairs -= 1

    return random_pairs

def choose_paths(queries, num_queries, all_pair_relation, all_objects):

    '''
        - choose which fact-chain we want to select
            * higher num of steps is better
            * various form of spatial calculus is important
        
        1_sym = 1 step of reasoning using symmetry or reverse rule
        1_tarns = 1 step of reasoning using transitivity
        'n' = n steps of reasoning using combination of rules for spatial calculus

        DELETE: After choosing each triplet compute needed triplets. 
                If the story triplet cannot be added to the stpry-triplet (considering all random options) we discard that query.
    '''
    max_num_of_samples = 0
    type_of_reasoning = {'1_trans':[], '1_sym':[]}
    for pair in queries:
        if queries[pair] == []: continue
        for path_ind, path in enumerate(queries[pair]):
            x = 1
            while x <= path["max_reasoning_steps"]:

                if x == 1 and x == path["num_facts"]-1:
                    type_of_reasoning['1_trans'] += [(pair,path_ind)]
                    if len(type_of_reasoning['1_trans'])> max_num_of_samples: max_num_of_samples = len(type_of_reasoning['1_trans'])
                elif x == 1:
                    type_of_reasoning['1_sym'] += [(pair,path_ind)]
                    if len(type_of_reasoning['1_sym'])> max_num_of_samples: max_num_of_samples = len(type_of_reasoning['1_sym'])

                else:
                    if str(x) not in type_of_reasoning: 
                        type_of_reasoning[str(x)] = [(pair,path_ind)]
                    else:
                        type_of_reasoning[str(x)] += [(pair,path_ind)]

                    if len(type_of_reasoning[str(x)])> max_num_of_samples: max_num_of_samples = len(type_of_reasoning[str(x)])
                x +=1


    '''
        After getting the answer from each query which is a story triplets and updated chain added that to the main list
    '''

    #dynamic computation for choosing num of step of reasioning for each path
    chosen_query_path = {}
    chosen_story_triplets = {}
    while len(chosen_query_path) < num_queries and max_num_of_samples > 0:
        balanced_samples = []
        
        for i in type_of_reasoning:
            if type_of_reasoning[i] == []: continue
            repeat_sample = max_num_of_samples// len(type_of_reasoning[i])
            balanced_samples += [(x,i) for h in range(repeat_sample) for x in type_of_reasoning[i]]
        
        random_choice = random.choice(balanced_samples)
        # chosen_query_path += [{"pair": random_choice[0][0], "path": queries[random_choice[0][0]][random_choice[0][1]], "reasoning": random_choice[1]}]
        _chosen_query_path = {"pair": random_choice[0][0], "path": queries[random_choice[0][0]][random_choice[0][1]], "reasoning": random_choice[1]}

        # compute story triplets for this query and update it based on the steps of reasoning
        chosen_story_triplets, _updated_query =  select_triplets_of_story_based_on_query(_chosen_query_path, all_objects ,all_pair_relation, all_fixed_relation= chosen_story_triplets, previous_queries = chosen_query_path)
        
        #remove this path from type of reasoning
        for i in type_of_reasoning:
            if random_choice[0] in type_of_reasoning[i]: type_of_reasoning[i].remove(random_choice[0])

        #compute max_num
        max_num_of_samples = 0
        for i in type_of_reasoning:
            # if type_of_reasoning[i] == []: type_of_reasoning.pop(i, None) ;continue
            if len(type_of_reasoning[i])> max_num_of_samples: max_num_of_samples = len(type_of_reasoning[i])    
        
        #if cannot find appropriate story's triplets
        if _updated_query == None: 
            continue
        #else
        chosen_query_path[list(_updated_query.keys())[0]] = list(_updated_query.values())[0]

    return chosen_story_triplets, chosen_query_path                 


def select_triplets_of_story_based_on_query(query, all_objects, all_pair_relation, all_fixed_relation = {}, previous_queries = []):

    '''
        - select the main facts
            - consider the number of step for reasoning 
        - select some random facts to make it more complex
        - double check the answer after random facts (?) 
    '''
    # max_num_entities = min(len(all_objects), 8)
    # max_num_of_objs_relations = None
    # # max_num_scn_relations = len(scenes_relations)+1

    # scns_scns, scn_objs, objs_objs = {}, {}, {}
    
    

    # all_fixed_relation = {} #all relations must have been in the story based on the queries
    updated_queries = {}
    
    
    _query, _story_triplets = update_query(query, existed_relations = {"facts": all_fixed_relation, "queries": previous_queries}, all_pair_relation = all_pair_relation )
    if _story_triplets == None: return all_fixed_relation, None
    updated_queries[_query["pair"]] = _query["info"]
    for trip in _story_triplets:
        if trip not in all_fixed_relation :
            all_fixed_relation[trip] = [_story_triplets[trip]]
        elif _story_triplets[trip] not in all_fixed_relation[trip]:
            all_fixed_relation[trip] += [_story_triplets[trip]]
    
    # for query in queries:
    #     _query, _story_triplets = update_query(query, existed_relations = all_fixed_relation, all_pair_relation = all_pair_relation )
    #     updated_queries[_query["pair"]] = _query["info"]
    #     for trip in _story_triplets:
    #         if trip not in all_fixed_relation :
    #             all_fixed_relation[trip] = [_story_triplets[trip]]
    #         elif _story_triplets[trip] != all_fixed_relation[trip]:
    #             all_fixed_relation[trip] += [_story_triplets[trip]]
    
    return all_fixed_relation, updated_queries
    



def update_query(query, existed_relations = [],  all_pair_relation = []):


    '''
        if from update change get discard command pass nothing and the query gets dismissed
    '''
    new_queries = []
    story_triplets = []
    # 
    
    if query["reasoning"] == '1_sym':
        _query = {'num_facts': query["path"]["num_facts"], 'reasoning_steps': 1, "asked_relation": None, "all_relations":[], "target_relation":  query["path"]["all_relation"], "chain": '', "goal_chain": query["path"]["chain"]}

        #change the triplet in a way that we have mentioned reasoning
        story_triplets, _query["chain"] = update_chain(query["path"]["chain"], all_pair_relation, query["path"]["num_facts"], num_of_changes = 1 - ( query["path"]["num_facts"] -1) , existed_rels = existed_relations)
        
    elif query["reasoning"] == '1_trans':
        _query = {'num_facts': query["path"]["num_facts"], 'reasoning_steps': 1, "asked_relation": None, "all_relations":[], "target_relation":  query["path"]["all_relation"], "chain": '', "goal_chain": query["path"]["chain"]}

        #change the triplet in a way that we have mentioned reasoning
        story_triplets, _query["chain"] = update_chain(query["path"]["chain"], all_pair_relation, query["path"]["num_facts"], num_of_changes = 1 - ( query["path"]["num_facts"] -1) , existed_rels = existed_relations)
        
    else:
        _query = {'num_facts': query["path"]["num_facts"], 'reasoning_steps': int(query["reasoning"]), "asked_relation": None, "all_relations": [], "target_relation": query["path"]["all_relation"], "chain": '', "goal_chain": query["path"]["chain"]}

        #change the triplet in a way that we have mentioned reasoning
        story_triplets, _query["chain"] = update_chain(query["path"]["chain"], all_pair_relation, query["path"]["num_facts"], num_of_changes = int(query["reasoning"]) -( query["path"]["num_facts"] -1), existed_rels = existed_relations)
    

    return {"pair": query["pair"],"info": _query}, story_triplets


def update_chain(main_chain, all_relations, num_facts, num_of_changes = 0, existed_rels = []):


    '''
        if the reverse existed in existed --> choose other changes on facts
        if there is no other things --> discard query
        ** must also consider the existence of triplet in queries

        output: updated chain + facts
                None -- > discard query
    '''
    story_triplet, new_chain = {}, []
    # while True:

    changes_on_which_facts = select_changes_on_facts(main_chain, num_facts, num_of_changes, existed_rels)
    if changes_on_which_facts == None: return None, None

    for chain_id, chain in enumerate(main_chain):
        if chain_id in changes_on_which_facts: 
            reverse_rel = reverse_relations_data(chain[2])
            new_chain += [ ((chain[1],chain[0]), reverse_rel)]
            story_triplet[(chain[1],chain[0])] =  reverse_rel
        
        else:
            story_triplet[(chain[0],chain[1])] = chain[2]
            new_chain += [((chain[0],chain[1]), chain[2])]
  

    return story_triplet, new_chain


def select_changes_on_facts(complete_chain, num_facts, num_of_changes, existed_relations):
    
    all_facts, all_queries = existed_relations["facts"], existed_relations["queries"]

    '''
        for each pair in chain check if the (pair and relation) exists in the all facts or queries
        why? changes meant reversing the pair and relation so if it already exists we already have the direct relation so it must not be added that. 

        for each pain in chain if the reverse relation already exists we don't need to add a new rel. 
        But for the sake of keeping the correct number of reasoning, we must included those in the changing facts.
        if the number of keeped pairs is more than num of changes it hurts the correct number of reasoning so we discard the query.
        If the number of changes is 0 we return the main chain. check after computing must_have and cannot_have
     
        output: 
            list of changes --> if [] no changes is needed
            None --> the query must be discarded
    '''


    must_change, cannot_change = [], []
    for chain_id, chain in enumerate(complete_chain):
        pair = (chain[0], chain[1])
        reverse_pair = (chain[1], chain[0])
        relation = chain[2]
        reverse_relation = reverse_relations_data(chain[2])


        '''
            # check if reverse pair  is in query --> if add it is the direct answer to another query and ruin the step of reasoning
            # pair cannot be in query since we selected unique queries
            # it is better to compute l;ike below but since we don't have all_relations we ignore all reverse pairs
            # if reverse_pair in all_queries and reverse_relation in all_queries[reverse_pair]["all_relations"]: 
            We cannot have any edge in the chain which is already a query
                unless:

        '''
        if pair in all_queries or reverse_pair in all_queries: 
            # if chain_id not in cannot_change: cannot_change += [chain_id]
            return None

        if pair in all_facts and relation in all_facts[pair]: 
            '''
                if the pair exists in the facts ading its reverse is redundant so we must not add this
            '''
            if chain_id not in cannot_change: cannot_change += [chain_id]
        
        elif reverse_pair in all_facts and reverse_relation in all_facts[reverse_pair]: 
            '''
                if the reverse already exists in the facts we must included that in the changed facts
            '''
            if chain_id not in must_change: must_change += [chain_id]

    if any(chain_id in must_change and chain_id in cannot_change for chain_id in range(len(complete_chain))): return None

    elif len(must_change) > num_of_changes or num_facts - len(cannot_change) < num_of_changes or num_facts - len(must_change) < 0: return None


    elif num_of_changes == 0: return []


    num_remianing_changes = num_facts - len(must_change)
    if num_remianing_changes == 0: return must_change

    selected_facts = must_change
    num_of_changes -= len(selected_facts)
    remaining_facts =  [x for x in range(num_facts) if x not in cannot_change and x not in must_change]
    selected_facts += random.sample(remaining_facts, num_of_changes)

    return selected_facts



# def existence_of_relation(pair, relation, all_relations):

#     all_facts, all_queries = all_relations["facts"], all_relations["queries"]

#     if pair not in all_facts and pair not in all_queries: return False
#     check_not_in_facts = True if pair in all_facts and relation not in all_facts[pair] else False
#     check_not_in_queries =  True if pair in all_queries and all_queries[pair]["target_relation"][0] != relation["relation_type"].lower() else False
#     if check_not_in_facts and check_not_in_queries : return False

#     return True


# def select_changes_on_facts(num_of_facts, num_of_changes, must_have = [], must_not_have= []):
    
#     if num_of_changes == 0 or len(must_have) == num_of_changes: return []
#     if len(must_have) > num_of_changes: return None

#     selected_facts = must_have
#     num_of_changes -= len(selected_facts)
#     all_facts = [x for x in range(num_of_facts) if x not in must_not_have and x not in selected_facts]
    
#     if len(all_facts) < num_of_changes: return None

#     selected_facts += random.sample(all_facts, num_of_changes)

#     return selected_facts

def check_type_of_pair(pair):

    #True means it is a block
    pair_0, pair_1 = True, True
    if 'x' in pair[0]: pair_0 = False

    if 'x' in pair[1]: pair_1 = False

    return [pair_0, pair_1]



def make_single_dic(scenes_relations,  scene_objects_relations, objects_object_relations):
    all_relations = {}

    for scn in scenes_relations:
        all_relations[scn] = scenes_relations[scn]

    for scn in scene_objects_relations:
        for rel in scene_objects_relations[scn]:
            all_relations[rel] = scene_objects_relations[scn][rel]

    # objects_object_relations = {}
    for scn in objects_object_relations:
        for rel in objects_object_relations[scn]:
            all_relations[rel] = objects_object_relations[scn][rel]

    return all_relations

def find_possible_query(scene_graph, pair):

    
    first_object = pair[0]
    second_object = pair[1]

    #Remove direct edge
    # num_edges = scene_graph.number_of_edges(first_object, second_object)
    # if scene_graph.has_edge(first_object, second_object):
    # for range(num_edges):
        # scene_graph.remove_edge(first_object,second_object)
    # scene_graph.remove_edges_from([(first_object, second_object)]*num_edges)

    
    
    '''
        1) check all the direct inverse relations (with high probability it has one)
        2) check all paths (with all relation) 
            2.a) select from those that have true result from prolog reasoner

        **
        If objects  are from the same block (first character of the ids are the same) we compute all path with length <= number of object in the same block -1
        If not we choose all paths with length of 1(obj-block) + num of blocks-1(block-block) +1 (block-obj)
    '''

    # direct inverse relation
    # all_directed_inverse_paths = (nx.all_simple_edge_paths(scene_graph, source=second_object, target=first_object, cutoff = 1))
    # for path in nx.all_simple_edge_paths(scene_graph, source=second_object, target=first_object, cutoff = 1):
    #     facts_chain = []
    #     retract_rel = []
    #path facts and relations to the reasoner


    #check all paths
    all_possible_query = []
    cutoff = compute_cutoff(list(scene_graph.nodes), pair)
    all_paths = list(nx.all_simple_edge_paths(scene_graph, source=first_object, target=second_object, cutoff = cutoff))
    if len(all_paths) > 200:
        all_paths = random.sample(all_paths, 200)

    for path in all_paths:
        facts_chain = []
        retract_rel = []
        for fact in list(path):
            
            relation = scene_graph.get_edge_data(fact[0],fact[1])[fact[2]]
            relation_prolog= convert_relations_prolog[relation["relation_type"].lower()]
            retract_rel += [relation_prolog]
            #TODO consider relation property
            f = f"{relation_prolog}('{fact[0]}','{fact[1]}')" #relation_prolog+'("'+fact[0]+'","'+fact[1]+'")'
            prolog.assertz(f)
            facts_chain += [(fact[0],fact[1], relation)]
        
        all_relations_between_args = find_all_relations_exists_between_args(first_object,second_object)
        if all_relations_between_args: 
            # if (first_object,second_object) not in all_possible_query: 
            all_possible_query += [{"num_facts": len(facts_chain), "max_reasoning_steps": (2*len(facts_chain))-1, "min_reasoning_steps": len(facts_chain)-1, "chain": facts_chain, "all_relation": all_relations_between_args}]
            # else: all_possible_query[(first_object,second_object)] += [{"num_facts": len(facts_chain),"chain": facts_chain, "all_relation": all_relations_between_args}]
        
        #retract_asserted_facts
        prolog_retract_all_facts(retract_rel)
       
    
    
    return all_possible_query
        
def compute_cutoff(all_nodes, pair):

    if pair[0][0] == pair[1][0]: #objects from the same block
        number_of_nodes_in_block = 0
        for node in all_nodes:
            if node[0] == pair[0][0]: number_of_nodes_in_block += 1
        return number_of_nodes_in_block - 2

    else: 
        number_of_scenes = 0
        for node in all_nodes:
            if len(node) == 1: number_of_scenes +=1
        return 1+ number_of_scenes


def prolog_retract_all_facts(all_prolog_facts_relation, _prolog = None):
    
    # if "behind_" in all_prolog_facts_relation:
    #     all_prolog_facts_relation
    for rel in all_prolog_facts_relation:
        if _prolog:
            _prolog.retractall(rel+'(X,Y)')
            _prolog.assertz(rel+'(none,none)')
        else:
            prolog.retractall(rel+'(X,Y)')
            prolog.assertz(rel+'(none,none)')

    return

def find_all_relations_exists_between_args(source,target, _prolog = None):

    true_predicates = []
    for rel in convert_relations_prolog:
        _query = f"{rel}('{source}','{target}')"
        if _prolog:
            result = list(_prolog.query(_query)) #list(prolog.query(rel+'("'+source+'","'+target+'")'))

        else:
            result = list(prolog.query(_query)) #list(prolog.query(rel+'("'+source+'","'+target+'")'))
        if result: true_predicates += [rel]

    return true_predicates
# def prolog_assertz_all_facts(all_triplets_list):
    

#     for i in all_triplets_list:
        
#         traj = [i['trajector']['entity_id']] 
#         land = [i['landmark']['entity_id']]
        
#         if i['spatial_value'].lower() in ['middle','around', 'nan']: continue
        
#         sp_indicator = convert_relations_prolog[i['spatial_value'].lower()]
        
#         query = sp_indicator+'('+str(t)+','+str(l)+')'
#         all_queries += [query]
#         prolog.assertz(query)


    

# def reverse_relations(rel):

#     reverse = {"DC": "DC",
#          "EC":"EC",
#          "PO":"PO",
#          "NTPP":"NTPPI",
#          "NTPPI":"NTPP",
#          "TPP":"TPPI",
#          "TPPI":"TPP",
#          'RIGHT': "LEFT",
#          'LEFT':"RIGHT",
#          'BELOW':"ABOVE",
#          'ABOVE':"BELOW",
#          "BEHIND": "FRONT" ,
#          "FRONT":"BEHIND" ,
#          'FAR':"FAR",
#          'NEAR':"NEAR"
#          }

#     return reverse[rel]

def reverse_relations_data(rel_data):

    RCC_pp_rel = {"TPPI","TPP","NTPP","NTPPI"}

    new_rel = {"relation_type": reverse_relations(rel_data["relation_type"]), "relation_property": rel_data["relation_property"] if rel_data["relation_type"] in RCC_pp_rel else reverse_relations( rel_data["relation_property"]) if rel_data["relation_property"] else ''}

    return new_rel


