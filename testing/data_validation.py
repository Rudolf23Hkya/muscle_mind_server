import re


#Functions used for API data validation
    
def validate_u_experience(experience):
    if experience not in ["NEW","INTERMEDIATE","EXPERIENCED","PROFESSIONAL"] :
        raise ValueError("Invalid user Experience value.")
    