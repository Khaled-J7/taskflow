# TaskFlow Model Relationships Guide

This document provides a detailed explanation of the database relationships in the TaskFlow project. Understanding these relationships is crucial for implementing the models correctly and building proper queries.

## Types of Relationships in Django

Django supports three main types of relationships between models:

1. **One-to-One**: One record in Model A is related to exactly one record in Model B
2. **One-to-Many (ForeignKey)**: One record in Model A can be related to multiple records in Model B
3. **Many-to-Many**: Multiple records in Model A can be related to multiple records in Model B

## TaskFlow Database Relationships Overview

The following table summarizes all the relationships between models in the TaskFlow project:

| Relationship Type | Model A | Model B | Description |
|------------------|---------|---------|-------------|
| One-to-One | User | UserProfile | Each user has exactly one profile |
| One-to-Many | Project | Task | A project can have many tasks |
| One-to-Many | User | Task (created_by) | A user can create many tasks |
| One-to-Many | User | Task (assigned_to) | A user can be assigned many tasks |
| One-to-Many | Task | Comment | A task can have many comments |
| One-to-Many | User | Comment | A user can write many comments |
| One-to-Many | Task | Attachment | A task can have many attachments |
| One-to-Many | User | Attachment | A user can upload many attachments |
| One-to-Many | User | Notification | A user can receive many notifications |
| Many-to-Many | User | Project | Users can be members of multiple projects, and projects can have multiple users |
| Many-to-Many | Task | Tag | Tasks can have multiple tags, and tags can be applied to multiple tasks |

## Detailed Explanation of Each Relationship

### One-to-One: User and UserProfile

```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # other fields...
```

**Explanation:**
- Each User has exactly one UserProfile
- Each UserProfile belongs to exactly one User
- The `OneToOneField` creates this 1:1 relationship
- `on_delete=models.CASCADE` means when a User is deleted, their UserProfile is also deleted

**Access pattern:**
```python
# From User to UserProfile
user.userprofile  # Get the profile of a user

# From UserProfile to User
profile.user  # Get the user of a profile
```

### One-to-Many (ForeignKey): Project and Task

```python
class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    # other fields...
```

**Explanation:**
- Each Project can have many Tasks
- Each Task belongs to exactly one Project
- The `ForeignKey` in the Task model creates this relationship
- In the database, this creates a `project_id` column in the Task table

**Access pattern:**
```python
# From Task to Project
task.project  # Get the project a task belongs to

# From Project to Tasks
project.task_set.all()  # Get all tasks for a project
```

### Many-to-Many: User and Project (via ProjectMember)

```python
class Project(models.Model):
    # fields...
    members = models.ManyToManyField(User, through='ProjectMember')

class ProjectMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)  # Additional field
    # other fields...
```

**Explanation:**
- Each User can be a member of multiple Projects
- Each Project can have multiple Users as members
- The `through='ProjectMember'` parameter specifies a custom intermediate model 
- The custom intermediate model allows storing additional data about the relationship (like role)
- This creates two one-to-many relationships in the database:
  - ProjectMember to User
  - ProjectMember to Project

**Access pattern:**
```python
# Get all projects a user is a member of
user.project_set.all()  

# Or with the related_name if defined
user.projects.all()

# Get all members (users) of a project
project.members.all()

# Get role information using the intermediate model
user_membership = ProjectMember.objects.get(user=user, project=project)
role = user_membership.role
```

### Many-to-Many: Task and Tag

```python
class Task(models.Model):
    # other fields...
    tags = models.ManyToManyField('Tag')

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
```

**Explanation:**
- Each Task can have multiple Tags
- Each Tag can be applied to multiple Tasks
- Django automatically creates a hidden junction table in the database to manage this relationship
- This table contains just two columns: `task_id` and `tag_id`

**Access pattern:**
```python
# Get all tags for a task
task.tags.all()

# Get all tasks with a specific tag
tag.task_set.all()

# Add a tag to a task
task.tags.add(tag)

# Remove a tag from a task
task.tags.remove(tag)
```

## Database Tables and Their Columns

Here's how the model relationships translate to database tables:

### User Table (Django's built-in)
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| username | Varchar | User's username |
| password | Varchar | Hashed password |
| email | Varchar | Email address |
| ... | ... | Other built-in fields |

### UserProfile Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | ForeignKey to User (ONE-TO-ONE) |
| profile_picture | Varchar | Path to profile image |
| bio | Text | User biography |
| job_title | Varchar | User's job title |
| ... | ... | Other profile fields |

### Project Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| title | Varchar | Project title |
| description | Text | Project description |
| created_date | DateTime | Creation timestamp |
| status | Varchar | Project status |
| ... | ... | Other project fields |

### ProjectMember Table (Junction table)
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | ForeignKey to User |
| project_id | Integer | ForeignKey to Project |
| role | Varchar | Member role in project |
| joined_date | DateTime | When user joined project |

### Task Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| title | Varchar | Task title |
| description | Text | Task description |
| project_id | Integer | ForeignKey to Project |
| assigned_to_id | Integer | ForeignKey to User (can be null) |
| status | Varchar | Task status |
| priority | Varchar | Task priority |
| due_date | Date | Due date |
| created_by_id | Integer | ForeignKey to User (creator) |
| created_date | DateTime | Creation timestamp |
| ... | ... | Other task fields |

### Tag Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| name | Varchar | Tag name (unique) |

### Task_Tags Table (Auto-created by Django)
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| task_id | Integer | ForeignKey to Task |
| tag_id | Integer | ForeignKey to Tag |

### Comment Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| task_id | Integer | ForeignKey to Task |
| author_id | Integer | ForeignKey to User |
| content | Text | Comment content |
| created_date | DateTime | Creation timestamp |
| ... | ... | Other comment fields |

### Attachment Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| task_id | Integer | ForeignKey to Task |
| file | Varchar | Path to file |
| file_name | Varchar | Original filename |
| uploaded_by_id | Integer | ForeignKey to User |
| upload_date | DateTime | Upload timestamp |
| ... | ... | Other attachment fields |

## Practical Examples Using Django ORM

### Getting all tasks for a project
```python
tasks = Project.objects.get(id=1).task_set.all()
```

### Finding all projects a user is a member of
```python
projects = User.objects.get(username='alice').project_set.all()
```

### Getting all tasks assigned to a specific user
```python
tasks = Task.objects.filter(assigned_to__username='bob')
```

### Finding all comments on a task
```python
comments = task.comment_set.all()
```

### Getting all users who are members of a specific project
```python
members = project.members.all()
```

### Finding the role of a user in a project
```python
role = ProjectMember.objects.get(user=user, project=project).role
```

### Getting all tasks with a specific tag
```python
tasks = Task.objects.filter(tags__name='urgent')
```

## Visual Representation of Relationships

```
User (1) ───────────── (1) UserProfile
  │
  │
  │ (M)
  ▼
ProjectMember
  │
  │ (M)
  ▼
Project (1) ─────────── (M) Task (M) ─────────── (M) Tag
                          │
                          │ (1)
                          ▼
                     Comment (M) ◄─── (1) User
                          │
                          │
                     Attachment (M) ◄─── (1) User
```

## Important Implementation Notes

1. **Cascading Deletions**: Be careful with `on_delete` parameters. `CASCADE` will delete related objects, which can lead to data loss.

2. **Related_name**: Consider using `related_name` parameter to customize reverse relation name:
   ```python
   assigned_to = models.ForeignKey(User, related_name='assigned_tasks', on_delete=models.SET_NULL, null=True)
   ```

3. **Null vs. Blank**: 
   - `null=True` determines if NULL is allowed in the database
   - `blank=True` determines if the field is required in forms
   - For optional ForeignKey fields, typically use both

4. **Query Optimization**: Use `select_related()` and `prefetch_related()` to optimize queries involving relationships:
   ```python
   # Efficient querying with foreign keys
   tasks = Task.objects.select_related('project', 'assigned_to').all()
   
   # Efficient querying with many-to-many relationships
   projects = Project.objects.prefetch_related('members').all()
   ```

Understanding these relationships will help you correctly implement the models and build efficient queries throughout your TaskFlow application.
