from django.shortcuts import render
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import UserSerializer,UserProfileSerializer

#Data validation done in the serializers

@api_view(['POST'])
def register_new_user(request):
    #Registering new user
    user_serializer = UserSerializer(data=request.data)
    if user_serializer.is_valid():
        user = user_serializer.save()
        user.set_password(user_serializer.validated_data['password'])
        user.save()

        profile_data = {**request.data, 'user': user.pk}
        profile_serializer = UserProfileSerializer(data=profile_data)
        if profile_serializer.is_valid():
            profile_serializer.save()
            
            # Generateing tokens
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            
            return Response({
                'email': user.email,
                'refresh': str(refresh),
                'access': str(access)
            }, status=status.HTTP_201_CREATED)
        else:
            user.delete()  # Cleanup if profile creation fails
            return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def login_user(request):
    #Handlest a reg. request
    user = User.objects.get()
    ser = UserSerializer(user,many=True)
    return JsonResponse({"users":ser.data})
    
    #If the data is valid saves it to the db and responds with OK
        
def login_with_google(request):
    #Handlest a reg. request
    user = User.objects.all()
    ser = UserSerializer(user,many=True)
    return JsonResponse({"users":ser.data})
    
    #If the data is valid saves it to the db and responds with OK
def workout_done(request):
    #Handlest a reg. request
    user = User.objects.all()
    ser = UserSerializer(user,many=True)
    return JsonResponse({"users":ser.data})

#@api_view('GET')
def get_calories(request):
    #Handlest a reg. request
    user = User.objects.all()
    ser = UserSerializer(user,many=True)
    return JsonResponse({"users":ser.data})
    
    #If the data is valid saves it to the db and responds with OK
    
def add_calories(request):
    #Handlest a reg. request
    user = User.objects.all()
    ser = UserSerializer(user,many=True)
    return JsonResponse({"users":ser.data})
    
    #If the data is valid saves it to the db and responds with OK
#@api_view('GET') 
def get_stats(request):
    #Handlest a reg. request
    user = User.objects.all()
    ser = UserSerializer(user,many=True)
    return JsonResponse({"users":ser.data})
    
    #If the data is valid saves it to the db and responds with OK
