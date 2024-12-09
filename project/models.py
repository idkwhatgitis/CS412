# File: models.py
# Author: Shuaiqi Huang (shuang20@bu.edu) 12/08/2024
# Description: Objects that appears in the web applications, along with functions associated
# with each objects. This file carries the essential fields(attributes) of all objects that is used in 
# the web application, with more details of each object shown in docstrings 

from django.db import models
from django.urls import reverse

from django.db.models import Q
from django.contrib.auth.models import User
# Create your models here.

class Customer(models.Model):
    '''Customer object, the most basic object which enables people to use all the features of web
    application, along with a username and password linked to ONE Customer object'''

    #attributes of this object:
    first_name = models.TextField(blank=False)
    last_name = models.TextField(blank=False)
    address = models.TextField(blank=True)
    email_address = models.TextField(blank=True)
    phone_number = models.TextField(blank=True)
    image_self = models.ImageField(blank=True) ##image field 
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def is_following(self, other_customer):
        '''find if one user is following the other, useful in follower_list and folliwng_list html file'''
        return Follower.objects.filter(customer1=self, customer2=other_customer).exists()

    def get_absolute_url(self) -> str:
        '''upon successfully creating a the account, redirect to the newly created account page'''
        return reverse('project:show_all')
    
    def get_sell_item(self):
        '''get all items that this person sells, used in show_user.html'''
        items = Item.objects.filter(customer=self)
        return items

    def __str__(self):
        '''string representation of the object'''

        return f"{self.first_name} {self.last_name}"

class Item(models.Model):
    '''Item object, which are the items that is being listed on the web application that people can buy,
    Item has to have a seller, which is this case is referring to the customer object as foreignkey
    '''

    #attributes of this object:
    title = models.TextField(blank=False)
    description = models.TextField(blank=False)
    price = models.FloatField(blank=False)
    date = models.DateTimeField(auto_now=True)
    quantity_left = models.IntegerField(blank=False)
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE, related_name='items')
    is_deleted = models.BooleanField(default=False) ##soft deletion, changes the visibility to customers(users)
    #newly added is_deleted field in 12/6, as it caused trouble in Order object

    def __str__(self):
        '''string representation of the object'''

        return f"{self.title}"
    
    def get_images(self):
        '''get all images of an item, used in detail page'''
        return Image.objects.filter(item=self)
    
    def get_first_image(self):
        '''get one images of an item, used in listview of all items'''
        first_image = Image.objects.filter(item=self).first()

        return first_image
    
class Image(models.Model):
    '''Image object, these are the images that an item can have. The Item object does not carry an Image field,
    but it makes sense for every item to have some images associated with it. This object is a way to link image
    to an Item object, but it's not the only way. Additionally, it will be used during the deletion of image
    in views.py, which is part of updating an item. '''

    #attributes of this object:
    item = models.ForeignKey("Item", on_delete=models.CASCADE)
    image = models.ImageField(blank=True)
    def __str__(self):
        '''string representation of the object'''
        return f"{self.item} image"

class CustomerOrder(models.Model):
    '''CustomerOrder, linked to each order that customer. This is used when customer placed an
    order from the shopping cart. For example, when an order of 2 items are placed, and those 2 
    items are not from the same seller, each item will create an order instance, along with 
    notification to the seller, but the CustomerOrder object will combine 2 items together, 
    despite not from the same seller.'''

    #attributes of this object:
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE, related_name="customer_orders")
    date = models.DateTimeField(auto_now_add=True)  # Timestamp for when the order was placed

    def get_total_price(self):
        # Calculate the total price of all items in this grouped order
        return sum(order.get_total_price() for order in self.orders.all())
    
    def __str__(self):
        return f"{self.customer} order on {self.date}"

class Order(models.Model):
    '''Order object, linked to 3 foreignkey: CustomerOrder, Item, and Customer. When an order is placed,
    each item gets divided into an own order, an order contatining N items will create N Order objects.
    Each Order will be linked with seller and buyer, the item that is being sold, and CustomerOrder
    which was mentioned before to track the order that buyer has placed.'''

    #attributes of this object:
    customer_order = models.ForeignKey("CustomerOrder", on_delete=models.CASCADE, related_name="orders")
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE)
    item = models.ForeignKey("Item", on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(blank=False)
    date = models.DateTimeField(auto_now=True)
    seller = models.ForeignKey("Customer", related_name="orders_received", on_delete=models.CASCADE)

    
    def get_total_price(self):
        # Check if the item exists before accessing its price
        if self.item:
            return self.quantity * self.item.price
        return 0
    
    def __str__(self):
        '''string representation of object'''
        return f"{self.customer} bought {self.item} on {self.date}"


class ChatMessage(models.Model):
    '''ChatMessage object, which is the object that captures message sent between 2 people. This will be created
    when one person sends a message to the other person, with optional image, hence referencing Customer
    as foreignkey as sender and receiver.'''

    #attributes of this object:
    date = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(
        "Customer", 
        on_delete=models.CASCADE, 
        related_name='sent_messages',  # Unique related_name
        db_index=True
    )
    receiver = models.ForeignKey(
        "Customer", 
        on_delete=models.CASCADE, 
        related_name='received_messages',  # Unique related_name
        db_index=True
    )
    message = models.TextField(blank=False)
    image_self = models.ImageField(blank=True)

    def __str__(self):
        '''string representation of the object'''
        return f"{self.sender} to {self.receiver}"


class Follower(models.Model):
    '''Follower object, which creates an relationship between 2 customer. Customer1 can follow Customer2,
    which caused Customer1 as a follower of Customer2, and will be shown in follower_list.html and 
    following_list.html file'''

    #attributes of this object:
    customer1 = models.ForeignKey(
        "Customer", 
        on_delete=models.CASCADE, 
        related_name='following',  # Unique related_name
    )
    customer2 = models.ForeignKey(
        "Customer", 
        on_delete=models.CASCADE, 
        related_name='followers',  # Unique related_name
    )

    def __str__(self):
        '''string representation of the object'''
        return f"{self.customer1} is following {self.customer2}"
    


class ShoppingCart(models.Model):

    '''ShoppingCart object, related to each user and is unique. This object is used when
    we add item into the shopping cart and serves as the foreignkey, especially useful
    when we want to know total price of what's in the cart'''

    #attributes of this object:
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shopping_cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total_price(self):
        '''Calculate the total price of all items in the cart.'''
        total = sum(item.get_total_price() for item in self.cart_items.all())
        return total

    def __str__(self):
        '''string representation of the object'''
        return f"Shopping Cart for {self.user.username}"


class CartItem(models.Model):
    '''CartItem object, used when we add item into the shopping cart. We add this item into the 
    shopping cart so that we can use to checkout. We can edit this item directly in the shopping cart
    '''

    #attributes of this object:
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE, related_name='cart_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        '''Calculate total price for this item.'''
        return self.item.price * self.quantity

    def __str__(self):
        '''string representation of the object'''
        return f"{self.quantity} x {self.item.title} in {self.cart}"



class Notification(models.Model):
    '''Notification object. When order is being placed, seller of the item will be notified. This
    object will be created when user submits an order and will have a red dot on the Notifications link
    to let the seller know someone has placed an order. The red dot will disappear when we mark this
    notification as read, and is accomplished by setting the 'is_read' field to True.
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey('Order', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):

        '''string representation of the object'''
        return f"Notification for {self.user.username}"



