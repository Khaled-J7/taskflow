from email import message
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import UserRegistrationForm

# Create your views here.


def home(request):
    """ View for the home page. """
    return render(request, 'home.html')


def register(request):
    """Handle user registration."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # 📍 Save the new user
            user = form.save()
            # 📍 Gets the username and password from the cleaned form data
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            # 📍 Authenticates the user with authenticate()
            user = authenticate(username=username, password=password)
            # 📍 Logs the user in with login()
            """ login()
                - Associates the user with the session
                - Updates the `request.user` attribute to the authenticated user
                - Saves the user's ID in the session data
                - This is what actually "logs in" the user - it creates a session that will persist across requests until they log out or the session expires.
                """
            login(request, user)
            # 📍 Adds a success message with messages.success()
            messages.success(
                request,
                f'Account created successfully! You are now logged in as {username}.'
            )
            # Redirects to the home page
            return redirect('home')
    else:
        """If the form is invalid (e.g., if validation fails), it renders the register.html template again, but with the form containing error messages."""
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Handle user login."""
    # 📍 If user is already logged in, redirect them
    """ `request.user` refers to the user who is currently making the request to your web application."""
    if request.user.is_authenticated:
        return redirect('home')

    # This line checks the HTTP method of the request (GET | POST)
    if request.method == 'POST':
        # 📍 Create a form instance with the submitted data
        form = AuthenticationForm(data=request.POST)
        """`request.POST` is a dictionary-like object that contains all POST parameters. When a form is submitted, its fields become keys in this dictionary."""

        if form.is_valid():
            # 📍 Retrieving the validated username and password
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # 📍 Authenticates the user
            user = authenticate(username=username, password=password)

            if user is not None:
                """ login()
                - Associates the user with the session
                - Updates the `request.user` attribute to the authenticated user
                - Saves the user's ID in the session data
                - This is what actually "logs in" the user - it creates a session that will persist across requests until they log out or the session expires.
                """
                login(request, user)

                # 📍 Check if "remember me" was selected
                """ 
                By default, Django sessions persist for a certain time period (defined in settings.py, typically 2 weeks). The "remember me" functionality modifies this behavior.
                request.POST.get('remember_me') checks if the "remember me" checkbox was checked in the form. If it wasn't, we set the session expiry to 0, which means the session will end when the browser is closed. This is a convenience feature that adds security for users on shared computers.
                request.session is the session object, which is a dictionary-like object that persists across requests. The set_expiry() method controls when the session expires.
                """
                remember_me = request.POST.get('remember_me')
                if not remember_me:
                    # Session will expire when browser is closed
                    request.session.set_expiry(0)

                # 📍 Redirect to next page if it exists, otherwise home
                """  
                Django's login-required decorator automatically adds a next parameter to the URL when redirecting unauthenticated users to the login page. This parameter contains the URL they were trying to access.
                `request.GET.get('next')` checks if this parameter exists. If it does, we redirect the user back to the page they were trying to access before being redirected to login. If not, we simply redirect them to the home page.
                This is a common pattern in authentication systems - it provides a seamless experience where users can continue what they were doing after logging in.
                """
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('home')
    else:
        # 📍Create an empty form for GET requests
        form = AuthenticationForm()
        """ 
        If the request method isn't POST (typically it's GET), we're just displaying the login form. We create an empty AuthenticationForm instance that will render the default form fields without any data or errors.
        """

    return render(request, 'accounts/login.html', {'form': form}) # type: ignore
    """ 
    Finally, we render the login template with the form. If it's a GET request, this displays an empty form. If it's a POST request with invalid data, this displays the form again but with error messages
    """
    