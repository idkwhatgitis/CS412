# File: views.py
# Author: Shuaiqi Huang (shuang20@bu.edu) 11/1/2024
# Description: presentation to the user: showall profiles and detail profiles
#creating profile and status message, and redirecting/rendering

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import *
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView, FormView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import *
from django.contrib import messages

from typing import Any
from django.urls import reverse

from django.http import HttpResponseRedirect

import random


from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.shortcuts import redirect


class ShowAllItemView(ListView):
    model = Item
    template_name = 'project/show_all_items.html'
    context_object_name = 'items'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()


        # Get filter and sort parameters
        search_title = self.request.GET.get('search_title', '')
        sort_by = self.request.GET.get('sort_by', '')
        print(search_title,sort_by)

        # Apply filters
        if search_title:
            queryset = queryset.filter(title__icontains=search_title)

        # Exclude soft-deleted items
        queryset = queryset.filter(is_deleted=False)

        # Apply sorting
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')  # Cheapest first
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')  # Expensive first
        elif sort_by == 'date_asc':
            queryset = queryset.order_by('date')  # Oldest first
        elif sort_by == 'date_desc':
            queryset = queryset.order_by('-date')  # Newest first

        return queryset



class ShowDetailItemView(DetailView):
    model = Item
    template_name = 'project/item_detail.html'
    context_object_name = 'item'


class ShowUserPageView(DetailView):
    '''show a specific profile from the databse'''
    model = Customer
    template_name = 'project/customer_detail.html'
    context_object_name = 'customer'

    def get_context_data(self, **kwargs):
        # Get the default context
        context = super().get_context_data(**kwargs)

        # Check if the logged-in user is following the current customer
        customer = context['customer']
        is_following = False
        if self.request.user.is_authenticated:
            is_following = self.request.user.customer.is_following(customer)

        items = customer.items.filter(is_deleted=False)  # Assuming `customer.items` is a related_name for `Item`
        context['items'] = items

        # Add the 'is_following' status to the context
        context['is_following'] = is_following
        return context

class ShowUserSelfView(LoginRequiredMixin, DetailView):
    '''show a specific profile from the databse'''
    model = Customer
    template_name = 'project/show_user.html'
    context_object_name = 'customer'

    def get_object(self, queryset=None):
        # Retrieve the Customer object for the logged-in user
        return get_object_or_404(Customer, user=self.request.user)
    
    def get_context_data(self, **kwargs):
        # Get the default context
        context = super().get_context_data(**kwargs)

        # Filter out soft-deleted items
        customer = self.get_object()
        items = customer.items.filter(is_deleted=False)  # Assuming `customer.items` is a related_name for `Item`
        context['items'] = items
        return context

class UpdateCustomerView(LoginRequiredMixin, UpdateView):
    '''show a specific profile from the databse'''
    model = Customer
    template_name = 'project/update_customer_form.html'
    form_class = UpdateCustomerForm

    def get_success_url(self):
        # Redirect to the ShowUserSelfView after a successful update
        return reverse('project:show_self')
    
    def get_object(self, queryset=None):
        #get profile of self
        return Customer.objects.get(user=self.request.user)

class ShowCartView(LoginRequiredMixin, TemplateView):
    model = ShoppingCart
    template_name = 'project/shopping_cart.html'
    context_object_name = 'cart'


    def post(self, request, *args, **kwargs):
        # Get the shopping cart associated with the logged-in user
        cart = ShoppingCart.objects.get(user=request.user)
        action = request.POST.get('action')  # Action to be performed

        if action == 'update':
            print("TRUEEE")
            # Update quantities for each item in the cart
            for cart_item in cart.cart_items.all():
                quantity_key = f'quantity_{cart_item.id}'
                if quantity_key in request.POST:
                    try:
                        new_quantity = int(request.POST[quantity_key])
                        # Ensure the new quantity is valid and does not exceed stock
                        if new_quantity > 0 and new_quantity <= cart_item.item.quantity_left:
                            cart_item.quantity = new_quantity
                            cart_item.save()
                        else:
                            # Handle invalid quantity (e.g., too high or zero)
                            cart_item.quantity = cart_item.quantity  # Retain original value
                            cart_item.save()
                    except ValueError:
                        # Handle invalid quantity (e.g., non-integer input)
                        continue
            return redirect('project:shopping_cart')

        elif action == 'delete':
            # Delete selected items from the cart
            delete_items = request.POST.getlist('delete_items')
            if delete_items:
                cart.cart_items.filter(id__in=delete_items).delete()

        elif action == 'submit_order':
            # Process the order and create a new order object
            # Ensure cart has items before submitting the order
            cart = request.user.shopping_cart
        cart_items = cart.cart_items.all()

        # Get the list of selected items' IDs from the checkbox
        selected_item_ids = request.POST.getlist('delete_items')

        if not selected_item_ids:
            return redirect('project:shopping_cart')

        selected_item_ids = [int(item_id) for item_id in selected_item_ids]

        # Create a grouped CustomerOrder for the customer
        customer_order = CustomerOrder.objects.create(customer=request.user.customer)

        for cart_item in cart_items:
            if cart_item.pk in selected_item_ids:
                if cart_item.quantity > cart_item.item.quantity_left:
                    cart_item.delete()  # Remove item if stock is insufficient
                    continue

                # Create an individual order for each item
                order = Order.objects.create(
                    customer_order=customer_order,
                    customer=request.user.customer,
                    item=cart_item.item,
                    quantity=cart_item.quantity,
                    seller=cart_item.item.customer,
                )

                # Notify the seller
                Notification.objects.create(
                    user=cart_item.item.customer.user,
                    message=(
                        f"You have received an order for {cart_item.item.title} "
                        f"(Quantity: {cart_item.quantity}). "
                        f"Total Price: ${cart_item.get_total_price()}"
                    ),
                    order=order,
                )

                # Reduce stock
                cart_item.item.quantity_left -= cart_item.quantity
                cart_item.item.save()

                # Remove the item from the cart
                cart_item.delete()

                return redirect('project:checkout_cart')  # Redirect to order confirmation page

            else:
                # If cart is empty, you can add a message or redirect back
                return redirect('project:shopping_cart')  # Redirect to shopping cart if no items are selected

        # Default return for other actions or invalid requests
        return redirect('project:shopping_cart')  # Redirect back to the shopping cart



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            cart, created = ShoppingCart.objects.get_or_create(user=self.request.user)
            context['cart'] = cart
            context['cart_items'] = cart.cart_items.all()
        else:
            context['cart'] = None
            context['cart_items'] = None
        return context



class ShowSubscriberView(ListView):
    '''show a specific profile from the databse'''
    model = User
    template_name = 'project/show_subscriber.html'
    context_object_name = 'users'

class AddFollowerView(LoginRequiredMixin, View):
    model = Follower

    def post(self, request, customer_pk):
        # Get the target customer
        target_customer = get_object_or_404(Customer, pk=customer_pk)
        
        # Get the logged-in user's customer object
        user_customer = request.user.customer
        
        # Check if the logged-in user is already following the target customer
        if Follower.objects.filter(customer1=user_customer, customer2=target_customer).exists():
            # If following, remove the follow (unfollow)
            Follower.objects.filter(customer1=user_customer, customer2=target_customer).delete()
        else:
            # If not following, create the follow relationship
            Follower.objects.create(customer1=user_customer, customer2=target_customer)

        # Redirect back to the target customer's profile page
        return redirect('project:show_user', pk=customer_pk)

class FollowingsListView(ListView):
    model = Follower
    template_name = 'project/following_list.html'
    context_object_name = 'followers'

    def get_queryset(self):
        customer = self.request.user.customer  # Ensure `customer` exists
        if customer:  # Check if the user has a profile (customer) linked
            # Get the people (customer2) the current user (customer1) is following
            return Customer.objects.filter(following__customer1=customer)
        return Customer.objects.none()
    
class FollowersListView(ListView):
    model = Follower
    template_name = 'project/follower_list.html'
    context_object_name = 'followers'

    def get_queryset(self):
        customer = self.request.user.customer  # Ensure `customer` exists
        if customer:  # Check if the user has a profile (customer) linked
            # Get the people (customer2) the current user (customer1) is following
            return Customer.objects.filter(following__customer2=customer)
        return Customer.objects.none()

class CreateCustomerView(CreateView):
    '''A view to create message on profile
        on get: send back the for for dispay
        on post: read/process the form and save it to the DB
    '''

    form_class = CreateCustomerForm #form that forms.py has
    template_name = "project/create_customer_form.html"

    def get_context_data(self, **kwargs):
        #get context data for creating new user
        context = super().get_context_data(**kwargs)
        # Add UserCreationForm to the context
        if not self.request.user.is_authenticated:
            context['user_creation_form'] = UserCreationForm()
        return context
   
    
    def dispatch(self, request, *args, **kwargs):
        #handle logic when trying to create new profile
        if request.user.is_authenticated:
            # If user has a profile, redirect them to the main page
            if Customer.objects.filter(user=request.user).exists():
                return HttpResponseRedirect(reverse('project:show_all'))
   
        return super().dispatch(request, *args, **kwargs)
    
    
    
    def form_valid(self, form):
        #  Reconstruct UserCreationForm from POST data
        if self.request.POST:
            user_creation_form = UserCreationForm(self.request.POST)
        
        # Check if UserCreationForm is valid before proceeding
        if user_creation_form.is_valid():
           #Save the new user and get the created User instance
            new_user = user_creation_form.save()
            
            #Attach the new user to the profile instance and log then in
            form.instance.user = new_user
            login(self.request, new_user)
            
            # Delegate the rest to the super class’ form_valid method
            return super().form_valid(form)
        else:
          #invalid form
            return self.form_invalid(form)



class CustomLoginView(LoginView):
    template_name = 'project/login.html'

    def get_success_url(self):
        # Get the next parameter in the query string if it exists
        next_url = self.request.GET.get('next')
        
        if next_url:
            return next_url  # Redirect to the page that was originally requested
        return super().get_success_url() 

    

class AddToCartView(LoginRequiredMixin, View):
    

    def get(self, request, item_pk):
        # Redirected after login, simulate the `POST` action
        return self.post(request, item_pk)

    def post(self, request, item_pk):
        # Get the item being added to the cart
        item = get_object_or_404(Item, pk=item_pk)

        # Check if the user has a cart, if not, create one
        cart, created = ShoppingCart.objects.get_or_create(user=request.user)

        # Check if the item is already in the cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)

        if not created:
            # If the item is already in the cart, increase the quantity
            cart_item.quantity += 1
            cart_item.save()

        # Redirect to the cart page
        messages.success(request, f'{item.title} has been added to your cart!')
        return redirect('project:shopping_cart')
    

class ChatListView(LoginRequiredMixin, ListView):
    template_name = 'project/chat_list.html'
    context_object_name = 'conversations'

    def get_queryset(self):
        customer = self.request.user.customer
        sent_to = ChatMessage.objects.filter(sender=customer).values_list('receiver', flat=True)
        received_from = ChatMessage.objects.filter(receiver=customer).values_list('sender', flat=True)
        unique_customers = Customer.objects.filter(pk__in=set(sent_to.union(received_from)))
        return unique_customers

class ChatDetailView(LoginRequiredMixin, ListView, FormView):
    template_name = 'project/chat_detail.html'
    context_object_name = 'messages'
    form_class = ChatMessage

    def get_queryset(self):
        customer = self.request.user.customer
        other_customer = get_object_or_404(Customer, pk=self.kwargs['customer_pk'])
        return ChatMessage.objects.filter(
            sender__in=[customer, other_customer],
            receiver__in=[customer, other_customer]
        ).order_by('date')

    def form_valid(self, form):
        form.instance.sender = self.request.user.customer
        form.instance.receiver = get_object_or_404(Customer, pk=self.kwargs['customer_pk'])
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('project:chat_detail', kwargs={'customer_pk': self.kwargs['customer_pk']})
    
    def get(self, request, customer_pk):
        customer = request.user.customer
        other_customer = get_object_or_404(Customer, pk=customer_pk)

        # Fetch the chat messages
        messages = ChatMessage.objects.filter(
            sender__in=[customer, other_customer],
            receiver__in=[customer, other_customer]
        ).order_by('date')

        # Create a blank form for the new message
        form = ChatMessageForm()

        context = {
            'messages': messages,
            'other_customer': other_customer,
            'form': form,
        }
        return render(request, 'project/chat_detail.html', context)

    def post(self, request, customer_pk):
        customer = request.user.customer
        other_customer = get_object_or_404(Customer, pk=customer_pk)

        # Handle the submitted form
        form = ChatMessageForm(request.POST, request.FILES)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.sender = customer
            new_message.receiver = other_customer
            new_message.save()
            return redirect(reverse('project:chat_detail', kwargs={'customer_pk': customer_pk}))

        # If the form is invalid, re-render the chat view with errors
        messages = ChatMessage.objects.filter(
            sender__in=[customer, other_customer],
            receiver__in=[customer, other_customer]
        ).order_by('date')

        context = {
            'messages': messages,
            'other_customer': other_customer,
            'form': form,
        }
        return render(request, 'project/chat_detail.html', context)


class CreateItemView(LoginRequiredMixin, CreateView):
    '''A view to create an item (with image upload)'''
    model = Item
    form_class = CreateItemForm
    template_name = "project/create_item_form.html"

    def form_valid(self, form):
        item = form.save(commit=False)
        item.customer = self.request.user.customer  # Associate the item with the logged-in customer
        item.save()

        # Handle the images uploaded for the item
        images = self.request.FILES.getlist('images')
        for image in images:
            Image.objects.create(item=item, image=image)

        return redirect('project:show_self')  # Redirect to the user's profile page after creating the item

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images_form'] = CreateItemForm()  # Handle images form
        return context

    def get(self, request, *args, **kwargs):
        if request.GET.get("cancel"):
            return redirect('project:show_all_items')  # Redirect if cancel button is clicked
        return super().get(request, *args, **kwargs)



class UpdateItemView(LoginRequiredMixin, UpdateView):
    '''A view to update an existing item'''
    model = Item
    form_class = UpdateItemForm
    template_name = "project/update_item_form.html"

    def form_valid(self, form):
        # Save the item first
        item = form.save(commit=False)
        item.save()  # Save the item to get its ID

        # Handle the images uploaded for the item
        images = self.request.FILES.getlist('images')  # 'images' is the name of the input field
        for image in images:
            Image.objects.create(item=item, image=image)  # Create Image objects for each uploaded file

        # Redirect to the user's profile page after updating the item
        return redirect('project:show_self')

    def get_object(self, queryset=None):
        item = super().get_object(queryset)
        # Ensure the logged-in user is the owner of the item
        if item.customer != self.request.user.customer:
            return redirect('project:show_all')  # Redirect to all items if the user doesn't own the item
        return item

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Provide the form for image upload, if any
        context['images_form'] = UpdateItemForm()
        context['item_images'] = self.get_object().get_images()  # Fetch the images associated with the item
        return context

    def get(self, request, *args, **kwargs):
        if request.GET.get("cancel"):
            return redirect('project:show_item_detail', pk=self.kwargs['pk'])  # Redirect if cancel button is clicked
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        item = self.get_object()  # Get the item object

        # Handle image deletion
        if 'delete_image' in request.POST:
            image_id = request.POST.get('delete_image')
            image = get_object_or_404(Image, id=image_id, item=item)
            image.delete()  # Delete the image

        return super().post(request, *args, **kwargs)


    
class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'project/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = Notification.objects.filter(user=self.request.user).order_by('-created_at')

        # Get filter parameters
        start_date = self.request.GET.get('start_date', '')
        end_date = self.request.GET.get('end_date', '')
        sort_by = self.request.GET.get('sort_by', '')

        # Filter by date range
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)

        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        # Apply sorting
        if sort_by == 'date_asc':
            queryset = queryset.order_by('created_at')  # Earliest first
        elif sort_by == 'date_desc':
            queryset = queryset.order_by('-created_at')  # Latest first

        return queryset


    def get_context_data(self, **kwargs):
        # We no longer need to override this unless you're adding custom context
        context = super().get_context_data(**kwargs)
        context['has_unread'] = Notification.objects.filter(user=self.request.user, is_read=False).exists()
        return context


class MarkNotificationReadView(View):
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        print(notification)

        # After marking as read, redirect back to the notification list or a specific page
        return redirect(reverse('project:notification'))


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'project/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        # Only allow the seller to see their orders
        return Order.objects.filter(item__customer=self.request.user.customer)
    

class CheckoutCartView(LoginRequiredMixin, TemplateView):
    template_name = 'project/checkout_cart.html'

    def post(self, request, *args, **kwargs):
        cart = request.user.shopping_cart
        cart_items = cart.cart_items.all()

        # Get the list of selected items' IDs from the checkbox
        selected_item_ids = request.POST.getlist('checkout_items')

        if not selected_item_ids:
            return redirect('project:shopping_cart')

        selected_item_ids = [int(item_id) for item_id in selected_item_ids]

        # Create a grouped CustomerOrder for the customer
        customer_order = CustomerOrder.objects.create(customer=request.user.customer)

        for cart_item in cart_items:
            if cart_item.pk in selected_item_ids:
                if cart_item.quantity > cart_item.item.quantity_left:
                    cart_item.delete()  # Remove item if stock is insufficient
                    continue

                # Create an individual order for each item
                order = Order.objects.create(
                    customer_order=customer_order,
                    customer=request.user.customer,
                    item=cart_item.item,
                    quantity=cart_item.quantity,
                    seller=cart_item.item.customer,
                )

                # Notify the seller
                Notification.objects.create(
                    user=cart_item.item.customer.user,
                    message=(
                        f"You have received an order for {cart_item.item.title} "
                        f"(Quantity: {cart_item.quantity}). "
                        f"Total Price: ${cart_item.get_total_price()}"
                    ),
                    order=order,
                )

                # Reduce stock
                cart_item.item.quantity_left -= cart_item.quantity
                cart_item.item.save()

                # Remove the item from the cart
                cart_item.delete()

        # Redirect to past orders or a confirmation page
        return redirect('project:checkout_cart')
    

class PastOrdersView(LoginRequiredMixin, ListView):
    model = CustomerOrder
    template_name = 'project/past_orders.html'
    context_object_name = 'customer_orders'
    paginate_by = 3

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = CustomerOrder.objects.filter(customer=self.request.user.customer).order_by("-date")

        # Get filter parameters
        start_date = self.request.GET.get('start_date', '')
        end_date = self.request.GET.get('end_date', '')
        sort_by = self.request.GET.get('sort_by', '')

        # Filter by date range
        if start_date:
            queryset = queryset.filter(date__gte=start_date)

        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        # Apply sorting
        if sort_by == 'date_asc':
            queryset = queryset.order_by('date')  # Earliest first
        elif sort_by == 'date_desc':
            queryset = queryset.order_by('-date')  # Latest first

        return queryset



class DeleteCartItemsView(View):
    def post(self, request, *args, **kwargs):
        print(request.POST.getlist)
        delete_items = request.POST.getlist('delete_items')
        print(delete_items)
        print("HELLO")
        # Delete the selected cart items
        if delete_items:
            CartItem.objects.filter(id__in=delete_items, cart__user=request.user).delete()

        # Redirect to the shopping cart page after deletion
        return redirect('project:shopping_cart')


class DeleteItemView(LoginRequiredMixin, DeleteView):
    model = Item
    template_name = 'project/item_confirm_delete.html'  # Confirmation template
    context_object_name = 'item'
   
    def get_success_url(self):
        # Redirect to the associated item's detail page after deletion
        return reverse('project:show_self')

    def dispatch(self, request, *args, **kwargs):
        # Ensure the logged-in user owns the item
        item = self.get_object()
        print(f"Dispatch called for item: {item}")  # Debugging output
        if item.customer.user != request.user:
            print("FASLE")
            return reverse('project:show_all')
        return super().dispatch(request, *args, **kwargs)
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(f"Item to delete: {context['item']}")  # Debugging output
        return context

    def post(self, request, *args, **kwargs):
        # Perform soft deletion (mark as deleted instead of actually deleting the object)
        item = self.get_object()
        item.is_deleted = True  # Mark as deleted
        item.save()
        return redirect(self.get_success_url())
