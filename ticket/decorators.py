from functools import wraps
from django.shortcuts import redirect

def jwt_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        token = request.session.get('jwt_token')
        if not token:
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    return wrapper
