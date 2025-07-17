
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Contact, MapUserContact, Profile
from .serializers import ContactSerializer

class ContactList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        contacts = Contact.objects.all()
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    def post(self, request):
        name = request.data.get("name")
        phone_number = request.data.get("phone_number")
        email = request.data.get("email")

        if not name or not phone_number:
            return Response({"Error": "Both name and phone_number are required"}, status=status.HTTP_400_BAD_REQUEST)

        contact = Contact.objects.create(name=name, phone_number=phone_number, email=email)
        MapUserContact.objects.create(user=request.user, contact=contact)

        return Response({"Message": "Contact saved successfully!"}, status=status.HTTP_201_CREATED)


@permission_classes((AllowAny,))
class Register(APIView):
    def post(self, request):
        name = request.data.get("name")
        phone_number = request.data.get("phone_number")
        password = request.data.get("password")
        email = request.data.get("email", "NONE")

        if not name or not phone_number or not password:
            return Response({"Error": "Name, phone_number, and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=name).exists():
            return Response({"Error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = User(username=name, email=email)
        user.set_password(password)
        user.save()

        Profile.objects.create(user=user, phone_number=phone_number, email=email)

        return Response({"Message": "Registered successfully"}, status=status.HTTP_201_CREATED)


@permission_classes((AllowAny,))
class Login(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"Error": "Please provide both username and password"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if not user:
            return Response({"Error": "Invalid Credentials"}, status=status.HTTP_404_NOT_FOUND)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({"Token": token.key}, status=status.HTTP_200_OK)


# class MarkSpam(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         phone_number = request.data.get("phone_number")

#         if not phone_number:
#             return Response({"Error": "Phone number required"}, status=status.HTTP_400_BAD_REQUEST)

#         contact_updated = Contact.objects.filter(phone_number=phone_number).update(spam=True)
#         profile_updated = Profile.objects.filter(phone_number=phone_number).update(spam=True)

#         if contact_updated or profile_updated:
#             return Response({"Message": "Contact marked as spam successfully!"}, status=status.HTTP_200_OK)
#         else:
#             return Response({"Error": "Phone number not found"}, status=status.HTTP_404_NOT_FOUND)
@permission_classes((AllowAny,))
class MarkSpam(APIView):
	def post(self,request):
		phone_number=request.data.get("phone_number")
		if request.data["phone_number"] is None:
			return Response(
				{
					"Error":"Phone number required!!"
				},
				status = status.HTTP_400_BAD_REQUEST
			)
		contact=Contact.objects.filter(phone_number=phone_number).update(spam=True)
		profile=Profile.objects.filter(phone_number=phone_number).update(spam=True)
		if (contact+profile):
			return Response(
				{
					"Message":"Contact marked as spam successfully!!"
				},
				status = status.HTTP_200_OK
			)
		else:
			return Response(
				{
					"Error":"Phone number not found!!"
				},
				status = status.HTTP_404_NOT_FOUND
			)
class SearchName(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        name = request.query_params.get("name")

        if not name:
            return Response({"Error": "Name is required"}, status=status.HTTP_400_BAD_REQUEST)

        profile_start = Profile.objects.filter(user__username__startswith=name)
        profile_contain = Profile.objects.filter(user__username__contains=name).exclude(user__username__startswith=name)
        contact_start = Contact.objects.filter(name__startswith=name)
        contact_contain = Contact.objects.filter(name__contains=name).exclude(name__startswith=name)

        response = []

        for profile in profile_start:
            response.append({
                "name": profile.user.username,
                "phone_number": profile.phone_number,
                "spam": profile.spam,
            })

        for contact in contact_start:
            response.append({
                "name": contact.name,
                "phone_number": contact.phone_number,
                "spam": contact.spam,
            })

        for profile in profile_contain:
            response.append({
                "name": profile.user.username,
                "phone_number": profile.phone_number,
                "spam": profile.spam,
            })

        for contact in contact_contain:
            response.append({
                "name": contact.name,
                "phone_number": contact.phone_number,
                "spam": contact.spam,
            })

        return Response(response, status=status.HTTP_200_OK)


class SearchPhoneNumber(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        phone_number = request.query_params.get("phone_number")

        if not phone_number:
            return Response({"Error": "Phone number required"}, status=status.HTTP_400_BAD_REQUEST)

        profile = Profile.objects.filter(phone_number=phone_number).first()

        if profile:
            user = User.objects.filter(id=profile.user.id, is_active=True).first()
            return Response({
                "name": user.username,
                "phone_number": profile.phone_number,
                "spam": profile.spam,
                "email": profile.email if request.user in user.profile.contacts.all() else None
            }, status=status.HTTP_200_OK)
        else:
            contacts = Contact.objects.filter(phone_number=phone_number)
            serializer = ContactSerializer(contacts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
