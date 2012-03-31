

class ProfilesMiddleware(object):
    
    def process_template_response(self, request, response):
        if request.user.is_authenticated():
            page_user = response.context_data.get('page_user', None)
            is_me = response.context_data.get('is_me', None)
            
            if page_user and is_me == None:
                user = request.user
                is_me = user == page_user
                
                response.context_data['is_me'] = is_me
        
        return response