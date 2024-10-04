from django.urls import path,include
from .views import *

from django.conf import settings
from django.conf.urls.static import static 

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='user_create'),

    path('profile/<int:id>/',ProfileView.as_view(),name="profile_detail"),

    path('category/<int:id>/',categoryView.as_view(),name="category_detail"),
    path('category/',categoryView.as_view(),name="category_create"),

    path('store/<int:id>/',StoreView.as_view(),name="store_detail"),
    path('store/',StoreView.as_view(),name="store_create"),

    path('size/<int:id>/', SizeView.as_view(), name='size_detail'),
    path('size/', SizeView.as_view(), name='size_list_create'),

    path('color/<int:id>/', ColorView.as_view(), name='color_detail'),
    path('color/', ColorView.as_view(), name='color_list_create'),

    path('product/<int:id>/', ProductView.as_view(), name='product_detail'),
    path('product/', ProductView.as_view(), name='product_list_create'),



#Session Authentication system
    path('account/csrf_cookie/', GetCSRFToken.as_view(), name='csrf_cookie'),
    path('account/checkauth/', CheckAuthenticatedView.as_view(), name='check_auth'),

    path('account/registration/', RegistrationView.as_view(), name='register'), 

    path('account/activate/<str:uid>/<str:token>/', ActivateView.as_view(), name='activate'),
    path('account/activate/', ActivationConfirm.as_view(), name='activation_confirm'),

    path('account/login/', LoginView.as_view(), name='login'),
    path('account/change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('account/logout/', LogoutView.as_view(), name='logout'),

    path('account/reset_password/', ResetPasswordEmailView.as_view(), name='reset_password_email'),
    path('account/reset_password/<str:uid>/<str:token>/', ResetPasswordView.as_view(), name='reset_password'),
    path('account/reset_password_confirm/', ResetPasswordConfirmView.as_view(), name='reset_password_confirm'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT) 
