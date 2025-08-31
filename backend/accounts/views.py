from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.db import connection


def login_view(request):
    """Custom login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')


@login_required
@never_cache
def dashboard_view(request):
    """User dashboard showing personalized content"""
    
    # Get user-specific stats from database
    with connection.cursor() as cursor:
        # Count total users (for admin)
        if request.user.is_superuser:
            cursor.execute("SELECT COUNT(*) FROM auth_user")
            total_users = cursor.fetchone()[0]
        else:
            total_users = None
        
        # Get user's login history
        cursor.execute("""
            SELECT last_login, date_joined 
            FROM auth_user 
            WHERE id = %s
        """, [request.user.id])
        user_data = cursor.fetchone()
    
    context = {
        'user': request.user,
        'full_name': request.user.get_full_name() or request.user.username,
        'is_admin': request.user.is_superuser,
        'total_users': total_users,
        'last_login': user_data[0] if user_data else None,
        'date_joined': user_data[1] if user_data else None,
    }
    
    return render(request, 'accounts/dashboard.html', context)


@login_required
def logout_view(request):
    """Logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')
