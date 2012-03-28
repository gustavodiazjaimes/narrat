from narrat.apps.projects.models import ProjectMember

class ProjectsMiddleware(object):
    
    def process_template_response(self, request, response):
        if request.user.is_authenticated():
            project = response.context_data.get('project', None)
            projectmember = response.context_data.get('projectmember', None)
            
            if project and projectmember == None:
                try:
                    projectmember = ProjectMember.objects.activemember().get(user=request.user, project=project)
                except ProjectMember.DoesNotExist:
                    projectmember = None
                
                response.context_data['projectmember'] = projectmember
        
        return response