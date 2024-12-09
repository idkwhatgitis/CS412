# File: context_processors.py
# Author: Shuaiqi Huang (shuang20@bu.edu) 12/09/2024
# Description: context_processor file for global scale usage(base.html)

'''particularly, a red dot will appear if a new notification comes and doesn't disappear once 'mark as read' 
is being clicked, user(the seller) is able to see the red dot at any page of all html pages as long it
is extending base.html'''


from .models import *

def unread_notifications(request):
    '''check for unread notifications, only when appears if the user is the seller of a specific item'''
    if request.user.is_authenticated:
        has_unread = Notification.objects.filter(user=request.user, is_read=False).exists()
    else:
        has_unread = False  # No unread notifications for unauthenticated users

    return {'has_unread': has_unread}