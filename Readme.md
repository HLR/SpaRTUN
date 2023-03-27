## SpaRTUN
In prolog directory, notebook called rules_text.ipynb, you can find text version of rules used in SpaRTUN.



For generating the data samples:

1. Create a Dataset and NLVR directory.

2. Put the NLVR train.json, test.json. dev.json in the NLVR directory.

3. Use below arguments on Dataset_gen.py for generting the data:


    "--num_image",  help="Number of image, 6660 for train, 1000 for other", type= int, default=1000
    
    "--story_per_image",  help="How many story do you want to create for each image", type= int, default=2
    
    "--num_question",  help="number of question for each question type.", type= int, default=2
    
    "--question_type",  help="name of the question types: all, YN, FB, FR, CO", type= str, default='all'
    
    "--no_save",  help="just testing generation phase", action='store_true', default = False
    
    "--seed_num", help="add seed number for random choices.", type= int, default=None
    
    "--skip_except", help="skip all examples expcept story X", type= int, default=None
    
    "--scene_graph", help="just testing generation phase", action='store_true', default = False
    
    "--vocabulary_object", help="the index of obejct names' list in the vocabulary file ", type=str, default = "1,2,3,4"
    
    "--vocabulary_relation", help="the index of relation expressions' list in the vocabulary file ", type=str, default = "1,2"
  

    for example:       python3 Dataset_gen.py --name dev --nlvr_data dev
    
    or :                      python3 Dataset_gen.py --name train --nlvr_data train --num_image 6660

  
  
  

  

Download [SpaRTUN](https://www.cse.msu.edu/~kordjams/data/SPARTUN.zip)

Download [ReSQ](https://www.cse.msu.edu/~kordjams/data/ReSQ.zip)

  


