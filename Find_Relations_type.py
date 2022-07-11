import random
import numpy as np


def scene_scene_relation(story, num_scenes = 2, seed = 0, right_front = 1):

    random.seed(seed)
    if num_scenes == 2: 
        scenes = [[('0','1'), ('1','0')]]
    else: # == 3
        scenes = random.sample([[('0','1'),('1','0')],[('1','2'), ('2','1')],[('0','2'), ('2','0')]], 2)
        # scenes[0] = random.choice(scenes[0])
        # scenes[1] = random.choice(scenes[1])
    #despite the other relation the relation between two scene(box) is imaginary
    
    scenes_rel = {}

    for scene_tuple in scenes:

        rels, reverse_rels = [], []

        topo_relation = random.choice(["DC"]*10+ ["EC"]+[ "PO"]+ ["NTPP"]*5+ ["NTPPI"]*5+ ["TPP"]*2+ ["TPPI"]*2) #ignore EQ since it doesn't mean
        # topo_relation = 'DC'

        if topo_relation != "DC" : 
            topo_relation_property = random.choice(['RIGHT', 'LEFT', 'BELOW', 'ABOVE'])
            rels += [{"relation_type": topo_relation, "relation_property": ''}]
            # rels += [{"relation_type": topo_relation, "relation_property": topo_relation_property}]
            if topo_relation in ["NTPP", "NTPPI", "TPP", "TPPI"]:
                # reverse_rels += [{"relation_type": reverse_relations(topo_relation), "relation_property": topo_relation_property}]
                reverse_rels += [{"relation_type": reverse_relations(topo_relation), "relation_property": ""}]
            else:
                # reverse_rels += [{"relation_type": reverse_relations(topo_relation), "relation_property": reverse_relations(topo_relation_property)}]
                reverse_rels += [{"relation_type": reverse_relations(topo_relation), "relation_property": ""}]

        else:
            rels += [{"relation_type": topo_relation, "relation_property": ''}]
            reverse_rels += [{"relation_type": topo_relation, "relation_property": ''}]
            dist_relation = random.choice(['NEAR', 'FAR'])
            rels += [{"relation_type": dist_relation, "relation_property": ''}]
            reverse_rels += [{"relation_type": reverse_relations(dist_relation), "relation_property": ''}]
            if right_front:
                X_dir_relation = random.choice(['RIGHT', 'LEFT'])
                rels += [{"relation_type": X_dir_relation, "relation_property": ''}]
                reverse_rels += [{"relation_type": reverse_relations(X_dir_relation), "relation_property": ''}]
            else:
                X_dir_relation = random.choice(['BEHIND', 'FRONT'])
                rels += [{"relation_type": X_dir_relation, "relation_property": ''}]
                reverse_rels += [{"relation_type": reverse_relations(X_dir_relation), "relation_property": ''}]
            
            Y_dir_relation = random.choice(['BELOW','ABOVE'])
            rels += [{"relation_type": Y_dir_relation, "relation_property": ''}]
            reverse_rels += [{"relation_type": reverse_relations(Y_dir_relation), "relation_property": ''}]

        scenes_rel[scene_tuple[0]] = rels
        scenes_rel[scene_tuple[1]] = reverse_rels

        

    return scenes_rel

def scene_obj_relation(story, scene, obj, seed = 0):
    
    random.seed(seed)

    # """
    #     Some data doesn't have th y_loc and x_loc. We ignore them
    # """
    # if "y_loc" not in story['structured_rep'][scene][obj] or "x_loc" not in story['structured_rep'][scene][obj]: return None
    
    y_loc = story['structured_rep'][scene][obj]['y_loc']
    x_loc = story['structured_rep'][scene][obj]['x_loc']
    size = story['structured_rep'][scene][obj]['size']
    
    rels, reverse_rels = [], []
    
    # T_B = random.choice([0,1])#Use top and bottom
    # Touching = random.choice([1,1,1])# TPP??
    
    repeat = 1        
    # if Touching: #TPP
    if y_loc == 0:
        # rels.append('touching the top edge of') 
        rels += [{"relation_type": 'TPPI', "relation_property": ''}]
        # rels += [{"relation_type": 'TPPI', "relation_property": 'ABOVE'}]
        reverse_rels += [{"relation_type": 'TPP', "relation_property": ''}]
        # reverse_rels += [{"relation_type": 'TPP', "relation_property": 'ABOVE'}]
        #repeat = 0
    elif y_loc+size == 100:
        # rels.append('touching the bottom edge of')
        rels += [{"relation_type": 'TPPI', "relation_property": ''}]
        # rels += [{"relation_type": 'TPPI', "relation_property": 'BELOW'}]
        reverse_rels += [{"relation_type": 'TPP', "relation_property": ''}]
        # reverse_rels += [{"relation_type": 'TPP', "relation_property": 'BELOW'}]
        #repeat = 0
    
    if x_loc == 0:
        # rels.append('touching the left edge of')
        rels += [{"relation_type": 'TPPI', "relation_property": ''}]
        # rels += [{"relation_type": 'TPPI', "relation_property": 'LEFT'}]
        reverse_rels += [{"relation_type": 'TPP', "relation_property": ''}]
        # reverse_rels += [{"relation_type": 'TPP', "relation_property": 'LEFT'}]
    elif x_loc+size == 100:
        # rels.append('touching the right edge of ')
        rels += [{"relation_type": 'TPPI', "relation_property": ''}]
        # rels += [{"relation_type": 'TPPI', "relation_property": 'RIGHT'}]
        reverse_rels += [{"relation_type": 'TPP', "relation_property": ''}]
        # reverse_rels += [{"relation_type": 'TPP', "relation_property": 'RIGHT'}]
    
    if not rels:
        rels += [{"relation_type": 'NTPPI', "relation_property": ''}]
        reverse_rels += [{"relation_type": 'NTPP', "relation_property": ''}]
            
    #adding top and bottom relation between object and scene      
    #if T_B and repeat:
    #    if 100 - y_loc > 70:
    #        rels.append('at the top of')
    #    elif 100 - y_loc < 30:
    #        rels.append('at the bottom of')
            
            
    return rels, reverse_rels
        

def obj_obj_relation(scene, fst, sec, limitation = None, seed = 0, front_right = 1):
    

    random.seed(seed)

    objs_rels = []
    obj1 = scene[fst]
    obj2 = scene[sec]
    
    x_1st = obj1['x_loc']
    y_1st = obj1['y_loc']
    size_1st = obj1['size']
    x_2nd = obj2['x_loc']
    y_2nd = obj2['y_loc']
    size_2nd = obj2['size']


    if x_1st - x_2nd < 0 and (x_1st+size_1st) - (x_2nd+size_2nd) < -10:
        if front_right:
            objs_rels.append({"relation_type": "LEFT", "relation_property": ''})
        else:
            objs_rels.append({"relation_type": "BEHIND", "relation_property": ''})
        
    elif x_1st - x_2nd > 0 and (x_1st+size_1st) - (x_2nd+size_2nd) > 10:
        if front_right:
            objs_rels.append({"relation_type": "RIGHT", "relation_property": ''})
        else:
            objs_rels.append({"relation_type": "FRONT", "relation_property": ''})



    if y_1st - y_2nd < 0 and (y_1st+size_1st) - (y_2nd+size_2nd) < -10:
        objs_rels.append({"relation_type": "ABOVE", "relation_property": ''})

        
    elif y_1st - y_2nd > 0 and (y_1st+size_1st) - (y_2nd+size_2nd) > 10:
        objs_rels.append({"relation_type": "BELOW", "relation_property": ''})


    #2 is a marginal errorfor touching
    if np.absolute((y_1st+size_1st) - y_2nd) < 2 and np.absolute(x_1st - x_2nd) < max(size_1st, size_2nd): 
        objs_rels.append({"relation_type": "EC", "relation_property": ''})
        # objs_rels.append({"relation_type": "EC", "relation_property": 'ABOVE'})

    elif np.absolute(y_1st - (y_2nd+size_2nd)) <2  and np.absolute(x_1st - x_2nd) < max(size_1st, size_2nd):
        objs_rels.append({"relation_type": "EC", "relation_property": ''})
        # objs_rels.append({"relation_type": "EC", "relation_property": 'BELOW'})

    elif np.absolute((x_1st+size_1st) - x_2nd) < 2 and np.absolute(y_1st - y_2nd) < max( size_1st, size_2nd):
        objs_rels.append({"relation_type": "EC", "relation_property": ''})
        # objs_rels.append({"relation_type": "EC", "relation_property": 'LEFT'})
    elif np.absolute(x_1st - (x_2nd+size_2nd)) <2 and np.absolute(y_1st - y_2nd) < max( size_1st, size_2nd):
        objs_rels.append({"relation_type": "EC", "relation_property": ''})
        # objs_rels.append({"relation_type": "EC", "relation_property": 'RIGHT'})
            


    up_treshhold, down_treshhold = 70, 20
    # if 'near to' not in forbid_rel :
            
    if  ((np.absolute((y_1st+size_1st) - y_2nd) < down_treshhold) or (np.absolute(y_1st - (y_2nd+size_2nd)) < down_treshhold)) and ((np.absolute((x_1st+size_1st) - x_2nd) < down_treshhold) or (np.absolute(x_1st - (x_2nd+size_2nd)) < down_treshhold)):
        objs_rels.append({"relation_type": "NEAR", "relation_property": ''})

            
    # if 'far from' not in forbid_rel:

    #     if ((np.absolute((y_1st+size_1st) - y_2nd) > up_treshhold) or (np.absolute(y_1st - (y_2nd+size_2nd)) > up_treshhold)) and ((np.absolute((x_1st+size_1st) - x_2nd) > up_treshhold) or (np.absolute(x_1st - (x_2nd+size_2nd)) > up_treshhold)):
    #         objs_rels.append('far from')

    #set limitation
    # forbid_rel= []
    # for x in limitation:
    #     if x[0][0] == sec and x[0][1] == fst:
    #         for r in x[1]:
    #             forbid_rel.append(forbid(r))

    
    # x = 2#random.choice([0,1,2])
    # if x == 0: dir_choose, dis_choose = 1, 0 # if choose direction in relations or not
    # elif x == 1: dir_choose, dis_choose = 0, 1 # if choose distant in relations or not
    # else: dir_choose, dis_choose = 1, 1 # both of them
        
    # if dir_choose:
        
    #     dir_type = 2 #random.choice([0,0,1,1,2])
        
    #     if dir_type == 0: #just left or right
            
    #         if x_1st - x_2nd < 0 and (x_1st+size_1st) - (x_2nd+size_2nd) < -10 and 'left' not in forbid_rel:
    #             objs_rels.append('left')
                
    #         elif x_1st - x_2nd > 0 and (x_1st+size_1st) - (x_2nd+size_2nd) > 10 and 'right' not in forbid_rel:
    #             objs_rels.append('right')
                
    #     elif dir_type == 1: #just below or above
            
    #         if y_1st - y_2nd < 0 and (y_1st+size_1st) - (y_2nd+size_2nd) < -10 and 'above' not in forbid_rel:
    #             objs_rels.append('above')
                
    #         elif y_1st - y_2nd > 0 and (y_1st+size_1st) - (y_2nd+size_2nd) > 10 and 'below' not in forbid_rel:
    #             objs_rels.append('below')
                
    #     elif dir_type == 2: #both of them
            
    #         if x_1st - x_2nd < 0 and (x_1st+size_1st) - (x_2nd+size_2nd) < -10 and 'left' not in forbid_rel:
    #             objs_rels.append('left')
                
    #         elif x_1st - x_2nd > 0 and (x_1st+size_1st) - (x_2nd+size_2nd) > 10 and 'right' not in forbid_rel:
    #             objs_rels.append('right')
                
    #         if y_1st - y_2nd < 0 and (y_1st+size_1st) - (y_2nd+size_2nd) < -10 and 'above' not in forbid_rel:
    #             objs_rels.append('above')
                
    #         elif y_1st - y_2nd > 0 and (y_1st+size_1st) - (y_2nd+size_2nd) > 10 and 'below' not in forbid_rel:
    #             objs_rels.append('below')
        
    # if dis_choose:

    #     if (y_1st+size_1st == y_2nd) or (y_2nd+size_2nd == y_1st) or (x_1st+size_1st == x_2nd) or (x_2nd+size_2nd == x_1st):
    #         if 'touching' not in forbid_rel:
    #             objs_rels.append('touching')


    #     up_treshhold, down_treshhold = 70, 20
    #     if 'near to' not in forbid_rel :
                
    #         if  ((np.absolute((y_1st+size_1st) - y_2nd) < down_treshhold) or (np.absolute(y_1st - (y_2nd++size_2nd)) < down_treshhold)) and ((np.absolute((x_1st+size_1st) - x_2nd) < down_treshhold) or (np.absolute(x_1st - (x_2nd++size_2nd)) < down_treshhold)):
    #             objs_rels.append('near to')

                
    #     if 'far from' not in forbid_rel:

    #         if ((np.absolute((y_1st+size_1st) - y_2nd) > up_treshhold) or (np.absolute(y_1st - (y_2nd++size_2nd)) > up_treshhold)) and ((np.absolute((x_1st+size_1st) - x_2nd) > up_treshhold) or (np.absolute(x_1st - (x_2nd++size_2nd)) > up_treshhold)):
    #             objs_rels.append('far from')

    return objs_rels
            
    
    
def forbid(word):
    
    words={'left':'right', 'right':'left', 'above':'below', 'below':'above', 'touching':'touching', 'far from':'far from','near to':'near to'}
    
    return words[word]


def reverse_relations(rel):

    reverse = {"DC": "DC",
         "EC":"EC",
         "PO":"PO",
         "NTPP":"NTPPI",
         "NTPPI":"NTPP",
         "TPP":"TPPI",
         "TPPI":"TPP",
         'RIGHT': "LEFT",
         'LEFT':"RIGHT",
         'BELOW':"ABOVE",
         'ABOVE':"BELOW",
         "BEHIND": "FRONT" ,
         "FRONT":"BEHIND" ,
         'FAR':"FAR",
         'NEAR':"NEAR"
         }
    return reverse[rel]