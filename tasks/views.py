
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from tasks.models import User, Task
from tasks.serializers import LoginSerializer, TaskSerializer, SignupSerializer
from tasks.utils import HandlingMessages, OnlyAdminPermission


# Create your views here.
class Register(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data
        try:
            if data['role_type'] == 1:
                User.objects.get(Q(email=data['email']) | Q(business=data['business']))
                print(1)
            elif data['role_type'] == 2:
                User.objects.get(email=data['email'])
                print(2)
            return Response({
                "message": HandlingMessages.already_exists.value.format(key='User or business'),
                "code": 400
            }, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            serializer = SignupSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.validated_data['is_active'] = True
            serializer.validated_data['password'] = make_password(data['password'])
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": HandlingMessages.success_msg.value.format(key='User'),
                "access_token": str(refresh.access_token),
                "data": serializer.data,
                "code": 201
            }, status=status.HTTP_201_CREATED)
        except KeyError as err:
            return Response({
                "message": HandlingMessages.required.value.format(key=err),
                "code": 400
            }, status=status.HTTP_400_BAD_REQUEST)


class Login(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = User.objects.get(email=request.data['email'])
            if user.check_password(serializer.validated_data['password']):
                user.save()
                refresh = RefreshToken.for_user(user)
                return Response({
                    "access_token": str(refresh.access_token),
                    "code": 200
                }, status=status.HTTP_200_OK)
            return Response({
                "message": HandlingMessages.password_wrong.value,
                "code": 400
            }, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({
                "message": HandlingMessages.email_wrong.value,
                "code": 400
            }, status=status.HTTP_400_BAD_REQUEST)


class TaskViews(APIView, PageNumberPagination):
    permission_classes = [IsAuthenticated, OnlyAdminPermission]

    def get(self, request, task_id=None):

        try:
            if task_id:
                if request.user.role_type == 1:
                    data = Task.objects.get(id=task_id)
                else:
                    data = Task.objects.get(id=task_id, assignee=request.user)
                serializer = TaskSerializer(data)
                return Response({
                    "data": serializer.data,
                    "code": 200
                }, status=status.HTTP_200_OK)

            else:
                task_status = request.GET.get('status', None)
                priority = request.GET.get('priority', None)
                assignee = request.GET.get('assignee', None)
                filter_query = {}
                if task_status:
                    filter_query['status'] = task_status
                if priority:
                    filter_query['priority'] = priority
                if assignee:
                    filter_query['assignee'] = assignee
                if request.user.role_type == 1:
                    data = Task.objects.filter(**filter_query)
                else:
                    data = Task.objects.filter(**filter_query, assignee=request.user.id)

                page = self.paginate_queryset(data, request)
                serializer = TaskSerializer(page, many=True)
                page_response = self.get_paginated_response(serializer.data)
                return Response({
                    "count": page_response.data["count"],
                    "size": self.page_size,
                    "next": page_response.data['next'],
                    "previous": page_response.data['previous'],
                    "code": 200,
                    "data": page_response.data["results"]
                }, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({
                "message": HandlingMessages.not_found.value.format(key='Task'),
                "code": 404
            }, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        data = request.data
        try:
            title = data['title']
            Task.objects.get(title=title)
            return Response({
                'message': HandlingMessages.already_exists.value.format(key='Task'),
                'code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
        except Task.DoesNotExist:
            data['created_at'] = timezone.now()
            serializer = TaskSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                'message': HandlingMessages.success_msg.value.format(key='New Task'),
                'data': serializer.data,
                'code': 201
            }, status=status.HTTP_201_CREATED)

    def put(self, request, task_id):
        try:
            data = request.data
            task = Task.objects.get(id=task_id)
            data['updated_at'] = timezone.now()
            serializer = TaskSerializer(task, data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': HandlingMessages.update_msg.value.format(key='Task'),
                    'data': serializer.data,
                    'code': 200
                }, status=status.HTTP_200_OK)
            return Response({
                "message": serializer.errors,
                "code": 400
            }, status=status.HTTP_400_BAD_REQUEST)
        except Task.DoesNotExist:
            return Response({
                "message": HandlingMessages.not_found.value.format(key='Task'),
                "code": 404
            }, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)
            task.delete()
            return Response({
                "message": HandlingMessages.delete_success.value.format(key='Task'),
                "code": 200
            }, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({
                "message": HandlingMessages.not_found.value.format(key='Task'),
                "code": 404
            }, status=status.HTTP_404_NOT_FOUND)


