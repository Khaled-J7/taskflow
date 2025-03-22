# TaskFlow Project Development Guide

## Project Overview

TaskFlow is a collaborative task management system built with Django. This system allows users to create projects, manage tasks, assign team members, track progress, add comments, and receive notifications.

## Technology Stack

- **Backend**: Django, Django REST Framework
- **Database**: PostgreSQL
- **Frontend**: HTML/CSS, Bootstrap 5, HTMX
- **Version Control**: Git
- **Future Extensions**: Django Channels (for real-time notifications)

## Database Schema

The application consists of the following models:

1. **User & UserProfile**:
   - Extends Django's User model with profile information
   - One-to-one relationship

2. **Project**:
   - Contains project details (title, description, status)
   - Connected to users through ProjectMember

3. **ProjectMember**:
   - Junction table connecting Users to Projects
   - Stores role information
   - Uses ForeignKey to both User and Project

4. **Task**:
   - Individual tasks with title, description, status, priority, due dates
   - Connected to Project via ForeignKey
   - Connected to User via ForeignKey (assigned_to)

5. **Tag & TaskTag**:
   - System for categorizing tasks
   - Many-to-many relationship between Task and Tag

6. **Comment**:
   - User comments on tasks
   - Connected to Task and User via ForeignKey

7. **Attachment**:
   - Files attached to tasks
   - Connected to Task and User via ForeignKey

8. **Notification**:
   - System messages for users
   - Connected to User via ForeignKey

## Model Relationships Recap

- **One-to-One**: 
  - UserProfile to User

- **One-to-Many (ForeignKey)**: 
  - Task to Project (each task belongs to one project)
  - Comment to Task (each comment belongs to one task)
  - Attachment to Task (each attachment belongs to one task)
  - Task to User (assigned_to field)
  - ProjectMember to User
  - ProjectMember to Project

- **Many-to-Many**: 
  - User to Project (via ProjectMember junction table)
  - Task to Tag

## Development Phases

### Phase 1: Project Setup and Environment Configuration
1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install necessary packages**
   ```bash
   pip install django djangorestframework psycopg2-binary pillow django-crispy-forms
   pip freeze > requirements.txt
   ```

3. **Set up PostgreSQL database**
   - Create a database for the project
   - Configure database settings in Django

4. **Initialize Django project**
   ```bash
   django-admin startproject taskflow .
   ```

5. **Create main applications**
   ```bash
   python manage.py startapp accounts
   python manage.py startapp projects
   python manage.py startapp tasks
   ```

6. **Configure settings.py**
   - Add installed apps
   - Configure database connection
   - Set up static and media files
   - Configure authentication

7. **Initialize Git repository**
   ```bash
   git init
   touch .gitignore  # Add appropriate files to ignore
   git add .
   git commit -m "Initial project setup"
   ```

### Phase 2: User Authentication System

1. **Extend User model with UserProfile**
   ```python
   # accounts/models.py
   class UserProfile(models.Model):
       user = models.OneToOneField(User, on_delete=models.CASCADE)
       profile_picture = models.ImageField(upload_to='profiles/', blank=True)
       bio = models.TextField(blank=True)
       job_title = models.CharField(max_length=100, blank=True)
       # Add other fields as needed
   ```

2. **Create authentication views**
   - Registration view
   - Login view
   - Logout view
   - Password reset views

3. **Create profile management**
   - Profile view
   - Profile update view

4. **Design authentication templates**
   - Registration form
   - Login form
   - Profile page
   - Password reset forms

5. **Set up URL patterns**
   ```python
   # accounts/urls.py
   urlpatterns = [
       path('register/', views.register, name='register'),
       path('login/', views.login_view, name='login'),
       path('logout/', views.logout_view, name='logout'),
       path('profile/', views.profile, name='profile'),
       path('profile/edit/', views.edit_profile, name='edit_profile'),
       # Add other authentication URLs
   ]
   ```

6. **Create a base template with navigation**
   - Include header, footer
   - Add navigation links
   - Set up message display

### Phase 3: Project Management

1. **Create Project model**
   ```python
   # projects/models.py
   class Project(models.Model):
       title = models.CharField(max_length=100)
       description = models.TextField()
       created_date = models.DateTimeField(auto_now_add=True)
       status = models.CharField(max_length=20, choices=[
           ('active', 'Active'),
           ('archived', 'Archived')
       ], default='active')
   ```

2. **Implement ProjectMember model for user-project relationships**
   ```python
   class ProjectMember(models.Model):
       user = models.ForeignKey(User, on_delete=models.CASCADE)
       project = models.ForeignKey(Project, on_delete=models.CASCADE)
       role = models.CharField(max_length=50, choices=[
           ('admin', 'Admin'),
           ('manager', 'Project Manager'),
           ('member', 'Team Member')
       ])
       joined_date = models.DateTimeField(auto_now_add=True)
   ```

3. **Create Project CRUD Views**
   - Project list view
   - Project detail view
   - Project creation view
   - Project update view
   - Project delete view
   - Member management views

4. **Design Project Templates**
   - Project list page
   - Project detail page
   - Project form (create/edit)
   - Member management page

5. **Set up Project URLs**
   ```python
   # projects/urls.py
   urlpatterns = [
       path('', views.project_list, name='project_list'),
       path('new/', views.project_create, name='project_create'),
       path('<int:pk>/', views.project_detail, name='project_detail'),
       path('<int:pk>/edit/', views.project_update, name='project_update'),
       path('<int:pk>/delete/', views.project_delete, name='project_delete'),
       path('<int:pk>/members/', views.manage_members, name='manage_members'),
       # Add other project-related URLs
   ]
   ```

### Phase 4: Task Management

1. **Create Task model**
   ```python
   # tasks/models.py
   class Task(models.Model):
       title = models.CharField(max_length=100)
       description = models.TextField()
       project = models.ForeignKey(Project, on_delete=models.CASCADE)
       assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
       status = models.CharField(max_length=20, choices=[
           ('todo', 'To Do'),
           ('in_progress', 'In Progress'),
           ('review', 'Review'),
           ('done', 'Done')
       ], default='todo')
       priority = models.CharField(max_length=20, choices=[
           ('low', 'Low'),
           ('medium', 'Medium'),
           ('high', 'High'),
           ('urgent', 'Urgent')
       ], default='medium')
       due_date = models.DateField(null=True, blank=True)
       created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
       created_date = models.DateTimeField(auto_now_add=True)
       updated_date = models.DateTimeField(auto_now=True)
   ```

2. **Create Tag model**
   ```python
   class Tag(models.Model):
       name = models.CharField(max_length=50, unique=True)

   class TaskTag(models.Model):
       task = models.ForeignKey(Task, on_delete=models.CASCADE)
       tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
   ```

3. **Implement Task CRUD Views**
   - Task list view (with filtering)
   - Task detail view
   - Task creation view
   - Task update view
   - Task delete view
   - Task status update view

4. **Design Task Templates**
   - Task list page (with filters)
   - Task detail page
   - Task form (create/edit)
   - Task board view (kanban style)

5. **Set up Task URLs**
   ```python
   # tasks/urls.py
   urlpatterns = [
       path('project/<int:project_id>/tasks/', views.task_list, name='task_list'),
       path('project/<int:project_id>/tasks/new/', views.task_create, name='task_create'),
       path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
       path('tasks/<int:pk>/edit/', views.task_update, name='task_update'),
       path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
       path('tasks/<int:pk>/status/', views.update_status, name='update_status'),
       # Add other task-related URLs
   ]
   ```

### Phase 5: Comments and Attachments

1. **Create Comment model**
   ```python
   # tasks/models.py
   class Comment(models.Model):
       task = models.ForeignKey(Task, on_delete=models.CASCADE)
       author = models.ForeignKey(User, on_delete=models.CASCADE)
       content = models.TextField()
       created_date = models.DateTimeField(auto_now_add=True)
       updated_date = models.DateTimeField(auto_now=True, null=True, blank=True)
   ```

2. **Create Attachment model**
   ```python
   class Attachment(models.Model):
       task = models.ForeignKey(Task, on_delete=models.CASCADE)
       file = models.FileField(upload_to='attachments/')
       file_name = models.CharField(max_length=255)
       file_type = models.CharField(max_length=100)
       file_size = models.IntegerField()  # Size in bytes
       uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
       upload_date = models.DateTimeField(auto_now_add=True)
   ```

3. **Implement Comment and Attachment Views**
   - Comment creation view
   - Comment listing view (for a task)
   - File upload view
   - File download view

4. **Add Comments and Attachments to Task Detail Template**
   - Comment section
   - Comment form
   - Attachment listing
   - File upload form

5. **Set up Comment and Attachment URLs**
   ```python
   # tasks/urls.py (additional URLs)
   urlpatterns += [
       path('tasks/<int:task_id>/comments/', views.add_comment, name='add_comment'),
       path('tasks/<int:task_id>/attachments/', views.add_attachment, name='add_attachment'),
       path('attachments/<int:pk>/download/', views.download_attachment, name='download_attachment'),
   ]
   ```

### Phase 6: API Development with Django REST Framework

1. **Set up Django REST Framework**
   - Add to installed apps
   - Configure authentication

2. **Create Serializers**
   ```python
   # api/serializers.py
   class UserSerializer(serializers.ModelSerializer):
       class Meta:
           model = User
           fields = ['id', 'username', 'email', 'first_name', 'last_name']

   class ProjectSerializer(serializers.ModelSerializer):
       class Meta:
           model = Project
           fields = '__all__'

   class TaskSerializer(serializers.ModelSerializer):
       class Meta:
           model = Task
           fields = '__all__'

   # Add serializers for other models
   ```

3. **Implement API Views**
   ```python
   # api/views.py
   @api_view(['GET'])
   def project_list_api(request):
       projects = Project.objects.all()
       serializer = ProjectSerializer(projects, many=True)
       return Response(serializer.data)

   @api_view(['GET'])
   def project_detail_api(request, pk):
       project = get_object_or_404(Project, pk=pk)
       serializer = ProjectSerializer(project)
       return Response(serializer.data)

   # Add views for other API endpoints
   ```

4. **Set up API URLs**
   ```python
   # api/urls.py
   urlpatterns = [
       path('projects/', views.project_list_api, name='api_project_list'),
       path('projects/<int:pk>/', views.project_detail_api, name='api_project_detail'),
       path('tasks/', views.task_list_api, name='api_task_list'),
       path('tasks/<int:pk>/', views.task_detail_api, name='api_task_detail'),
       # Add other API endpoints
   ]
   ```

5. **Add Authentication to API**
   - Token authentication
   - Permission classes

### Phase 7: Advanced Features

1. **Implement Search Functionality**
   - Search projects
   - Search tasks

2. **Create Notification System**
   ```python
   # notifications/models.py
   class Notification(models.Model):
       user = models.ForeignKey(User, on_delete=models.CASCADE)
       content = models.TextField()
       link = models.CharField(max_length=255, blank=True)
       read = models.BooleanField(default=False)
       created_date = models.DateTimeField(auto_now_add=True)
   ```

3. **Add Dashboard with Statistics**
   - Project completion rates
   - Task status distribution
   - Upcoming deadlines

4. **Enhance UI with HTMX for Dynamic Updates**
   - Live task status updates
   - Comment addition without page reload
   - Dynamic filtering

5. **Polish Design and User Experience**
   - Refine responsive design
   - Add animations and transitions
   - Improve form validation feedback

## Implementation Workflow

For each feature, follow this consistent approach:

1. **Define Models**: Create and migrate database models
2. **Create URLs**: Set up URL patterns
3. **Implement Views**: Build function-based views
4. **Design Templates**: Create HTML templates with Bootstrap
5. **Add Forms**: Create Django forms for data validation
6. **Test Thoroughly**: Verify functionality before moving forward

## Development Best Practices

1. **Regular Commits**: Make small, frequent commits with clear messages
2. **Code Organization**: Keep related functionality together
3. **Documentation**: Add comments to complex code sections
4. **Testing**: Test each feature thoroughly
5. **Security**: Validate all user input and check permissions
6. **Performance**: Optimize database queries where needed

## Getting Started Checklist

- [ ] Set up development environment
- [ ] Install required packages
- [ ] Configure database
- [ ] Create project structure
- [ ] Define initial models
- [ ] Start with user authentication

## Useful Django Commands

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Run tests
python manage.py test

# Shell for experimenting with models
python manage.py shell
```

## References

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)
- [HTMX Documentation](https://htmx.org/docs/)
