from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions


class ChatAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
