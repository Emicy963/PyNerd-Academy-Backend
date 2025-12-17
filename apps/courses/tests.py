from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework import status
from apps.courses.models import Course, Module, Lesson, Enrollment, Progress, Quiz
from apps.accounts.models import Certificate

User = get_user_model()


class CourseModelTests(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            username="instructor",
            email="instructor@example.com",
            password="pass",
            role="INSTRUCTOR",
            is_approved=True,
            is_active=True,
        )
        self.student = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="pass",
            role="STUDENT",
            is_active=True,
        )
        self.course = Course.objects.create(
            title="Python Basic",
            description="Intro",
            instructor=self.instructor,
            is_published=True,
            duration=60,
            slug="python-basic",
        )
        self.module = Module.objects.create(
            course=self.course, title="Intro Module", order=1
        )

    def test_course_str(self):
        """Test Course string representation"""
        self.assertEqual(str(self.course), "Python Basic")

    def test_module_str(self):
        """Test Module string representation"""
        self.assertEqual(str(self.module), "Python Basic - Intro Module")

    def test_lesson_creation_and_str(self):
        """Test Lesson creation, string representation and valid url"""
        lesson = Lesson.objects.create(
            module=self.module,
            title="First Lesson",
            video_url="https://youtube.com/watch?v=123",
            duration_seconds=120,
        )
        self.assertEqual(str(lesson), "First Lesson")

    def test_lesson_invalid_video_url(self):
        """Test validation for invalid video domains"""
        lesson = Lesson(
            module=self.module,
            title="Bad Lesson",
            video_url="https://badsite.com/video",
            duration_seconds=100,
        )
        with self.assertRaises(ValidationError):
            lesson.clean()

    def test_course_clean_instructor_check(self):
        """Test that only instructors can be assigned to courses"""
        course = Course(
            title="Hacker Course",
            description="...",
            instructor=self.student,  # Invalid role
            duration=10,
        )
        with self.assertRaises(ValidationError):
            course.clean()

    def test_enrollment_str(self):
        """Test Enrollment string representation"""
        enrollment = Enrollment.objects.create(student=self.student, course=self.course)
        self.assertEqual(
            str(enrollment), f"{self.student.email} enrolled in {self.course.title}"
        )

    def test_progress_clean_requires_enrollment(self):
        """Test that progress cannot be created without enrollment"""
        lesson = Lesson.objects.create(
            module=self.module,
            title="Lesson",
            video_url="https://youtube.com/123",
            duration_seconds=10,
        )
        progress = Progress(student=self.student, lesson=lesson)

        # Should fail as student is not enrolled
        with self.assertRaises(ValidationError):
            progress.clean()


class CourseAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create Verify Users
        self.instructor = User.objects.create_user(
            username="instructor",
            email="instructor@example.com",
            password="pass",
            role="INSTRUCTOR",
            is_approved=True,
            is_active=True,
        )
        self.student = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="pass",
            role="STUDENT",
            is_active=True,
        )

        # Create Course Data
        self.course = Course.objects.create(
            title="Python 101",
            description="Intro to Python",
            instructor=self.instructor,
            is_published=True,
            price=0,
            duration=100,
            slug="python-101",
        )
        self.module = Module.objects.create(course=self.course, title="Basics", order=1)
        self.lesson = Lesson.objects.create(
            module=self.module,
            title="Hello World",
            video_url="https://youtube.com/watch?v=123",
            duration_seconds=600,
        )

    def test_list_courses_public(self):
        """Everyone should be able to list courses"""
        url = "/api/courses/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_course_instructor(self):
        """Instructors can create courses"""
        self.client.force_authenticate(user=self.instructor)
        data = {
            "title": "Advanced Python",
            "description": "Deep dive",
            "price": 100,
            "level": "intermediate",
            "category": "Programming",
            "duration": 120,
            "slug": "adv-python",
        }
        url = "/api/courses/"
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)

    def test_create_course_student_forbidden(self):
        """Students cannot create courses"""
        self.client.force_authenticate(user=self.student)
        data = {"title": "Hacker Course"}
        url = "/api/courses/"
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_enroll_course(self):
        """Student can enroll in a course"""
        self.client.force_authenticate(user=self.student)
        url = f"/api/courses/{self.course.id}/enroll/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Enrollment.objects.filter(student=self.student, course=self.course).exists()
        )

    def test_update_progress(self):
        """Student can update progress"""
        # Enroll first
        Enrollment.objects.create(student=self.student, course=self.course)
        # Create progress object manually
        progress = Progress.objects.create(student=self.student, lesson=self.lesson)

        self.client.force_authenticate(user=self.student)
        url = f"/api/progress/{progress.id}/"
        data = {"is_completed": True}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        progress.refresh_from_db()
        self.assertTrue(progress.is_completed)

    def test_list_quizzes(self):
        """Student can list quizzes for a lesson"""
        # Create Quiz
        quiz = Quiz.objects.create(lesson=self.lesson, time_limit=300, passing_score=70)

        self.client.force_authenticate(user=self.student)
        url = f"/api/quizzes/?lesson_id={self.lesson.id}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], quiz.id)

    def test_certificate_generation(self):
        """Certificate is generated when course is completed"""
        Enrollment.objects.create(student=self.student, course=self.course)
        # Create progress and mark complete
        progress = Progress.objects.create(student=self.student, lesson=self.lesson)

        self.client.force_authenticate(user=self.student)
        url = f"/api/progress/{progress.id}/"
        data = {"is_completed": True}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check certificate
        self.assertTrue(
            Certificate.objects.filter(
                student=self.student, course=self.course
            ).exists()
        )
