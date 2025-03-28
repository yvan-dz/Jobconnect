from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Freelancer, Company, Application, Job

# 🔐 User-Daten (Basis)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

# 👤 Freelancer-Registrierung
class FreelancerSignupSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Freelancer
        fields = ['user', 'skills', 'bio']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        freelancer = Freelancer.objects.create(user=user, **validated_data)
        return freelancer

# 🏢 Company-Registrierung
class CompanySignupSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Company
        fields = ['user', 'company_name', 'website']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        company = Company.objects.create(user=user, **validated_data)
        return company

# 📄 Job-Serialisierung
class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'

# 📩 Bewerbung-Serialisierung
class ApplicationSerializer(serializers.ModelSerializer):
    freelancer_username = serializers.CharField(source='freelancer.user.username', read_only=True)

    class Meta:
        model = Application
        fields = ['id', 'job', 'cover_letter', 'applied_at', 'freelancer_username']
        read_only_fields = ['id', 'applied_at', 'freelancer_username']

    def create(self, validated_data):
        request = self.context.get('request')
        try:
            freelancer = request.user.freelancer
        except Exception:
            raise serializers.ValidationError("Nur Freelancer können sich bewerben.")

        validated_data['freelancer'] = freelancer
        return super().create(validated_data)