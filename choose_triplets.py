import json

data = [json.loads(line) for line in open('NLVR/'+nlvr_data+'.json', 'r')]



x = 1
    while x:
        try : 
            _temp = random_choice(story)
            if _temp == -1: return -1
            elif _temp == []: continue 
            else: scn_rels, scn_objs, objs_rels = _temp
            
            if scn_objs != []:
                x=0
        except: 
            raise
            return -1
        
    _num_scenes = len(scn_rels)+1 #number of scenes