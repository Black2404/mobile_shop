from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'address']

    def create(self, validated_data):
        # Dùng create_user để mật khẩu được mã hóa
        return User.objects.create_user(**validated_data)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        # authenticate kiểm tra email, password và cả is_active
        user = authenticate(email=data['email'], password=data['password'])

        if not user:
            raise serializers.ValidationError("Email hoặc mật khẩu không đúng")

        # Tạo Token JWT
        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            }
        }
# serializers.py
class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=6)

    class Meta:
        model = User
        fields = ['name', 'address', 'password'] # Chỉ cho phép user tự sửa các trường này

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password) # Mã hóa mật khẩu mới
        
        return super().update(instance, validated_data)