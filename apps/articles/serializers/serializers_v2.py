from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.core.validators import FileExtensionValidator

from apps.articles.models import Article, ArticleHistory, Comment
from apps.authors.models import Author
from apps.categories.models import Category
from apps.journals.models import JournalIssue
from apps.notification.models import Notification

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = [
            'id', 'first_name', 'last_name', 'country', 'city',
            'workplace', 'level', 'email', 'phone', 'telegram_contact',
            'whatsapp_contact', 'academic_degree', 'academic_title', 'orcid'
        ]


class ArticleListSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'status', 'status_display',
            'author', 'author_name', 'category', 'category_name',
            'submission_date', 'last_updated'
        ]

    def get_author_name(self, obj):
        if obj.author and hasattr(obj.author, 'profile'):
            return f"{obj.author.profile.first_name} {obj.author.profile.last_name}"
        return None

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None


class ArticleDetailSerializer(serializers.ModelSerializer):
    author_details = UserSerializer(source='author', read_only=True)
    secretary_details = UserSerializer(source='secretary', read_only=True)
    reviewer_details = UserSerializer(source='reviewer', read_only=True)
    editor_details = UserSerializer(source='editor', read_only=True)
    deputy_chief_details = UserSerializer(source='deputy_chief', read_only=True)
    status_display = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    history = serializers.SerializerMethodField()
    authors_info = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'keywords', 'annotation', 'references',
            'category', 'category_name', 'status', 'status_display',
            'author', 'author_details', 'authors_info',
            'secretary', 'secretary_details',
            'reviewer', 'reviewer_details', 'editor', 'editor_details',
            'deputy_chief', 'deputy_chief_details',
            'original_file', 'revised_file', 'anti_plagiarism_certificate',
            'submission_date', 'revision_requested_date', 'acceptance_date', 'publication_date',
            'journal_issue', 'start_page', 'end_page',
            'views_count', 'downloads_count', 'history'
        ]
        read_only_fields = [
            'slug', 'status', 'submission_date', 'revision_requested_date',
            'acceptance_date', 'publication_date',
            'views_count', 'downloads_count'
        ]

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

    def get_history(self, obj):
        history = obj.history.all()
        return ArticleHistorySerializer(history, many=True).data

    def get_authors_info(self, obj):
        authors = obj.authors.all()
        return AuthorSerializer(authors, many=True).data


class ArticleSubmissionSerializer(serializers.ModelSerializer):
    direction_id = serializers.IntegerField(write_only=True, required=True)
    authors_data = serializers.JSONField(write_only=True, required=False)
    anti_plagiarism_certificate = serializers.FileField(
        required=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text='Accepted file types: .pdf'
    )
    original_file = serializers.FileField(
        required=True,
        validators=[FileExtensionValidator(allowed_extensions=['doc', 'docx', 'odt'])],
        help_text='Article original file, types: doc, docx, odt'
    )

    class Meta:
        model = Article
        fields = [
            'direction_id', 'title', 'keywords', 'annotation', 'references',
            'authors_data', 'anti_plagiarism_certificate', 'original_file'
        ]

    def validate_direction_id(self, value):
        if not value:
            raise serializers.ValidationError(_('Direction id is required'))

        if not Category.objects.filter(id=value).exists():
            raise serializers.ValidationError(_('Invalid direction id'))

        return value

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user

        try:
            author = user.profile
        except Author.DoesNotExist:
            raise serializers.ValidationError(
                {"user": _("User profile does not exist. Please create a profile first.")})

        authors_data = validated_data.pop('authors_data', [])
        direction_id = validated_data.pop('direction_id')

        category = Category.objects.get(id=direction_id)
        validated_data['category'] = category
        article = Article.objects.create(**validated_data)

        article.authors.add(author)
        article.author = user
        article.save()

        for author_data in authors_data:
            author_id = author_data.get('author_id')
            try:
                co_author = Author.objects.get(id=author_id)
                article.authors.add(co_author)
            except Author.DoesNotExist:
                raise serializers.ValidationError({"detail": _("Author with id {} not found.").format(author_id)})

        # Create initial history entry
        ArticleHistory.objects.create(
            article=article,
            user=user,
            new_status='SUBMITTED',
            comment=_('Maqola yuborildi')
        )

        # Send notification to secretaries
        Notification.notify_secretary(
            article,
            _("Yangi maqola yuborildi"),
            _(f"Yangi maqola yuborildi: {article.title}")
        )

        return article


class ArticleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            'title', 'category', 'keywords', 'annotation', 'references',
            'original_file', 'anti_plagiarism_certificate'
        ]


class ArticleRevisionSubmitSerializer(serializers.Serializer):
    revised_file = serializers.FileField(
        required=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text='Accepted file types: .pdf'
    )
    comment = serializers.CharField(required=False)

    def validate(self, attrs):
        article = self.instance
        if article.status != 'REVISION_REQUESTED':
            raise serializers.ValidationError(_("Faqat tahrir uchun qaytarilgan maqolani qayta yuborish mumkin"))
        return attrs

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.submit_revision(
            author=user,
            revised_file=validated_data.get('revised_file'),
            comment=validated_data.get('comment', '')
        )
        return instance


class AssignSecretarySerializer(serializers.Serializer):
    secretary = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def validate_secretary(self, value):
        # Check if user has secretary role
        if value.role != User.Role.SECRETARY:
            raise serializers.ValidationError(_("Foydalanuvchi mas'ul kotib emas"))
        return value

    def validate(self, attrs):
        article = self.instance
        if article.status != 'SUBMITTED':
            raise serializers.ValidationError(_("Faqat yuborilgan maqolaga mas'ul kotib tayinlash mumkin"))
        return attrs

    def update(self, instance, validated_data):
        secretary = validated_data.get('secretary')
        instance.assign_secretary(secretary)
        return instance


class AssignReviewerSerializer(serializers.Serializer):
    reviewer = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def validate_reviewer(self, value):
        # Check if user has reviewer role
        if value.role != User.Role.REVIEWER:
            raise serializers.ValidationError(_("Foydalanuvchi taqrizchi emas"))
        return value

    def validate(self, attrs):
        article = self.instance
        user = self.context['request'].user

        if article.status != 'SECRETARY_REVIEW':
            raise serializers.ValidationError(
                _("Faqat mas'ul kotib tekshiruvida bo'lgan maqolaga taqrizchi tayinlash mumkin"))

        if article.secretary != user:
            raise serializers.ValidationError(_("Faqat mas'ul kotib taqrizchi tayinlashi mumkin"))

        return attrs

    def update(self, instance, validated_data):
        user = self.context['request'].user
        reviewer = validated_data.get('reviewer')
        instance.assign_reviewer(user, reviewer)
        return instance


class AssignEditorSerializer(serializers.Serializer):
    editor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def validate_editor(self, value):
        # Check if user has editor role
        if value.role != User.Role.EDITOR:
            raise serializers.ValidationError(_("Foydalanuvchi muharrir emas"))
        return value

    def validate(self, attrs):
        article = self.instance
        user = self.context['request'].user

        if article.status != 'SECRETARY_REVIEW' or article.reviewer is None:
            raise serializers.ValidationError(
                _("Faqat taqrizchi tekshiruvidan o'tgan maqolaga muharrir tayinlash mumkin"))

        if article.secretary != user:
            raise serializers.ValidationError(_("Faqat mas'ul kotib muharrir tayinlashi mumkin"))

        return attrs

    def update(self, instance, validated_data):
        user = self.context['request'].user
        editor = validated_data.get('editor')
        instance.assign_editor(user, editor)
        return instance


class AssignDeputySerializer(serializers.Serializer):
    deputy = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def validate_deputy(self, value):
        # Check if user has deputy role
        if value.role != User.Role.DEPUTY_EDITOR:
            raise serializers.ValidationError(_("Foydalanuvchi bosh muharrir o'rinbosari emas"))
        return value

    def validate(self, attrs):
        article = self.instance
        user = self.context['request'].user

        if article.status != 'SECRETARY_REVIEW' or article.editor is None:
            raise serializers.ValidationError(
                _("Faqat muharrir tekshiruvidan o'tgan maqolaga bosh muharrir o'rinbosari tayinlash mumkin"))

        if article.secretary != user:
            raise serializers.ValidationError(_("Faqat mas'ul kotib bosh muharrir o'rinbosari tayinlashi mumkin"))

        return attrs

    def update(self, instance, validated_data):
        user = self.context['request'].user
        deputy = validated_data.get('deputy')
        instance.deputy_chief = deputy
        instance.status = 'DEPUTY_REVIEW'
        instance.save()

        # Tarix yozuvini yaratish
        ArticleHistory.objects.create(
            article=instance,
            user=user,
            old_status='SECRETARY_REVIEW',
            new_status='DEPUTY_REVIEW',
            comment=f'Bosh muharrir o\'rinbosari tayinlandi'
        )

        # Bildirishnoma yuborish
        Notification.notify_deputy(
            instance,
            _("Sizga yangi maqola tayinlandi"),
            _(f"Sizga yangi maqola tayinlandi: {instance.title}")
        )

        return instance


class ReviewerDecisionSerializer(serializers.Serializer):
    is_approved = serializers.BooleanField(required=True)
    comment = serializers.CharField(required=False)
    file = serializers.FileField(required=False)

    def validate(self, attrs):
        article = self.instance
        user = self.context['request'].user

        if article.status != 'REVIEWER_REVIEW':
            raise serializers.ValidationError(
                _("Faqat taqrizchi tekshiruvida bo'lgan maqola bo'yicha qaror qabul qilish mumkin"))

        if article.reviewer != user:
            raise serializers.ValidationError(_("Faqat tayinlangan taqrizchi qaror qabul qilishi mumkin"))

        return attrs

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.reviewer_decision(
            reviewer=user,
            is_approved=validated_data.get('is_approved'),
            comment=validated_data.get('comment', ''),
            file=validated_data.get('file')
        )
        return instance


class EditorDecisionSerializer(serializers.Serializer):
    is_approved = serializers.BooleanField(required=True)
    comment = serializers.CharField(required=False)
    file = serializers.FileField(required=False)

    def validate(self, attrs):
        article = self.instance
        user = self.context['request'].user

        if article.status != 'EDITOR_REVIEW':
            raise serializers.ValidationError(
                _("Faqat muharrir tekshiruvida bo'lgan maqola bo'yicha qaror qabul qilish mumkin"))

        if article.editor != user:
            raise serializers.ValidationError(_("Faqat tayinlangan muharrir qaror qabul qilishi mumkin"))

        return attrs

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.editor_decision(
            editor=user,
            is_approved=validated_data.get('is_approved'),
            comment=validated_data.get('comment', ''),
            file=validated_data.get('file')
        )
        return instance


class DeputyDecisionSerializer(serializers.Serializer):
    is_approved = serializers.BooleanField(required=True)
    comment = serializers.CharField(required=False)

    def validate(self, attrs):
        article = self.instance
        user = self.context['request'].user

        if article.status != 'DEPUTY_REVIEW':
            raise serializers.ValidationError(
                _("Faqat bosh muharrir o'rinbosari tekshiruvida bo'lgan maqola bo'yicha qaror qabul qilish mumkin"))

        if article.deputy_chief != user:
            raise serializers.ValidationError(
                _("Faqat tayinlangan bosh muharrir o'rinbosari qaror qabul qilishi mumkin"))

        return attrs

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.deputy_decision(
            deputy=user,
            is_approved=validated_data.get('is_approved'),
            comment=validated_data.get('comment', '')
        )
        return instance


class SecretaryRevisionRequestSerializer(serializers.Serializer):
    comment = serializers.CharField(required=True)
    file = serializers.FileField(required=False)

    def validate(self, attrs):
        article = self.instance
        user = self.context['request'].user

        if article.status != 'SECRETARY_REVIEW':
            raise serializers.ValidationError(
                _("Faqat mas'ul kotib tekshiruvida bo'lgan maqolani tahrir uchun qaytarish mumkin"))

        if article.secretary != user:
            raise serializers.ValidationError(_("Faqat mas'ul kotib tahrir uchun qaytarishi mumkin"))

        return attrs

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.secretary_request_revision(
            secretary=user,
            comment=validated_data.get('comment', ''),
            file=validated_data.get('file')
        )
        return instance


class SecretaryRejectSerializer(serializers.Serializer):
    comment = serializers.CharField(required=True)

    def validate(self, attrs):
        article = self.instance
        user = self.context['request'].user

        if article.status != 'SECRETARY_REVIEW':
            raise serializers.ValidationError(_("Faqat mas'ul kotib tekshiruvida bo'lgan maqolani rad etish mumkin"))

        if article.secretary != user:
            raise serializers.ValidationError(_("Faqat mas'ul kotib rad etishi mumkin"))

        return attrs

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.secretary_reject(
            secretary=user,
            comment=validated_data.get('comment', '')
        )
        return instance


class PublishArticleSerializer(serializers.Serializer):
    journal_issue = serializers.PrimaryKeyRelatedField(queryset=JournalIssue.objects.filter(is_published=False))
    start_page = serializers.IntegerField(min_value=1, required=True)
    end_page = serializers.IntegerField(min_value=1, required=True)
    revised_file = serializers.FileField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text='Accepted file types: .pdf'
    )

    def validate(self, attrs):
        article = self.instance
        user = self.context['request'].user

        if article.status != 'ACCEPTED':
            raise serializers.ValidationError(_("Faqat qabul qilingan maqolani chop etish mumkin"))

        if attrs['start_page'] >= attrs['end_page']:
            raise serializers.ValidationError(_("Boshlanish sahifasi tugash sahifasidan kichik bo'lishi kerak"))

        return attrs

    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.publish(instance, validated_data)
        user = self.context['request'].user
        instance.publish(
            user=user,
            journal_issue=validated_data.get('journal_issue'),
            start_page=validated_data.get('start_page'),
            end_page=validated_data.get('end_page'),
            revised_file=validated_data.get('revised_file')
        )
        return instance


class ArticleHistorySerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    old_status_display = serializers.SerializerMethodField()
    new_status_display = serializers.SerializerMethodField()

    class Meta:
        model = ArticleHistory
        fields = [
            'id', 'user', 'user_details', 'old_status', 'old_status_display',
            'new_status', 'new_status_display', 'comment', 'file', 'created_at'
        ]

    def get_old_status_display(self, obj):
        if not obj.old_status:
            return ""
        for status, display in Article.STATUS_CHOICES:
            if status == obj.old_status:
                return display
        return obj.old_status

    def get_new_status_display(self, obj):
        for status, display in Article.STATUS_CHOICES:
            if status == obj.new_status:
                return display
        return obj.new_status


class CommentSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'article', 'user', 'user_details', 'text', 'file', 'created_at']
        read_only_fields = ['user']

    def create(self, validated_data):
        user = self.context['request'].user
        return Comment.objects.create(user=user, **validated_data)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'article', 'title', 'message', 'is_read', 'created_at']
        read_only_fields = ['user', 'article', 'title', 'message', 'created_at']
