# import logging

# import pytz
# from django.contrib.auth import password_validation
# from django.contrib.auth.models import User
# from django.core.exceptions import ValidationError

# from rest_framework import serializers
# from rest_framework.exceptions import ValidationError as drf_ValidationError

# from website.database_apps.guided_practice.models import (
#     UserPractice,
#     UserPracticeEventLog,
# )
# from localtime.models import TimeZone

# logger = logging.getLogger(__name__)


# class UserPracticeEventLogSerializer(serializers.ModelSerializer):
#     """
#     ModelSerializer for EventLog objects.
#     """

#     user = serializers.HiddenField(default=serializers.CurrentUserDefault())

#     class Meta:
#         model = UserPracticeEventLog
#         fields = "__all__"


# class UserPracticeSerializer(serializers.ModelSerializer):
#     """
#     ModelSerializer for CRUD operations on UserPractice objects.
#     """

#     update_url = serializers.HyperlinkedIdentityField(
#         view_name="user-practice-detail-v3", lookup_field="id"
#     )

#     events = serializers.HyperlinkedIdentityField(
#         view_name="user-practice-event-log-v3", lookup_field="id", read_only=True
#     )

#     user = serializers.HiddenField(default=serializers.CurrentUserDefault())

#     class Meta:
#         model = UserPractice
#         fields = ("id", "update_url", "events", "guided_practice", "committed", "user")


# class UserSerializer(serializers.ModelSerializer):
#     """
#     ModelSerializer for CRUD operations on Django User objects.

#     Attributes
#     ----------
#     timezone: TimeZone
#         a properly formatted timezone
#     password: str
#         a write only field to store the user's password
#     """

#     timezone = serializers.ChoiceField(choices=pytz.all_timezones)
#     password = serializers.CharField(write_only=True)
#     id = serializers.IntegerField(read_only=True)
#     referral_code = serializers.SerializerMethodField()
#     class Meta:
#         model = User
#         fields = (
#             "id",
#             "username",
#             "first_name",
#             "last_name",
#             "email",
#             "timezone",
#             "password",
#             "referral_code",
#         )

#     def get_referral_code(self, user: User):
#         if hasattr(user, "portaluser"):
#             subject = user.portaluser.subject
#             if subject.referral_code:
#                 return subject.referral_code.code
#             else:
#                 return None

#     def create(self, validated_data):
#         """
#         Overrides create method of model serializer,
#         to create users with timezones and passwords.

#         Parameters
#         ----------
#         validated_data: dict
#             validated date to be used to create the user

#         Returns
#         -------
#         user: User
#             A user object
#         """
#         timezone__str = validated_data.pop("timezone", None)
#         password = validated_data.pop("password", None)
#         user = User(**validated_data)

#         if password:
#             user.set_password(password)

#         user.save()

#         if timezone__str:
#             TimeZone.objects.create(user=user, timezone_str=timezone__str)
#         else:
#             TimeZone.objects.create(user=user)
#         return user

#     def update(self, instance: User, validated_data: dict):
#         """

#         Parameters
#         ----------
#         instance: User
#             a User instance to be updated
#         validated_data: dict
#             validated data

#         Returns
#         -------
#         instance: User
#             The updated instance
#         """

#         if "timezone" in validated_data:
#             timezone__str = validated_data.pop("timezone", None)
#             if hasattr(instance, "timezone"):
#                 instance.timezone.timezone_str = timezone__str
#                 instance.timezone.save()
#             else:
#                 TimeZone.objects.create(user=instance, timezone_str=timezone__str)
#                 logger.debug(f"timezone created for {instance.username}")

#         if "password" in validated_data:
#             instance.set_password(validated_data.pop("password"))

#         for field in self.Meta.fields:
#             if field in validated_data:
#                 setattr(instance, field, validated_data[field])

#         instance.save()
#         return instance

#     def validate(self, attrs: dict):
#         """
#         Validates password using django password validation

#         Parameters
#         ----------
#         attrs: dict
#             attributes to be validated

#         Returns
#         -------
#         attrs: dict
#             validated attributes
#         """
#         if self.instance:
#             # make a copy which will error if saved
#             instance = User.objects.get(pk=self.instance.pk)
#             instance.pk = None
#         else:
#             instance = User()

#         for key, value in attrs.items():
#             if key == "password":
#                 instance.set_password(value)
#             elif key == "timezone":
#                 pass
#             else:
#                 setattr(instance, key, value)

#         if "password" in attrs:
#             if hasattr(self, "instance"):
#                 try:
#                     password_validation.validate_password(
#                         attrs["password"], user=instance
#                     )
#                 except ValidationError as e:
#                     raise drf_ValidationError({'password': e.messages}) from e

#         return attrs
