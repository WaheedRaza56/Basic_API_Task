from .models import *
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()



############################################### Create User  #############################################################


class UsercreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

############################################### Profile serializer #######################################################


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id','user','email_verified']
       

############################################### Category serializer ######################################################


class categorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name','description']


############################################### Store serializer #########################################################


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'description', 'seller', 'is_approved']



############################################### Size serializer ###########################################################


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['size_code']


############################################### Color serializer ###########################################################



class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['color']



############################################### Product serializer #########################################################



class ProductSerializer(serializers.ModelSerializer):
    sizes = serializers.PrimaryKeyRelatedField(queryset=Size.objects.all(), many=True,)
    colors = serializers.PrimaryKeyRelatedField(queryset=Color.objects.all(), many=True)
    store = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all()) 

    class Meta:
        model = Product
        fields = ['id','store','name','description','price','sizes','colors','discount_percentage','main_image',
                'hover_image','on_sale','category','stock','created_by_super_admin','get_discounted_price', 'get_discount_percentage'  ]
        
        read_only_fields = ['get_discounted_price', 'get_discount_percentage']  

    



############################################### DRF  Authentication system with Token ######################################






class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('User with this email already exists.')
        return value

    def create(self, validated_data):
        user = User.objects.create_user(email=validated_data['email'],name=validated_data['name'],password=validated_data['password'])
        user.is_active = False  
        user.save()
        return user
