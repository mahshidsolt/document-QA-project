from rest_framework import generics
from .models import Document, QAHistory
from .serializers import DocumentSerializer, QAHistorySerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import answer_question


class DocumentListCreateView(generics.ListCreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

class QAHistoryListView(generics.ListAPIView):
    queryset = QAHistory.objects.all().order_by('-created_at')
    serializer_class = QAHistorySerializer

@api_view(['POST'])
def ask_question(request):
    question = request.data.get('question', '')

    result = answer_question(question)

    history = QAHistory.objects.create(
        question=question,
        answer=result['answer']
    )

    document_ids = {
        source.get('document_id')
        for source in result['sources']
        if source.get('document_id') is not None
    }

    documents = Document.objects.filter(id__in=document_ids)
    history.documents.set(documents)

    return Response({
        'question': question,
        'answer': result['answer'],
        'sources': result['sources'],
    })