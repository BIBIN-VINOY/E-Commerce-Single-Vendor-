from rest_framework.views import APIView
from rest_framework.response import Response


class ProtectedTestView(APIView):

    def get(self, request):

        return Response({
            'message': 'JWT authentication successful',
            'username': request.user.get_username(),
            'user_id': request.user.pk,
        })