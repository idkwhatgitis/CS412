
from django.db import models
from django.urls import reverse

from django.db.models import Q
from django.contrib.auth.models import User
# Create your models here.

class Customer(models.Model):
    #attributes:
    first_name = models.TextField(blank=False)
    last_name = models.TextField(blank=False)
    address = models.TextField(blank=True)
    email_address = models.TextField(blank=True)
    phone_number = models.TextField(blank=True)
    image_self = models.ImageField(blank=True) ##image field 
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def is_following(self, other_customer):
        return Follower.objects.filter(customer1=self, customer2=other_customer).exists()

    def get_absolute_url(self) -> str:
        '''upon successfully creating a profile, redirect to the newly created profile page'''
        return reverse('project:show_all')
    
    def get_sell_item(self):
        '''get all items that this person sells'''
        items = Item.objects.filter(customer=self)
        return items

    def __str__(self):
        '''string representation of the object'''

        return f"{self.first_name} {self.last_name}"

class Item(models.Model):
    title = models.TextField(blank=False)
    description = models.TextField(blank=False)
    price = models.FloatField(blank=False)
    date = models.DateTimeField(auto_now=True)
    quantity_left = models.IntegerField(blank=False)
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE, related_name='items')
    is_deleted = models.BooleanField(default=False)

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
    item = models.ForeignKey("Item", on_delete=models.CASCADE)
    image = models.ImageField(blank=True)
    def __str__(self):
        '''string representation of the object'''

        return f"{self.item}"
    

# class Order(models.Model):
#     date = models.DateTimeField(auto_now=True)
#     customer = models.ForeignKey("Customer", on_delete=models.CASCADE)
#     item = models.ForeignKey("Item", on_delete=models.CASCADE)
#     quantity = models.IntegerField(blank=False)
#     seller = models.ForeignKey("Customer", related_name="orders_received", on_delete=models.CASCADE)

#     def get_total_price(self):
#         return self.quantity * self.item.price
    

class CustomerOrder(models.Model):
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE, related_name="customer_orders")
    date = models.DateTimeField(auto_now_add=True)  # Timestamp for when the order was placed

    def get_total_price(self):
        # Calculate the total price of all items in this grouped order
        return sum(order.get_total_price() for order in self.orders.all())

class Order(models.Model):
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
        return f"{self.customer}"


class ChatMessage(models.Model):
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
        return f"{self.sender} to {self.receiver}"


class Follower(models.Model):
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
        return f"{self.customer1} is following {self.customer2}"
    


class ShoppingCart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shopping_cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total_price(self):
        '''Calculate the total price of all items in the cart.'''
        total = sum(item.get_total_price() for item in self.cart_items.all())
        return total

    def __str__(self):
        return f"Shopping Cart for {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE, related_name='cart_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        '''Calculate total price for this item.'''
        return self.item.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.item.title} in {self.cart}"



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey('Order', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Notification for {self.user.username}"



