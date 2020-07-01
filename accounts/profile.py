from .models import UserProfile
from .forms import UserProfileForm

def retrieve(request):
    """
    This requires an authenticated user before we try calling it
    """
    try:
        profile = request.user.get_profile()
        profile.is_active = True
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=request.user)
        profile.save()
    return profile


def set(request):
    profile = retrieve(request)
    profile_form = UserProfileForm(request.POST, instance=profile)
    profile_form.save(commit=False)
    profile_form.instance.is_active = True
    profile_form.save()