from django.contrib.auth import get_user_model
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

User = get_user_model()


class LoginSerializer(serializers.ModelSerializer):
    """Сериализатор для представления LoginView."""

    phone = PhoneNumberField(required=True)

    class Meta:
        model = User
        read_only_fields = ("id", )
        fields = ('id', 'phone')


class AuthSerializer(serializers.Serializer):
    phone = PhoneNumberField(required=True)
    verification_code = serializers.CharField(required=True,
                                              min_length=4, max_length=4)


class UserProfileSerializer(serializers.ModelSerializer):
    referal_user = serializers.SerializerMethodField()
    referal_user_code = serializers.CharField(write_only=True)
    refered_users = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('phone', 'referal_user', 'referal_user_code',
                  'refered_users')

    def get_referal_user(self, obj):
        referal_user = obj.referal_user
        return str(referal_user) if referal_user else None

    def get_refered_users(self, obj):
        return [str(user) for user in obj.refered_users.all()]

    def update(self, instance, validated_data):
        referal_user_code = validated_data.pop('referal_user_code', None)

        if referal_user_code:
            try:
                referal_user = User.objects.get(
                    my_invite_code=referal_user_code)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    "Введен неверный код приглашения.")

            if instance.referal_user:
                raise serializers.ValidationError(
                    "Код приглашения вами уже был активирован.")

            instance.referal_user = referal_user
            instance.save()

        return instance
