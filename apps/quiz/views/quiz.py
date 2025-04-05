import random

from django.db import transaction

from .base import *
from ..models import Lesson, Question, QuizAttempt
from ..serializers import (
    QuizStartResponseSerializer,
    QuestionResponseSerializer,
    QuizSubmitSerializer,
    QuizSubmitResponseSerializer,
)


class QuizStartView(APIView):
    permission_classes = [IsAuthenticated]

    # Start a new quiz with randomized questions for a lesson
    @swagger_auto_schema(
        tags=["Quiz-Game"],
        operation_id="quiz_game_start",
        operation_description=(
            "Start a new quiz with up to 15 randomized questions for a lesson"
        ),
        manual_parameters=[
            openapi.Parameter(
                'lesson_id',
                openapi.IN_PATH,
                description="ID of the lesson to start quiz for",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                'Success: Ok',
                QuizStartResponseSerializer
            ),
            400: 'Error: Bad request',
            401: 'Error: Unauthorized',
            404: 'Error: Not found',
            429: 'Error: Too many requests',
            500: 'Error: Internal server error'
        }
    )
    def post(self, request, lesson_id):
        try:
            lesson = Lesson.objects.get(id=lesson_id)

            # Get a list of question IDs for the lesson
            question_ids = list(
                lesson.questions.values_list('id', flat=True)
            )
            
            # Select random IDs (up to 15)
            selected_ids = random.sample(
                question_ids, 
                min(len(question_ids), 15)
            )
            
            # Fetch only the selected questions
            questions = lesson.questions.filter(id__in=selected_ids)
            
            # Create a new quiz attempt
            attempt = QuizAttempt.objects.create(
                user=request.user,
                lesson=lesson,
                score=0
            )
            
            return Response(
                {
                    'attempt_id': attempt.id,
                    'questions': QuestionResponseSerializer(questions, many=True).data
                },
                status=status.HTTP_200_OK
            )
        
        except Lesson.DoesNotExist:
            return Response(
                {"detail": "Lesson not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            # Log the error for debugging
            logger.error(
                f"Error in QuizStartView.post(): {str(e)}",
                exc_info=True
            )

            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QuizSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    # Submit quiz answers, calculate score & update user profile
    @swagger_auto_schema(
        tags=["Quiz-Game"],
        operation_id="quiz_game_submit_answer",
        operation_description=(
            "Submit quiz answers & get score "
            "(get attempt_id by starting a quiz)"
        ),
        manual_parameters=[
            openapi.Parameter(
                'attempt_id',
                openapi.IN_PATH,
                description="ID of the quiz attempt to submit answers for",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'answers': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    additional_properties=openapi.Schema(type=openapi.TYPE_STRING),
                    description='Dictionary of "question_id": "selected_option"'
                )
            },
            required=['answers'],
            example={
                "answers": {
                    "101": "1",
                    "102": "3",
                    "103": "2"
                }
            }
        ),
        responses={
            200: openapi.Response(
                'Success: Ok',
                QuizSubmitResponseSerializer
            ),
            400: 'Error: Bad request',
            401: 'Error: Unauthorized',
            404: 'Error: Not found',
            429: 'Error: Too many requests',
            500: 'Error: Internal server error'
        }
    )
    @transaction.atomic
    def post(self, request, attempt_id):
        try:
            attempt = QuizAttempt.objects.select_for_update().get(
                id=attempt_id,
                user=request.user
            )
            # Return detailed message if quiz is already completed
            if attempt.completed == True:
                return Response(
                    {"detail": "Quiz already completed."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Proceed to data validation
            serializer = QuizSubmitSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            answers = serializer.validated_data['answers']  # {"question_id": "selected_option"}
            questions = Question.objects.filter(
                id__in=answers.keys()
            ).values('id', 'correct_answer')
            
            score = 0
            for question in questions:
                user_answer = int(answers[str(question['id'])])
                if user_answer == question['correct_answer']:
                    score += 1
            
            attempt.score = score
            attempt.completed = True
            attempt.save()
            
            # Update user profile
            user = request.user
            user.total_played += 1
            user.highest_score = max(user.highest_score, score)
            user.save()
            
            return Response(
                QuizSubmitResponseSerializer(attempt).data,
                status=status.HTTP_200_OK
            )
        
        except QuizAttempt.DoesNotExist:
            return Response(
                {"detail": "Quiz attempt not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            # Log the error for debugging
            logger.error(
                f"Error in QuizSubmitView.post(): {str(e)}",
                exc_info=True
            )  

            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
