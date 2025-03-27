### DRF QuizLeader API **v1.0.0** - [Live Deployment](https://rafiulislam18.pythonanywhere.com/quiz-leader-drf-api/)  
The API allows us to play quizzes (start quiz & submit answers), track player scores with leaderboards (subject-specific & global) & CRUD on subjects, lessons & questions.

#

# Installation

1. **Environment Setup**
   ```bash
   # Copy demo environment file
   cp demo.env .env
   ```
   Edit the `.env` file with your development environment variables.

2. **Create Virtual Environment**
   ```powershell
   # Windows PowerShell
   python -m venv env
   ```
   ```bash
   # macOS/Linux
   python3 -m venv env
   ```

3. **Activate Virtual Environment**
   ```powershell
   # Windows PowerShell
   .\env\Scripts\activate
   ```
   ```bash
   # macOS/Linux
   source env/bin/activate
   ```

4. **Install Dependencies**
   ```powershell
   # Windows PowerShell
   # For development
   pip install -r .\requirements\dev.txt
   # For testing (optional)
   pip install -r .\requirements\test.txt
   ```
   ```bash
   # macOS/Linux
   # For development
   pip install -r requirements/dev.txt
   # For testing (optional)
   pip install -r requirements/test.txt
   ```

5. **Run Development Server**
   ```powershell
   # Windows PowerShell
   python manage.py runserver
   ```
   ```bash
   # macOS/Linux
   python manage.py runserver
   ```

6. **Create Superuser** (Optional)
   ```powershell
   # Windows PowerShell
   python manage.py createsuperuser
   ```
   ```bash
   # macOS/Linux
   python manage.py createsuperuser
   ```
   Follow the prompts to create an admin user.

The API will be available at `http://127.0.0.1:8000/`

#

# Project Features

### JWT Authentication

The API implements JWT (JSON Web Token) authentication using `djangorestframework-simplejwt` for secure user authentication:

- **Token Types**
  - **Access Token**: Short-lived token (30 minutes) for API access
  - **Refresh Token**: Long-lived token (7 days) for obtaining new access tokens & logout

- **Authentication Flow**
  1. **Registration**
     ```http
     POST /api/auth/register/
     {
       "username": "user123",
       "password": "securepass123"
     }
     Response: {
       "refresh": "refresh_token",
       "access": "access_token",
       "id": 1,
       "username": "user123"
     }
     ```

  2. **Login**
     ```http
     POST /api/auth/login/
     {
       "username": "user123",
       "password": "securepass123"
     }
     Response: {
       "refresh": "refresh_token",
       "access": "access_token",
       "user": {
         "id": 1,
         "username": "user123",
         ...
       }
     }
     ```

  3. **Token Refresh**
     ```http
     POST /api/auth/token/refresh/
     {
       "refresh": "refresh_token"
     }
     Response: {
       "access": "new_access_token",
       "refresh": "new_refresh_token"
     }
     ```

  4. **Logout**
     ```http
     POST /api/auth/logout/
     {
       "refresh": "refresh_token"
     }
     Response: 204 No Content
     ```

- **Security Features**
  - Token blacklisting after logout/refresh
  - Automatic refresh token rotation
  - Rate limiting on authentication endpoints
  - Secure token storage in HTTP-only cookies
  - Bearer token authentication scheme

- **Implementation Details**
  ```python
  # JWT Settings
  SIMPLE_JWT = {
      'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
      'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
      'ROTATE_REFRESH_TOKENS': True,
      'BLACKLIST_AFTER_ROTATION': True,
      'ALGORITHM': 'HS256',
      'AUTH_HEADER_TYPES': ('Bearer',),
  }
  ```

- **Usage in Requests**
  ```http
  Authorization: Bearer <access_token>
  ```

- **Error Handling**
  - 401 Unauthorized: Invalid/expired token
  - 400 Bad Request: Invalid token format
  - 429 Too Many Requests: Rate limit exceeded

- **Best Practices**
  - Store tokens securely (HTTP-only cookies)
  - Implement token refresh mechanism
  - Handle token expiration gracefully
  - Use HTTPS for all authentication requests
  - Implement proper error handling
  - Follow rate limiting guidelines

### Rate-Limiting

The API implements a multi-tier rate limiting strategy to protect against abuse while ensuring fair access:

- **Global Rate Limits**

   - **Anonymous Users**: 120 requests per minute
   - **Authenticated Users**: 180 requests per minute
   - **Staff & Superusers**: Exempt from rate limiting
  
- **Authentication-Specific Limits**

   - **Registration**: 5 requests per minute
   - **Login/Logout/Token Refresh**: 60 requests per minute

- **Implementation Details**

   - Uses Django REST Framework's built-in throttling system
   - Custom throttles for different user roles and endpoints
   - Rate limits are enforced per IP address for anonymous users
   - Rate limits are enforced per user for authenticated users
   - Staff and superusers are exempt from rate limiting for administrative tasks

### Pagination

The API implements a flexible pagination system with view-specific settings to efficiently handle different types of data:

- **View-Specific Settings**
  - **Subjects List**: 10 items per page (max 25)
  - **Lessons List**: 10 items per page (max 50)
  - **Questions List**: 15 items per page (max 30)
  - **Subject Leaderboard**: 10 items per page (max 50)
  - **Global Leaderboard**: 25 items per page (max 100)

- **Pagination Features**
  - **PageNumberPagination**: Standard page-based navigation
  - **CustomPageNumberPagination**: Enhanced version with:
    - Configurable page size via query parameter
    - Maximum page size limit per view
    - Optimized for specific data types

- **Response Format**
  ```json
  {
    "count": 100,          // Total number of items
    "next": "url?page=2",  // URL for next page
    "previous": null,      // URL for previous page
    "results": [...]       // Items for current page
  }
  ```

- **Usage Examples**
  - Default: `GET /api/endpoint/`
  - Custom page size: `GET /api/endpoint/?page_size=20`
  - Specific page: `GET /api/endpoint/?page=2`

### Permissions

The API implements a role-based permission system to control access to different endpoints:

- **Authentication Endpoints**
  
  - **Registration, Login, Logout, Token Refresh**: `AllowAny` - Public access with rate limiting

- **Quiz Management**

  - **Subjects/Lessons/Questions**: `IsAdminOrReadOnly`
    - Read operations (GET): Public access
    - Write operations (POST/PUT/PATCH/DELETE): Staff & Superusers only

  - **Quiz Game**: `IsAuthenticated`
    - Start quiz: Authenticated users only
    - Submit answers: Authenticated users only

  - **Leaderboard**: `AllowAny`
    - View leaderboards (GET): Public access

- **Permission Classes**

  - **IsAdminOrReadOnly**: Custom permission class
    - Allows read access to anyone (public)
    - Restricts write access to staff & superusers

  - **IsAuthenticated**: DRF's built-in permission
    - Ensures user is logged in
    - Requires valid JWT access token

  - **AllowAny**: DRF's built-in permission
    - Allows all requests
    - Used for public endpoints

- **Implementation Details**

  - JWT-based authentication
  - Role-based access control
  - Granular permission checks per endpoint
  - Consistent error responses (401/403)

### Caching

The API implements a strategic caching system to optimize performance and reduce database load:

- **Cache Configuration**
  - Uses Django's built-in caching framework
  - Default backend: LocMemCache (in-memory cache)
  - Cache timeout: 15 minutes for most endpoints
  - Cache invalidation on data modifications

- **Cached Endpoints**

  - **Leaderboard Data**
    - Global leaderboard cache key: `leaderboard:global:page:{page_number}:size:{page_size}`
    - Subject-specific leaderboard cache key: `leaderboard:subject:{subject_id}:page:{page_number}:size:{page_size}`
    - Caches paginated leaderboard data
    - Invalidated every single minute (for refreshed data)

  - **Subjects List**
    - Cache key: `subjects:page:{page_number}:size:{page_size}`
    - Caches paginated subject lists
    - Invalidated on subject creation/update/deletion

  - **Lessons List**
    - Cache key: `lessons:subject:{subject_id}:page:{page_number}:size:{page_size}`
    - Caches paginated lessons within subjects
    - Invalidated on lesson creation/update/deletion

  - **Questions List**
    - Cache key: `questions:lesson:{lesson_id}:page:{page_number}:size:{page_size}`
    - Caches paginated questions within lessons
    - Invalidated on question creation/update/deletion

- **Cache Invalidation Strategy**
  - Automatic cache clearing on data modifications
  - Full cache invalidation on write operations (as Django default caching doesn't support specific cache key invalidation)
  - Granular cache keys for efficient updates
  - Prevents stale data issues

- **Implementation Details**
  ```python
  # Cache key generation
  cache_key = f'resource_type:page:{page_number}:size:{page_size}'
  
  # Cache retrieval
  cached_data = cache.get(cache_key)
  
  # Cache setting
  cache.set(cache_key, data, timeout=60*15)  # 15 minutes
  
  # Cache invalidation
  cache.clear()  # On data modifications
  ```

- **Performance Benefits**
  - Reduced database queries
  - Faster response times
  - Lower server load
  - Better scalability

### Database Optimization

The API implements several database optimization strategies to enhance performance and scalability:

- **Strategic Indexing**

  - **User Model Indexes**
    - `username_idx`: Optimizes user lookups by username
    - `high_score_idx`: Improves leaderboard queries

  - **Subject Model Indexes**
    - `subject_name_idx`: Accelerates subject name searches
    - Unique constraint on `name` field

  - **Lesson Model Indexes**
    - `lesson_subject_title_idx`: Optimizes subject-lesson queries
    - Unique constraint on `(subject, title)` combination

  - **Question Model Indexes**
    - `question_lesson_idx`: Improves lesson-question queries

  - **QuizAttempt Model Indexes**
    - `attempt_user_lesson_idx`: Optimizes user attempt history
    - `attempt_score_idx`: Enhances leaderboard performance

- **Query Optimization**

  - **Selective Field Loading**
    ```python
    # Only fetch required fields
    question_ids = lesson.questions.values_list('id', flat=True)
    ```

  - **Efficient Joins**
    ```python
    # Optimized leaderboard query with annotations
    leaderboard_data = QuizAttempt.objects.filter(
        lesson__subject__id=subject_id,
        completed=True
    ).values(username=F('user__username')).annotate(
        high_score=Max('score'),
        avg_score=Avg('score'),
        total_played=Count('id')
    )
    ```

  - **Bulk Operations**
    - Atomic transactions for data consistency
    - Efficient batch updates for user stats
    ```python
    # Example from quiz submission process
    @transaction.atomic
    def post(self, request, attempt_id):
        # Get and lock the attempt record
        attempt = QuizAttempt.objects.select_for_update().get(
            id=attempt_id,
            user=request.user
        )
        
        # Calculate score and update attempt
        attempt.score = score
        attempt.completed = True
        attempt.save()
        
        # Update user stats in the same transaction
        user = request.user
        user.total_played += 1
        user.highest_score = max(user.highest_score, score)
        user.save()
    ```

- **Model Design Optimizations**

  - **JSONField for Question Options**
    - Efficiently stores multiple options in a single field
    - Enables flexible option structure without schema changes
    - Reduces table complexity and query overhead
    - Example: `{"1": "option1", "2": "option2", "3": "option3"}`

  - **Optimized Model Relationships**
    - Strategic use of `related_name` for efficient reverse lookups
    - Enables direct access to related objects without additional queries
    - Example: `subject.lessons.all()` instead of `Lesson.objects.filter(subject=subject)`

- **Performance Features**

  - **View-Specific Pagination**
    - Customized page sizes per view type
    - Prevents large data dumps and memory issues
    - Example: Subjects (10/25), Lessons (10/50), Questions (15/30)

  - **Atomic Transaction Management**
    - Ensures data consistency in concurrent operations
    - Prevents race conditions in quiz submissions
    - Handles user stats updates safely
    - Example: Quiz submission with score calculation and user stats update

  - **Caching Integration**
    - Database query result caching
    - Reduced database load
    - Improved response times

### Logging

The API implements a comprehensive logging system with environment-specific configurations:

- **Logging Configuration**

  - **Formatters**
    ```python
    'verbose': '[{levelname}] [{asctime}] [{module}] [{pathname}] [{lineno}] >> {message}'
    'simple': '[{levelname}] >> {message}'
    ```

  - **Handlers**
    - **Console Handler**: Streams logs to console
    - **File Handler**: Rotating file handler with:
      - 5MB max file size
      - 5 backup files
      - Environment-specific log files

  - **Loggers**
    - Root logger: `''` - Catches all unhandled logs
    - Django logger: `django` - Framework-specific logs
    - App loggers: `apps.authentication`, `apps.quiz`

- **Environment-Specific Settings**

  - **Development**
    - Log level: DEBUG
    - Log file: `logs/dev.log`
    - Both console and file logging

  - **Production**
    - Log level: INFO/WARNING
    - Log file: `logs/prod.log`
    - Both console and file logging
    - Django logs set to ERROR

  - **Testing**
    - Log level: WARNING
    - Console-only logging
    - File handler disabled
    - Optimized for test performance

- **Implementation Example**
  ```python
  # Example from RegisterView
  try:
      serializer = RegisterSerializer(data=request.data)
      serializer.is_valid(raise_exception=True)
      user = serializer.save()
      # ... success logic ...

  # ... properly handling expectable errors without logging them ...
  
  # Log only unexpected errors
  except Exception as e:
      # Log the error for debugging
      logger.error(
          f"Error in RegisterView.post(): {str(e)}",
          exc_info=True
      )
      return Response(
          {"detail": "An error occurred while processing your request."},
          status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )
  ```

- **Logging Features**

  - **Error Tracking**
    - Detailed error logging with stack traces (`exc_info=True`)
    - Contextual information in log messages (view name, error type)
    - Exception details preserved for debugging

  - **Environment-Specific Logging**
    - Development: Detailed DEBUG logs for troubleshooting
    - Production: WARNING/ERROR logs for critical issues
    - Testing: Minimal WARNING logs, file logging disabled

  - **Log Management**
    - Automatic log rotation (5MB max size)
    - 5 backup files maintained
    - Environment-specific log files (`dev.log`, `prod.log`)

### API Documentation

The API uses drf-yasg (Yet Another Swagger Generator) to provide interactive documentation. We have serializer dependent & also custom made request body API docs using drf-yasg:

- **Serializer-Based Documentation** (For standard CRUD endpoints)
  ```python
  @swagger_auto_schema(
        tags=["Quiz-Lessons"],
        operation_description="Create a new lesson within a subject",
        manual_parameters=[
            openapi.Parameter(
                'subject_id',
                openapi.IN_PATH,
                description="ID of the subject to create lesson for",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        request_body=LessonSerializer,
        responses={
            201: openapi.Response(
                'Success: Created',
                LessonResponseSerializer
            ),
            400: 'Error: Bad Request',
            401: 'Error: Unauthorized',
            403: 'Error: Forbidden',
            404: 'Error: Not found',
            429: 'Error: Too many requests',
            500: 'Error: Internal server error'
        }
    )
  ```

- **Custom Schema Documentation** (For complex payloads)
  ```python
  @swagger_auto_schema(
      tags=["Quiz-Game"],
      operation_description="Submit quiz answers & get score",

      # ... codes for manual_parameters ...

      # ... custom payload docs ...
      request_body=openapi.Schema(
          type=openapi.TYPE_OBJECT,
          properties={
              'answers': openapi.Schema(
                  type=openapi.TYPE_OBJECT,
                  description='Dictionary of "question_id": "selected_option"'
              )
          },
          example={
              "answers": {
                  "101": "1",
                  "102": "3"
              }
          }
      ),

      # ... other existing codes ...
  )
  ```

- **Key Features**
  - Interactive Swagger UI with try-it-out functionality
  - JWT authentication support
  - Grouped endpoints by feature tags
  - Request/response examples
  - Detailed error responses
  - Parameter validation rules

- **Documentation Standards**
  - Clear operation descriptions
  - Consistent response formats
  - Complete parameter documentation
  - Authentication requirements
  - Status code documentation

#

# Project Structure

Allowing to play quizzes, track player scores with leaderboards & manage subjects, lessons & questions, the API project ensures a modular, scalable & maintainable DRF architecture:

```
Py-DRF__QuizLeader_API/
├── apps/                          # Custom django apps (authentication, quiz)
│   ├── authentication/            # Authentication app (user auth & authorization with player stats)
│   │   ├── serializers/
│   │   │   ├── __init__.py
│   │   │   ├── login.py
│   │   │   ├── logout.py
│   │   │   ├── register.py
│   │   │   ├── token_refresh.py
│   │   │   └── user.py
│   │   │   
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Import common dependencies for views
│   │   │   ├── login.py
│   │   │   ├── logout.py
│   │   │   ├── register.py
│   │   │   └── token_refresh.py
│   │   │   
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── throttles.py            # Rate-limiting configs for Authentication app
│   │   └── urls.py
│   │   
│   ├── quiz/                       # Quiz app (quiz game & leaderboard)
│   │   ├── serializers/
│   │   │   ├── __init__.py
│   │   │   ├── leaderboard.py
│   │   │   ├── lesson.py
│   │   │   ├── question.py
│   │   │   ├── quiz.py
│   │   │   └── subject.py
│   │   │   
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Import common dependencies for views
│   │   │   ├── leaderboard.py      # Leaderboard views logics
│   │   │   ├── lesson.py           # Lesson CRUD
│   │   │   ├── question.py         # Question CRUD
│   │   │   ├── quiz.py             # Quiz game logics
│   │   │   └── subject.py          # Subject CRUD
│   │   │   
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── paginators.py           # Custom paginator classes
│   │   ├── permissions.py          # Custom permission classes
│   │   ├── signals.py              # Model-level validation & business rules
│   │   ├── tests.py
│   │   └── urls.py
│   │   
│   └── __init__.py
│   
├── config/                         # Project configs
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                 # Common settings
│   │   ├── development.py          # Dev-env specific settings
│   │   ├── production.py           # Prod-env specific settings
│   │   └── test.py                 # Test-env specific settings
│   │   
│   ├── __init__.py
│   ├── asgi.py
│   ├── urls.py                     # Main URL routing
│   └── wsgi.py
│   
├── logs/                           # Logs for debugging
│   └── dev.log                     # 'prod.log' for production logging
│   
├── requirements/                   # Project dependencies
│   ├── base.txt                    # Common dependencies
│   ├── dev.txt                     # Dev-env specific dependencies
│   ├── prod.txt                    # Prod-env specific dependencies
│   └── test.txt                    # Test-env specific dependencies
│   
├── scripts/                        # Utility scripts
│   ├── __init__.py
│   └── generate_secret_key.py      # Django secret key generator
│   
├── tests/
│   ├── authentication/             # Authentication app tests
│   │   ├── test_models/            # Models tests
│   │   ├── test_serializers/       # Serializers tests
│   │   ├── test_views/             # Views tests
│   │   └── __init__.py
│   │   
│   └── quiz/                       # Quiz app tests
│   │   ├── test_models/            # Models tests
│   │   ├── test_serializers/       # Serializers tests
│   │   ├── test_views/             # Views tests
│   │   └── __init__.py
│   │   
│   ├── __init__.py
│   └── conftest.py                 # Pytest configuration and fixtures
│   
├── utils/
│   ├── __init__.py
│   └── throttles.py                # Global rate-limiting utils
│   
├── .env                            # Environment variables for dev-env & test-env (not in git)
├── .gitignore                    
├── demo.env                        # Example environment variables
├── manage.py                     
├── pytest.ini                      # Pytest configuration
└── README.md                       # Project documentation
```

### Key Features of the Structure

- **Django Best Practices**:

   - Modular app-based architecture
   - Clear separation of concerns
   - Environment-specific settings management
   - Secure configuration handling with environment variables

- **API Design Standards**:

   - RESTful endpoint structure
   - Consistent URL routing patterns
   - Proper HTTP method handling
   - Standardized response formats

- **Security & Performance**:

   - JWT-based authentication
   - Rate limiting and throttling
   - Caching mechanisms
   - Input validation and sanitization

- **Testing & Quality**:

   - Comprehensive test coverage
   - Isolated test environments
   - Automated test suite
   - Shared test fixtures

#

# Terms of Service

### User Registration
- Usernames are unique, can't be updated or deleted yet. Be sure to select one
- Registration is limited to 5 attempts per minute per IP address
- Users are responsible for maintaining the confidentiality of their account credentials
- The API reserves the right to suspend or terminate accounts that violate any term

### User Authentication
- Users must authenticate using JWT (JSON Web Token) authentication for core experience
- Access tokens expire after 30 minutes and must be refreshed
- Refresh tokens are valid for 7 days and are blacklisted after use
- Login attempts are limited to 5 per minute per IP address
- Logout invalidates the current refresh token
- Users are responsible for all activities performed under their authenticated sessions
- The API reserves the right to revoke access tokens for security violations

### Quiz Game
- Each quiz attempt consists of up to 15 randomly selected questions
- Quiz answers cannot be modified after submission
- Each quiz attempt can only be submitted once
- The API reserves the right to invalidate quiz attempts that violate fair play rules
- Users must not attempt to manipulate quiz scores or bypass security measures

### Player Stats
- Player statistics are calculated based on actual quiz performance
- Stats include total games played, highest score, and average score
- Statistics are updated in real-time after quiz completion
- Historical performance data is retained for leaderboard purposes
- Users can view their own statistics but cannot modify them
- The API reserves the right to adjust statistics for fair play violations

### Leaderboard
- Leaderboard rankings are based on verified quiz scores
- Subject-specific leaderboards show top 10 players per subject
- Global leaderboard displays top 25 players across all subjects
- Leaderboard data is cached for performance optimization
- Rankings are updated automatically after each quiz completion (mostly after 1 minute, when cache gets timed out)
- The API reserves the right to remove users from leaderboards for violations
- Historical leaderboard data may be archived after specified periods

### General Terms
- The API reserves the right to modify these terms at any time
- Continued use of the service constitutes acceptance of updated terms
- Violation of these terms may result in account suspension or termination
- Rate limiting applies to all API endpoints based on user type and endpoint
- All API list responses are paginated with view-specific limits
- The API implements caching mechanisms for all paginated list responses

#

#### **Upcoming version 1.0.1 features**:
- Redis for caching
- Check for available Lessons within Subjects having valid number of questions (min-15) to play quiz
- Add detailed docs in README.md on how to use the full API step by step
