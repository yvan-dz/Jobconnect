from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404

from .models import Job, Application
from .serializers import (
    FreelancerSignupSerializer,
    CompanySignupSerializer,
    JobSerializer,
    ApplicationSerializer
)

# 🔐 Registrierung Freelancer
class FreelancerSignupView(APIView):
    def post(self, request):
        serializer = FreelancerSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Freelancer account created'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 🔐 Registrierung Company
class CompanySignupView(APIView):
    def post(self, request):
        serializer = CompanySignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Company account created'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 👤 Aktuelles Profil abrufen
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_profile(request):
    user = request.user
    data = {
        'username': user.username,
        'email': user.email,
        'role': 'freelancer' if hasattr(user, 'freelancer') else 'company' if hasattr(user, 'company') else 'none'
    }
    if hasattr(user, 'freelancer'):
        data['skills'] = user.freelancer.skills
        data['bio'] = user.freelancer.bio
    return Response(data)

# 📄 Alle Jobs auflisten
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def job_list(request):
    location = request.GET.get('location')
    skills = request.GET.get('skills')

    jobs = Job.objects.all()

    if location:
        jobs = jobs.filter(location__icontains=location)
    if skills:
        jobs = jobs.filter(skills_required__icontains=skills)

    serializer = JobSerializer(jobs, many=True)
    return Response(serializer.data)

# 📝 Job erstellen (nur für Unternehmen)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_job(request):
    if not hasattr(request.user, 'company'):
        return Response({'detail': 'Nur Unternehmen dürfen Jobs erstellen.'}, status=403)

    data = request.data.copy()
    data['company_name'] = request.user.company.company_name

    serializer = JobSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

# 🛠️ Freelancer-Profil aktualisieren
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_freelancer_profile(request):
    user = request.user

    if not hasattr(user, 'freelancer'):
        return Response({'detail': 'Nur Freelancer dürfen ihr Profil bearbeiten.'}, status=403)

    # update User model
    user.username = request.data.get('username', user.username)
    user.email = request.data.get('email', user.email)
    user.save()

    # update Freelancer model
    freelancer = user.freelancer
    freelancer.skills = request.data.get('skills', freelancer.skills)
    freelancer.bio = request.data.get('bio', freelancer.bio)
    freelancer.save()

    return Response({'message': 'Profil aktualisiert.'})

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_company_profile(request):
    user = request.user

    if not hasattr(user, 'company'):
        return Response({'detail': 'Nur Unternehmen dürfen ihr Profil bearbeiten.'}, status=403)

    # update User model
    user.username = request.data.get('username', user.username)
    user.email = request.data.get('email', user.email)
    user.save()

    # update Company model
    company = user.company
    company.company_name = request.data.get('company_name', company.company_name)
    company.website = request.data.get('website', company.website)
    company.save()

    return Response({'message': 'Profil aktualisiert.'})


# 📩 Auf Job bewerben
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_to_job(request):
    user = request.user

    # ✅ Nur Freelancer dürfen sich bewerben
    if not hasattr(user, 'freelancer'):
        return Response({'detail': 'Nur Freelancer dürfen sich bewerben.'}, status=403)

    freelancer = user.freelancer
    job_id = request.data.get('job')

    # ✅ Job abrufen oder 404
    job = get_object_or_404(Job, id=job_id)

    # ✅ Doppelte Bewerbung verhindern
    if Application.objects.filter(job=job, freelancer=freelancer).exists():
        return Response({'detail': 'Du hast dich bereits beworben.'}, status=400)

    # ✅ Bewerbung speichern
    data = {
        'job': job.id,
        'cover_letter': request.data.get('cover_letter', '')  # Verwende 'cover_letter'
    }

    serializer = ApplicationSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Bewerbung erfolgreich!'}, status=201)

    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_jobs(request):
    if not hasattr(request.user, 'company'):
        return Response({'detail': 'Nur Unternehmen können ihre Jobs einsehen.'}, status=403)

    jobs = Job.objects.filter(company_name=request.user.company.company_name)
    serializer = JobSerializer(jobs, many=True)
    return Response(serializer.data)

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def update_or_delete_job(request, job_id):
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return Response({'detail': 'Job nicht gefunden.'}, status=404)

    # Zugriff nur für das eigene Unternehmen
    if not hasattr(request.user, 'company') or job.company_name != request.user.company.company_name:
        return Response({'detail': 'Nicht autorisiert.'}, status=403)

    if request.method == 'PUT':
        serializer = JobSerializer(job, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        job.delete()
        return Response({'message': 'Job wurde gelöscht.'}, status=204)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_job_applications(request):
    if not hasattr(request.user, 'company'):
        return Response({'detail': 'Nur Unternehmen können Bewerbungen einsehen.'}, status=403)

    # Alle Bewerbungen für Jobs des eingeloggten Unternehmens
    applications = Application.objects.filter(job__company_name=request.user.company.company_name).select_related('freelancer__user', 'job')
    serializer = ApplicationSerializer(applications, many=True)
    return Response(serializer.data)