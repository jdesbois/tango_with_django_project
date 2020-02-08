from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from django.shortcuts import redirect
from django.urls import reverse
from rango.forms import CategoryForm
from rango.forms import PageForm
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def index(request):
    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage matches to {{ boldmessage }} in the template!
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {}

    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list

    # Return a rendered responce to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    context_dict = {'boldmessage' : 'John Desbois'}
    return render(request, 'rango/about.html', context=context_dict)

def show_category(request, category_name_slug):
    context_dict = {}
    
    try:
        category = Category.objects.get(slug=category_name_slug)

        pages = Page.objects.filter(category=category)

        context_dict['pages'] = pages
        context_dict['category'] = category

    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context=context_dict)
@login_required
def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)

            return redirect('/rango/')
        else:
            print(form.errors)
    
    return render(request, 'rango/add_category.html', {'form': form})
@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    if category is None:
        return redirect('/rango/')

    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))

        else:
            print(form.errors)
    
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)

def register(request):
    #Boolean vaue to let form know where the registration was successful
    registered = False
    #If post processed interested in processing Form data
    if request.method == 'POST':
        #Attempt to grab information from the raw form 
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        #If the forms are valid - save the users form data to the database
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            #Hash the users password and save it to the database
            user.set_password(user.password)
            user.save()
            #Commit = False so its not commited until ready to avoid integrity issues
            profile = profile_form.save(commit=False)
            profile.user = user
            #Did user provide a profile picture? if so grab it and put it in the user profile model
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            
            #Save userprofile instance
            profile.save()
            #Update registered variable to say it was successfull
            registered = True
        else: 
            #invalid forms, mistakes or something else
            print(user_form.errors, profile_form.errors)
    else:
        #Not HTTP POST, so we render our form using two ModelForm instances. Blank and ready for input
        user_form = UserForm()
        profile_form = UserProfileForm()
    #Render the template depending on the context
    return render(request, 'rango/register.html', context= {'user_form':user_form, 'profile_form': profile_form, 'registered':registered})

def user_login(request):
    if request.method == 'POST':
        #Gather username and password from user, obtained from login form. 
        username = request.POST.get('username')
        password = request.POST.get('password')

        #Use djangos machinery to attempt to see if the username/password combo is valid 
        user = authenticate(username=username, password=password)

        #if we have a User object returned, the details are correct. if None then no user is found.
        if user:
            if user.is_active:
                #if user is valid and active, send them to homepage
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                return HttpResponse('Your Rango account is disabled.')
        else:
            #bad login details were provided, so cant login
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")

    #request is not POST so display login form
    else:
        return render(request, 'rango/login.html')

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))