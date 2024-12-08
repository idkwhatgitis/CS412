
from .models import *

def unread_notifications(request):
    
    if request.user.is_authenticated:
        has_unread = Notification.objects.filter(user=request.user, is_read=False).exists()
    else:
        has_unread = False  # No unread notifications for unauthenticated users

    return {'has_unread': has_unread}