## SpaRTUN


Recent research shows synthetic data as a source of supervision helps pretrained language models (PLM) transfer learning to new target tasks/domains. However, this idea is less explored for spatial language. We provide two new data resources on multiple spatial language processing tasks. The first dataset is synthesized for transfer learning on spatial question answering (SQA) and spatial role labeling (SpRL). Compared to previous SQA datasets, we include a larger variety of spatial relation types and spatial expressions. Our data generation process is easily extendable with new spatial expression lexicons. The second one is a real-world SQA dataset with human-generated questions built on an existing corpus with SPRL annotations. This dataset can be used to evaluate spatial language processing models in realistic situations. We show pretraining with automatically generated data significantly improves the SOTA results on several SQA and SPRL benchmarks, particularly when the training data in the target domain is small.



### Citation of [Transfer Learning with Synthetic Corpora for Spatial Role Labeling and Reasoning](https://aclanthology.org/2022.emnlp-main.413/):

    @inproceedings{mirzaee-kordjamshidi-2022-transfer,
        title = "Transfer Learning with Synthetic Corpora for Spatial Role Labeling and Reasoning",
        author = "Mirzaee, Roshanak  and
          Kordjamshidi, Parisa",
        booktitle = "Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing",
        month = dec,
        year = "2022",
        address = "Abu Dhabi, United Arab Emirates",
        publisher = "Association for Computational Linguistics",
        url = "https://aclanthology.org/2022.emnlp-main.413",
        pages = "6148--6165",
        abstract = "",
    }



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

  


