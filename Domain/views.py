from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from User.models import User
from .serializers import MemberSimpleSerializer
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class DomainAndYearWiseUserAPIView(APIView):
    """
    API endpoint that group users by year and domain.
    Only includes users from the '2nd' and '3rd' years.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        allowed_years = ['2nd', '3rd']
        # Initialize the result dictionary for each allowed year.
        result = {year: {} for year in allowed_years}

        users = User.objects.filter(
            year__in=allowed_years
        ).select_related('domain')

        # print (users)

        # Group users by their year and by their domain.
        for user in users:
            year_key = user.year  # Either '2nd' or '3rd'
            domain_key = user.domain.name.lower() if user.domain else "undefined"

            if domain_key not in result[year_key]:
                result[year_key][domain_key] = []

            serialized = MemberSimpleSerializer(user).data
            result[year_key][domain_key].append(serialized)

        return Response(result, status=status.HTTP_200_OK)
    

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from User.models import Domain
from .serializers import DomainSerializer

class DomainsByYearAPIView(APIView):
    """
    API to get a list of domains grouped by year.
    Since the domains are the same for all years, we perform a single query.
    """
    def get(self, request, *args, **kwargs):
        # Retrieve all domains in a single query
        domains = Domain.objects.all()
        serializer = DomainSerializer(domains, many=True)
        
        # Prepare a list of years based on the choices in the User model
        years = []
        for year_id, year_label in User.YEAR_CHOICES:
            years.append({
                "id": year_id,
                "label": year_label,
                "domains": serializer.data 
            })
        
        return Response(years, status=status.HTTP_200_OK)