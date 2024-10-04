from .serializers import *
from ecomus.models import User
from django.urls import reverse
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from ecomus.utils import send_activation_email, send_reset_password_email

# Create your views here.




#################################################################  Authentication system   #######################################################################



#################################################################  Get CSRFToken

@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFToken(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({'success':'CSRF Cookie Set'})
    


#################################################################  Check_Authenticated_View

@method_decorator(csrf_protect, name='dispatch')
class CheckAuthenticatedView(APIView):
    permission_classes=[AllowAny]
    def get(self, request):
        if request.user.is_authenticated:
            return Response({'isAuthenticated': True})
        else:
            return Response({'isAuthenticated': False})
        

#################################################################  Registration_View

@method_decorator(csrf_protect, name='dispatch')
class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("Received Data: ", request.data)
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            print("Serializer Validated Data: ", serializer.validated_data)
            user = serializer.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = reverse('activate', kwargs={'uid': uid, 'token': token})
            activation_url = f'{settings.SITE_DOMAIN}{activation_link}'

            print("Activation URL: ", activation_url)
            send_activation_email(user.email, activation_url)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("Serializer Errors: ", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#################################################################  Activate_View

@method_decorator(csrf_protect, name='dispatch')
class ActivateView(APIView):
    permission_classes = [AllowAny]


#################################################################  Activation_Confirm

@method_decorator(csrf_protect, name='dispatch')
class ActivationConfirm(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        if not uid or not token:
            return Response({'detail': 'Missing uid or token.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                if user.is_active:
                    return Response({'detail': 'Account is already activated.'}, status=status.HTTP_200_OK)
 
                user.is_active = True
                user.save()
                return Response({'detail': 'Account activated successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Invalid activation link.'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'detail': 'Invalid activation link.'}, status=status.HTTP_400_BAD_REQUEST)
        




#################################################################  Login_View

@method_decorator(csrf_protect, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, email=email, password=password)
     
        if user is not None:
            if user.is_active:
                login(request, user)
                return Response({'detail':'Logged in successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Email or Password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        



#################################################################  Change_Password_View

class ChangePasswordView(APIView):
    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        user = request.user

        if not user.check_password(old_password):
            return Response({'detail': 'Invalid old password.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Password changed successfully.'}, status=status.HTTP_200_OK)
    


#################################################################  Logout_View

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'detail': 'Logged out successfully.'}, status=status.HTTP_200_OK)
    



#################################################################  Reset_Password_Email_View

@method_decorator(csrf_protect, name='dispatch')
class ResetPasswordEmailView(APIView):
    permission_classes=[AllowAny]
    def post(self, request):
        email = request.data.get('email')

        if not User.objects.filter(email=email).exists():
            return Response({'detail': 'User with this email does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(email=email)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = reverse('reset_password', kwargs={'uid': uid, 'token': token})
        # print("Reset Link", reset_link)
        reset_url = f'{settings.SITE_DOMAIN}{reset_link}'
        # print("Reset URL", reset_url)
        send_reset_password_email(user.email, reset_url)

        return Response({'detail': 'Password reset email sent successfully.'}, status=status.HTTP_200_OK)
    


################################################################# Reset_Password_View

@method_decorator(csrf_protect, name='dispatch')
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]




################################################################# Reset_Password_Confirm_View

@method_decorator(csrf_protect, name='dispatch')
class ResetPasswordConfirmView(APIView):
    permission_classes=[AllowAny]
    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        if not uid or not token:
            return Response({'detail': 'Missing uid or token.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                new_password = request.data.get('new_password')

                if not new_password:
                    return Response({'detail': 'New password is required.'}, status=status.HTTP_400_BAD_REQUEST)

                user.set_password(new_password)
                user.save()
                return Response({'detail': 'Password reset successful.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Invalid reset password link.'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'detail': 'Invalid reset password link.'}, status=status.HTTP_400_BAD_REQUEST)








#################################################################  create User  ########################################################################

class UserCreateView(APIView):
    def post(self, request):
        serializer = UsercreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

#################################################################  Profile view  #######################################################################


class ProfileView(APIView):
    def get(self,request,id):
        try:
            obj = Profile.objects.get(id=id)
        except Profile.DoesNotExist:
            msg = {"msg":"not found"}
            return Response(msg,status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProfileSerializer(obj)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    
#################################################################  Category CRUD  ######################################################################

@method_decorator(csrf_protect, name='dispatch')
class categoryView(APIView):
    def get(self,request,id):
        try:
            obj = Category.objects.get(id=id)
        except Category.DoesNotExist:
            msg = {"msg":"not found"}
            return Response(msg,status=status.HTTP_404_NOT_FOUND)
        
        serializer = categorySerializer(obj)
        return Response(serializer.data,status=status.HTTP_200_OK)
    

    
    def post(self,request):
        serializer = categorySerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    
    def put(self,request,id):
        try:
            obj = Category.objects.get(id=id)
        except Category.DoesNotExist:
            msg = {"msg":"not found"}
            return Response(msg,status=status.HTTP_404_NOT_FOUND)
        
        serializer = categorySerializer(obj,data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    
    def patch(self,request,id):
        try:
            obj = Category.objects.get(id=id)
        except Category.DoesNotExist:
            msg = {"msg":"not found"}
            return Response(msg,status=status.HTTP_404_NOT_FOUND)
        
        serializer = categorySerializer(obj,data = request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def delete(self, id):
        try:
            obj = Category.objects.get(id=id)
        except Category.DoesNotExist:
            msg = {"msg": "not found"}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
        
        obj.delete() 
        msg = {"msg": "deleted successfully"}
        return Response(msg, status=status.HTTP_204_NO_CONTENT)

        
#################################################################  Store CRUD  #########################################################################

@method_decorator(csrf_protect, name='dispatch')
class StoreView(APIView):

    def get(self, request, id):
        try:
            obj = Store.objects.get(id=id)
        except Store.DoesNotExist:
            msg = {"msg": "not found"}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
        
        serializer = StoreSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


    def post(self, request):
        serializer = StoreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


    def put(self, request, id):
        try:
            obj = Store.objects.get(id=id)
        except Store.DoesNotExist:
            msg = {"msg": "not found"}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
        
        serializer = StoreSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


    def patch(self, request, id):
        try:
            obj = Store.objects.get(id=id)
        except Store.DoesNotExist:
            msg = {"msg": "not found"}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
        
        serializer = StoreSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


    def delete(self, request, id):
        try:
            obj = Store.objects.get(id=id)
        except Store.DoesNotExist:
            msg = {"msg": "not found"}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
        
        obj.delete()
        msg = {"msg": "deleted successfully"}
        return Response(msg, status=status.HTTP_204_NO_CONTENT)
    
    

#################################################################  Size CRUD  ##########################################################################

@method_decorator(csrf_protect, name='dispatch')
class SizeView(APIView):

    def get(self, request, id=None):
        if id:
            try:
                size = Size.objects.get(id=id)
                serializer = SizeSerializer(size)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Size.DoesNotExist:
                return Response({"msg": "Size not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            sizes = Size.objects.all()
            serializer = SizeSerializer(sizes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        


    def post(self, request):
        serializer = SizeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


    def put(self, request, id):
        try:
            size = Size.objects.get(id=id)
        except Size.DoesNotExist:
            return Response({"msg": "Size not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SizeSerializer(size, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



    def patch(self, request, id):
        try:
            size = Size.objects.get(id=id)
        except Size.DoesNotExist:
            return Response({"msg": "Size not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SizeSerializer(size, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    




    def delete(self, request, id):
        try:
            size = Size.objects.get(id=id)
            size.delete()
            return Response({"msg": "Size deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Size.DoesNotExist:
            return Response({"msg": "Size not found"}, status=status.HTTP_404_NOT_FOUND)
        


#################################################################  Color CRUD  #########################################################################



@method_decorator(csrf_protect, name='dispatch')
class ColorView(APIView):

    def get(self, request, id=None):
        if id:
            try:
                color = Color.objects.get(id=id)
                serializer = ColorSerializer(color)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Color.DoesNotExist:
                return Response({"msg": "Color not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            colors = Color.objects.all()
            serializer = ColorSerializer(colors, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        



    def post(self, request):
        serializer = ColorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    




    def put(self, request, id):
        try:
            color = Color.objects.get(id=id)
        except Color.DoesNotExist:
            return Response({"msg": "Color not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ColorSerializer(color, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    




    def patch(self, request, id):
        try:
            color = Color.objects.get(id=id)
        except Color.DoesNotExist:
            return Response({"msg": "Color not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ColorSerializer(color, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    




    def delete(self, request, id):
        try:
            color = Color.objects.get(id=id)
            color.delete()
            return Response({"msg": "Color deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Color.DoesNotExist:
            return Response({"msg": "Color not found"}, status=status.HTTP_404_NOT_FOUND)
        


#################################################################  Product CRUD  #######################################################################


@method_decorator(csrf_protect, name='dispatch')
class ProductView(APIView):

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = ProductSerializer(data=data)
        
        if serializer.is_valid():
            new_product = serializer.save()
            self._handle_sizes_and_colors(new_product, data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


    def put(self, request, id):
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response({"msg": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductSerializer(product, data=request.data, partial=True)
        
        if serializer.is_valid():
            product = serializer.save()
            self._handle_sizes_and_colors(product, request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, id):
        try:
            obj = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response({"msg": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        try:
            obj = Product.objects.get(id=id)
            obj.delete()
            return Response({"msg": "Product deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response({"msg": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    def _handle_sizes_and_colors(self, product, data):
        sizes = data.get('sizes', [])
        colors = data.get('colors', [])

        product.sizes.clear()
        for size_id in sizes:
            try:
                size_obj = Size.objects.get(id=size_id)
                product.sizes.add(size_obj)
            except Size.DoesNotExist:
                return Response({"msg": f"Size with ID '{size_id}' not found"}, status=status.HTTP_400_BAD_REQUEST)

        product.colors.clear()
        for color_id in colors:
            try:
                color_obj = Color.objects.get(id=color_id)
                product.colors.add(color_obj)
            except Color.DoesNotExist:
                return Response({"msg": f"Color with ID '{color_id}' not found"}, status=status.HTTP_400_BAD_REQUEST)
