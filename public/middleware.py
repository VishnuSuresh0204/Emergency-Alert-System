from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

class NoCacheMiddleware(MiddlewareMixin):
    def process_request(self, request):
        path = request.path
        # Protected path prefixes
        protected_prefixes = ['/admin_', '/staff_', '/volunteer_', '/citizen_', '/chat_room/', '/view_my_chats/']
        
        is_protected = any(path.startswith(prefix) for prefix in protected_prefixes)
        
        if is_protected:
            if 'lid' not in request.session:
                return redirect('/')
        return None

    def process_response(self, request, response):
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
