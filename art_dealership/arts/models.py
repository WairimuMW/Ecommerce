from django.db import models
from django.db.models.enums import Choices
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
# from phone_field import PhoneField


# Artist Table
class ArtistProfile(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    phonenumber = models.IntegerField(null=True)
    email = models.EmailField(max_length=254, null=True)
    bio = models.CharField(max_length=500, null=True)
    profile_pic = models.ImageField(null=True, blank=True, default="profpic.png")
    
    def __str__ (self):
        return str(self.user)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        ArtistProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    instance.artistprofile.save()


# Customer Table
class CustomerProfile(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    phonenumber = models.IntegerField(null=True)
    email = models.EmailField(max_length=254, null=True)
    profile_pic = models.ImageField(null=True, blank=True, default="profpic.png")
    
    def __str__ (self):
        return str(self.user)
    
@receiver(post_save, sender=User)
def create_profile_signal(sender, instance, created, **kwargs):
    if created:
        CustomerProfile.objects.create(user=instance)
    try:
        instance.customerprofile.save()
    except ObjectDoesNotExist:
        CustomerProfile.objects.create(user=instance)



# Art Table
class Art(models.Model):
    MEDIUM = (
        ('Paper', 'Paper'),
        ('Canvas', 'Canvas'),
        ('Wood', 'Wood'),
        ('Leather', 'Leather'),
        ('Plastic', 'Plastic'),
        ('Yarn', 'Yarn'),
        ('Glass', 'Glass'),
        ('Clay', 'Clay'),
        ('Metal', 'Metal'),
        ('Fabric', 'Fabric'),
        ('Beads', 'Beads'),
        ('Mixed-Media', 'Mixed-Media'),
        ('Other', 'Other'),
    )
    TYPE = (
        ('Drawing', 'Drawing'),
        ('Painting', 'Painting'),
        ('Sculpture', 'Sculpture'),
        ('Tapestry', 'Tapestry'),
        ('Ceramic', 'Ceramic'),
        ('Weaving', 'Weaving'),
        ('Beadwork', 'Beadwork'),
        ('Mosaic', 'Mosaic'),
        ('Collage', 'Collage'),
        ('Other', 'Other'),
    )
    STATUS = (
        ('Available', 'Available'),
        ('Booked', 'Booked'),
        ('Sold', 'Sold'),
    )
    artphoto = models.ImageField(null=True, blank=True, default="placeholder.png")
    price = models.FloatField(null=True)
    description = models.CharField(max_length=500, null=True)
    artist = models.ForeignKey(ArtistProfile, on_delete=models.SET_NULL, blank=True, null=True)
    material = models.CharField(max_length=200, null=True, choices= MEDIUM)
    art_type = models.CharField(max_length=200, null=True, choices= TYPE)
    status = models.CharField(max_length=200, null=True, choices= STATUS)
    date_added = models.DateField(auto_now_add=True)
    
    def __str__ (self):
        return self.description
    
    @property
    def artphotoURL(self):
        try:
            url = self.artphoto.url
        except:
            url = ''
        return url


# Order Table
class Order(models.Model):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.SET_NULL, blank=True, null=True)
    date_ordered = models.DateField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=100, null=True)
    
    def __str__ (self):
        return str(self.id)
    
    @property
    def delivery(self):
        delivery = True
        orderitems = self.orderitem_set.all()
        return delivery
        
    
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total
    
    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total
    

class OrderItem(models.Model):
    art = models.ForeignKey(Art, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__ (self):
        return str(self.art)
    
    
    @property
    def get_total(self):
        total = self.art.price * self.quantity
        return total
    
    

class Delivery(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Delivered', 'Delivered'),
    )
    PAYMENT = (
        ('Complete', 'Complete'),
        ('Incomplete', 'Incomplete'),
    )
    customer = models.ForeignKey(CustomerProfile, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    address = models.CharField(max_length=200, null=True)
    country = models.CharField(max_length=200, null=True)
    county = models.CharField(max_length=200, null=True)
    town = models.CharField(max_length=200, null=True)
    status = models.CharField(default="Pending", max_length=200, null=True, choices= STATUS)
    payment = models.CharField(default="Incomplete", max_length=200, null=True, choices= PAYMENT)
     
    def __str__ (self):
        return str(self.order.id)