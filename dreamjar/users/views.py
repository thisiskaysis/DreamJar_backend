from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .models import Parent, Child
from .serializers import ParentSerializer, ChildSerializer

# Create your views here.
class ParentList(APIView):
    def get(self, request, format=None):
        """
        List all parents
        """
        parents = Parent.objects.all()
        serializer = ParentSerializer(parents, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        """
        Create a new parent
        """
        serializer = ParentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
                )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
            )
    
class ParentDetail(APIView):
    def get_object(self, pk):
        try:
            return Parent.objects.get(pk=pk)
        except Parent.DoesNotExist:
            raise Http404
    
    def get(self, request, pk, format=None):
        """
        Retrieve a parent by ID
        """
        parent = self.get_object(pk)
        serializer = ParentSerializer(parent)
        return Response(serializer.data)

class ChildList(APIView):
    def get(self, request, format=None):
        """
        List all children
        """
        children = Child.objects.all()
        serializer = ChildSerializer(children, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        """
        Create a new child
        The parent is set to the currently authenticated user.
        """
        serializer = ChildSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
                )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
            )
    
class ChildDetail(APIView):
    def get_object(self, pk):
        try:
            return Child.objects.get(pk=pk)
        except Child.DoesNotExist:
            raise Http404
    
    def get(self, request, pk, format=None):
        """
        Retrieve a child by ID
        """
        child = self.get_object(pk)
        serializer = ChildSerializer(child)
        return Response(serializer.data)
    
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        """
        Custom authentication to return token and user info
        """
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
            )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.id,
            'email': user.email
        })