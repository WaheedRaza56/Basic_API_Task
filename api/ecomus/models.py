from django.db import models
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser,PermissionsMixin



class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
models.signals.post_save.connect(create_user_profile, sender=User)


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(default='')

    def __str__(self):
        return self.name
    

class Store(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stores')
    name = models.CharField(max_length=100)
    description = models.TextField(default='')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Size(models.Model):
    size_code = models.CharField(max_length=2, choices=[
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
    ])

    def __str__(self):
        return self.get_size_code_display()

class Color(models.Model):
    color = models.CharField(max_length=20, default='brown', choices=[
        ('brown', 'Brown'),
        ('purple', 'Light Purple'),
        ('green', 'Light Green'),
        ('dark', 'Black'),
        ('blue', 'Blue-2'),
        ('dark-blue', 'Dark Blue'),
        ('white', 'White'),
        ('light-grey', 'Light Grey'),
        ('orange', 'Orange-3'),
        ('pink', 'Pink'),
    ])

    def __str__(self):
        return self.get_color_display()
    
class Product(models.Model):
    name = models.CharField(max_length=255, default='')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sizes = models.ManyToManyField('Size', related_name='products')
    colors = models.ManyToManyField('Color', related_name='products')
    discount_percentage = models.PositiveIntegerField(default=0, help_text="Discount percentage applied to the product")
    main_image = models.ImageField(upload_to='static/images/products', null=True, blank=True)
    hover_image = models.ImageField(upload_to='static/images/products', null=True, blank=True)
    on_sale = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,null=False , default='' , blank=False, related_name='products')
    stock = models.PositiveIntegerField(default=0)
    created_by_super_admin = models.BooleanField(default=False) 

    def __str__(self):
        return self.name

    def get_discounted_price(self):
        if self.discount_percentage > 0:
            return self.price * (Decimal(1) - (Decimal(self.discount_percentage) / Decimal(100)))
        return self.price

    def get_discount_percentage(self):
        if self.discount_percentage > 0:
            return self.discount_percentage
        return 0




class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if email is None or name is None:
            raise ValueError("Email or Name cannot be None")

        user = self.model(email=self.normalize_email(email),name=name,)
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, email, name, password=None):
            user = self.create_user(email=email, password=password, name=name)
            user.is_admin = True
            user.is_staff = True  
            user.is_superuser = True 
            user.save(using=self._db)
            return user

class User(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(verbose_name="Email",max_length=255,unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return self.name
    
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
