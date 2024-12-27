from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


@require_POST
@login_required
def toggle_dark_mode(request):
    user = request.user
    user.prefers_dark_mode = not user.prefers_dark_mode
    user.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
