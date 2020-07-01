from django.contrib.auth.forms import UserCreationForm
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core import urlresolvers
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required

from .forms import UserProfileForm, RegistrationForm

from . import profile

from checkout.models import Order, OrderItem


def register(request, template_name="registration/register.html"):
    if request.method == 'POST':
        postdata = request.POST.copy()
        form = RegistrationForm(postdata)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = postdata.get('email','')
            user.save()
            username = postdata.get('username', '')
            password = postdata.get('password1', '')
            new_user = authenticate(username=username, password=password)
            if new_user and new_user.is_active:
                login(request, new_user)
                url = urlresolvers.reverse('my_account')
                return redirect(url)
    else:
        form = RegistrationForm()
    page_title = 'User Registration'
    context = RequestContext(request, locals())
    return render_to_response(template_name, context)

@login_required
def my_account(request, template_name="register/my_account.html"):
    page_title = "My Account"
    user = request.user
    orders = Order.objects.filter(user=user)
    name = user.username
    context = RequestContext(request, locals())
    return render_to_response(template_name, context)

@login_required
def order_details(request, order_id, template_name="registration/order_details.html"):
    user = request.user
    order = get_object_or_404(Order, id=order_id, user=user)
    page_title = "Order details for Order #%s" % (order_id)
    order_items = OrderItem.objects.filter(order=order)
    context = RequestContext(request, locals())
    return render_to_response(template_name, context)

@login_required
def order_info(request, template_name="register/order_info.html"):
    if request.method == 'POST':
        postdata = request.POST.copy()
        form = UserProfileForm(postdata)
        if form.is_valid():
            profile.set(request)
            url = urlresolvers.reverse('my_account')
            return redirect(url)
    else:
        user_profile = profile.retrieve(request)
        form = UserProfileForm(instance=user_profile)
    page_title = 'Edit Order Information'
    context = RequestContext(request, locals())
    return render_to_response(template_name, context)