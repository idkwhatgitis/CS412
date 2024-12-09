# File: views.py
# Author: Shuaiqi Huang (shuang20@bu.edu) 12/08/2024
# Description: all views that the web applictaion use, including login/logout of user
# also includes form that applications that will be used

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import *
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView, FormView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import *
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.shortcuts import redirect


class ShowAllItemView(ListView):
    '''shows all the item, which is the homepage, and allows filtering based on criteria
    to avoid too many item being dispaged, add a paginate_by field to limit the number of items shown'''
    model = Item
    template_name = 'project/show_all_items.html'
    context_object_name = 'items'
    paginate_by = 10

    def get_queryset(self):
        '''once search form is submitted, filter out the unmatching criteria'''
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
    '''Detail of an item, can be accessed many ways, one of the way is by hitting the item
    in the ShowItemsView'''
    model = Item
    template_name = 'project/item_detail.html'
    context_object_name = 'item'


class ShowUserPageView(DetailView):
    '''show a specific account from the databse, this is the version that doesnt require any logins
    this does not include updating account info, and selling new items, etc.'''
    model = Customer
    template_name = 'project/customer_detail.html'
    context_object_name = 'customer'

    def get_context_data(self, **kwargs):
        '''showuserpageview versin of get_context_data'''
        context = super().get_context_data(**kwargs)

        # Check if the logged-in user is following the current customer
        customer = context['customer']
        is_following = False
        if self.request.user.is_authenticated:
            is_following = self.request.user.customer.is_following(customer)

        items = customer.items.filter(is_deleted=False) 
        context['items'] = items

        # Add the 'is_following' status to the context
        context['is_following'] = is_following
        return context

class ShowUserSelfView(LoginRequiredMixin, DetailView):
    '''show a specific account from the database, this version requires login, which allows
    update of info, selling an item, updating an existing item. Additionally, the user who is not
    associated with this account cannot access this page, but only the ShowUserPageView(previous view)'''
    model = Customer
    template_name = 'project/show_user.html'
    context_object_name = 'customer'

    def get_object(self, queryset=None):
        # Retrieve the Customer object for the logged-in user
        return get_object_or_404(Customer, user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Filter out soft-deleted items so that it does not get shown
        customer = self.get_object()
        items = customer.items.filter(is_deleted=False)
        context['items'] = items
        return context

class UpdateCustomerView(LoginRequiredMixin, UpdateView):
    '''update an existing customer, and have to be the correct user to make such update, updates
    are performed using the form in forms.py'''
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
    '''showing the shopping cart of the user, the user can only access the shopping cart that associated
    with them, and has no access to other people's shopping cart, shopping cart allows CRUD on item'''
    model = ShoppingCart
    template_name = 'project/shopping_cart.html'
    context_object_name = 'cart'


    def post(self, request, *args, **kwargs):
        '''once a submit of form is observed, do corresponding action'''
        # Get the shopping cart associated with the logged-in user
        cart = ShoppingCart.objects.get(user=request.user)
        action = request.POST.get('action')  # Action to be performed

        if action == 'update':
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
            return redirect('project:shopping_cart') #redirect after update completes

        elif action == 'delete':
            # Delete selected items from the cart
            delete_items = request.POST.getlist('delete_items')
            if delete_items:
                cart.cart_items.filter(id__in=delete_items).delete()
            return redirect('project:shopping_cart') #redirect after delete completes

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

                # Notify the seller by creating a Notification object
                Notification.objects.create(
                    user=cart_item.item.customer.user,
                    message=(
                        f"You have received an order for {cart_item.item.title} "
                        f"(Quantity: {cart_item.quantity}). "
                        f"Total Price: ${cart_item.get_total_price()}"
                    ),
                    order=order,
                )

                # Reduce stock of the item
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
        '''get context data for shopping cart, which shows the items that the shopping cart has'''
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            cart, created = ShoppingCart.objects.get_or_create(user=self.request.user)
            context['cart'] = cart
            context['cart_items'] = cart.cart_items.all()
        else:
            context['cart'] = None
            context['cart_items'] = None
        return context



class AddFollowerView(LoginRequiredMixin, View):
    '''adding a following relationship, for one user to follow/unfollow another user'''
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
    '''display a list of user that one is following'''
    model = Follower
    template_name = 'project/following_list.html'
    context_object_name = 'followers'


    def get_queryset(self):
        '''Get the users the current user is following and filter by search query'''
        customer = self.request.user.customer  
        if not customer:
            return Customer.objects.none()  # Return an empty queryset if no customer is linked

        queryset = Customer.objects.filter(following__customer1=customer)

        # Get search input
        search_last = self.request.GET.get('search_last', '').strip()
        search_first = self.request.GET.get('search_first', '').strip()

        if search_last:
            queryset = queryset.filter(last_name__icontains=search_last)
    
        if search_first:
            queryset = queryset.filter(first_name__icontains=search_first)
           
        return queryset
    
class FollowersListView(ListView):
    '''display a list of user that is following the user'''
    model = Follower
    template_name = 'project/follower_list.html'
    context_object_name = 'followers'
    
    def get_queryset(self):
        '''Get the users the current user is following and filter by search query'''
        customer = self.request.user.customer  
        if not customer:
            return Customer.objects.none()  # Return an empty queryset if no customer is linked

        # Get the search input from the request
        queryset = Customer.objects.filter(following__customer2=customer)
        # Apply filters based on input values
        search_last = self.request.GET.get('search_last', '').strip()
        search_first = self.request.GET.get('search_first', '').strip()

        if search_last:
            queryset = queryset.filter(last_name__icontains=search_last)

        if search_first:
            queryset = queryset.filter(first_name__icontains=search_first)

        return queryset

class CreateCustomerView(CreateView):
    '''A view to create a new user, and uses form in forms.py for creation
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
            # If user has a profile, redirect them to the main page, but this shouldn't happen
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
    '''login page that was designed, a very simple html page'''
    template_name = 'project/login.html'

    def get_success_url(self):
        # Get the next parameter in the query string if it exists
        next_url = self.request.GET.get('next')
        
        if next_url:
            return next_url  # Redirect to the page that was originally requested
        return super().get_success_url() 

    

class AddToCartView(LoginRequiredMixin, View):
    '''adding an item to the cart, requires the user to login for such option to even exist'''

    def get(self, request, item_pk):
        # Redirected after login, simulate the `POST` action as we are not using a form
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
    '''View to see a list of chat messages and includes history messages, user is able
    to see those history if they click into their chat window'''
    template_name = 'project/chat_list.html'
    context_object_name = 'conversations'

    def get_queryset(self):
        #get the ChatMessage and filter out unique user that we chat with, to display a list of users that we chatted
        customer = self.request.user.customer
        sent_to = ChatMessage.objects.filter(sender=customer).values_list('receiver', flat=True)
        received_from = ChatMessage.objects.filter(receiver=customer).values_list('sender', flat=True)
        unique_customers = Customer.objects.filter(pk__in=set(sent_to.union(received_from)))
        return unique_customers

class ChatDetailView(LoginRequiredMixin, ListView, FormView):
    '''Detail view of chat, which will be directed from ChatListView'''
    template_name = 'project/chat_detail.html'
    context_object_name = 'messages'
    form_class = ChatMessage

    def get_queryset(self):
        '''get the previous sent messages between users'''
        customer = self.request.user.customer
        other_customer = get_object_or_404(Customer, pk=self.kwargs['customer_pk'])
        return ChatMessage.objects.filter(
            sender__in=[customer, other_customer],
            receiver__in=[customer, other_customer]
        ).order_by('date')

    def form_valid(self, form):
        '''sending a message, which was done by a form'''
        form.instance.sender = self.request.user.customer
        form.instance.receiver = get_object_or_404(Customer, pk=self.kwargs['customer_pk'])
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        #upon sucessfully sent, user will not be directed to other page, but to see the just sent messages
        return reverse('project:chat_detail', kwargs={'customer_pk': self.kwargs['customer_pk']})
    
    def get(self, request, customer_pk):
        #sending the message, which was done by the form, works together with form_valid
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
        #similarly, post the sent message if it's valid
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
    '''A view to create an item (with image upload), implementing form from forms.py'''
    model = Item
    form_class = CreateItemForm
    template_name = "project/create_item_form.html"

    def form_valid(self, form):
        #form_valid function when we create an item
        item = form.save(commit=False)
        item.customer = self.request.user.customer  # Associate the item with the logged-in customer
        item.save()

        # Handle the images uploaded for the item
        images = self.request.FILES.getlist('images')
        for image in images:
            Image.objects.create(item=item, image=image)

        return redirect('project:show_self')  # Redirect to the user's profile page after creating the item

    def get_context_data(self, **kwargs):
        '''handling image submission and linking with Item object'''
        context = super().get_context_data(**kwargs)
        context['images_form'] = CreateItemForm()  # Handle images form
        return context

    def get(self, request, *args, **kwargs):
        #only takes care when user choose not to create an item
        if request.GET.get("cancel"):
            return redirect('project:show_all_items')  # Redirect if cancel button is clicked
        return super().get(request, *args, **kwargs)



class UpdateItemView(LoginRequiredMixin, UpdateView):
    '''A view to update an existing item, using form from forms.py'''
    model = Item
    form_class = UpdateItemForm
    template_name = "project/update_item_form.html"

    def form_valid(self, form):
         #form_valid function when we update an item
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
        #get the object that we are updating
        item = super().get_object(queryset)
        # Ensure the logged-in user is the owner of the item
        if item.customer != self.request.user.customer:
            return redirect('project:show_all')  # Redirect to all items if the user doesn't own the item
        return item

    def get_context_data(self, **kwargs):
        '''get context data for updating, and handles image adding/deleting'''
        context = super().get_context_data(**kwargs)
        # Provide the form for image upload, if any
        context['images_form'] = UpdateItemForm()
        context['item_images'] = self.get_object().get_images()  # Fetch the images associated with the item
        return context

    def get(self, request, *args, **kwargs):
        #only takes care of cancelling update
        if request.GET.get("cancel"):
            return redirect('project:show_item_detail', pk=self.kwargs['pk'])  # Redirect if cancel button is clicked
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        '''handles image deletion and item update and posting such update '''
        item = self.get_object()  # Get the item object

        # Handle image deletion
        if 'delete_image' in request.POST:
            image_id = request.POST.get('delete_image')
            image = get_object_or_404(Image, id=image_id, item=item)
            image.delete()  # Delete the image

        return super().post(request, *args, **kwargs)


    
class NotificationListView(LoginRequiredMixin, ListView):
    '''A view to see the list of Notifications, including past notifications, to avoid having too
    many notifications, add a paginate_by field to limit the number of notifications'''
    model = Notification
    template_name = 'project/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 5

    def get_queryset(self):
        '''get the notifications we want to see and allows searching for notifications matching
        the criteria'''
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
        #only checks if we have unread notifications, if not, then this function is not needed
        context = super().get_context_data(**kwargs)
        context['has_unread'] = Notification.objects.filter(user=self.request.user, is_read=False).exists()
        return context


class MarkNotificationReadView(View):
    '''View to mark notifications as read, since when notifications were sent, it comes as 
    unread, which will have a red dot on Notification link. Marking notification as read will
    make the red dot dissapear'''
    def post(self, request, pk):
        #when we click the button to mark notification as read, we update the notification
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.is_read = True
        notification.save()

        # After marking as read, redirect back to the notification list or a specific page
        return redirect(reverse('project:notification'))


class OrderDetailView(LoginRequiredMixin, DetailView):
    '''Detail view of the order, when an order is placed, order objects were created,
    user can be directed to this page from the notification list page'''
    model = Order
    template_name = 'project/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        # Only allow the seller to see their orders
        return Order.objects.filter(item__customer=self.request.user.customer)
    

class CheckoutCartView(LoginRequiredMixin, TemplateView):
    '''Checkout confirmation page to the user, once the user selects the items in the shopping cart 
    and hits checkout, user are directed to this page as a confirmation'''
    template_name = 'project/checkout_cart.html'

    

class PastOrdersView(LoginRequiredMixin, ListView):
    '''A list of previuos order of the user. This is different than the Order object, this object
    is created when user submits one or more items from the shopping cart, and will combine all those
    items together as an object, which is easier for the user to track with'''
    model = CustomerOrder
    template_name = 'project/past_orders.html'
    context_object_name = 'customer_orders'
    paginate_by = 3 #pagination to avoid all orders being listed

    def get_queryset(self):
        #get the orders that the user placed before
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
    


class DeleteItemView(LoginRequiredMixin, DeleteView):
    '''The view to delete an item, i.e., stop selling this item'''
    model = Item
    template_name = 'project/item_confirm_delete.html'
    context_object_name = 'item'

    def get_success_url(self):
        '''redirect once successfully delete'''
        return reverse('project:show_self') 

    def post(self, request, *args, **kwargs):
        '''method to delete the item in form submission'''
        item = self.get_object()
        item.is_deleted = True  # Mark as deleted
        item.save()
        return redirect(self.get_success_url())
