from pyswip import *

prolog = Prolog()


def example_path(path):
    import os.path
    
    x = os.path.normpath(os.path.join(os.path.split(os.path.abspath(__file__))[0], "..", path)).replace("\\", "\\\\")
    print(x)
    return x

prolog.consult(example_path("prolog/spatial_rules.pl"))


print(list(prolog.query("ntpp(apple,box1).")))



