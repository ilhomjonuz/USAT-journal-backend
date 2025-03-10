from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.articles.models import Article, ArticleHistory, Comment
from apps.notification.models import Notification
from apps.articles.serializers.serializers_v2 import (
    ArticleListSerializer, ArticleDetailSerializer, ArticleSubmissionSerializer,
    ArticleUpdateSerializer, ArticleRevisionSubmitSerializer,
    AssignSecretarySerializer, AssignReviewerSerializer, AssignEditorSerializer,
    AssignDeputySerializer, ReviewerDecisionSerializer, EditorDecisionSerializer,
    DeputyDecisionSerializer, SecretaryRevisionRequestSerializer, SecretaryRejectSerializer,
    PublishArticleSerializer, ArticleHistorySerializer, CommentSerializer,
    NotificationSerializer, UserSerializer
)
from core.utils.permissions import (
    IsAuthorOrReadOnly, IsSecretaryOrReadOnly, IsReviewerOrReadOnly,
    IsEditorOrReadOnly, IsDeputyOrReadOnly
)

User = get_user_model()


class ArticleSubmissionView(APIView):
    """
    API endpoint for submitting a new article.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    @swagger_auto_schema(
        operation_summary="Article submission",
        operation_description="Submit a new article with authors",
        manual_parameters=[
            openapi.Parameter(
                'Accept-Language',
                openapi.IN_HEADER,
                description="Language code (uz, ru, or en)",
                type=openapi.TYPE_STRING,
                enum=['uz', 'ru', 'en']
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'direction_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Direction ID'),
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Article title'),
                'keywords': openapi.Schema(type=openapi.TYPE_STRING, description='Keywords separated by commas'),
                'annotation': openapi.Schema(type=openapi.TYPE_STRING, description='Article annotation'),
                'references': openapi.Schema(type=openapi.TYPE_STRING, description='List of references'),
                'anti_plagiarism_certificate': openapi.Schema(type=openapi.TYPE_FILE,
                                                              description='Anti-Plagiarism Certificate'),
                'original_file': openapi.Schema(type=openapi.TYPE_FILE, description='Original article file'),
                'authors_data': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'author_id': openapi.Schema(type=openapi.TYPE_INTEGER)
                        }
                    ),
                    description='List of authors data',
                ),
            },
            required=['direction_id', 'title', 'keywords', 'annotation', 'original_file']
        ),
        responses={
            201: openapi.Response(
                description="Article created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'article': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            400: openapi.Response(
                description="Bad Request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                        'errors': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            401: openapi.Response(
                description="Unauthorized",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            500: openapi.Response(
                description="Internal server error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            serializer = ArticleSubmissionSerializer(
                data=request.data,
                context={'request': request}
            )

            if serializer.is_valid():
                article = serializer.save()
                return Response(
                    {
                        'success': True,
                        'message': _('Article submitted successfully'),
                        'article': ArticleDetailSerializer(article).data
                    },
                    status=status.HTTP_201_CREATED
                )

            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ArticleViewSet(viewsets.ModelViewSet):
    """
    Maqolalar uchun API
    """
    queryset = Article.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'author', 'secretary', 'reviewer', 'editor', 'deputy_chief']
    search_fields = ['title', 'keywords', 'annotation']
    ordering_fields = ['submission_date', 'last_updated', 'publication_date', 'title']
    ordering = ['-submission_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleListSerializer
        elif self.action in ['update', 'partial_update']:
            return ArticleUpdateSerializer
        elif self.action == 'submit_revision':
            return ArticleRevisionSubmitSerializer
        elif self.action == 'assign_secretary':
            return AssignSecretarySerializer
        elif self.action == 'assign_reviewer':
            return AssignReviewerSerializer
        elif self.action == 'assign_editor':
            return AssignEditorSerializer
        elif self.action == 'assign_deputy':
            return AssignDeputySerializer
        elif self.action == 'reviewer_decision':
            return ReviewerDecisionSerializer
        elif self.action == 'editor_decision':
            return EditorDecisionSerializer
        elif self.action == 'deputy_decision':
            return DeputyDecisionSerializer
        elif self.action == 'secretary_request_revision':
            return SecretaryRevisionRequestSerializer
        elif self.action == 'secretary_reject':
            return SecretaryRejectSerializer
        elif self.action == 'publish':
            return PublishArticleSerializer
        elif self.action == 'history':
            return ArticleHistorySerializer
        elif self.action in ['comments', 'add_comment']:
            return CommentSerializer
        return ArticleDetailSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'submit_revision']:
            permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
        elif self.action in ['assign_secretary', 'assign_reviewer', 'assign_editor', 'assign_deputy',
                             'secretary_request_revision', 'secretary_reject', 'publish']:
            permission_classes = [permissions.IsAuthenticated, IsSecretaryOrReadOnly]
        elif self.action == 'reviewer_decision':
            permission_classes = [permissions.IsAuthenticated, IsReviewerOrReadOnly]
        elif self.action == 'editor_decision':
            permission_classes = [permissions.IsAuthenticated, IsEditorOrReadOnly]
        elif self.action == 'deputy_decision':
            permission_classes = [permissions.IsAuthenticated, IsDeputyOrReadOnly]
        elif self.action == 'add_comment':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user

        # Filter articles based on user role
        if user.role == User.Role.SECRETARY:
            # Secretary sees all articles
            return Article.objects.all()
        elif user.role == User.Role.REVIEWER:
            # Reviewer sees articles assigned to them and published articles
            return Article.objects.filter(
                reviewer=user
            ) | Article.objects.filter(
                status='PUBLISHED'
            )
        elif user.role == User.Role.EDITOR:
            # Editor sees articles assigned to them and published articles
            return Article.objects.filter(
                editor=user
            ) | Article.objects.filter(
                status='PUBLISHED'
            )
        elif user.role == User.Role.DEPUTY_EDITOR:
            # Deputy editor sees articles assigned to them and published articles
            return Article.objects.filter(
                deputy_chief=user
            ) | Article.objects.filter(
                status='PUBLISHED'
            )
        else:
            # Regular users (authors) see their own articles and published articles
            return Article.objects.filter(
                author=user
            ) | Article.objects.filter(
                status='PUBLISHED'
            )

    @swagger_auto_schema(
        operation_summary="Submit revised article",
        operation_description="Submit a revised article after revision request",
        request_body=ArticleRevisionSubmitSerializer,
        responses={
            200: ArticleDetailSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['post'])
    def submit_revision(self, request, pk=None):
        """Tahrirlangan maqolani yuborish"""
        article = self.get_object()
        serializer = self.get_serializer(article, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ArticleDetailSerializer(article).data)

    @swagger_auto_schema(
        operation_summary="Assign secretary",
        operation_description="Assign a secretary to the article",
        request_body=AssignSecretarySerializer,
        responses={
            200: ArticleDetailSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['post'])
    def assign_secretary(self, request, pk=None):
        """Mas'ul kotib tayinlash"""
        article = self.get_object()
        serializer = self.get_serializer(article, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ArticleDetailSerializer(article).data)

    @swagger_auto_schema(
        operation_summary="Assign reviewer",
        operation_description="Assign a reviewer to the article",
        request_body=AssignReviewerSerializer,
        responses={
            200: ArticleDetailSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['post'])
    def assign_reviewer(self, request, pk=None):
        """Taqrizchi tayinlash"""
        article = self.get_object()
        serializer = self.get_serializer(article, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ArticleDetailSerializer(article).data)

    @swagger_auto_schema(
        operation_summary="Assign editor",
        operation_description="Assign an editor to the article",
        request_body=AssignEditorSerializer,
        responses={
            200: ArticleDetailSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['post'])
    def assign_editor(self, request, pk=None):
        """Muharrir tayinlash"""
        article = self.get_object()
        serializer = self.get_serializer(article, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ArticleDetailSerializer(article).data)

    @swagger_auto_schema(
        operation_summary="Assign deputy",
        operation_description="Assign a deputy editor to the article",
        request_body=AssignDeputySerializer,
        responses={
            200: ArticleDetailSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['post'])
    def assign_deputy(self, request, pk=None):
        """Bosh muharrir o'rinbosari tayinlash"""
        article = self.get_object()
        serializer = self.get_serializer(article, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ArticleDetailSerializer(article).data)

    @swagger_auto_schema(
        operation_summary="Reviewer decision",
        operation_description="Submit reviewer's decision on the article",
        request_body=ReviewerDecisionSerializer,
        responses={
            200: ArticleDetailSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['post'])
    def reviewer_decision(self, request, pk=None):
        """Taqrizchi qarori"""
        article = self.get_object()
        serializer = self.get_serializer(article, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ArticleDetailSerializer(article).data)

    @swagger_auto_schema(
        operation_summary="Editor decision",
        operation_description="Submit editor's decision on the article",
        request_body=EditorDecisionSerializer,
        responses={
            200: ArticleDetailSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['post'])
    def editor_decision(self, request, pk=None):
        """Muharrir qarori"""
        article = self.get_object()
        serializer = self.get_serializer(article, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ArticleDetailSerializer(article).data)

    @swagger_auto_schema(
        operation_summary="Deputy editor decision",
        operation_description="Submit deputy editor's decision on the article",
        request_body=DeputyDecisionSerializer,
        responses={
            200: ArticleDetailSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['post'])
    def deputy_decision(self, request, pk=None):
        """Bosh muharrir o'rinbosari qarori"""
        article = self.get_object()
        serializer = self.get_serializer(article, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ArticleDetailSerializer(article).data)

    @swagger_auto_schema(
        operation_summary="Secretary request revision",
        operation_description="Secretary requests revision for the article",
        request_body=SecretaryRevisionRequestSerializer,
        responses={
            200: ArticleDetailSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['post'])
    def secretary_request_revision(self, request, pk=None):
        """Mas'ul kotib tahrir talab qilishi"""
        article = self.get_object()
        serializer = self.get_serializer(article, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ArticleDetailSerializer(article).data)

    @swagger_auto_schema(
        operation_summary="Secretary reject",
        operation_description="Secretary rejects the article",
        request_body=SecretaryRejectSerializer,
        responses={
            200: ArticleDetailSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['post'])
    def secretary_reject(self, request, pk=None):
        """Mas'ul kotib rad etishi"""
        article = self.get_object()
        serializer = self.get_serializer(article, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ArticleDetailSerializer(article).data)

    @swagger_auto_schema(
        operation_summary="Publish article",
        operation_description="Publish the article in a journal issue",
        request_body=PublishArticleSerializer,
        responses={
            200: ArticleDetailSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Maqolani chop etish"""
        article = self.get_object()
        serializer = self.get_serializer(article, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ArticleDetailSerializer(article).data)

    @swagger_auto_schema(
        operation_summary="Get article history",
        operation_description="Get the history of the article",
        responses={
            200: ArticleHistorySerializer(many=True),
            401: "Unauthorized",
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Maqola tarixini olish"""
        article = self.get_object()
        history = article.history.all()
        serializer = self.get_serializer(history, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Get article comments",
        operation_description="Get the comments of the article",
        responses={
            200: CommentSerializer(many=True),
            401: "Unauthorized",
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """Maqola izohlarini olish"""
        article = self.get_object()
        comments = article.comments.all()
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Add comment to article",
        operation_description="Add a comment to the article",
        request_body=CommentSerializer,
        responses={
            201: CommentSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Maqolaga izoh qo'shish"""
        article = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(article=article, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ArticleWorkflowViewSet(viewsets.ViewSet):
    """
    Maqola jarayoni (workflow) uchun API
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get my articles",
        operation_description="Get articles based on user role",
        responses={
            200: ArticleListSerializer(many=True),
            401: "Unauthorized"
        }
    )
    @action(detail=False, methods=['get'])
    def my_articles(self, request):
        """Foydalanuvchi maqolalarini olish"""
        user = request.user

        if user.role == User.Role.AUTHOR:
            articles = Article.objects.filter(author=user)
        elif user.role == User.Role.SECRETARY:
            articles = Article.objects.filter(secretary=user)
        elif user.role == User.Role.REVIEWER:
            articles = Article.objects.filter(reviewer=user)
        elif user.role == User.Role.EDITOR:
            articles = Article.objects.filter(editor=user)
        elif user.role == User.Role.DEPUTY_EDITOR:
            articles = Article.objects.filter(deputy_chief=user)
        else:
            articles = Article.objects.none()

        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Get pending articles",
        operation_description="Get articles pending for user action",
        responses={
            200: ArticleListSerializer(many=True),
            401: "Unauthorized"
        }
    )
    @action(detail=False, methods=['get'])
    def pending_articles(self, request):
        """Foydalanuvchi uchun kutilayotgan maqolalarni olish"""
        user = request.user

        if user.role == User.Role.AUTHOR:
            # Articles that need revision from author
            articles = Article.objects.filter(author=user, status='REVISION_REQUESTED')
        elif user.role == User.Role.SECRETARY:
            # Articles that need secretary review
            articles = Article.objects.filter(status='SUBMITTED') | \
                       Article.objects.filter(status='SECRETARY_REVIEW', secretary=user)
        elif user.role == User.Role.REVIEWER:
            # Articles that need reviewer review
            articles = Article.objects.filter(reviewer=user, status='REVIEWER_REVIEW')
        elif user.role == User.Role.EDITOR:
            # Articles that need editor review
            articles = Article.objects.filter(editor=user, status='EDITOR_REVIEW')
        elif user.role == User.Role.DEPUTY_EDITOR:
            # Articles that need deputy editor review
            articles = Article.objects.filter(deputy_chief=user, status='DEPUTY_REVIEW')
        else:
            articles = Article.objects.none()

        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Get available reviewers",
        operation_description="Get available reviewers for article assignment",
        responses={
            200: openapi.Response(
                description="List of available reviewers",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'username': openapi.Schema(type=openapi.TYPE_STRING),
                            'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'email': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                )
            ),
            401: "Unauthorized",
            403: "Forbidden"
        }
    )
    @action(detail=False, methods=['get'])
    def available_reviewers(self, request):
        """Mavjud taqrizchilarni olish"""
        if request.user.role != User.Role.SECRETARY:
            return Response(
                {"detail": _("You do not have permission to perform this action.")},
                status=status.HTTP_403_FORBIDDEN
            )

        reviewers = User.objects.filter(role=User.Role.REVIEWER)
        serializer = UserSerializer(reviewers, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Get available editors",
        operation_description="Get available editors for article assignment",
        responses={
            200: openapi.Response(
                description="List of available editors",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'username': openapi.Schema(type=openapi.TYPE_STRING),
                            'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'email': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                )
            ),
            401: "Unauthorized",
            403: "Forbidden"
        }
    )
    @action(detail=False, methods=['get'])
    def available_editors(self, request):
        """Mavjud muharrirlarni olish"""
        if request.user.role != User.Role.SECRETARY:
            return Response(
                {"detail": _("You do not have permission to perform this action.")},
                status=status.HTTP_403_FORBIDDEN
            )

        editors = User.objects.filter(role=User.Role.EDITOR)
        serializer = UserSerializer(editors, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Get available deputy editors",
        operation_description="Get available deputy editors for article assignment",
        responses={
            200: openapi.Response(
                description="List of available deputy editors",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'username': openapi.Schema(type=openapi.TYPE_STRING),
                            'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'email': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                )
            ),
            401: "Unauthorized",
            403: "Forbidden"
        }
    )
    @action(detail=False, methods=['get'])
    def available_deputy_editors(self, request):
        """Mavjud bosh muharrir o'rinbosarlarini olish"""
        if request.user.role != User.Role.SECRETARY:
            return Response(
                {"detail": _("You do not have permission to perform this action.")},
                status=status.HTTP_403_FORBIDDEN
            )

        deputy_editors = User.objects.filter(role=User.Role.DEPUTY_EDITOR)
        serializer = UserSerializer(deputy_editors, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Get available journal issues",
        operation_description="Get available journal issues for article publication",
        responses={
            200: openapi.Response(
                description="List of available journal issues",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'title': openapi.Schema(type=openapi.TYPE_STRING),
                            'year': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'number': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'is_published': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        }
                    )
                )
            ),
            401: "Unauthorized",
            403: "Forbidden"
        }
    )
    @action(detail=False, methods=['get'])
    def available_journal_issues(self, request):
        """Mavjud jurnal sonlarini olish"""
        if request.user.role != User.Role.SECRETARY:
            return Response(
                {"detail": _("You do not have permission to perform this action.")},
                status=status.HTTP_403_FORBIDDEN
            )

        from apps.journals.models import JournalIssue
        journal_issues = JournalIssue.objects.filter(is_published=False)
        from apps.journals.serializers import JournalIssueListSerializer
        serializer = JournalIssueListSerializer(journal_issues, many=True)
        return Response(serializer.data)


    @swagger_auto_schema(
        operation_summary="Get workflow statistics",
        operation_description="Get statistics about article workflow",
        responses={
            200: openapi.Response(
                description="Workflow statistics",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total_articles': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'submitted': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'secretary_review': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'reviewer_review': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'editor_review': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'deputy_review': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'revision_requested': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'accepted': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'rejected': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'published': openapi.Schema(type=openapi.TYPE_INTEGER),
                    }
                )
            ),
            401: "Unauthorized"
        }
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Maqola jarayoni statistikasini olish"""
        user = request.user

        # Base queryset depends on user role
        if user.role == User.Role.SECRETARY:
            # Secretary sees all articles
            queryset = Article.objects.all()
        elif user.role == User.Role.REVIEWER:
            # Reviewer sees articles assigned to them
            queryset = Article.objects.filter(reviewer=user)
        elif user.role == User.Role.EDITOR:
            # Editor sees articles assigned to them
            queryset = Article.objects.filter(editor=user)
        elif user.role == User.Role.DEPUTY_EDITOR:
            # Deputy editor sees articles assigned to them
            queryset = Article.objects.filter(deputy_chief=user)
        else:
            # Regular users (authors) see their own articles
            queryset = Article.objects.filter(author=user)

        # Calculate statistics
        stats = {
            'total_articles': queryset.count(),
            'submitted': queryset.filter(status='SUBMITTED').count(),
            'secretary_review': queryset.filter(status='SECRETARY_REVIEW').count(),
            'reviewer_review': queryset.filter(status='REVIEWER_REVIEW').count(),
            'editor_review': queryset.filter(status='EDITOR_REVIEW').count(),
            'deputy_review': queryset.filter(status='DEPUTY_REVIEW').count(),
            'revision_requested': queryset.filter(status='REVISION_REQUESTED').count(),
            'accepted': queryset.filter(status='ACCEPTED').count(),
            'rejected': queryset.filter(status='REJECTED').count(),
            'published': queryset.filter(status='PUBLISHED').count(),
        }

        return Response(stats)


class ArticleHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Maqola tarixi uchun API
    """
    queryset = ArticleHistory.objects.all()
    serializer_class = ArticleHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['article', 'user', 'new_status']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    @swagger_auto_schema(
        operation_summary="List article history",
        operation_description="Get a list of article history entries",
        responses={
            200: ArticleHistorySerializer(many=True),
            401: "Unauthorized"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get article history entry",
        operation_description="Get details of an article history entry",
        responses={
            200: ArticleHistorySerializer,
            401: "Unauthorized",
            404: "Not Found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Maqola izohlari uchun API
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['article', 'user']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    @swagger_auto_schema(
        operation_summary="List comments",
        operation_description="Get a list of comments",
        responses={
            200: CommentSerializer(many=True),
            401: "Unauthorized"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get comment",
        operation_description="Get details of a comment",
        responses={
            200: CommentSerializer,
            401: "Unauthorized",
            404: "Not Found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create comment",
        operation_description="Create a new comment",
        request_body=CommentSerializer,
        responses={
            201: CommentSerializer,
            400: "Bad Request",
            401: "Unauthorized"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update comment",
        operation_description="Update an existing comment",
        request_body=CommentSerializer,
        responses={
            200: CommentSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found"
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partial update comment",
        operation_description="Partially update an existing comment",
        request_body=CommentSerializer,
        responses={
            200: CommentSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found"
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete comment",
        operation_description="Delete a comment",
        responses={
            204: "No Content",
            401: "Unauthorized",
            404: "Not Found"
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    """
    Bildirishnomalar uchun API
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_read']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_summary="List notifications",
        operation_description="Get a list of notifications for the current user",
        responses={
            200: NotificationSerializer(many=True),
            401: "Unauthorized"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get notification",
        operation_description="Get details of a notification",
        responses={
            200: NotificationSerializer,
            401: "Unauthorized",
            404: "Not Found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Mark notification as read",
        operation_description="Mark a notification as read",
        responses={
            200: NotificationSerializer,
            401: "Unauthorized",
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Bildirishnomani o'qilgan deb belgilash"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Mark all notifications as read",
        operation_description="Mark all notifications as read",
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: "Unauthorized"
        }
    )
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Barcha bildirishnomalarni o'qilgan deb belgilash"""
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({
            'success': True,
            'message': _('All notifications marked as read')
        })

    @swagger_auto_schema(
        operation_summary="Get unread notifications count",
        operation_description="Get the count of unread notifications",
        responses={
            200: openapi.Response(
                description="Unread notifications count",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            ),
            401: "Unauthorized"
        }
    )
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """O'qilmagan bildirishnomalar sonini olish"""
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'count': count})