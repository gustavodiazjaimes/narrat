from narrat.apps.projects.models import ProjectMember

class ProjectsMiddleware(object):
    
    def process_template_response(self, request, response):
        if request.user.is_authenticated():
            project = response.context_data.get('project', None)
            projectmember = response.context_data.get('projectmember', None)
            
            if project and not projectmember:
                projectmember = project.members.active(user=request.user, project=project)
                if not projectmember.exists():
                    projectmember = None
                
                response.context_data['projectmember'] = projectmember
        
        return response