from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message  

@login_required
def chat_view(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    messages = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).order_by('timestamp')

    if request.method == 'POST':
        text = request.POST.get('message')
        if text:
            Message.objects.create(sender=request.user, receiver=other_user, text=text)
        return redirect('chat_view', user_id=other_user.id)

    return render(request, 'chat/chat.html', {
        'messages': messages,
        'other_user': other_user
    })
