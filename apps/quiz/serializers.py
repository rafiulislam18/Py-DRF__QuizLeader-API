from rest_framework import serializers
from .models import Question, QuizAttempt, Subject, Lesson
from rest_framework.exceptions import ValidationError


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class SubjectPaginatedResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField(
        help_text="Total number of subjects"
    )
    next = serializers.CharField(
        help_text="URL for next page(null if no more pages)",
        allow_null=True
    )
    previous = serializers.CharField(
        help_text="URL for previous page (null if first page)",
        allow_null=True
    )
    results = SubjectSerializer(
        help_text="List of subjects",
        many=True
    )


class LessonSerializer(serializers.ModelSerializer):
    title = serializers.CharField(
        help_text="Title of the lesson",
        max_length=200
    )

    class Meta:
        model = Lesson
        fields = ['title']


class LessonResponseSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'subject']


class LessonPaginatedResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField(
        help_text="Total number of lessons"
    )
    next = serializers.CharField(
        help_text="URL for next page(null if no more pages)",
        allow_null=True
    )
    previous = serializers.CharField(
        help_text="URL for previous page (null if first page)",
        allow_null=True
    )
    results = LessonResponseSerializer(
        help_text="List of lessons",
        many=True
    )


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['text', 'options', 'correct_answer']

    def validate_options(self, value):
        # Ensure exactly 3 options with keys '1', '2', '3'
        if not (isinstance(value, dict) and len(value) == 3 and all(str(i) in value for i in range(1, 4))):
            raise serializers.ValidationError('Must provide exactly 3 options numbered 1-3. Example: {"1": "option1", "2": "option2", "3": "option3"}. Please check documentation for example.')
        
        # Ensure no empty options
        if any(not option.strip() for option in value.values()):
            raise serializers.ValidationError('Options cannot be empty. Please check documentation for example.')
        
        return value


class QuestionResponseSerializer(serializers.ModelSerializer):
    lesson = LessonResponseSerializer(read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'options', 'correct_answer', 'lesson']


class QuestionPaginatedResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField(
        help_text="Total number of questions"
    )
    next = serializers.CharField(
        help_text="URL for next page (null if no more pages)",
        allow_null=True
    )
    previous = serializers.CharField(
        help_text="URL for previous page (null if first page)",
        allow_null=True
    )
    results = QuestionResponseSerializer(
        help_text="List of questions",
        many=True
    )
    

class QuizStartResponseSerializer(serializers.Serializer):
    attempt_id = serializers.IntegerField(
        help_text="ID of the created quiz attempt"
    )
    questions = QuestionResponseSerializer(
        many=True,
        help_text="List of randomized questions for the quiz",
        read_only=True
    )


class QuizSubmitSerializer(serializers.Serializer):
    answers = serializers.DictField(
        child=serializers.CharField(),
        help_text='Dictionary of "question_id": "selected_option"'
    )

    def validate_answers(self, value):
        if len(value) == 0:
            raise ValidationError("Answers dictionary cannot be empty. Please check documentation for example.")
        
        # Check if payload format is correct
        for question_id, selected_option in value.items():
            if not question_id.isdigit() or not selected_option.isdigit():
                raise ValidationError("Invalid input format. Please check documentation for example.")
            # Check if selected option is valid (1, 2, or 3)
            if int(selected_option) not in [1, 2, 3]:
                raise ValidationError(f"Invalid option for question {question_id}. Must be 1, 2, or 3. Please check documentation for example.")
        
        # Check if all question IDs are valid
        valid_question_ids = set(str(q.id) for q in Question.objects.all())
        if not set(value.keys()).issubset(valid_question_ids):
            raise ValidationError("Invalid question IDs provided")
        
        return value


class QuizSubmitResponseSerializer(serializers.ModelSerializer):
    lesson = LessonResponseSerializer(read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = ['id', 'user', 'score', 'start_time', 'completed', 'lesson']
