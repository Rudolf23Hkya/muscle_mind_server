def generate_full_auth_data(user, profile, refresh, access):
    response_data = {
        'userData': {
            'email': user.email,
            'password': "",
            'username': user.username,
            'gender': profile.gender,
            'experiencelevel': profile.experiencelevel,
            'age': profile.age,
            'weight': profile.weight,
            'height': profile.height,
        },
        'tokens': {
            'refresh': str(refresh),
            'access': str(access)
        }
    }
    return response_data

def generate_auth_data(refresh, access):
    response_data = {
            'refresh': str(refresh),
            'access': str(access)
    }
    return response_data
def generate_only_user_data(user, profile):
    response_data = {
        'userData': {
            'email': user.email,
            'password': "",
            'username': user.username,
            'gender': profile.gender,
            'experiencelevel': profile.experiencelevel,
            'age': profile.age,
            'weight': profile.weight,
            'height': profile.height,
        }
    }
    return response_data