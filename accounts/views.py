from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import userRegistrationForm,userUpdationForm,addAddressForm,editAddressForm
from django.contrib import messages
from .models import User,Address
from django.shortcuts import get_object_or_404
from django.urls import reverse
from products.models import Product

# Create your views here.

def user_dashboard(request):
    featured_products = Product.objects.filter(status="published", is_deleted=False, is_featured=True)
    context = {"featured_products": featured_products}
    
    return render(request, 'dashboard.html', context)

@login_required(login_url='login')
def user_profile(request):
    profile=request.user
    address=profile.addresses.all()
    home_address = address.filter(address_type='home').first()
    office_address = address.filter(address_type='office').first()
    context={'profile':profile,'home_address':home_address,'office_address':office_address}
    return render(request,'account/profile.html',context)

@login_required(login_url='login')
def accountSettings(request):
    user=request.user
    context={'user':user}
    return render(request,'account/account_settings.html',context)


def createUser(request):

    form=userRegistrationForm()

    if request.method=='POST':
        form=userRegistrationForm(request.POST)
        if form.is_valid():
            user=form.save()
            login(request,user)
            messages.success(request,"Account was successfully created🎉")
            return redirect('user_dashboard')
        
    
    context={'form':form}
    return render(request,'account/register.html',context)


def Userlogin(request):
    
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)
            messages.success(request,"User loged in successfully")
            return redirect('user_dashboard')
    messages.error(request,"Such user does not exists")
    return render(request,'account/login.html')

def logout_confirmation(request):

    if request.method == "POST":

        logout(request)

        messages.success(
            request,
            "User logged out successfully."
        )

        return redirect('user_dashboard')

    return render(
        request,
        'account/logout_confirm.html'
    )


def editProfile(request):
    if request.method == 'POST':
        form = userUpdationForm(
            request.POST,
            request.FILES,
            instance=request.user
        )

        if form.is_valid():
            form.save()
            return redirect('account_settings')

    else:
        form = userUpdationForm(instance=request.user)
    
    context={'form':form}
    return render(request,'account/profile_edit.html',context)


def delete_account(request):

    if request.method == "POST":
        request.user.delete()

        messages.success(
            request,
            "Your account has been deleted successfully."
        )

        return redirect("user_dashboard")  # Change to your homepage URL name

    context = {
        "object_name": "Account",
        "object_display": request.user.username,
        "cancel_url": "/account_settings/",  # Or use reverse()
    }

    return render(
        request,
        "delete.html",
        context
    )

@login_required(login_url='login')
def address(request):
    user=request.user
    addresses=user.addresses.all()
    home_address = addresses.filter(address_type='home').first()
    office_address = addresses.filter(address_type='office').first()
    context={'home_address':home_address,'office_address':office_address}
    return render(request,'account/address.html',context)

def addAddress(request):
    form=addAddressForm()
    if request.method=='POST':
        form=addAddressForm(request.POST)
        if form.is_valid():
          address = form.save(commit=False)
          address.user = request.user
          address.save()
          messages.success(request,"Address added successfully!")
          return redirect('address')
        print(form.errors)   
        messages.error(request,"Adding address failed!")
                
    context={'form':form}
    return render(request,'account/add_address.html',context)

def editAddress(request,pk):
    address = get_object_or_404(Address,id=pk,user=request.user)
    form=editAddressForm(instance=address)
    if request.method=='POST':
        form=editAddressForm(request.POST,instance=address)
        if form.is_valid():
            form.save()
            messages.success(request,"Address Updated successfully!")
            return redirect('address')
        print(form.errors)
        messages.error(request,"Error updating address")
        
    context={'form':form,}
    return render(request,'account/edit_address.html',context)





def deleteAddress(request, pk):
    address = get_object_or_404(
        Address,
        id=pk,
        user=request.user
    )

    if request.method == "POST":
        address.delete()

        messages.success(
            request,
            "Address deleted successfully!"
        )

        return redirect("address")

    context = {
        "object_name": "Address",
        "object_display": (
            f"{address.full_name} - "
            f"{address.address_type.title()} Address"
        ),
        "cancel_url": reverse("address"),
    }

    return render(
        request,
        "delete.html",
        context
    )




        

