from __future__ import annotations
from dataclasses import replace
import json
import random
import re
# from matplotlib.cbook import simple_linear_interpolation
import numpy as np
from Vocabulary import vocabulary, relation_vocabulary
from Generate_graph import relation_formalism
# from random_choice import random_choice


_final_story = ""
annotation = {"story": "", "annotations": []}
temp_annot_sent, traj, land, sp_ind, sp_type, block_temp, sen_temp = "",[],[],[],[],[],""
land_obj_id, traj_obj_id = [], []
scn_rels, scn_objs, objs_rels = {}, {}, {}  # [],[],[]
all_objects_data = []
key_sentence = {}

#described_objects and described_relations are a storing dictionary to remember which objects and relations are described.
described_objects, described_relations, obj_scn_queue = {},{}, []

vocab_selection = None
_relation_vocab_selection = None
temp_checked_obj_sc, checked_obj_sc, checked_obj_obj, finished_objs , seen_objects = [], [], [], [], {}
objs_attrs_f, objs_objs_f = [], []
object_shared_prop, shared_prop = [], []
recent_objs = []
treshhold = 0
cannot_have_which = 0
cannot_have_with = 0
has_with = False
G_color, G_size, G_type, G_scene_rel = "", "", "", ""
End_of_block = 0
factor = 0.5
max_treshhold_for_rels = 4
num_of_blocks = 0  # number of scenes
block_id = None  # the scene number
entity_phrases = {}


prepositions_relations = [
    "LEFT",
    "RIGHT",
    "ABOVE",
    "BELOW",
    "BEHIND",
    "FRONT",
    "NEAR",
    "FAR",
    "DC",
    "NTPP",
    "TPP",
]
verb_relations = ["EC", "PO", "TPPI", "NTPPI"]


"""
    TODO:
    For having the supporting fact sentences :
    Just check wherever that we create a sentence and check which triplets this sentence is related to, then assigne that sentence to the triplet

    We are ignoring spatial property but it should be considered and added to the object description

    A medium grey hexagon is north of the medium red hexagon. Block HHH has this shape. -- > Block HHH has A medium gre ... which is north ... 

"""

def nullification():
    global scn_rels, scn_objs, objs_rels, num_of_blocks, _final_story, objs_attrs_f, objs_objs_f, checked_obj_sc, checked_obj_obj, finished_objs, object_shared_prop, shared_prop, recent_objs, treshhold, cannot_have_which, G_color, G_size, G_type, G_scene_rel, End_of_block, annotation, described_objects, described_relations, obj_scn_queue, key_sentence

    _final_story, objs_attrs_f, objs_objs_f = "", [], []
    scn_rels, scn_objs, objs_rels = {}, {}, {}
    all_objects_data = []
    annotation = {"story": "", "annotations": []}
    described_objects, described_relations = {},{}
    temp_annot_sent, traj, land, sp_ind, block_temp, sen_temp = "", [], [], [], [], ""
    all_objects_data = all_objects_data
    checked_obj_sc, checked_obj_obj, finished_objs = [], [], []
    obj_scn_queue = []
    objs_attrs_f, objs_objs_f = [], []
    object_shared_prop, shared_prop = [], []
    recent_objs = []
    key_sentence = {}
    treshhold = 0
    cannot_have_which = 0
    cannot_have_with = 0
    has_with = False
    G_color, G_size, G_type, G_scene_rel = "", "", "", ""
    End_of_block = 0
    num_of_blocks = 0
    described_objects, described_relations = {},{}


def creating_story(story_triplets, _all_objects_data, _vocab_selection, _relation_vocab_selection, f):

    global scn_rels, scn_objs, objs_rels, num_of_blocks, vocab_selection, all_objects_data, relation_vocab_selection

    all_objects_data = _all_objects_data
    vocab_selection = _vocab_selection
    relation_vocab_selection = _relation_vocab_selection
    nullification()

    # x = 1
    # while x:
    #     try :
    #         _temp = random.choice(story)
    #         if _temp == -1: return -1
    #         elif _temp == []: continue
    #         else: scn_rels, scn_objs, objs_rels = _temp

    #         if scn_objs != []:
    #             x=0
    #     except:
    #         raise
    #         return -1

    # categorize data in the story triplet based on the scene-scene relations, object-scene relations, object-object relations in each scene
    for key in story_triplets:
        if len(key[0]) == 1 and len(key[1]) == 1:
            scn_rels[key] = story_triplets[key]
        elif len(key[0]) == 1:
            if key[0] in scn_objs:
                scn_objs[key[0]][key] = story_triplets[key]
            else:
                scn_objs[key[0]] = {key: story_triplets[key]}

        elif len(key[1]) == 1:
            if key[1] in scn_objs:
                scn_objs[key[1]][key] = story_triplets[key]
            else:
                scn_objs[key[1]] = {key: story_triplets[key]}

        else:  # both are objects
            if key[0][0] in objs_rels:
                objs_rels[key[0][0]][key] = story_triplets[key]
            else:
                objs_rels[key[0][0]] = {key: story_triplets[key]}

    compute_objects_features()
    # number of blocks
    # num_of_blocks = 0
    # for obj in all_objects_data:
    #     if len(obj) == 1 : num_of_blocks += 1
    num_of_blocks = len([ i for i in all_objects_data if len(i) == 1]) # blocks id has length of 1 eg: "0", "1", "2"

    #####for checking
    # if num_of_blocks != 3:
    #     return -1

    _final_story = start()

    # reshape the text
    _final_story = edit_text_form(_final_story)

    SOT(_final_story)

    #     print('##', objs_attrs_f, objs_objs_f)
    #     print('final story\n', _final_story)
    return [_final_story, all_objects_data, objs_attrs_f, objs_objs_f, annotation, num_of_blocks]


# **********************************************************
# *************Start describing functions*******************
# **********************************************************

"""
    ******************************************************
    First we start with mentioning blocks names:
    B is for first sentence with description introducing the blocks.
    D is for relation between blocks
    B0 --> B0D0 (1 block) B0D01 (2 blocks) B0D03 (3 blocks) just name the block then start describe each block's object and when want to describe the objects in a new block describe their relations
    possible combinations:
        BD
        BD0
        B0D0
    ******************************************************
"""

def start():
    
    sentence = ""
    # block_id = "0"
    #0 = B0D0, 1 = BD0, 2 = BD

    y = random.choice(range(3))
    # y = 2
    if y == 0:
        sentence = B0D0()
    
    elif y == 1:
        sentence = BD0()

    else: #y ==2
        sentence = BD()
    
    return sentence

def B0D0():
    """
    based on the number of blocks goes to B0D01, B0D02, or B0D03
    """
    sen = ''
    sen += (
            D(block_id = "0",blocks = ['0'], B_is_Null= True)
            # + BD_obj("0")
            + P("0")
            # + P(scn_objs["0"])
        )
    if num_of_blocks >1:
        sen += (
            # "\n"
            D(block_id = "1",blocks = ['0', '1'], B_is_Null= True)
            + P("1")
            # + P(scn_objs["1"])
        )
    if num_of_blocks > 2:
        sen += (
            # "\n"
            D(block_id = "2",blocks = ['0', '1', '2'], B_is_Null= True)
            + P("2")
            # + P(scn_objs["2"])
        )

    return sen


def BD0():

    sen = ''
    sen += (
            B()
            # + "\n"
            + D(block_id = "0",blocks = ['0'])
            # + BD_obj("0")
            + P("0")
            # + P(scn_objs["0"])
        )
    if num_of_blocks >1:
        sen += (
            # "\n"
            D(block_id = "1",blocks = ['0', '1'])
            + P("1")
            # + P(scn_objs["1"])
        )
    if num_of_blocks > 2:
        sen += (
            # "\n"
            D(block_id = "2",blocks = ['0', '1', '2'])
            + P("2")
            # + P(scn_objs["2"])
        )

    return sen


def BD():
    sen = ''
    #id num of blocks == 1 D return null
    sen += (
            B()
            # + "\n"
            + D()
            # + "\n"
            + BD_obj("0")
            + P("0")
        )
    
    if num_of_blocks > 1:
        
        sen += (
            #  "\n"
            BD_obj("1")
            + P("1")
        )
    if num_of_blocks > 2:

        sen += (
            # "\n"
            BD_obj("2")
            + P("2")
        )

    return sen 

def B():
    #checked
    global recent_objs, traj, traj_obj_id, sp_ind, sp_type, land, land_obj_id, all_objects_data
    sentence = ''
    _sen = ''

    y = random.choice([0, 1,2, 3, 4]) # y == 1 There [is/are] y == 0 We have, y== 2 there exists.
    _sen = name_block_all(num_of_blocks)
    
    if num_of_blocks == 1:
        recent_objs = ["0"]

    if y == 0:
        
        sentence += ("There "
                + ("are " if num_of_blocks > 1 else "is ")
                + _sen
                +". "
        )
        land += [["There"]]
        land_obj_id += [["-1"]]
        sp_ind += [["are" if num_of_blocks > 1 else "is"]]
        sp_type += [["NTPP"]]
        traj += [[_sen]]
        traj_obj_id += [[str(m) for m in range(num_of_blocks)]]
        all_objects_data

    elif y == 1:
        sentence += ("We have "
                + _sen
                +". "
        )
        traj += [['We']]
        traj_obj_id += [["-1"]]
        sp_ind += [["have"]]
        sp_type += [["NTPPI"]]
        land += [[_sen]]
        land_obj_id += [[str(m) for m in range(num_of_blocks)]]

    elif y == 2: # y == 2
        sentence += ("There "
                +( "exist " if num_of_blocks > 1 else "exists ")
                + _sen
                +". "
        )
        land += [["There"]]
        land_obj_id += [["-1"]]
        sp_ind += [["exist" if num_of_blocks > 1 else "exists"]]
        sp_type += [["NTPP"]]
        traj += [[_sen]]
        traj_obj_id += [[str(m) for m in range(num_of_blocks)]]
    
    elif y == 3:
        
        sentence += (start_word(_sen) 
                +( " exist. " if num_of_blocks > 1 else " exists. ")
        )
        traj += [[_sen]]
        traj_obj_id += [[str(m) for m in range(num_of_blocks)]]
        sp_ind += [["exist" if num_of_blocks > 1 else "exists"]]
        sp_type += [["NTPP"]]
        land += [[""]]
        land_obj_id += [["-1"]]

    else: #y ==4

        sentence += (start_word(_sen) 
                +( " exist in an image. " if num_of_blocks > 1 else " exists in an image. ")
        )
        traj += [[_sen]]
        traj_obj_id += [[str(m) for m in range(num_of_blocks)]]
        sp_ind += [["exist in" if num_of_blocks > 1 else "exists in"]]
        sp_type += [["NTPP"]]
        land += [["an image"]]
        land_obj_id += [["-1"]]
    
    #add the idea of group (e.g. three blocks) in to the all objects data as "other_id"
    # for i in range(num_of_blocks):
    #     all_objects_data[i]["other_id"] = [num_of_blocks+1]

    described_objects['0'] = []
    if num_of_blocks > 1: described_objects['1'] = []
    if num_of_blocks > 2: described_objects['2'] = []

    create_annotation(sentence)
    return start_word(sentence)
    

def B_id(block_id):
    #checked
    global recent_objs, traj, traj_obj_id, sp_ind, sp_type, land, land_obj_id
    sentence = ''
    _sen = ''

    y = random.choice([0, 1,2, 3, 4]) # y == 1 There [is/are] y == 0 We have, y== 2 there exists.
    # _sen = name_block_all(num_of_blocks)
    _sen = "a "+select_vocab("block")+" "+name_call()+select_vocab("block_name", block_id)
    
    if num_of_blocks == 1:
        recent_objs = ["0"]

    if y == 0:
        
        sentence += ("There "
                +  "is "
                + _sen
                +". "
        )
        land += [["There"]]
        land_obj_id += [["-1"]]
        sp_ind += [["is"]]
        sp_type += [["NTPP"]]
        traj += [[_sen]]
        traj_obj_id += [[block_id]]

    elif y == 1:
        sentence += ("We have "
                + _sen
                +". "
        )
        traj += [['We']]
        traj_obj_id += [["-1"]]
        sp_ind += [["have"]]
        sp_type += [["NTPPI"]]
        land += [[_sen]]
        land_obj_id += [[block_id]]

    elif y == 2: # y == 2
        sentence += ("There "
                +"exists "
                + _sen
                +". "
        )
        land += [["There"]]
        land_obj_id += [["-1"]]
        sp_ind += [["exists"]]
        sp_type += [["NTPP"]]
        traj += [[_sen]]
        traj_obj_id += [[block_id]]
    
    elif y == 3:
        
        sentence += (start_word(_sen) 
                +" exists. "
        )
        traj += [[_sen]]
        traj_obj_id += [[block_id]]
        sp_ind += [["exists"]]
        sp_type += [["NTPP"]]
        land += [[""]]
        land_obj_id += [["-1"]]

    else: #y ==4

        sentence += (start_word(_sen) 
                +" exists in an image. "
        )
        traj += [[_sen]]
        traj_obj_id += [[block_id]]
        sp_ind += [["exists in"]]
        sp_type += [["NTPP"]]
        land += [["an image"]]
        land_obj_id += [["-1"]]
    
    described_objects[block_id] = []

    create_annotation(sentence)
    return sentence


def BD_obj(block_id, between_blocks_relations = False, B_is_Null = False):  

    """
        We already describe each blocks and their relation (eather in D or D0 situation)
        We want to describe the objects in each block in the beginning of of the block description.

    """

    sen = ""
    G_name = select_vocab("block")
    global recent_objs,traj, sp_ind, traj_obj_id, land, land_obj_id, block_temp, sen_temp, has_with

    _temp_block_name = G_name + " " + name_block(block_id)

    if sen_temp or between_blocks_relations: 
        #CHECKED
        """
            mentioned objects that this block have in the relation description between blocks
            if not cannot_have_which and cannot_have_with create this
            when it comes in this part it means that it should have which or with
            we check with if it is possible select between them if not go with which/that
        """
        object_block_rel_description = obj_rel_scene(block_id, is_traj= False, check_with = False if cannot_have_with else True, fixed_relation = ["NTPPI"]) # is_traj is for object so if block_as_traj == 1 obj should be land
        if object_block_rel_description != None:
            if has_with:
                sen += ' '+ object_block_rel_description
                has_with = False
            else:
                sen += ' '+wh_th()+' '+ object_block_rel_description
            # traj += [[block_temp]]* len(sp_ind)
            # traj_obj_id += [[block_id]]* len(sp_ind)
        else: return None

    else: # we want to start a new sentence
        #CHECKED
        
        block_as_traj = random.choice([False,True])
        object_block_rel_description = obj_rel_scene(block_id, is_traj= False if block_as_traj else True ) # is_traj is for object so if block_as_traj == 1 obj should be land
        if object_block_rel_description == None: #there isn't any rel with block as traj
            block_as_traj = not block_as_traj
            object_block_rel_description = obj_rel_scene(block_id, is_traj= False if block_as_traj else True) 

        if object_block_rel_description == None: #if it is still none it means that this block doesn't have object
            return ""
        # if this object is the subject of previous sentence we can use pronouns
        block_mention = select_pronoun(is_subject= block_as_traj, is_block=True, plural= True if len(recent_objs) > 1 else False) if [block_id] == recent_objs else _temp_block_name

        if block_as_traj:
            if B_is_Null:
                _, new_mention = B0_call_block(block_id, is_traj = True)
                block_mention = new_mention
            # else: 
            #     starter_phrase =  block_mention   
            sen += start_word(block_mention) + ' '+ object_block_rel_description+'. '
            traj += [[block_mention]]* len(sp_ind)
            traj_obj_id += [[block_id]]* len(sp_ind)
            recent_objs = [block_id]
        else:
            if B_is_Null:
                _, new_mention = B0_call_block(block_id)
                block_mention = new_mention 
            sen += start_word(object_block_rel_description)+ ' '+block_mention+'. '
            land += [[block_mention]]* len(sp_ind)
            land_obj_id += [[block_id]]* len(sp_ind)
        create_annotation(sen)   
        sen = start_word(sen)
    return sen


def D(block_id = None,blocks = [], B_is_Null = False):  # D is a description about positions of block to each other right after first block description. for BD

    # global traj, sp_ind, land, land_obj_id, traj_obj_id, sp_type, recent_objs
    sen = ""

    """
        D is for describing the relation between objects
        if block_id, it means it is D0 else it is D which we describe all relations between blocks
        D0:
            blocks list show which blocks we are describing their relation
            between the describing the relations we can also add BD_obj(with/which)
    """


    if block_id == None:  # D != Null  and we want to describe all relations between blocks at the beginning of story.
        
        # if blocks == ['0']: #we don't have relation between blocks yet
        #     return ""

        shared_relations_keys = find_shared_rel(
                searching_list= scn_rels, num_objects= num_of_blocks
            )

        for shared_rel in shared_relations_keys:

            relation_need_verb = shared_rel["need_verb"] # if True we need to add verb to the relation and we can have Sp_ind+land+traj sentences
            shared_info = describe_shared_scn_scn(shared_rel)
            """
                shared_info:{
                    "land_obj_desc": land_obj, 
                    "traj_obj_desc": traj_obj,
                    "relation_text": relation_text,
                    }
            """
            #concat the information, create the sentence, create the annotation
            _sen = ''
            
            if shared_rel["has_common_key"]: #elif shared_rel["has_common_key"] 

                if shared_rel["is_traj"]:
                    #connect the obj and rel
                    obj_desc = ''
                    for ind, desc in enumerate(shared_info["land_obj_desc"]):
                        if obj_desc: obj_desc += ', '
                        if relation_need_verb[ind]:
                            obj_desc += check_verb("[is/are]", is_singular=True)+" "+shared_info["relation_text"][ind]+ " " +desc
                        else:
                            obj_desc += shared_info["relation_text"][ind]+ " " +desc
                    land_obj = add_and(obj_desc)
                    traj_obj = shared_info["traj_obj_desc"][0]
                else:
                    obj_desc = ''
                    for ind, desc in enumerate(shared_info["traj_obj_desc"]):
                        if obj_desc: obj_desc += ', '
                        if relation_need_verb[ind]:
                            obj_desc += desc +" "+check_verb("[is/are]", is_singular=True)+" "+ shared_info["relation_text"][ind]
                        else:
                            obj_desc += desc +" "+ shared_info["relation_text"][ind]
                    traj_obj = add_and(obj_desc)
                    land_obj = shared_info["land_obj_desc"][0]

                _sen = start_word(traj_obj)+" "+land_obj+'. '
                #create sentence
                create_annotation(_sen)
                sen += _sen
            else: #if shared_rel["has_common_rel"]: or no common part
                
                if shared_rel["is_traj"]:
                    #connect the shared part
                    obj_desc = ''
                    for desc in shared_info["land_obj_desc"]:
                        if obj_desc: obj_desc += ', '
                        obj_desc += desc
                    land_obj = add_and(obj_desc)
                    traj_obj = shared_info["traj_obj_desc"][0]
                else:
                    obj_desc = ''
                    for desc in shared_info["traj_obj_desc"]:
                        if obj_desc: obj_desc += ', '
                        obj_desc += desc
                    traj_obj = add_and(obj_desc)
                    land_obj = shared_info["land_obj_desc"][0]
                
                #create sentence
                if relation_need_verb[0]:
                    #We need to add [is/are] verb and also have sp_id+land+traj sentences
                    h = random.choice([0,1,1])
                    # if h:
                    #     verb_singularity = True if len(shared_info["traj_obj_desc"]) == 1 else False
                    # else: 
                    #     verb_singularity = True if len(shared_info["land_obj_desc"]) == 1 else False
                    verb_singularity = False if shared_rel["has_common_rel"] else True
                    verb_text = check_verb("[is/are]", is_singular= verb_singularity)
                    
                    if h:
                        _sen = (start_word(shared_info["relation_text"][0])
                                +" "
                                +land_obj
                                +" "
                                +("there " if random.choice([0,1]) else "")
                                + verb_text
                                +" "
                                +traj_obj+". "
                                )
                    else:
                        _sen = start_word(traj_obj)+" "+verb_text +" "+shared_info["relation_text"][0]+" "+land_obj+'. '

                else:    
                    _sen = start_word(traj_obj)+" "+shared_info["relation_text"][0]+" "+land_obj+'. '
                
                create_annotation(_sen)
                sen += _sen
            # else: # we only have one triplet and no common part
            #     if relation_need_verb[0]:
            #         #We need to add [is/are] verb and also have sp_id+land+traj sentences
            #         verb_text = check_verb("[is/are]", is_singular= True) 
            #         if random.choice([0,1,1]):
            #             _sen = (start_word(shared_info["relation_text"][0])
            #                     +" "
            #                     +land_obj
            #                     +" "
            #                     +("there " if random.choice([0,1]) else "")
            #                     + verb_text
            #                     +traj_obj+". "
            #                     )
            #         else:
            #             _sen = start_word(traj_obj)+" "+verb_text +" "+shared_info["relation_text"][0]+" "+land_obj+'.'

            #     else:    
            #         _sen = start_word(traj_obj)+" "+shared_info["relation_text"][0]+" "+land_obj+'.'

    else: 
        """
            we have block_id
            it means that we want to describe the relation between the current block and others 
            also if it is possible add some objects in the block in between
            if not add the obj_rel description (BD_obj) at the end

        """
        if blocks == ['0']: #we don't have relation between blocks yet
            sen = BD_obj('0', B_is_Null= B_is_Null)
            # if _sen == '' and B_is_Null: _sen =  B_id('0')
            
        
        else:

            shared_relations_keys = find_shared_rel(
                searching_list= limit_the_list(scn_rels, block_id,blocks), num_objects=len(blocks)
            )

            for shared_rel in shared_relations_keys:

                relation_need_verb = shared_rel["need_verb"]
                shared_info = describe_shared_scn_scn(shared_rel, scn_id = block_id , check_having_obj_scn_rels= True, B_is_Null = B_is_Null)
                """
                    shared_info:{
                        "land_obj_desc": land_obj, 
                        "traj_obj_desc": traj_obj,
                        "relation_text": relation_text,
                        # "new_block_description": B0_value
                        }
                """
                #concat the information, create the sentence, create the annotation
                _sen = ''
                
                if shared_rel["has_common_key"]:

                    if shared_rel["is_traj"]:
                        #connect the obj and rel
                        obj_desc = ''
                        for ind, desc in enumerate(shared_info["land_obj_desc"]):
                            if obj_desc: obj_desc += ', '
                            if relation_need_verb[ind]:
                                obj_desc += check_verb("[is/are]", is_singular=True)+" "+shared_info["relation_text"][ind]+ " " +desc
                            else:
                                obj_desc += shared_info["relation_text"][ind]+ " " +desc
                        land_obj = add_and(obj_desc)
                        traj_obj = shared_info["traj_obj_desc"][0]
                    else:
                        obj_desc = ''
                        for ind, desc in enumerate(shared_info["traj_obj_desc"]):
                            if obj_desc: obj_desc += ', '
                            if relation_need_verb[ind]:
                                obj_desc += desc +" "+check_verb("[is/are]", is_singular=True)+" "+ shared_info["relation_text"][ind]
                            else:
                                obj_desc += desc +" "+ shared_info["relation_text"][ind]
                        traj_obj = add_and(obj_desc)
                        land_obj = shared_info["land_obj_desc"][0]

                    _sen = start_word(traj_obj)+" "+land_obj+'. '
                    
                    create_annotation(_sen)
                    sen += _sen
                else: #if shared_rel["has_common_rel"]: or no common part
                    if shared_rel["is_traj"]:
                        #connect the shared part
                        obj_desc = ''
                        for desc in shared_info["land_obj_desc"]:
                            if obj_desc: obj_desc += ', '
                            obj_desc += desc
                        land_obj = add_and(obj_desc)
                        traj_obj = shared_info["traj_obj_desc"][0]
                    else:
                        obj_desc = ''
                        for desc in shared_info["traj_obj_desc"]:
                            if obj_desc: obj_desc += ', '
                            obj_desc += desc
                        traj_obj = add_and(obj_desc)
                        land_obj = shared_info["land_obj_desc"][0]
                    
                    if relation_need_verb[0]:
                        #We need to add [is/are] verb and also have sp_id+land+traj sentences
                        
                        h = random.choice([0,1,1])
                        # if h:
                        verb_singularity = False if shared_rel["has_common_rel"] else True
                        # else: 
                        #     verb_singularity = True if len(shared_info["land_obj_desc"]) == 1 else False

                        verb_text = check_verb("[is/are]", is_singular= verb_singularity) 
                        if h:
                            _sen = (start_word(shared_info["relation_text"][0])
                                    +" "
                                    +land_obj
                                    +" "
                                    +("there " if random.choice([0,1]) else "")
                                    + verb_text
                                    +" "
                                    +traj_obj+". "
                                    )
                        else:
                            _sen = start_word(traj_obj)+" "+verb_text +" "+shared_info["relation_text"][0]+" "+land_obj+'. '

                    else:    
                        _sen = start_word(traj_obj)+" "+shared_info["relation_text"][0]+" "+land_obj+'. '

                    # _sen = start_word(traj_obj)+" "+shared_info["relation_text"]+" "+land_obj+'.'
                    
                    create_annotation(_sen)
                    sen += _sen

            
        if sen == '' and B_is_Null: sen =  B_id(block_id)


    return sen



def describe_shared_scn_scn(shared_rel, scn_id = '0' , check_having_obj_scn_rels= False, B_is_Null = False):

    """
        This function is for generating the shared and un-shared relations between blocks
        Compared to described shared_relation in obj-scn, this one can have pronouns as objects, also we have both the land and trajector descriptiopn
        Also since this the only place that we decribe the relation between blocks and the find_shared find all possible relations there is no need to pop the described relations
        The verb is based on the is_traj value. If the shared part is_traj verb shoudl be singular if not it may be plural.

        The output of this function is traj_objects, relation, and land_object description, alongside their annotation. 
        Check_with means if the block_id object can have with relation or not
        We also check if it can have 
    """
    global all_objects_data, described_objects, described_relations, recent_objs
    global sp_ind, sp_type, traj, traj_obj_id, land_obj_id, land
    relation_text = ''
    _recent_objs = []
    is_traj = shared_rel["is_traj"]
    
    land_obj, traj_obj = [], []
    B0_value = ""
    if shared_rel["has_common_rel"] == True:

         
        if is_traj:
            traj_desc = select_vocab("block")+" "+ select_vocab("block_name",key = shared_rel["keys"][0][0]) if [shared_rel["keys"][0][0]] != recent_objs else select_pronoun()
            
            
            extra_relation = ""
            if shared_rel["keys"][0][0] == scn_id: 
                
                if B_is_Null:
                    
                    """
                        we can have scn_obj rels
                        If this a new block we add the definition sentence or phrase:
                        "We have another block" "called --" "let's call it --"
                        "There is another block"
                        + "which" 
                        or + ". It is .. "

                        Simiplify B0_call_block and only return another or a block called ....
                    """
                    _, new_block_mention = B0_call_block(scn_id, is_traj = True)
                    traj_desc = new_block_mention

                previous_len_of_land = len(land)# we want to see how many objects are added afer BD_obj 
                extra_relation = BD_obj(scn_id, between_blocks_relations= True)
                if extra_relation:
                    num_of_added_obj = len(land) - previous_len_of_land
                    # the extra relation and obejct are landmark so we add another one to trajector
                    traj_obj_id += [[scn_id]]*num_of_added_obj
                    traj += [[traj_desc]]*num_of_added_obj # repeat the traj as the trajector of the new triplet we added
                else: extra_relation = ""

            # traj_obj = [B0_value + extra_relation] if B0_value else [traj_desc+extra_relation]
            traj_obj = [traj_desc+extra_relation]
            traj += [[traj_desc]]*len(shared_rel["keys"])
            traj_obj_id +=[[shared_rel["keys"][0][0]]]*len(shared_rel["keys"])
            described_objects[shared_rel["keys"][0][0]] = []
            _recent_objs = [shared_rel["keys"][0][0]]
                  

        else:
            land_desc =  select_vocab("block")+" "+ select_vocab("block_name",key = shared_rel["keys"][0][1]) if [shared_rel["keys"][0][1]] != recent_objs else select_pronoun(is_subject= False)
            extra_relation = ""

            if shared_rel["keys"][0][1] == scn_id: # we can have scn_obj rels

                if B_is_Null:
                    
                    """
                        "another block"
                    """
                    _, new_block_mention = B0_call_block(scn_id)
                    land_desc = new_block_mention

                previous_len_of_land = len(land)# we want to see how many objects are added afer BD_obj 
                extra_relation = BD_obj(scn_id, between_blocks_relations= True)
                if extra_relation:
                    num_of_added_obj = len(land) - previous_len_of_land
                    # the extra relation and obejct are landmark so we add another one to trajector
                    traj_obj_id += [[scn_id]]*num_of_added_obj
                    traj += [[land_desc]]*num_of_added_obj # repeat the traj as the trajector of the new triplet we added
                else: extra_relation = ""

            land_obj = [land_desc+extra_relation]
            land += [[land_desc]]*len(shared_rel["keys"])
            land_obj_id +=[[shared_rel["keys"][0][1]]]*len(shared_rel["keys"])
            described_objects[shared_rel["keys"][0][1]] = []

            
                
        #check the verb singularity
        # if is_traj: verb_is_singular = True
        # elif len(shared_rel["keys"]) == 1:  verb_is_singular = True
        # else: verb_is_singular = False

        #start describing the objects and their shared relations
        sp_ind += check_verb(shared_rel["spatial_indicators"], is_singular=True )*len(shared_rel["keys"])
        sp_type += shared_rel["relation"]*len(shared_rel["keys"])
        
        relation_text = check_verb(shared_rel["relation_text"], is_singular=True) #check verb correct the plural or singular verbs

        #shared_part    
        
        for i_ind, i in enumerate(shared_rel["keys"]):

            expanded_rel = expand_rel_describtion(shared_rel["relation"][0])
            if i not in described_relations:
                described_relations[i] = expanded_rel
            else:
                described_relations[i] += expanded_rel
            
            for r in expanded_rel:
                if i in scn_rels and r in scn_rels[i]:
                    scn_rels[i].remove(r)

            if i in scn_rels and scn_rels[i] == []: scn_rels.pop(i,None)

            if is_traj: # we have multiple land
                if i[1] in described_objects:
                    obj_desc = select_vocab("block")+" "+ select_vocab("block_name",key = i[1]) if [i[1]] != recent_objs else select_pronoun(is_subject=False)
                else: _, obj_desc = B0_call_block(i[1])
                land_obj += [obj_desc]
                land += [[obj_desc]]
                land_obj_id += [[i[1]]]
                described_objects[i[1]]=[]

            else: # we have multiple traj
                if i[0] in described_objects:   
                    obj_desc = select_vocab("block")+" "+ select_vocab("block_name",key = i[0]) if [i[0]] != recent_objs else select_pronoun()
                else: _,obj_desc = B0_call_block(i[0])
                traj_obj += [obj_desc]
                traj += [[obj_desc]]
                traj_obj_id += [[i[0]]]
                _recent_objs += [i[0]]
                described_objects[i[0]]=[]
        #describing the shared part
        
    

    else:  #elif shared_rel["has_common_key"] == True or only one object has the relation and is the trajector or landmark of this relation (based on is_traj value)
        

        if is_traj:
            traj_desc = select_vocab("block")+" "+ select_vocab("block_name",key = shared_rel["keys"][0][0]) if [shared_rel["keys"][0][0]] != recent_objs else select_pronoun()
            extra_relation = ""

            if shared_rel["keys"][0][0] == scn_id: # we can have scn_obj rels

                if B_is_Null:
                    
                    """
                        If this a new block we add the definition sentence or phrase:
                        "We have another block" "called --" "let's call it --"
                        "There is another block"
                        + "which" 
                        or + ". It is .. "

                        make it simple like land part
                    """
                    _, new_block_mention = B0_call_block(scn_id, is_traj = True)
                    traj_desc = new_block_mention

                previous_len_of_land = len(land)# we want to see how many objects are added afer BD_obj 
                extra_relation = BD_obj(scn_id, between_blocks_relations= True)
                if extra_relation:
                    num_of_added_obj = len(land) - previous_len_of_land
                    # the extra relation and obejct are landmark so we add another one to trajector
                    traj_obj_id += [[scn_id]]*num_of_added_obj
                    traj += [[traj_desc]]*num_of_added_obj # repeat the traj as the trajector of the new triplet we added
                else: extra_relation = ""

            # traj_obj = [B0_value + extra_relation] if B0_value else [traj_desc+extra_relation]
            traj_obj = [traj_desc+extra_relation]
            traj += [[traj_desc]]*len(shared_rel["keys"])
            traj_obj_id +=[[shared_rel["keys"][0][0]]]*len(shared_rel["keys"])
            described_objects[shared_rel["keys"][0][0]] = []
            _recent_objs = [shared_rel["keys"][0][0]]


        else:
            land_desc =  select_vocab("block")+" "+ select_vocab("block_name",key = shared_rel["keys"][0][1]) if [shared_rel["keys"][0][1]] != recent_objs else select_pronoun(is_subject=False)
            
            extra_relation = ""
            if shared_rel["keys"][0][1] == scn_id: # we can have scn_obj rels

                if B_is_Null:
                    
                    """
                        "another block"
                    """
                    _, new_block_mention = B0_call_block(scn_id)
                    land_desc = new_block_mention

                previous_len_of_land = len(land)# we want to see how many objects are added afer BD_obj 
                extra_relation = BD_obj(scn_id, between_blocks_relations= True)
                if extra_relation:
                    num_of_added_obj = len(land) - previous_len_of_land
                    # the extra relation and obejct are landmark so we add another one to trajector
                    traj_obj_id += [[scn_id]]*num_of_added_obj
                    traj += [[land_desc]]*num_of_added_obj # repeat the traj as the trajector of the new triplet we added
                else: extra_relation = ""

            land_obj = [land_desc+extra_relation]
            land += [[land_desc]]*len(shared_rel["keys"])
            land_obj_id +=[[shared_rel["keys"][0][1]]]*len(shared_rel["keys"])
            described_objects[shared_rel["keys"][0][1]] = []

            

        #the verb remain singular since each has own relations
        sp_ind += check_verb(shared_rel["spatial_indicators"], is_singular=True)
        sp_type += shared_rel["relation"]
        relation_text = check_verb(shared_rel["relation_text"], is_singular=True)
        
        obj_rel_description = ''

        for i_ind, i in enumerate(shared_rel["keys"]):
            
            """
                traj, traj_obj_id, described_objects, described_rel, obj_description
            """
            expanded_rel = expand_rel_describtion(shared_rel["relation"][i_ind])
            if i not in described_relations:
                described_relations[i] = expanded_rel
            else:
                described_relations[i] += expanded_rel
            
            for r in expanded_rel:
                if i in scn_rels and r in scn_rels[i]:
                    scn_rels[i].remove(r)
            if i in scn_rels and scn_rels[i] == []: scn_rels.pop(i,None)


            if is_traj: #describe different lands
                land_obj_id += [[i[1]]]
                # described_objects[i[1]] = []
                if i[1] in described_objects:
                    obj_desc = select_vocab("block")+" "+ select_vocab("block_name",key = i[1]) if [i[1]] != recent_objs else select_pronoun(is_subject=False)
                else: _,obj_desc = B0_call_block(i[1])
                land_obj += [obj_desc] 
                land += [[obj_desc]]
                if obj_rel_description: obj_rel_description+= ', '
                obj_rel_description += relation_text[i_ind]+' '+obj_desc 
                described_objects[i[1]] = []

                
            else: #describe different tra
                traj_obj_id += [[i[0]]]
                _recent_objs += [i[0]]
                # described_objects[i[0]] = []
                if i[0] in described_objects:
                    obj_desc = select_vocab("block")+" "+ select_vocab("block_name",key = i[0]) if [i[0]] != recent_objs else select_pronoun()
                else: _,obj_desc = B0_call_block(i[0])
                traj_obj += [obj_desc]
                traj += [[obj_desc]]
                if obj_rel_description: obj_rel_description+= ', '
                obj_rel_description += obj_desc+' '+relation_text[i_ind] 
                described_objects[i[0]] = []


    recent_objs = _recent_objs    

    return {
            "land_obj_desc": land_obj, 
            "traj_obj_desc": traj_obj,
            # "traj": traj, 
            # "land": land, 
            # "traj_obj_id": traj_obj_id,
            # "land_obj_id": land_obj_id,
            # "sp_ind": sp_ind,
            # "sp_type": sp_type,
            "relation_text": relation_text,
            # "new_block_description" : B0_value
            # "obj_scn_rel": can_have_obj_scn_rel
            }


def limit_the_list(main_list, block_id, allowed_ids):

    new_list = {}

    for key in main_list:
        if (allowed_ids and key[0] in allowed_ids and key[1] in allowed_ids) and block_id in key:
            new_list[key] = main_list[key]
    return new_list

def limit_the_list_obj(main_list, obj_id = None,  block_id = None, allowed_ids  = []):

    new_list = {}

    for key in main_list:
        if (not allowed_ids or (key[0] in allowed_ids and key[1] in allowed_ids)) and (not block_id or block_id in key) and (not obj_id or obj_id in key):
            new_list[key] = main_list[key]
    return new_list


def find_shared_rel(
    searching_list=None,
    fixed_traj_id=None,
    fixed_land_id=None,
    fixed_rel=None,
    relation_return=False,
    num_objects=None,
    check_with = False
):

    """
    we want to find all shared relations between different keys, like (1,2): LEFT, ABIVE and (1,0): LEFT, ABOVE
    fixed_traj: serach between keys with passed traj
    fixed_land: serach between keys with passed land
    fixed_rel: Only check the sharing this relation.

    We create a matrix with each object as key, then add the relation between each key in the matrix.
    The diameters are null since no object has relation with itself.
    checking row 0 means checking all key with 0 as trajector (head), and all other objects as land.
    """

    # relation_list = {}
    # How to the number of total objects
    if num_objects:
        relation_matrix = [[[] for _ in range(num_objects) ] for _ in range(num_objects)]
    else:
        relation_matrix = [[[] for _ in range(len(searching_list)*2) ] for _ in range(len(searching_list)*2)]

    id_ind = []

    for key in searching_list:
        if key[0] not in id_ind: id_ind += [key[0]]
        if key[1] not in id_ind: id_ind += [key[1]]
        key_0_ind = id_ind.index(key[0])
        key_1_ind = id_ind.index(key[1])
        if (
            fixed_traj_id
            and key[0] == fixed_traj_id
            and fixed_land_id
            and key[1] == fixed_land_id
        ):
            # if fixed_rel == None or any(rel["relation_type"] in _fixed_rel and rel["relation_property"] in _fixed_rel  for rel in searching_list[key] for _fixed_rel in fixed_rel):
            if fixed_rel == None or any(rel["relation_type"] == _fixed_rel for rel in searching_list[key] for _fixed_rel in fixed_rel):
                _, relation_list = generate_relation(
                    searching_list[key], only_list=True, fixed_rel = fixed_rel if fixed_rel else []
                )
                relation_matrix[key_0_ind][key_1_ind] = relation_list
                # relation_list[key] = {'relation_text': all_relation_text, "relation_list": relation_list }
            # traj_2[key] = scn_rels[key]
        elif fixed_traj_id and key[0] == fixed_traj_id:
            # if fixed_rel == None or any(rel["relation_type"] in _fixed_rel and rel["relation_property"] in _fixed_rel  for rel in searching_list[key] for _fixed_rel in fixed_rel):
            if fixed_rel == None or any(rel["relation_type"] == _fixed_rel for rel in searching_list[key] for _fixed_rel in fixed_rel):
                _, relation_list = generate_relation(
                    searching_list[key], only_list=True, fixed_rel = fixed_rel if fixed_rel else []
                )
                relation_matrix[key_0_ind][key_1_ind] = relation_list
                # relation_list[key] = {'relation_text': all_relation_text, "relation_list": relation_list }

        elif fixed_land_id and key[1] == fixed_land_id:
            # if fixed_rel == None or any(rel["relation_type"] in _fixed_rel and rel["relation_property"] in _fixed_rel  for rel in searching_list[key] for _fixed_rel in fixed_rel):
            if fixed_rel == None or any(rel["relation_type"] == _fixed_rel for rel in searching_list[key] for _fixed_rel in fixed_rel):
                _, relation_list = generate_relation(
                    searching_list[key], only_list=True, fixed_rel = fixed_rel if fixed_rel else []
                )
                relation_matrix[key_0_ind][key_1_ind] = relation_list
                # relation_list[key] = {'relation_text': all_relation_text, "relation_list": relation_list }
        elif fixed_traj_id == None and fixed_land_id == None:
            # if fixed_rel == None or any(rel["relation_type"] in _fixed_rel and rel["relation_property"] in _fixed_rel  for rel in searching_list[key] for _fixed_rel in fixed_rel):
            if fixed_rel == None or any(rel["relation_type"] == _fixed_rel for rel in searching_list[key] for _fixed_rel in fixed_rel):
                _, relation_list = generate_relation(
                    searching_list[key], only_list=True, fixed_rel = fixed_rel if fixed_rel else []
                )
                relation_matrix[key_0_ind][key_1_ind] = relation_list
                # relation_list[key] = {'relation_text': all_relation_text, "relation_list": relation_list }
        #else: do nothing
    found_shared_keys = find_shared_part(relation_matrix, id_ind)

    # generate relation text for each
    for shared_part in found_shared_keys:
        if shared_part["has_common_key"]:
            for key_ind, key in enumerate(shared_part["keys"]):
                relation_text, spatial_indicators, need_verb = generate_relation(
                    searching_list[key],
                    fixed_rel=shared_part["relation"][key_ind],
                    return_spatial_indicator=True,
                    check_with = check_with,
                    return_if_need_verb = True
                )
                shared_part["need_verb"] += [need_verb]
                shared_part["relation_text"] += [relation_text]
                shared_part["spatial_indicators"] += [spatial_indicators]
        else:  # if shared_part["has_common_rel"] or none is true
            #TODO check has_common_rel
            #plural for is_traj=False and has shared part
            relation_text, spatial_indicators, need_verb = generate_relation(
                searching_list[shared_part["keys"][0]],
                fixed_rel=shared_part["relation"][0],
                return_spatial_indicator=True,
                check_with = check_with,
                return_if_need_verb = True
            )
            shared_part["need_verb"] = [need_verb]
            shared_part["relation_text"] = [relation_text]
            shared_part["spatial_indicators"] = [spatial_indicators]

    return found_shared_keys


def find_shared_part(matrix_list, matrix_id_to_key):

    """
    It has three recursive phase:
        1) check the matrix to find the maximal commmon relations in each row or column (check matrix and its transpose)
        2) remove the selected relations
        3) update the matrix
    It will continue untill there is no common and we get the single relations.
    """
    maximum_shared = []
    while 1:
        # TODO add shared traj or land without shared rel
        # start with row_wise search for shared_rels
        max_rel, max_row, max_col = [], -1, -1
        max_rel, max_row = check_matrix_for_common_part(matrix_list, max_rel, max_row)

        # check column
        trans_matrix_list = np.transpose(np.array(matrix_list)).tolist()
        max_rel, max_col = check_matrix_for_common_part(
            trans_matrix_list, max_rel, max_col
        )
        if max_col != -1:
            max_row = -1

        max_rel = max_rel.copy()
        # if we have the common rel, add that to the maximum shared, and remove the rel from the main matrix
        if max_rel != []:
            shared_keys = []
            is_traj = False
            if max_row != -1:
                is_traj = True
                for col_ind, col in enumerate(matrix_list[max_row]):               
                    if col == max_rel:
                        shared_keys += [(matrix_id_to_key[max_row], matrix_id_to_key[col_ind])]
                        matrix_list[max_row][col_ind] = []
                    # for rel in col:
                    #     if rel in max_rel:
                    #         shared_keys += [(matrix_id_to_key[max_row], matrix_id_to_key[col_ind])]
                    #         matrix_list[max_row][col_ind].remove(rel)
            elif max_col != -1:
                for row_ind, row in enumerate(trans_matrix_list[max_col]):
                    if row == max_rel:
                        shared_keys += [(matrix_id_to_key[row_ind], matrix_id_to_key[max_col])]
                        matrix_list[row_ind][max_col] = []
                    # for rel in row:
                    #     if rel in max_rel:
                    #         shared_keys += [(matrix_id_to_key[row_ind], matrix_id_to_key[max_col])]
                    #         matrix_list[row_ind][max_col].remove(rel)

            maximum_shared += [
                {
                    "is_traj": is_traj,
                    "has_common_rel": True,
                    "has_common_key": False,
                    "keys": shared_keys,
                    "relation": [max_rel],
                    "relation_text": [],
                    "spatial_indicators": [],
                    "need_verb" : []
                }
            ]

        # if we cannot find any common rel, first check shared keys and if don't find anything check each individual rel will be added to the list
        else:  # max_rel == []:
            # first check keys

            max_num, max_row, max_col = 0, -1, -1
            max_num, max_row = check_matrix_for_common_key(
                matrix_list, max_num, max_row
            )
            max_num, max_col = check_matrix_for_common_key(
                trans_matrix_list, max_num, max_col
            )
            if max_col != -1:
                max_row = -1

            if max_num:
                _keys = []
                _rel = []
                is_traj = False
                if max_row != -1:
                    is_traj = True
                    for col_ind, col in enumerate(matrix_list[max_row]):
                        if col and len(col) == 1:
                            _keys += [(matrix_id_to_key[max_row], matrix_id_to_key[col_ind])]
                            _rel += [col]
                            matrix_list[max_row][col_ind] = []
                            if len(_rel) == 2: break
                        # for rel in col:
                        #     _keys += [(matrix_id_to_key[max_row], matrix_id_to_key[col_ind])]
                        #     _rel += [[rel]]
                        #     matrix_list[max_row][col_ind] = []
                elif max_col != -1:
                    for row_ind, row in enumerate(trans_matrix_list[max_col]):
                        # for rel in row:
                        if row and len(row) == 1:
                            _keys += [(matrix_id_to_key[row_ind], matrix_id_to_key[max_col])]
                            _rel += [row]
                            matrix_list[row_ind][max_col] = []
                            if len(_rel) == 2: break
                        # for rel in row:
                        #     _keys += [(matrix_id_to_key[row_ind], matrix_id_to_key[max_col])]
                        #     _rel += [[rel]]
                        #     matrix_list[row_ind][max_col] = []

                maximum_shared += [
                    {
                        "is_traj": is_traj,
                        "has_common_rel": False,
                        "has_common_key": True,
                        "keys": _keys,
                        "relation": _rel,
                        "relation_text": [],
                        "spatial_indicators": [],
                        "need_verb" : []
                    }
                ]

            # if no shared key go for individual
            else:
                for row_ind, row in enumerate(matrix_list):
                    for col_ind, col in enumerate(row):
                        if matrix_list[row_ind][col_ind]:
                            maximum_shared += [
                                {
                                    "is_traj": True,
                                    "has_common_rel": False,
                                    "has_common_key": False,
                                    "keys": [(matrix_id_to_key[row_ind], matrix_id_to_key[col_ind])],
                                    "relation": [matrix_list[row_ind][col_ind]],
                                    "relation_text": [],
                                    "spatial_indicators": [],
                                    "need_verb" : []
                                }
                            ]
                            matrix_list[row_ind][col_ind] = []

                break

    return maximum_shared


def check_matrix_for_common_part(matrix_list, max_rel, max_row):

    # max_rel, max_row = [], -1
    _max_row = -1
    for row_ind, row in enumerate(matrix_list):
        num_shared, shared_rel = extract_shared_part(row)
        if shared_rel:
            if num_shared > len(max_rel) and num_shared > 1:
                max_rel = shared_rel
                _max_row = row_ind

    if _max_row != -1:
        max_row = _max_row

    return max_rel, max_row


def check_matrix_for_common_key(matrix_list, max_num, max_row):

    # max_rel, max_row = [], -1
    _max_row = -1
    for row_ind, row in enumerate(matrix_list):
        num_shared_key = extract_shared_key(row)
        if num_shared_key:
            if num_shared_key > max_num:
                max_num = num_shared_key
                _max_row = row_ind

    if _max_row != -1:
        max_row = _max_row

    return max_num, max_row


def extract_shared_part(relation_list):

    _max = 1
    max_rel = []
    
    if len(relation_list) - relation_list.count([]) < 2 :
        return _max, max_rel

    num_of_shared = {}
    for rel in relation_list:
        if rel:
            if tuple(rel) not in num_of_shared: num_of_shared[tuple(rel)] = relation_list.count(rel)
    
    #find the highest
    
    for i in num_of_shared:
        if num_of_shared[i] > _max : 
            _max = num_of_shared[i]
            max_rel = list(i)
        elif num_of_shared[i] == _max and _max > 1 and len(i) > len(max_rel):
            _max = num_of_shared[i]
            max_rel = list(i)


    return _max,max_rel


def extract_shared_key(relation_list):

    _common_key = 0
    
    if len(relation_list) - relation_list.count([]) < 2:
        return _common_key

    #compare to the below one this one onle consider 
    _common_key = len([r for r in relation_list if len(r) == 1])
    #The below one can have a complex and confusing relation description
    #e.g, the medium yellow apple is to the north of and touches and medium orange apple number two touches medium orange apple number one.
    # _common_key = len([r for r in relation_list if r != []])

    return _common_key


"""
    ************************************************************************
    functions fors describing objects after describing the main block (P)
    it can be describing relation between objects --> Q
    or describing an object for the first time in this block --> U
    ************************************************************************
"""

def P(block_id):

    """
        In this function we want tod describe the remaining obj_scn relations and obj_obj relations
        1) Start randomly with one of these, remove the described rel from the main list, until the list become empty.
            - if obj_obj:
                Select the first key in obj_obj.
                Find the shared rels only over the objs_rels wich has these traj or landmark keys.
                Select the first one and describe it using the correct proun. 
                    If the object_scn relation is not defined if it's possible describe the obj_scn in the same sentence.
                                                            If not add the object id to que of describing obj-scn rels
            - If obj_scn:
                if the relation in NTPP or NTPPI, check the shared_rel for that and describe it.
        
        For mention of some objects which described before we can use their rel to another obj to unified it.

    """

    global objs_rels, scn_objs, obj_scn_queue
    global traj, traj_obj_id, land, land_obj_id, sp_ind, sp_type, recent_objs
    _recent_objs = []


    sen = ""

    if block_id not in described_objects:
        sen += B_id(block_id)

    _obj_rels = objs_rels[block_id] if block_id in objs_rels else {}
    _obj_scns = scn_objs[block_id] if block_id in scn_objs else {}

    while _obj_rels or _obj_scns:

        # x == 1: obj_obj rels, x == 0, obj_scn rels

        if _obj_scns == {} and _obj_rels != {} : x = 1
        elif (_obj_rels == {} and _obj_scns != {}) or obj_scn_queue: x = 0 
        else: x = random.choice([0,1])

        #describe obj_obj
        if x: 
            # select first_key
            key = list(_obj_rels.keys())[0]

            # select randomly : x = 1 :check shared_rel x ==0: schoose exact triplet with fixed land and traj
            y =  0 if len(_obj_rels[key]) > 1 else random.choice([0,1])
            if y: #Has more than one relation
                if random.choice([0,1]):
                    shared_rels = find_shared_rel(searching_list= _obj_rels, fixed_traj_id= key[0])
                else:
                    shared_rels = find_shared_rel(searching_list= _obj_rels, fixed_land_id = key[1])

            else: 
                shared_rels = find_shared_rel(searching_list= _obj_rels, fixed_traj_id= key[0], fixed_land_id = key[1])

            for shared_rel in shared_rels:
                
                relation_need_verb = shared_rel["need_verb"]
                shared_info = describe_shared_obj_obj(shared_rel, block_id=block_id) 
                #concat the information, create the sentence, create the annotation
                _sen = ''
                
                if shared_rel["has_common_key"]:

                    if shared_rel["is_traj"]:
                        #connect the obj and rel
                        obj_desc = ''
                        for ind, desc in enumerate(shared_info["land_obj_desc"]):
                            if obj_desc: obj_desc += ', '
                            if relation_need_verb[ind]:
                                obj_desc += check_verb("[is/are]", is_singular=True)+" "+shared_info["relation_text"][ind]+ " " +desc
                            else:
                                obj_desc += shared_info["relation_text"][ind]+ " " +desc
                        land_obj = add_and(obj_desc)
                        traj_obj = shared_info["traj_obj_desc"][0]
                    else:
                        obj_desc = ''
                        for ind, desc in enumerate(shared_info["traj_obj_desc"]):
                            if obj_desc: obj_desc += ', '
                            if relation_need_verb[ind]:
                                obj_desc += desc +" "+check_verb("[is/are]", is_singular=True)+" "+ shared_info["relation_text"][ind]
                            else:
                                obj_desc += desc +" "+ shared_info["relation_text"][ind]
                        traj_obj = add_and(obj_desc)
                        land_obj = shared_info["land_obj_desc"][0]

                    #create sentence
                    _sen = start_word(traj_obj)+" "+land_obj+'. '
                    create_annotation(_sen)
                    sen += _sen
                
                else: #if shared_rel["has_common_rel"]: or no common

                    if shared_rel["is_traj"]:
                        #connect the shared part
                        obj_desc = ''
                        for desc in shared_info["land_obj_desc"]:
                            if obj_desc: obj_desc += ', '
                            obj_desc += desc
                        land_obj = add_and(obj_desc)
                        traj_obj = shared_info["traj_obj_desc"][0]
                    else:
                        obj_desc = ''
                        for desc in shared_info["traj_obj_desc"]:
                            if obj_desc: obj_desc += ', '
                            obj_desc += desc
                        traj_obj = add_and(obj_desc)
                        land_obj = shared_info["land_obj_desc"][0]
                    
                    if relation_need_verb[0]:
                        #We need to add [is/are] verb and also have sp_id+land+traj sentences
                        
                        h = 0 if shared_info["cannot_change_order"] else random.choice([0,1,1])
                        # if h: # reorder the description
                        #     verb_singularity = True if len(shared_info["traj_obj_desc"]) <2 else False
                        # else: 
                        #     verb_singularity = True if len(shared_info["land_obj_desc"]) <2 else False
                        verb_singularity = False if shared_rel["has_common_rel"] else True


                        verb_text = check_verb("[is/are]", is_singular= verb_singularity) 
                        if h:
                            _sen = (start_word(shared_info["relation_text"][0])
                                    +" "
                                    +land_obj
                                    +" "
                                    +("there " if random.choice([0,1]) else "")
                                    + verb_text
                                    +" "
                                    +traj_obj+". "
                                    )
                        else:
                            _sen = start_word(traj_obj)+" "+verb_text +" "+shared_info["relation_text"][0]+" "+land_obj+'.'

                    else:    
                        #create sentence
                        _sen = start_word(traj_obj)+" "+shared_info["relation_text"][0]+" "+land_obj+'.'
                        
                    create_annotation(_sen)
                    sen += _sen

        #describe obj_scn relation            
        else:

            """
                First if obj_scn_queue has something we want to describe those
                    first we only consider the scn_objs rels that has the obj in queue and collect the shared_rel list
                if not just search the scn_obj[block_id] and choose the first one
                TODO: if the relation is NTPP or NTPPI, also consider inplace obj-obj relation
            """
            # obj_block_list = scn_objs[block_id] if block_id in scn_objs else None
            # if obj_block_list == None: print("ERRROOORRR: IT DOESN'T HAVE THE BLOCK ID IN SCN_OBJ BUT STILL COMES HERE." )
            
            if obj_scn_queue:
                for obj in obj_scn_queue:
                    _sen =""
                    shared_rels = find_shared_rel(searching_list= limit_the_list_obj(_obj_scns, block_id  = block_id, obj_id = obj))

                    for shared_rel in shared_rels:
                        #is_traj is for objects not block
                        is_traj = True if shared_rel["keys"][0][1] == block_id else False

                        block_description = select_pronoun(is_subject= False if is_traj else True) if [block_id] == recent_objs else select_vocab("block")+" "+select_vocab("block_name", key = block_id)
                        obj_scn_rel = describe_shared_obj_scn(shared_rel, scn_id = block_id, is_traj = is_traj)
                        if is_traj: #block is landmark
                            land += [[block_description]] *len(traj)
                            land_obj_id += [[block_id]] * len(traj)
                            _sen += start_word(obj_scn_rel)+" "+ block_description+". "
                            
                        else: # block is trajector
                            _recent_objs = [block_id]
                            traj += [[block_description]] *len(land)
                            traj_obj_id += [[block_id]] * len(land)
                            _sen += start_word(block_description)+" "+ obj_scn_rel+". "

                        if _recent_objs: recent_objs = _recent_objs
                        #else: recent object is filled in described_shared_obj_scne
                        create_annotation(_sen)
                        sen += _sen
                obj_scn_queue = []


            else:
                _sen =""
                shared_rels = find_shared_rel(searching_list= limit_the_list_obj(_obj_scns, block_id  = block_id))
                
                #is_traj is for objects not block
                is_traj = True if shared_rels[0]["keys"][0][1] == block_id else False

                block_description = select_pronoun(is_subject= False if is_traj else True) if [block_id] == recent_objs else select_vocab("block")+" "+select_vocab("block_name", key = block_id)
                obj_scn_rel = describe_shared_obj_scn(shared_rels[0], scn_id = block_id, is_traj = is_traj)
                if is_traj: #block is landmark
                    land += [[block_description]] *len(traj)
                    land_obj_id += [[block_id]] * len(traj)
                    _sen += start_word(obj_scn_rel)+" "+ block_description+". "
                    
                else: # block is trajector
                    _recent_objs = [block_id]
                    traj += [[block_description]] *len(land)
                    traj_obj_id += [[block_id]] * len(land)
                    _sen += start_word(block_description)+" "+ obj_scn_rel+". "

                if _recent_objs: recent_objs = _recent_objs
                #create sentence
                create_annotation(_sen)
                sen += _sen

        _obj_rels = objs_rels[block_id] if block_id in objs_rels else {}
        _obj_scns = scn_objs[block_id] if block_id in scn_objs else {}
        sen += ' '

    return sen


def obj_desc(obj):  # an element . describe other features of object
    features, article = "", 0
    global G_size, G_color, G_type, G_scene_rel

    for l, ch in enumerate(obj):
        tag_name = ""  # name of the feature
        if ch == "" and random.choice([0, 1, 1, 1, 1]):
            if l == 0 or l == 4:
                continue
            if l == 1:
                features += " and " if features else " "
                features += size(scn_objs[block_id][obj[0]][1]["size"])
            elif l == 2:
                features += " and " if features else " "
                features += color(scn_objs[block_id][obj[0]][1]["color"])
            elif l == 3:
                features += " " + shape(scn_objs[block_id][obj[0]][1]["type"])
                article = 1
            # elif l == 4: features+= Rel(scn_rels[block_id][obj[0]][0])

    if article:
        features = " a" + features

    update_checked_obj_sc(obj[0], G_size, G_color, G_type, G_scene_rel)
    G_size, G_color, G_type, G_scene_rel = "", "", "", ""
    return features


def obj_ide(obj):  # id of the object . The identification description for an object

    global traj, land, sp_ind, traj_obj_id, land_obj_id
    sen = ""
    obj_sha_name = sh_ob_single()
    s = []
    uniq_attr = unique_attr_check()
    ind_check = ind_check_obj(obj)
    uniq_id = ""
    s = [0] * 6
    for l, c in enumerate(checked_obj_sc[ind_check]):
        if c != "" and l != 0:
            if l != 4 and l != 5:
                # considering mentioned just by unique features

                s[l] = 1
                # always with all attributes if random.choice([1,1,0,1,1]): s[l]=1
            elif l == 4:
                continue
            #                 if s.count(1) == 0: #there is not any attribute till now
            #                     s[l] = 1
            else:
                s[l] = 1  # l == 5

    sen1, sen2, sen3 = "", "", ""
    if s[1] == 1:
        sen1 += checked_obj_sc[ind_check][1]["size"] + " "
    if s[2] == 1:
        sen1 += checked_obj_sc[ind_check][2]["color"] + " "
    if s[3] == 1:
        obj_sha_name = ""
        sen1 += checked_obj_sc[ind_check][3]["type"] + " "
    if s[4] == 1:
        sen2 += " which is " + checked_obj_sc[ind_check][4]["rel"] + " the block "
    if s[5] == 1:
        sen3 += " number " + object_num(checked_obj_sc[ind_check][5]) + " "

    # has touching relation
    #     if s[4] == 1:
    #         traj += [['the '+sen1 + obj_sha_name+sen3]]
    #         land += [['the block']]
    #         sp_ind += [[checked_obj_sc[ind_check][4]['rel']]]
    #         traj_obj_id += [[obj]]
    #         land_obj_id += [[100+ block_id]]

    sen += sen1 + obj_sha_name + sen3 + sen2
    return sen


def new_obj(obj_in_scn_rel, obj, temp=""):  # obj -> number

    global G_size, G_color, G_type, G_scene_rel
    s = [1, 1, 1]

    Size = " " + size(obj_in_scn_rel[obj][1]["size"]) if s[0] else ""
    Color = " " + color(obj_in_scn_rel[obj][1]["color"]) if s[1] else ""
    Shape = " " + shape(obj_in_scn_rel[obj][1]["type"])

    update_checked_obj_sc(obj, G_size, G_color, G_type, G_scene_rel, temp=temp)
    G_size, G_color, G_type, G_scene_rel = "", "", "", ""
    return Size + Color + Shape


def ObjP(s="", c="", sh=""):

    Size = " " + size(s) if s else ""
    Color = " " + color(c) if c else ""
    Shape = " " + shape(sh) if G_type else " shape"

    return Size + Color + Shape

def describe_shared_obj_obj(shared_rel, block_id, obj_id = None):

    global sp_ind, sp_type, traj, traj_obj_id, land_obj_id, land
    global objs_rels, all_objects_data, described_objects, described_relations, recent_objs, obj_scn_queue

    _recent_objs = []
    is_traj = shared_rel["is_traj"]
    traj_obj, land_obj = [], []
    cannot_change_order = False
    #shared traj or land
    """
        For describing the shared traj or land mark:
        first by checking the shared_rel["is_traj] we can find that which part is shared or described solely.
        Then we want a object description for that:
        1) If the object is equal to recent_objs-> use pronouns
        2) elif object is in the described_objs: use full name and select correct identifier
        3) else it is a new object.
            3.1) Use in place obj_rel relation (if NTPP) 
            3.2) use a pronoun and in the next sentence describe the obj_scn relation in other cases.

    """
    if is_traj:
        traj_id = shared_rel["keys"][0][0] # the key[0] in all shared keys are the shared part.

        has_extra = False
        if [traj_id] == recent_objs:
            traj_desc = select_pronoun(is_block=False)
            main_obj_desc = traj_desc

        elif traj_id in described_objects:
            traj_desc, _extra_annotation = predifined_description_of_objects(traj_id, no_nesting = True if shared_rel["has_common_key"] else False, forbiden_keys = shared_rel["keys"])
            main_obj_desc = _extra_annotation["traj"]
            if "sp_ind" in _extra_annotation: #it has extra annotation
                traj += [[_extra_annotation["traj"]]]
                traj_obj_id += [[traj_id]]
                land += [[_extra_annotation["land"]]]
                sp_ind += [_extra_annotation["sp_ind"]] # already has []
                sp_type += [[_extra_annotation["sp_type"]]]
                land_obj_id += [[_extra_annotation["land_id"]]]

            # choose_identifier(traj_id) +" "+all_objects_data[traj_id]["full_name"]
        else: #It is a new described object
            
            obj_scn_rel = find_shared_rel(searching_list=scn_objs[block_id], fixed_land_id= traj_id, fixed_rel = ["NTPPI", "TPPI"])
            # obj_scn_rel = []
            
            if obj_scn_rel:
                if block_id in described_objects:
                    block_name = select_vocab("block")+" "+ select_vocab("block_name",key = block_id) if [block_id] != recent_objs else select_pronoun()
                else: 
                    _, block_name = B0_call_block(block_id)

                # has_extra = True
                cannot_change_order = True
                find_extra_rel = describe_shared_obj_scn(obj_scn_rel[0], scn_id = block_id, is_traj = False , check_with= False)
                main_obj_desc = land[-1][0]
                traj_desc = block_name+" "+find_extra_rel+" which "

                
                traj_obj_id += [[block_id]]
                traj += [[block_name]]

            else:
                if any(sim_obj in described_objects for sim_obj in all_objects_data[traj_id]["similar_objects"]):
                    traj_desc = choose_identifier(traj_id, text = all_objects_data[traj_id]["general_name"], another= True) +all_objects_data[traj_id]["general_name"]
                    update_number_in_name(traj_id)
                else:
                    traj_desc = choose_identifier(traj_id, use_general= True) +all_objects_data[traj_id]["general_name"]

                # traj_desc = choose_identifier(traj_id) +" "+all_objects_data[traj_id]["full_name"]
                main_obj_desc = traj_desc
                obj_scn_queue += [traj_id]
                

        traj_obj =  [traj_desc]
        # traj += [[main_obj_desc]]*len(shared_rel["keys"])
        # traj_obj_id +=[[traj_id]]*len(shared_rel["keys"])
        described_objects[traj_id] = []
        _recent_objs = [traj_id]
                

    else:
        land_id = shared_rel["keys"][0][1] # the key[0] in all shared keys are the shared part.

        has_extra = False
        if [land_id] == recent_objs:
            land_desc = select_pronoun(is_subject= False, is_block=False)
            main_obj_desc = land_desc
        elif land_id in described_objects:
            # land_desc = choose_identifier(land_id) +" "+all_objects_data[land_id]["full_name"]
            land_desc, _extra_annotation = predifined_description_of_objects(land_id, no_nesting = True if shared_rel["has_common_key"] else False, forbiden_keys = shared_rel["keys"])
            main_obj_desc = _extra_annotation["traj"]
            if "sp_ind" in _extra_annotation: #it has extra annotation
                traj += [[_extra_annotation["traj"]]]
                traj_obj_id += [[land_id]]
                land += [[_extra_annotation["land"]]]
                sp_ind += [_extra_annotation["sp_ind"]] # already has []
                sp_type += [[_extra_annotation["sp_type"]]]
                land_obj_id += [[_extra_annotation["land_id"]]]

        else: #It is a new described object
            
            obj_scn_rel = find_shared_rel(searching_list=scn_objs[block_id], fixed_traj_id= land_id, fixed_rel = ["NTPP"])

            if obj_scn_rel:

                if block_id in described_objects:
                    block_name = select_vocab("block")+" "+ select_vocab("block_name",key = block_id) if [block_id] != recent_objs else select_pronoun()
                else: 
                    _, block_name = B0_call_block(block_id)

                # has_extra = True
                cannot_change_order = True
                find_extra_rel = describe_shared_obj_scn(obj_scn_rel[0], scn_id = block_id, is_traj = True , check_with= False, has_which = True)
                main_obj_desc = traj[-1][0]
                land_desc = find_extra_rel+" "+ block_name
                
                land_obj_id += [[block_id]]
                land += [[block_name]]

            else:
                if any(sim_obj in described_objects for sim_obj in all_objects_data[land_id]["similar_objects"]):
                    land_desc = choose_identifier(land_id, another=True) +all_objects_data[land_id]["general_name"]
                    update_number_in_name(land_id)
                else:
                    land_desc = choose_identifier(land_id, use_general=True) +all_objects_data[land_id]["general_name"]

                # land_desc = choose_identifier(land_id) +" "+all_objects_data[land_id]["full_name"]
                main_obj_desc = land_desc
                obj_scn_queue += [land_id]
                

        land_obj = [land_desc]
        # land += [[main_obj_desc]]*len(shared_rel["keys"])
        # land_obj_id +=[[land_id]]*len(shared_rel["keys"])
        described_objects[land_id] = []
            
    if shared_rel["has_common_rel"] == True:

        
        #check the verb singularity
        # if is_traj: verb_is_singular = True
        # elif len(shared_rel["keys"]) == 1:  
        #     verb_is_singular = True
        #     # _recent_objs = [shared_rel["keys"][0][1]]
        # else: 
        #     verb_is_singular = False
            # _recent_objs = []

        #start describing the objects and their shared relations
        #for describing the objects first check if they have shared features.
        
        #check if each object in shared_rel_keys has similar attrubutes
        seen_obj, similars = {}, {}
        for i_ind, i in enumerate(shared_rel["keys"]):
            

            expanded_rel = expand_rel_describtion(shared_rel["relation"][0])
            if i not in described_relations:
                described_relations[i] = expanded_rel
            else:
                described_relations[i] += expanded_rel
            
            for r in expanded_rel:
                if block_id in objs_rels and i in objs_rels[block_id] and r in objs_rels[block_id][i]:
                    objs_rels[block_id][i].remove(r)

            if block_id in objs_rels and i in objs_rels[block_id] and objs_rels[block_id][i] == []: objs_rels[block_id].pop(i,None)

            
            traj_land = 1 if is_traj else 0
            if i[traj_land] not in seen_obj:
                similar_num = 1#[j for j in all_objects_data[i[traj_land]]["similar_objects"] if any(j in key for key in shared_rel["keys"]) ]
                similars[i[traj_land]] = [i[traj_land]]
                #if there isn't any described object with shared feature which are not in this shared key
                if all( j not in described_objects or any(j == key[traj_land] for key in shared_rel["keys"]) for j in all_objects_data[i[traj_land]]["similar_objects"]):
                    for j in all_objects_data[i[traj_land]]["similar_objects"]:
                        if ( any(j == key[traj_land] for key in shared_rel["keys"]) and
                            (
                                (i[traj_land] in described_objects and j in described_objects)
                                or
                                (i[traj_land] not in described_objects and j not in described_objects)
                            )
                            ):
                            similar_num += 1#[j]
                            similars[i[traj_land]]+= [j]
                            seen_obj[j] = None

                if similar_num > 1: 

                    cannot_change_order = True
                    if i[traj_land] in described_objects:    
                        # seen_obj[i[traj_land]] = choose_identifier(i[traj_land], text = all_objects_data[i[traj_land]]["general_name"], use_general=True ) + num_to_word(str(similar_num)) +" "+all_objects_data[i[traj_land]]["general_name"]+ "s"
                        seen_obj[i[traj_land]] = num_to_word(str(similar_num)) +" "+all_objects_data[i[traj_land]]["general_name"]+ "s"
                        # update_number_in_name(i[traj_land])
                    else:
                        seen_obj[i[traj_land]] = num_to_word(str(similar_num)) +" "+all_objects_data[i[traj_land]]["general_name"]+ "s"
                        # seen_obj[i[traj_land]] = choose_identifier(i[traj_land], use_general=True)+" "+num_to_word(str(similar_num)) +" "+all_objects_data[i[traj_land]]["general_name"]+ "s"


                else: 
                    if i[traj_land] in described_objects:
                       seen_obj[i[traj_land]], _ = predifined_description_of_objects(i[traj_land], no_nesting = True)

                    else:
                        seen_obj[i[traj_land]] =  choose_identifier(i[traj_land], text = all_objects_data[i[traj_land]]["general_name"] , use_general=True)+all_objects_data[i[traj_land]]["general_name"]

       
        obj_description = []
        num_repeated_rel = 0
        for i_ind, i in enumerate(shared_rel["keys"]):

            if is_traj: #if shared is traj so the lands should be iterated
                if seen_obj[i[1]] != None: #the name comes in the name of the mentioned object
                    # update_number_in_name(i[1])
                    # land += [[seen_obj[seen_obj[i[1]][0]]]]
                # else: #if type(seen_obj[i[1]]) == str: #it is the name
                    land += [[seen_obj[i[1]]]]
                    obj_description += [seen_obj[i[1]]]
                    land_obj_id += [similars[i[1]]]
                    num_repeated_rel += 1

                    #add the main traj
                    traj += [[main_obj_desc]]
                    traj_obj_id +=[[traj_id]]

                if any(sim_obj in described_objects for sim_obj in all_objects_data[i[1]]["similar_objects"]) or seen_obj[i[1]] == None or len(similars[i[1]])>0:
                    update_number_in_name(i[1])
                    cannot_change_order = True
                described_objects[i[1]]=[]

            else:
                
                if seen_obj[i[0]] != None: #the name comes in the name of the mentioned object
                    # traj += [[seen_obj[seen_obj[i[0]][0]]]]
                    # update_number_in_name(i[0])
                # else: #if type(seen_obj[i[0]]) == str: #it is the name
                    traj += [[seen_obj[i[0]]]]
                    obj_description += [seen_obj[i[0]]]
                    traj_obj_id += [similars[i[0]]]
                    _recent_objs += similars[i[0]]
                    num_repeated_rel += 1

                    # add the mian land
                    land += [[main_obj_desc]]
                    land_obj_id +=[[land_id]]
                if any(sim_obj in described_objects for sim_obj in all_objects_data[i[0]]["similar_objects"])  or seen_obj[i[0]] == None or len(similars[i[0]])>0:
                    update_number_in_name(i[0])
                    cannot_change_order = True
                described_objects[i[0]]=[]

        sp_ind += check_verb(shared_rel["spatial_indicators"], is_singular=False)*num_repeated_rel
        sp_type += shared_rel["relation"]*num_repeated_rel
    
        relation_text = check_verb(shared_rel["relation_text"], is_singular=False) #check verb correct the plural or singular verbs


        # obj_desc = ''
        # for desc in obj_description:
        #     if obj_desc: obj_desc += ', '
        #     obj_desc += desc
        # obj_desc = add_and(obj_desc)
        if is_traj: #first object description then relation text
            # relation_text is only one since we have shared rel here.
            land_obj = obj_description
            # sent = obj_desc+' '+relation_text[0]            
        else: #first relation then object description
            traj_obj = obj_description
            # sent = relation_text[0]+' '+obj_desc   

    else:  #elif shared_rel["has_common_key"] == True or only one object has the relation and is the trajector or landmark of this relation (based on is_traj value)
        # the verb remain singular since each has own relations
        sp_ind += check_verb(shared_rel["spatial_indicators"], is_singular=True)
        sp_type += shared_rel["relation"]
        relation_text = check_verb(shared_rel["relation_text"], is_singular=True)

        obj_description = []
        # obj_rel_description = ''

        for i_ind, i in enumerate(shared_rel["keys"]):
            
            """
                traj, traj_obj_id, described_objects, described_rel, obj_description
                if similar feature use "another" TODO or start from the second one use number
                If object is new just use correct identifier and add the object to the queue
            """
            expanded_rel = expand_rel_describtion(shared_rel["relation"][i_ind])
            if i not in described_relations:
                described_relations[i] = expanded_rel
            else:
                described_relations[i] += expanded_rel

            for r in expanded_rel:
                if block_id in objs_rels and i in objs_rels[block_id] and r in objs_rels[block_id][i]:
                    objs_rels[block_id][i].remove(r)

            if block_id in objs_rels and i in objs_rels[block_id] and objs_rels[block_id][i] == []: objs_rels[block_id].pop(i,None)

            # if obj_rel_description: obj_rel_description+= ', '
            # obj_rel_description += relation_text[i_ind]+' '+obj_description[-1]

            if is_traj:
                land_obj_id += [[i[1]]]
                #add main traj
                traj += [[main_obj_desc]]
                traj_obj_id +=[[traj_id]]

                if [i[1]] == recent_objs:
                    land_desc = select_pronoun(is_subject= False, is_block=False)
                    land += [[land_desc]]
                    obj_description +=[land_desc] 

                elif i[1] in described_objects:

                    """
                        We can describe a pre-defined objects in several ways:
                        1) With full name
                        2) With unique feature
                        3) With relation to another object but it should be unique.
                    """
                    obj_desc, _extra_annotation = predifined_description_of_objects(i[1], no_nesting = True if shared_rel["has_common_key"] or shared_rel["has_common_rel"] else False, forbiden_keys = shared_rel["keys"])
                    # land_desc = choose_identifier(i[1]) +" "+all_objects_data[i[1]]["full_name"]
                    land += [[_extra_annotation["traj"]]]
                    if "sp_ind" in _extra_annotation: #it has extra annotation
                        traj += [[_extra_annotation["traj"]]]
                        traj_obj_id += [[i[1]]]
                        land += [[_extra_annotation["land"]]]
                        sp_ind += [_extra_annotation["sp_ind"]] # already has []
                        sp_type += [[_extra_annotation["sp_type"]]]
                        land_obj_id += [[_extra_annotation["land_id"]]]

                    obj_description +=[obj_desc] 

                elif any(sim_obj in described_objects for sim_obj in all_objects_data[i[1]]["similar_objects"]):
                    land += [[choose_identifier(i[1], another=True) +all_objects_data[i[1]]["general_name"]]]
                    update_number_in_name(i[1])
                    obj_description += [choose_identifier(i[1], another=True) +all_objects_data[i[1]]["general_name"]]
                else:
                    land += [[choose_identifier(i[1], use_general=True) +all_objects_data[i[1]]["general_name"]]]
                    obj_description += [choose_identifier(i[1], use_general=True) +all_objects_data[i[1]]["general_name"]]
                    
                if i[1] not in described_objects:
                    described_objects[i[1]] = []
                    obj_scn_queue += [i[1]]
#                 land += [[all_objects_data[i[1]]["general_name"]]]
                
                

            else:

                traj_obj_id += [[i[0]]]
                _recent_objs += [i[0]]
                
                #add main land
                land += [[main_obj_desc]]
                land_obj_id +=[[land_id]]

                if [i[0]] == recent_objs:
                    traj_desc = select_pronoun(is_block=False)
                    traj += [[traj_desc]]
                    obj_description +=[traj_desc] 

                elif i[0] in described_objects:

                    """
                        We can describe a pre-defined objects in several ways:
                        1) With full name
                        2) With unique feature
                        3) With relation to another object but it should be unique.
                    """
                    obj_desc, _extra_annotation = predifined_description_of_objects(i[0], no_nesting = True if shared_rel["has_common_key"] or shared_rel["has_common_rel"] else False, forbiden_keys = shared_rel["keys"])
                    # land_desc = choose_identifier(i[1]) +" "+all_objects_data[i[1]]["full_name"]
                    traj += [[_extra_annotation["traj"]]]
                    if "sp_ind" in _extra_annotation: #it has extra annotation
                        traj += [[_extra_annotation["traj"]]]
                        land += [[_extra_annotation["land"]]]
                        sp_ind += [_extra_annotation["sp_ind"]] # already has []
                        sp_type += [[_extra_annotation["sp_type"]]]
                        land_obj_id += [[_extra_annotation["land_id"]]]
                        traj_obj_id += [[i[0]]]
                        
                    obj_description +=[obj_desc] 

                elif any(sim_obj in described_objects for sim_obj in all_objects_data[i[0]]["similar_objects"]):
                    traj += [[choose_identifier(i[0], another= True) +all_objects_data[i[0]]["general_name"]]]
                    update_number_in_name(i[0])
                    obj_description += [choose_identifier(i[0], another= True) +all_objects_data[i[0]]["general_name"]]
                else:
                    traj += [[choose_identifier(i[0], use_general= True) +all_objects_data[i[0]]["general_name"]]]
                    obj_description += [choose_identifier(i[0], use_general= True) +all_objects_data[i[0]]["general_name"]]
                
                
                if i[0] not in described_objects:
                    described_objects[i[0]] = []
                    obj_scn_queue += [i[0]]

                
                

        if is_traj: #first object description then relation text
            # relation_text is only one since we have shared rel here.
            land_obj = obj_description
            # sent = obj_desc+' '+relation_text[0]            
        else: #first relation then object description
            traj_obj = obj_description
            # sent = relation_text[0]+' '+obj_desc 

        # sent = add_and(obj_rel_description)

    recent_objs = _recent_objs

    return {
            "land_obj_desc": land_obj, 
            "traj_obj_desc": traj_obj,
            "relation_text": relation_text,
            "cannot_change_order": cannot_change_order
            }

def seperate_similar_list(obj_id, similar_list):

    undefined = []
    defined = []
    has_defined_not_similar_rel = False
    for i in all_objects_data[obj_id]["similar_objects"]:
        if i in described_objects and i not in similar_list:
            has_defined_not_similar_rel = True
        elif i in described_objects:
            defined += [i]
        else: # is not defined 
            undefined += [i]
    return defined, undefined, has_defined_not_similar_rel
# def describe_shared_features(obj_id, similar_objs):

#     """
#         We need to first find out which are defined and which are not.
#         then we group the defined and undefined ones together
#         the + num_of_defined+ general 

#         We first find if there is any defined obj similar to obj_id that are not in the similar_objs(doesn't share similar rel)
#         if find use full name for the defined
#         else use general_name
#     """
#     sen = ''

#     sim_obj_not_having_shared_rel = [ x for x in all_objects_data[obj_id]["similar_objects"] if x in described_objects and x not in similar_objs]

#     if sim_obj_not_having_shared_rel: # there is an object with similar feature but not similar rel

    
#     else:


def predifined_description_of_objects(obj_id, no_nesting = False, use_general = False, another = False, forbiden_keys = []):

    """
        We can describe a pre-defined objects in several ways:
        1) With full name
        2) With unique feature
        3) With relation to another object but it should be unique. (also add the annotation)
        choose_identifier(text = None,another = False, use_general = False)
    """
    obj_description = ""
    rel_annotation = {}
    unique_described_relation = find_unique_described_relation(obj_id, forbiden_keys)
    if (unique_described_relation == [] or no_nesting) and all_objects_data[obj_id]["unique_features"] == []: x = 2
    elif unique_described_relation == [] or no_nesting: x = random.choice([1, 1,2])  
    elif all_objects_data[obj_id]["unique_features"] == []:  x = random.choice([0,2])
    else: x = random.choice([0, 1, 1,2])
    
    if x == 2: #use full_name
        obj_description = choose_identifier(obj_id, another = another, use_general= use_general) +all_objects_data[obj_id]["full_name"]
        rel_annotation["traj"] = obj_description

    elif x == 1: #use unique name
        feature = random.choice(all_objects_data[obj_id]["unique_features"])
        unique_feature = select_vocab(feature, key = all_objects_data[obj_id][feature])
        obj_description = choose_identifier(obj_id, text=unique_feature, another = another, use_general= use_general) +unique_feature+ (" " + select_vocab("object_general_name") if feature != "type" else "")
        rel_annotation["traj"] = obj_description

    else: # use obj_obj rels
        selected_relation = random.choice(unique_described_relation)
        G_name = select_vocab("object_general_name")
        traj_description =  choose_identifier(obj_id, text = G_name, another = another, use_general= use_general)+G_name
        relation_text, _sp_ind, need_verb = generate_relation(selected_relation[1], return_spatial_indicator = True, return_if_need_verb = True)
        land_description, _ = predifined_description_of_objects(selected_relation[0][1], no_nesting = True)
        obj_description = (
            traj_description
            +" "
            +wh_th()
            +" "
            +(check_verb("[was/were]", is_singular=True)+" " if need_verb else " ")
            + check_verb(relation_text)
            + " "
            +land_description
            )
        rel_annotation["traj"] = traj_description
        rel_annotation["land"] = land_description
        rel_annotation["sp_ind"] = check_verb(_sp_ind)
        rel_annotation["land_id"] = selected_relation[0][1]
        rel_annotation["sp_type"] = selected_relation[1][0]["relation_type"]
            
    return obj_description, rel_annotation

def find_unique_described_relation(obj_id, forbiden_keys = []):

    possible_options = [] #((key), rel)
    for key in described_relations:
        if obj_id == key[0] and (len(key[0]) != 1 and len(key[1])!= 1) and key not in forbiden_keys and (key[1], key[0]) not in forbiden_keys: #don't consider relation with blocks
            for rel in described_relations[key]:
                # if cannot find any other key that the land are similar and the relation are similar we can choose this.
                if not any((_key[1] == key[1] and  rel in described_relations[_key]) for _key in described_relations if _key != key):
                    possible_options += [(key, [rel])]
    return possible_options


# check relations betwee objects and their scene, alongside check if objects have shared properties
def obj_rel_scene(scn_id = '0', is_traj = True , check_with= False, fixed_relation = None):

    """
        This function is responsible for describing the relation between group of objects and their mainn blocks.
        It's not neccessary to describe all object-block relation here
        The priority is for those objects which have shared relations or features.
        Is_traj demonstrate that the block is the trajector or landmark in this description. 
        shared_features only appear when the shared_relations also exists.
        whenever we described an object we remove it from the list of objects or relations
        The shared_rel is sorted based on the highest number of shared rels or keys
    """
    # global sp_ind, sp_type, traj, traj_obj_id, land_obj_id, land
    # global all_objects_data, described_objects, described_relations, recent_objs
    sen = ''
    #compute shared relations 

    obj_block_list = scn_objs[scn_id] if scn_id in scn_objs else None
    if obj_block_list == None: return None

    if is_traj:
        """
            Is_traj means the shared part was landmard so the objects are trajector
        """
        shared_rel = find_shared_rel(searching_list=obj_block_list, fixed_land_id=scn_id, fixed_rel= fixed_relation)
    else:
        shared_rel = find_shared_rel(searching_list=obj_block_list, fixed_traj_id=scn_id, check_with = check_with, fixed_rel= fixed_relation)

    if shared_rel == []: return None

    """
        There can be three situations:
            1) It has common relations --> shared_rel[0][has_common_rel] == True
            2) It has common keys -->  shared_rel[0][has_common_key] == True
            3) It has some objects with different relations --> shared_rel[0][has_common_rel] == False and shared_rel[0][has_common_key] == False
        
        So we check the first one,
            If it is from 1 or 2 --> we select the first 
            else: we select at most 3 of them.
    """

    sent = describe_shared_obj_scn(shared_rel[0], scn_id = scn_id, is_traj = is_traj , check_with= check_with)
    return sent

def expand_rel_describtion(rel):

    expanded_list = []
    for r in rel:
        # rel_type, rel_prop = r.split('#')
        expanded_list += [{"relation_type": r, "relation_property": ""}]
        # expanded_list += [{"relation_type": rel_type, "relation_property": rel_prop}]
    return expanded_list

def describe_shared_obj_scn(shared_rel, scn_id = '0', is_traj = True , check_with= False, has_which = False):

    """
        Is_traj means the shared part was landmark so the objects are trajector
    """
    global sp_ind, sp_type, traj, traj_obj_id, land_obj_id, land
    global scn_objs ,all_objects_data, described_objects, described_relations, recent_objs

    _recent_objs = []
    relation_need_verb = shared_rel["need_verb"]

    if shared_rel["has_common_rel"] == True:
        #start describing the objects and their shared relations
        #for describing the objects first check if they have shared features.
        
        #check if each object in shared_rel_keys has similar attrubutes
        seen_obj, similars = {}, {}
        for i_ind, i in enumerate(shared_rel["keys"]):
            expanded_rel = expand_rel_describtion(shared_rel["relation"][0])
            if i not in described_relations:
                described_relations[i] = expanded_rel
            else:
                described_relations[i] += expanded_rel

            for r in expanded_rel:
                if scn_id in scn_objs and i in scn_objs[scn_id] and r in scn_objs[scn_id][i]:
                    scn_objs[scn_id][i].remove(r)

            if scn_id in scn_objs and i in scn_objs[scn_id] and scn_objs[scn_id][i] == []: scn_objs[scn_id].pop(i,None)

            #TODO add described situation
            traj_land = 0 if is_traj else 1
            #TODO another medium circle, another medium circle and another medium circle
            if i[traj_land] not in seen_obj:
                similar_num = 1
                similars[i[traj_land]] = [i[traj_land]]
                #if there isn't any described object with shared feature which are not in this shared key
                
                if all( j not in described_objects or any(j == key[traj_land] for key in shared_rel["keys"]) for j in all_objects_data[i[traj_land]]["similar_objects"]):
                    for j in all_objects_data[i[traj_land]]["similar_objects"]:
                        if ( any(j == key[traj_land] for key in shared_rel["keys"]) and
                            (
                                (i[traj_land] in described_objects and j in described_objects)
                                or
                                (i[traj_land] not in described_objects and j not in described_objects)
                            )
                            ):
                            similar_num += 1
                            similars[i[traj_land]]+= [j]
                            seen_obj[j] = None

                if similar_num>1: 
                    if i[traj_land] in described_objects:    
                        seen_obj[i[traj_land]] = num_to_word(str(similar_num)) +" "+all_objects_data[i[traj_land]]["general_name"]+ "s"
                    else:
                        seen_obj[i[traj_land]] = num_to_word(str(similar_num)) +" "+all_objects_data[i[traj_land]]["general_name"]+ "s"
                else:
                    if i[traj_land] in described_objects:
                       seen_obj[i[traj_land]], _ = predifined_description_of_objects(i[traj_land], no_nesting = True)
                    else:
                        seen_obj[i[traj_land]] =  choose_identifier(i[traj_land], use_general=True)+all_objects_data[i[traj_land]]["general_name"]


        obj_description = []
        num_repeated_rel = 0
        for i_ind, i in enumerate(shared_rel["keys"]):
            if is_traj:
                
                if seen_obj[i[0]] != None: #the name comes in the name of the mentioned object
                    # traj += [[seen_obj[seen_obj[i[0]][0]]]]
                    # update_number_in_name(i[0])
                # else: #it is the name
                    traj += [[seen_obj[i[0]]]]
                    obj_description += [seen_obj[i[0]]]
                    traj_obj_id += [similars[i[0]]]
                    _recent_objs += similars[i[0]]
                    num_repeated_rel += 1
                if any(sim_obj in described_objects for sim_obj in all_objects_data[i[0]]["similar_objects"]) or seen_obj[i[0]] == None or len(similars[i[0]])>0:
                    update_number_in_name(i[0])
                described_objects[i[0]]=[]

            else:
                if seen_obj[i[1]] != None: #the name comes in the name of the mentioned object
                    # land += [[seen_obj[seen_obj[i[1]][0]]]]
                    # update_number_in_name(i[1])

                # else: #it is the name
                    land += [[seen_obj[i[1]]]]
                    obj_description += [seen_obj[i[1]]]
                    land_obj_id += [similars[i[1]]]
                    num_repeated_rel += 1
                if any(sim_obj in described_objects for sim_obj in all_objects_data[i[1]]["similar_objects"]) or seen_obj[i[1]] == None or len(similars[i[1]])>0:
                    update_number_in_name(i[1])

                described_objects[i[1]]=[]
        
        
        sp_ind += check_verb(shared_rel["spatial_indicators"], is_singular=False )*num_repeated_rel
        sp_type += shared_rel["relation"]*num_repeated_rel
        
        relation_text = check_verb(shared_rel["relation_text"], is_singular=False ) #check verb correct the plural or singular verbs


        obj_desc = ''
        for desc in obj_description:
            if obj_desc: obj_desc += ', '
            obj_desc += desc
        obj_desc = add_and(obj_desc)
        if is_traj: #first object description then relation text
            # relation_text is only one since we have shared rel here.
            if relation_need_verb[0]:
                sent = obj_desc+' '+("which " if has_which else "" )+check_verb("[is/are]", is_singular= False)+' '+relation_text[0]            
            else:
                sent = obj_desc+' '+("which " if has_which else "" )+relation_text[0]            
        else: #first relation then object description
            if relation_need_verb[0]:
                sent = ("which " if has_which else "" )+check_verb("[is/are]", is_singular= False)+' '+relation_text[0]+' '+obj_desc   
            else:
                sent = ("which " if has_which else "" )+relation_text[0]+' '+obj_desc   

    else:  #elif shared_rel["has_common_key"] == True or only one object has the relation and is the trajector or landmark of this relation (based on is_traj value)
        sp_ind += check_verb(shared_rel["spatial_indicators"], is_singular=True)
        sp_type += shared_rel["relation"]
        relation_text = check_verb(shared_rel["relation_text"], is_singular=True)
        obj_description = []
        obj_rel_description = ''
        for i_ind, i in enumerate(shared_rel["keys"]):
            
            """
                traj, traj_obj_id, described_objects, described_rel, obj_description
                if similar feature use "another" TODO or start from the second one use number
            """
            # remove the described relations from the main list to not compute after this 

            expanded_rel = expand_rel_describtion(shared_rel["relation"][i_ind])
            if i not in described_relations:
                described_relations[i] = expanded_rel
            else:
                described_relations[i] += expanded_rel

            for r in expanded_rel:
                if scn_id in scn_objs and i in scn_objs[scn_id] and r in scn_objs[scn_id][i]:
                    scn_objs[scn_id][i].remove(r)

            if scn_id in scn_objs and i in scn_objs[scn_id] and scn_objs[scn_id][i] == []: scn_objs[scn_id].pop(i,None)
            
            if is_traj:
                
                if any(sim_obj in described_objects for sim_obj in all_objects_data[i[0]]["similar_objects"]):
                    _temp = select_pronoun(is_subject=  True, is_block = False) if [i[0]] == recent_objs else choose_identifier(i[0], another= True) + all_objects_data[i[0]]["general_name"]
                    update_number_in_name(i[0])
                    traj += [[_temp]]
                    obj_description += [_temp]
                else:
                    _temp = select_pronoun(is_subject=  True, is_block = False) if [i[0]] == recent_objs else choose_identifier(i[0], use_general= True) +all_objects_data[i[0]]["general_name"]
                    traj += [[_temp]]
                    obj_description += [_temp]
                    
                traj_obj_id += [[i[0]]]
                _recent_objs += [i[0]]
                described_objects[i[0]] = []
                
                
                if obj_rel_description: obj_rel_description+= ', '
                if relation_need_verb[i_ind]:
                    obj_rel_description += obj_description[-1]+' '+("which " if has_which else "" )+check_verb("[is/are]", is_singular= True)+' '+relation_text[i_ind] 
                else:
                    obj_rel_description += obj_description[-1]+' '+("which " if has_which else "" )+relation_text[i_ind] 

            else:
                if any(sim_obj in described_objects for sim_obj in all_objects_data[i[1]]["similar_objects"]):
                    _temp = select_pronoun(is_subject= False, is_block=False) if [i[1]] == recent_objs else choose_identifier(i[1], another=True) +all_objects_data[i[1]]["general_name"]
                    update_number_in_name(i[1])
                    land += [[_temp]]
                    obj_description += [_temp]
                else:
                    _temp = select_pronoun(is_subject= False, is_block=False) if [i[1]] == recent_objs else choose_identifier(i[1], use_general=True) +all_objects_data[i[1]]["general_name"]
                    land += [[_temp]]
                    obj_description += [_temp]

                land_obj_id += [[i[1]]]
                described_objects[i[1]] = []

                if obj_rel_description: obj_rel_description+= ', '

                if relation_need_verb[i_ind]:
                    obj_rel_description += ("which " if has_which else "" )+check_verb("[is/are]", is_singular= True)+' '+relation_text[i_ind]+' '+obj_description[-1]  
                else:
                    obj_rel_description += ("which " if has_which else "" )+relation_text[i_ind]+' '+obj_description[-1]  

        sent = add_and(obj_rel_description)

    if _recent_objs: recent_objs = _recent_objs

    return sent

def update_number_in_name(obj_id):
    global all_objects_data
    highest_number = 1

    _list = [i for i in all_objects_data[obj_id]["similar_objects"] if i in described_objects ]
    if _list == []: return

    for i in _list:
        if "number" in all_objects_data[i]:
            if int(all_objects_data[i]["number"]) >= highest_number: highest_number = int(all_objects_data[i]["number"])+1
    for i in _list:
        if  "number" not in all_objects_data[i]:
            all_objects_data[i]["number"] = str(highest_number)
            all_objects_data[i]["full_name"] = all_objects_data[i]["full_name"]+" number "+num_to_word(str(highest_number))

            highest_number += 1

    if "number" not in  all_objects_data[obj_id]:
        all_objects_data[obj_id]["number"] = str(highest_number)
        all_objects_data[obj_id]["full_name"] = all_objects_data[obj_id]["full_name"]+" number "+num_to_word(str(highest_number))


    return


def update_checked_obj_sc(n, G_size, G_color, G_type, G_scene_rel, nth="", temp=False):

    global checked_obj_sc, temp_checked_obj_sc

    if temp:
        if len(temp_checked_obj_sc) == 0:
            temp_checked_obj_sc.append([n, G_size, G_color, G_type, G_scene_rel, nth])
            return
        else:
            for i in temp_checked_obj_sc:
                if i[0] == n:
                    if G_size:
                        i[1] = G_size
                    if G_color:
                        i[2] = G_color
                    if G_type:
                        i[3] = G_type
                    if G_scene_rel:
                        i[4] = G_scene_rel
                    if nth:
                        i[5] = nth
                    return

            temp_checked_obj_sc.append([n, G_size, G_color, G_type, G_scene_rel, nth])
            return

    if checked_obj_sc:
        check = 1
        for che in range(len(checked_obj_sc)):
            if checked_obj_sc[che][0] == n:
                if G_size:
                    checked_obj_sc[che][1] = G_size
                if G_color:
                    checked_obj_sc[che][2] = G_color
                if G_type:
                    checked_obj_sc[che][3] = G_type
                if G_scene_rel:
                    checked_obj_sc[che][4] = G_scene_rel
                check = 0
                break
        if check:
            checked_obj_sc.append([n, G_size, G_color, G_type, G_scene_rel, nth])

    else:
        checked_obj_sc.append([n, G_size, G_color, G_type, G_scene_rel, nth])
    if not temp and temp_checked_obj_sc:
        temp_checked_obj_sc.pop(-1)


def check_id(obj):
    id_obj = -1
    for ind, i in enumerate(checked_obj_sc):
        if i[0] == obj:
            id_obj = ind
    return int(id_obj)



def compute_objects_features():

    """
    we check all objects to find its common and unique features
    unique feature used for describing object as a unique entity
        if there isn't any unique feature we add a new feature called "name" which has a assigned number that makes it unique
    shared feature used to describe group of objects
    delete unused features from the all_data
    """
    # compute fearture describtion, add shared objects, add unique name
    global all_objects_data

    #first add features part to the blocks
    for obj1 in all_objects_data:

        if len(obj1) == 1: #it is block
            all_objects_data[obj1]['type'] = select_vocab("block")
            all_objects_data[obj1]['name'] = select_vocab("block_name", key = obj1)
            # if word_to_num(all_objects_data[obj1]['name']):
            #     all_objects_data[obj1]['number'] = word_to_num(all_objects_data[obj1]['name'])


    unique_features, similar_objects = unique_common_features()
    # compute name
    for obj in all_objects_data:
        # if len(obj) == 1:
        #     all_objects_data[obj]["unique_features"] = []
        #     all_objects_data[obj]["similar_objects"] = []
        #     continue  # all blocks has id with len of 1
        # else:
        all_objects_data[obj]["unique_features"] = unique_features[obj] if obj in unique_features else []
        all_objects_data[obj]["similar_objects"] = similar_objects[obj] if obj in similar_objects else []

        # if there are other objects with similar features assign a number and generate the text
        # if there isn't any object with full shared name and this object has no unique feature generate the name
        # if obj in similar_objects and similar_objects[obj]:
        #     if "number" not in all_objects_data[obj]:
        #         all_objects_data[obj]["number"] = "1"
        #         number = 2
        #         for obj2 in similar_objects[obj]:
        #             if "number" not in all_objects_data[obj2]:
        #                 all_objects_data[obj2]["number"] = str(number)
        #                 number += 1

        text, general_name = obj_create_name(
            obj, 
            unique_feature_list=unique_features[obj], 
            has_similar = True if obj in similar_objects and similar_objects[obj] else False
            )
        all_objects_data[obj]["full_name"] = text
        all_objects_data[obj]["general_name"] = general_name if  obj in similar_objects and similar_objects[obj] else text

def unique_common_features():

    feature_matrix = [[[] for _ in range(len(all_objects_data))] for _ in range(len(all_objects_data))]

    objects_id = list(all_objects_data)
    # compute feature matrix which shows the common features between different objects
    for obj1 in all_objects_data:

        if len(obj1) != 1: #it is not block
            # all_objects_data[obj1]['type'] = select_vocab("block")
            # all_objects_data[obj1]['name'] = select_vocab("block_name", key = obj1)

        # else:
            # remove "y_loc" and "x_loc"
            all_objects_data[obj1].pop("y_loc", None)
            all_objects_data[obj1].pop("x_loc", None)

        for obj2 in all_objects_data:
            if obj2 == obj1:

                common_features = []
            else:
                common_features = [
                    feature
                    for feature in all_objects_data[obj1]
                    if feature in all_objects_data[obj1]
                    and feature in all_objects_data[obj2]
                    and all_objects_data[obj1][feature]
                    == all_objects_data[obj2][feature]
                ]
            feature_matrix[objects_id.index(obj1)][objects_id.index(obj2)] = common_features

    unique_feature, shared_obj = {}, {}

    for row_ind, row in enumerate(feature_matrix):

        # find unique
        _unique_feature = []
        for feature in all_objects_data[objects_id[row_ind]]:
            find = False
            for with_other_obj_feature in row:
                if feature in with_other_obj_feature:
                    find = True
                    break
            if not find:
                _unique_feature += [feature]
        unique_feature[objects_id[row_ind]] = _unique_feature

        if _unique_feature == []:
            all_obj_with_shared_feature = []
            if len(row) != row.count([]): #if there is any features do the next loop
                for obj_ind, with_other_obj_feature in enumerate(row):
                    if (sorted(with_other_obj_feature) == [
                        "color",
                        "size",
                        "type",
                    ]
                    and objects_id[obj_ind][0] == objects_id[row_ind][0]
                    ):  # has all the features
                        all_obj_with_shared_feature += [objects_id[obj_ind]]
            shared_obj[objects_id[row_ind]] = all_obj_with_shared_feature

    return unique_feature, shared_obj


def obj_create_name(id, unique_feature_list=[], has_similar = False):
    global all_objects_data
    
    if len(id) == 1: #it is a block
        return select_vocab("block")+' '+select_vocab("block_name", key = id), select_vocab("block")+' '+select_vocab("block_name", key = id)
    # size = 0, color = 1, type = 2, name = 3
    if unique_feature_list:
        s = random.sample([0, 1, 1, 1], 3) + [0]
        if "size" in unique_feature_list:
            s[0] = 1
        if "color" in unique_feature_list:
            s[1] = 1
        if "type" in unique_feature_list:
            s[2] = 1

        if s[0] == 0:
            all_objects_data[id].pop("size", None)
        if s[1] == 0:
            all_objects_data[id].pop("color", None)
        if s[2] == 0:
            all_objects_data[id].pop("type", None)
    else:
        s = [1, 1, 1, 1 if has_similar else 0]
    
    Size =  size(all_objects_data[id]["size"])+" " if s[0] else ""
    Color =  color(all_objects_data[id]["color"])+" " if s[1] else ""
    Shape =  shape(all_objects_data[id]["type"])+" " if s[2] else sh_ob_single()+" "
    Number = (
        "number " + num_to_word(str(all_objects_data[id]["number"]))+" "
        if s[3] and "number" in all_objects_data[id]
        else ""
    )


    return (Size+ Color+ Shape + Number)[:-1], (Size + Color+ Shape)[:-1]


def defined_obj_create_name(id, all_obj_data, list_of_features = [], has_similar = False):
    
    # global all_objects_data
    
    # if len(id) == 1: #it is a block
    #     return select_vocab("block")+' '+select_vocab("block_name", key = id), select_vocab("block")+' '+select_vocab("block_name", key = id)
    
    # size = 0, color = 1, type = 2, name = 3
    if len(id) == 1:
        if list_of_features == []:
            return select_vocab("block")
        if "type" in list_of_features:
            #
            return all_obj_data[id]["type"]

        else:
            if word_to_num(all_obj_data[id]["name"]):
                list_of_features += ['type']
                return all_obj_data[id]["full_name"]
            return all_obj_data[id]["name"]



    s = [0,0,0,0]
    if "size" in list_of_features:
        s[0] = 1
    if "color" in list_of_features:
        s[1] = 1
    if "type" in list_of_features:
        s[2] = 1
    if "number" in list_of_features:
        s[3] = 1


    Size =  size(all_obj_data[id]["size"])+" " if s[0] else ""
    Color =  color(all_obj_data[id]["color"])+" " if s[1] else ""
    Shape =  shape(all_obj_data[id]["type"])+" " if s[2] else sh_ob_single()+" "
    Number = (
        "number " + num_to_word(all_obj_data[id]["number"])+" "
        if s[3] and "number" in all_obj_data[id]
        else ""
    )

    return (Size+ Color+ Shape + Number)[:-1]

def choose_identifier(obj_id, text = None,another = False, use_general = False):

    if len(obj_id) == 1: return ''

    if obj_id in described_objects: 

        """
            object is already described so:
                - if have number or specific name --> add nothing
                - select the
        """
        if text and "number" not in text: return "the "
        if use_general and "number" not in all_objects_data[obj_id]["general_name"]: return "the "
        elif "number" not in all_objects_data[obj_id]: return "the "
        else: return ""


    else:
        """
            It is the first time we want to describe this object.
                - if another --> another 
                - has number in name --> nothing
                - if start with vowels --> an
                - if start with not vowels --> a
        """

        if another or any(sim_obj in described_objects for sim_obj in all_objects_data[obj_id]["similar_objects"]): return "another "
        elif "number" not in all_objects_data[obj_id]:
            name = text[0] if text else all_objects_data[obj_id]["full_name"][0]
            if name in ['a', 'e', 'i', 'o', 'u']: return 'an '
            else: return 'a '
        elif use_general: #"number" is in all_objects_data[obj_id]
            name = text[0] if text else all_objects_data[obj_id]["general_name"][0]
            if name in ['a', 'e', 'i', 'o', 'u']: return 'an '
            else: return 'a '
        else:
            return ""



def Obj(x):
    s = [1, 1, 1]
    # remove random choosing
    #     s[0] = random.choice([0,1,1,1])
    #     s[1] = random.choice([0,1,1,1])
    #     s[2] = random.choice([0,1,1,1,1,1,1])

    #     if s[0] == 0 and s[1] == 0 and s[2] ==0:
    #         z = random.choice([0,1,2])
    #         s[z] = 1

    Size = " " + size(x[1]["size"]) if s[0] else ""
    Color = " " + color(x[1]["color"]) if s[1] else ""
    Shape = " " + shape(x[1]["type"]) if s[2] else " " + sh_ob_single()

    return Size + Color + Shape


# chose just part of the description
def Obj_random(x):
    s = [0, 0, 0]
    s[0] = random.choice([0, 1])
    s[1] = random.choice([0, 1])
    s[2] = random.choice([0, 1])

    if s[0] == 0 and s[1] == 0 and s[2] == 0:
        z = random.choice([0, 1, 2])
        s[z] = 1

    Size = " " + size(x[1]["size"]) if s[0] else ""
    Color = " " + color(x[1]["color"]) if s[1] else ""
    Shape = " " + shape(x[1]["type"])  # if s[2] else ' '+sh_ob_single()

    return Size + Color + Shape


def color(x):
    global G_color
    # x = x.lower()
    # if x == '#0099ff': x = 'blue'
    # else: x = x.lower()
    _color = select_vocab("color", key=x.lower())
    G_color = {"color": _color}
    return _color


def size(x):
    global G_size
    # z = ''
    # i = x
    # if type(x) == str : x = int(i)
    # if i == 10: z= 'small'
    # elif i == 20: z= 'medium'
    # elif i == 30: z= 'big'
    # else: z= 'unknown'
    _size = select_vocab("size", key=int(x))
    G_size = {"size": _size}
    return _size


def shape(x):
    global G_type
    # x = x.lower()
    _shape = select_vocab("type", key=x.lower())
    G_type = {"type": _shape}
    return _shape


def Rel(x):
    # check
    global G_scene_rel
    if x != "in":
        G_scene_rel = {"rel": x}
    rel = " " + x
    return rel


def R(x):
    # check
    return "to the " + x + " of" if x == "right" or x == "left" else x


def generate_relation(
    all_rels,
    only_list=False,
    fixed_rel=[],
    plural=False,
    return_spatial_indicator=False,
    return_has_verb=False,
    check_with = False,
    return_if_need_verb = False
):

    # fixed re only contains the relation types
    # all_rels = [{'relation_type': '', 'relation_property': ''}]

    # TODO also consider combination of relation like Northwest or above left
    extracted_rels = []
    all_extracted_rels = []
    verb_extracted_rels = []
    preposition_extracted_rels = []
    has_verb = False
    need_verb = False
    # if len(fixed_rel)>1: print("EERRROOORR IN GENERATE TEXT FOR MORE THAN ONE FIXED_REL")
    for rel in all_rels:
        # if fixed_rel == [] or any(rel["relation_type"] in _fixed_rel and rel["relation_property"] in _fixed_rel for _fixed_rel in fixed_rel):
        if fixed_rel == [] or any(rel["relation_type"] == _fixed_rel for _fixed_rel in fixed_rel):
            # _temp = rel["relation_type"] + "#" + rel["relation_property"]
            _temp = rel["relation_type"] #+ "#" + rel["relation_property"]
            extracted_rels += [_temp]
            if rel["relation_type"] in verb_relations:
                verb_extracted_rels += [_temp]
            elif rel["relation_type"] in prepositions_relations:
                preposition_extracted_rels += [_temp]

    extracted_rels.sort()

    if only_list:
        return (None, extracted_rels,)

    preposition_extracted_rels.sort()
    verb_extracted_rels.sort()

    if preposition_extracted_rels: need_verb = True # just consider the first relation for adding the verb. e.g. Is above and touches ...
    # if preposition_extracted_rels and not verb_extracted_rels: need_verb = True

    spatial_indicator = []
    final_relation = ""
    # It is not possible the relation between two objects exists in both preposition and verb rels
    # if preposition_extracted_rels and verb_extracted_rels:
    #     print("ERRORR! HAS PREPOSITIONA AND VERB AT THE SAME TIME")
    if preposition_extracted_rels:
        for rel in preposition_extracted_rels:
            rel_type = rel
            # rel_type, rel_property = rel.split("#")
            # if fixed_rel == [] or any(rel_type in _fixed_rel and rel_property in _fixed_rel for _fixed_rel in fixed_rel):
            if fixed_rel == [] or any(rel_type in _fixed_rel for _fixed_rel in fixed_rel):
                rel_text = select_vocab("relation_in_text", key = rel_type)
                # if rel_property: rel_text = rel_text.replace("[rel]", select_vocab("relation", key = rel_property))
                spatial_indicator += [rel_text]
        final_relation = add_and(", ".join(spatial_indicator))
        if not need_verb : final_relation = "[is/are] " + final_relation

    verb_spatial_indicator = []
    if verb_extracted_rels:  # several relation from verb_relations cannot happened at the same time.
        has_verb = True
        for rel in verb_extracted_rels:
            rel_type = rel
            # rel_type, rel_property = rel.split("#")
            # if fixed_rel == [] or any(rel_type in _fixed_rel and rel_property in _fixed_rel for _fixed_rel in fixed_rel):
            if fixed_rel == [] or any(rel_type in _fixed_rel for _fixed_rel in fixed_rel):
                rel_text = select_vocab("relation_in_text", key = rel_type, check_with = check_with)
                # rel_text = vocabulary[vocab_selection]["relation_in_text"][rel_type]
                # if rel_property: rel_text = rel_text.replace("[rel]", select_vocab("relation", key = rel_property))
                # if rel_property: rel_text = rel_text.replace("[rel]", vocabulary[vocab_selection]["relation"][rel_property])
                
                verb_spatial_indicator += [rel_text]
        if final_relation: final_relation += " and " # has relation from preposition
        final_relation += add_and(", ".join(verb_spatial_indicator))
    spatial_indicator += verb_spatial_indicator

    # for rel in all_rels:
    #     if fixed_rel == [] or rel["relation_type"] in fixed_rel:
    #         rel_text = vocabulary[vocab_selection]["relation_in_text"][rel["relation_type"]]
    #         rel_text.replace('[rel]', vocabulary[vocab_selection]["relation"][rel["relation_property"]])
    #         extracted_rels += [rel_text]

    # extracted_rels = extracted_rels.sort()
    # final_relation = add_and(', '.join(extracted_rels))
    output = (final_relation,)
    if return_spatial_indicator:
        output = output + (spatial_indicator,)
    if return_has_verb:
        output = output + (has_verb,)
    if return_if_need_verb:
        output = output + (need_verb,)

    return output

def check_verb(text, is_singular = True ):

    if type(text) == str:
        rel_text = text
        if is_singular:
            rel_text = rel_text.replace("[es]", "es").replace("[s/ve]", "s").replace( "[s]", "s").replace("[is/are]","is").replace("[was/were]", "was").replace("[does/do]", "does")
        else:
            rel_text = rel_text.replace("[es]", "").replace("[s/ve]", "ve").replace("[s]", "").replace("[is/are]","are").replace("[was/were]", "were").replace("[does/do]", "do")
        
        return rel_text
    else:
        converted_list = []
        txt_str = False
        for txt in text:
            _temp_list = []
            if type(txt) == str: txt = [txt]; txt_str = True
            
            for rel_text in txt:
                # rel_text = txt if type(txt) == str else txt[0]
                if is_singular:
                    rel_text = rel_text.replace("[es]", "es").replace("[s/ve]", "s").replace( "[s]", "s").replace("[is/are]","is").replace("[was/were]", "was").replace("[does/do]", "does")
                else:
                    rel_text = rel_text.replace("[es]", "").replace("[s/ve]", "ve").replace("[s]", "").replace("[is/are]","are").replace("[was/were]", "were").replace("[does/do]", "do")
                _temp_list += [rel_text]
            if not txt_str: converted_list += [_temp_list]
            else: converted_list += _temp_list
        return converted_list

def select_vocab(text, key='name',id=None, check_with = False, return_list = False):

    # select from the vocabulary based on the category of vocabulary which is selected in the Dataset_gen
    global has_with
    if text == "number":
        vocab_list = num_to_word(key)
    elif "relation" in text:
        vocab_list = relation_vocabulary[relation_vocab_selection][text.lower()][key.upper()]

    else:
        vocab_list = vocabulary[vocab_selection][text.lower()][key.lower() if type(key) == str else key]

    if (type(vocab_list) in [list, dict]) and id:
        return vocab_list[id]
    elif type(vocab_list) == list:
        if key == "NTPPI" and check_with:
            has_with = True
            return "with"
        if return_list: return vocab_list
        else:
            return vocab_list[random.choice(range(len(vocab_list)))]
    else:  # it is not a list and we have id
        return vocab_list

def select_pronoun(is_subject = True, is_block = True, plural = False):

    pronoun = ''
    if plural:
        x = random.choice([0,1])
        if x: # use they/them
            if is_subject: pronoun = "they"
            else: pronoun = "them"
        else: #use these blocks/objects
            if is_block: pronoun = "these "+ select_vocab("blocks")
            else: pronoun = "these "+ select_vocab("objects_general_name")
    else:
        x = random.choice([0,0,1]) if is_subject or not is_block else 0
        if x: # use they/them
            pronoun = "it"
        else: #use these blocks/objects
            if is_block: pronoun = "this "+ select_vocab("block")
            else: pronoun = "this "+ select_vocab("object_general_name")
    
    return pronoun

def wh_th():

    sen = "which" if random.choice([0, 1, 1, 1]) else "that"
    return sen


def s_num():  # choose between a or one for block

    return "a" if random.choice([0, 1]) else "one"


def one_blk():
    return "one" if random.choice([0, 1]) else "block"


def num_to_word(x):
    n_w = {
        "0": "zero",
        "1": "one",
        "2": "two",
        "3": "three",
        "4": "four",
        "5": "five",
        "6": "six",
        "7": "seven",
        "8": "eight",
        "9": "nine",
    }
    return n_w[x]

def word_to_num(text):
    n_w = {
        "zero": '0',
        "one": '1',
        "two": '2',
        "three": '3',
        "four": '4',
        "five": '5',
        "six": '6',
        "seven": '7',
        "eight": '8',
        "nine": '9',
    }

    if text in n_w: return n_w[text]
    return None


def sh_ob():
    return "shapes" if random.choice([0, 1]) else "objects"


def sh_ob_single():
    # return "shape" if random.choice([0, 1]) else "object"
    return select_vocab("object_general_name")


def nth(x):
    z = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh"]
    return z[x]


def reverse(word):
    # words={'left':'right', 'right':'left', 'above':'below', 'below':'above'}
    # by reverse we mean if x rel y --> y reverse_rel x
    reverse_rel = (
        {
            "LEFT": "RIGHT",
            "RIGHT": "LEFT",
            "ABOVE": "BELOW",
            "BELOW": "ABOVE",
            "BEHIND": "FRONT",
            "FRONT": "BEHIND",
            "NEAR": "FAR",
            "FAR": "NEAR",
            "DC": "DC",
            "EC": "EC",
            "PO": "PO",
            "TPP": "TPPI",
            "NTPP": "NTPPI",
            "TPPI": "TPP",
            "NTPPI": "NTPP",
        },
    )
    return reverse_rel[word]


def reorder(x):

    z = x.copy()
    for j, i in enumerate(z):
        if "size" in i:
            x.remove(i)
            x.insert(0, i)
        elif "type" in i:
            x.remove(i)
            x.append(i)

    return x


def start_word(x):  # make first character uppercase
    for i in range(len(x)):
        if x[i] != " ":
            z = x[i].upper() + x[i + 1 :]
            return z


def ind_check_obj(obj):
    global checked_obj_sc
    ind = None
    obj_attr = checked_obj_sc
    for ind1, o_a in enumerate(obj_attr):
        if o_a[0] == obj:
            ind = ind1
            break
    return ind


# should be checked
def unique_attr_check():
    global checked_obj_sc
    unique, list_all_attrs = [], []
    obj_attr = checked_obj_sc
    for scn in range(num_of_blocks):
        #         print('%%', obj_attr)
        for i in obj_attr:
            list_all_attrs += i
    unique = [x for x in list_all_attrs if list_all_attrs.count(x) == 1]
    return unique


def name_call():
    x = random.choice([0, 1])
    if x:
        return "named "
    # elif x == 1:
    #     return ""
    else:
        return "called "


def name_block(num):

    return select_vocab("block_name", key=num)

def B0_call_block(block_id, is_traj = False):

    # global recent_objs, described_objects
    # global traj, land, traj_obj_id, land_obj_id, sp_ind, sp_type
    new_mention = ( 
            ("another" if block_id != "0" else "a")
            +" "
            + select_vocab("block") 
            + " "
            + name_call()
            + name_block(block_id) 
        )
    described_objects[block_id] = []

    sen = ''

    # if is_traj:
    #     # if block_id == "2" : Finally, if block_id == "2" or "1" add also
    #     if random.choice([0,1]):
    #          _sen = "We have "
    #          traj += [["we"]]
    #          traj_obj_id += [[""]]
    #          land_obj_id += [[block_id]]
    #          land += [[new_mention]]
    #          sp_ind += [["have"]]
    #          sp_type += [["NTPPI"]]
    #     else:
    #         _sen = "There is "
    #         traj += [[""]]
    #         traj_obj_id += [[""]]
    #         land_obj_id += [[block_id]]
    #         land += [[new_mention]]
    #         sp_ind += [["is"]]
    #         sp_type += [["NTPP"]]

    #     if block_id == "2":
    #         _sen = "Finally, "+ _sen if random.choice([0,1]) else _sen
    #     if block_id != "0": # it is "1", "2"
    #         _sen += "also " if random.choice([0,1]) else ""
    #     _sen += new_mention

    #     # selec if we want to finish this sentence and start the other with it or continue this one with which

    #     # if random.choice([0,1]): # finish the sentence
    #     #     recent_objs = [block_id]
    #     #     _sen+= '.'
    #     #     _sen = start_word(_sen)
    #     #     create_annotation(_sen)
    #     #     new_mention = select_pronoun()
    #     #     _sen += ' '+new_mention+' '+check_verb("[is/are]", is_singular=True) +' '

    #     # else: # continue
    #     #     _sen += " which "+check_verb("[is/are]", is_singular=True) +' '
        
    #     sen = _sen+" "

    return sen, new_mention

def name_block_all(num):

    sen = ""

    block_name = select_vocab("blocks") if num_of_blocks > 1 else select_vocab("block")

    _sen = num_to_word(str(num))+ " "+block_name

    x = 1#random.choice([0, 1])
    # we have three blocks, A,B and C.
    if x:
        if num == 1:
            _sen += " "+ name_call()+ name_block("0")
        elif num == 2:
            _sen += ", " + name_call()+ name_block("0") + " and " + name_block("1")
        elif num == 3:
            _sen += (
                ", "
                + name_call()
                + name_block("0")
                + ", "
                + name_block("1")
                + " and "
                + name_block("2")
                
            )
        else:
            _sen += " ERROR in blockname"
    # We/lets call them A,B and C.
    # else:
    #     y = random.choice([0, 1])  # 1 -> we, 0 -> lets
    #     if num == 1:
    #         _sen += ". We call it " if y else ". Lets call it "
    #         _sen += name_block("0")+'.'
    #     elif num == 2:
    #         _sen += ". We call them " if y else ". Lets call them "
    #         _sen += name_block("0") + " and " + name_block("1") + ". "
    #     elif num == 3:
    #         _sen += ". We call them " if y else ". Lets call them "
    #         _sen += (
    #             name_block("0")
    #             + ", "
    #             + name_block("1")
    #             + " and "
    #             + name_block("2")
    #             + ". "
    #         )
    #     else:
    #         _sen += "Error in blockname. "
    
    return _sen


def name_block_single(id, coref=False):

    #TODO if use correct this
    sen = ""
    name = name_block(id)

    x = random.choice([0, 1, 2, 3])
    if x == 0:
        sen = "We call"
    elif x == 1:
        sen = "We name"
    elif x == 2:
        sen = "let's call"
    else:
        sen = "let's name"
    sen += " it " 
    return sen


def object_num(num):
    z = ["one", "two", "three", "four", "five", "six", "seven"]
    return z[num]


def add_and(x):
    sen = x
    index = sen.rfind(",")
    if index != -1:
        sen = list(sen)
        sen[index] = "and"
        sen.insert(index, " ")
        sen = "".join(sen)
    return sen


def unique_with_rel(obj1, rel, obj2):

    similar_obj = []
    for obj_obj in checked_obj_obj:
        if obj2 == obj_obj[0][1] and rel in obj_obj[1] and obj1 != obj_obj[0][0]:
            similar_obj += [obj_obj[0][0]]

    ind_obj1 = ind_check_obj(obj1)
    differ = [i for i in checked_obj_sc[ind_obj1][1:4] if i != ""]

    for i in similar_obj:
        ind_i = ind_check_obj(i)
        differ = [i for i in differ if i not in checked_obj_sc[ind_i] and i != ""]

    if differ:
        f = random.choice(differ)
        for i in enumerate(f):
            value_differ = f[i[1]]
            return (
                value_differ + " " + sh_ob_single() if i[1] != "type" else value_differ
            )
    else:
        return -1


def add_num_name(recent_objs):

    global checked_obj_sc
    pre_defined = (
        recent_objs if recent_objs else ""
    )  # knowing objects that are referenced in the previous sentence.

    # the order of object for mentin them by it. the first object, or the second one.
    if len(pre_defined) > 1:
        for ind, p_d in enumerate(pre_defined):
            if len(p_d) > 1:
                for ind1, p in enumerate(p_d):
                    if len(p_d) > 1:
                        checked_obj_sc[check_id(p)][5] = ind1
    elif len(pre_defined) == 1:
        for ind, p_d in enumerate(pre_defined[0]):
            if len(pre_defined[0]) > 1:
                checked_obj_sc[check_id(p_d)][5] = ind


def check_number_for_obj():

    global checked_obj_sc, checked_obj_obj
    for ind, obj in enumerate(checked_obj_sc):
        check = 0
        if obj[5] != "":
            for obj_obj in checked_obj_obj:
                if obj[0] in obj_obj[0]:
                    check = 1
                    break
            if check == 0:
                checked_obj_sc[ind][5] = ""


def edit_text_form(story):
    f_story = ""

    # remove extra space
    tokens = story.split()
    f_story = " ".join(tokens)

    # remove space before "." or "?"
    f_story = f_story.replace(" .", ".")
    f_story = f_story.replace(" ?", "?")
    # remove extra "."s
    f_story = f_story.replace("...", ".")
    f_story = f_story.replace("..", ".")

    return f_story


# **********************************************************
# *************The end of describing functions**************
# **********************************************************


# **********************************************************
# ******************Annotation functions********************
# **********************************************************


def create_annotation(sen):
    
    global annotation, land, traj, sp_ind, traj_obj_id, land_obj_id, sp_type
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

    ann = {"sentence": sen, "spatial_description": []}

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

    annotation["annotations"].append(ann)
    land, traj, sp_ind, sp_type = [], [], [], []
    traj_obj_id, land_obj_id = [], []


def spatial_indicator(sp_type):

    g_type, s_type = "", ""

    # val1 = ["left", "right", "above", "below"]
    # val2 = ["far from", "near to"]
    # val3 = ["touching"]
    # val4 = ["in", "has", "contains", "have", "contain"]  # edge for touching edge

    if relation_formalism[sp_type.lower()] in ["dir", "dir_"]:
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


def SOT(story):

    global annotation, entity_phrases
    sum_char = 0

    # _file = open("repeated_annot.txt", "a+")

    for ann in annotation["annotations"]:
        sum_char = story.find(ann["sentence"])
        if sum_char == -1:
            print("!!! ERROR sum char")
        _annot = ann["sentence"].lower()
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
                        if j - 1 >= 0 and (
                            _annot[j - 1].isalpha()
                            or _annot[j + len(traj_phrase)].isalpha()
                        ):
                            start.remove(j)
                        if (
                            "lock" not in traj_phrase
                            and j - 5 >= 0 
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
                        if j - 1 >=0 and (
                            _annot[j - 1].isalpha()
                            or _annot[j + len(land_phrase)].isalpha()
                        ):
                            start.remove(j)
                        if (
                            "lock" not in land_phrase
                            and j - 5 >= 0
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
                            if traj_end+5 <  len(_annot) and _annot[traj_end+1: traj_end+5] in ["that","whic"]:
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
            elif traj_end+5 < len(_annot) and _annot[traj_end+1: traj_end+5] in ["that","whic"]:
                for j in start:
                    if j > traj_end: 
                        _start = j
            else:

                start2 = start
                for j in start2:
                    if j - 1 >= 0 and (
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
