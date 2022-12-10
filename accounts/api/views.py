from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.api.serializers import (
    UserSerializer,
    LoginSerializer,
    SignupSerializer
)

from django.contrib.auth import (
    login as django_login,
    logout as django_logout,
    authenticate as django_authenticate,
)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class AccountViewSet(viewsets.ViewSet):
    serializer_class = SignupSerializer
    #serializer_class = LoginSerializer
    @action(methods = ['GET'], detail = False)
    def login_status(self, request):
        data = {'has_logged_in':request.user.is_authenticated}
        if request.user.is_authenticated:
            # By User Serializer serializes user info to a Json format
            data['user'] = UserSerializer(request.user).data
        return Response(data)

    @action(methods = ['POST'], detail = False)
    def logout(self, request):
        django_logout(request)
        return Response({'success':True})

    @action(methods = ['POST'], detail = False)
    def login(self, request):
        #get username and password from request
        serializer = LoginSerializer(data = request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status = 400) #400 means bad request due to client


        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        '''
        debug trick. The output can be found in cmd window
        queryset = User.objects.filter(username = username)
        print(queryset.query)
        '''


        if not User.objects.filter(username = username).exists():
            return   Response({
                    'success' : False,
                    'message' : 'User does not exist.'
                }, status = 400)
        #validate done. go to login stage
        user = django_authenticate(username = username, password = password)
        if not user or user.is_anonymous:
            return Response({
                'success' : False,
                'message' : 'Username and password does not match'
            }, status = 400)

        django_login(request, user)
        return Response({
            'success':True,
            'user': UserSerializer(instance = user).data,
        })

    @action(methods = ['POST'], detail = False)
    def signup(self, request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return   Response({
                    'success' : False,
                    'message' : 'input is not valid.'
                }, status = 400)

        user = serializer.save()
        django_login(request, user)
        return Response({
            'success': True,
            'user': UserSerializer(user).data,
        }, status = 201)





