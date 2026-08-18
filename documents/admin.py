from django.contrib import admin

from .models import Document, QAHistory
from .utils import answer_question


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'uploaded_at')


@admin.register(QAHistory)
class QAHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'short_question',
        'source_documents',
        'created_at',
    )

    readonly_fields = (
        'answer',
        'source_documents',
        'created_at',
    )

    fields = (
        'question',
        'answer',
        'source_documents',
        'created_at',
    )

    def short_question(self, obj):
        return obj.question[:70]

    short_question.short_description = 'Question'

    def source_documents(self, obj):
        if not obj.pk:
            return '-'

        return ', '.join(
            document.title
            for document in obj.documents.all()
        ) or '-'

    source_documents.short_description = 'Source Documents'

    def save_model(self, request, obj, form, change):

        # Generate an answer only when a new question is created
        if not change:
            result = answer_question(obj.question)

            obj.answer = result['answer']

            # First save QAHistory so it gets an ID
            super().save_model(request, obj, form, change)

            document_ids = {
                source.get('document_id')
                for source in result['sources']
                if source.get('document_id') is not None
            }

            documents = Document.objects.filter(
                id__in=document_ids
            )

            obj.documents.set(documents)

        else:
            super().save_model(request, obj, form, change)