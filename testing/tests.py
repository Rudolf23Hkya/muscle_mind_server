from django.test import TestCase

import datetime
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock,Mock
from django.contrib.auth.models import User
from testing.models import *
from testing.views import *
from testing.data_processors import *
'''
Django's TestCase class provides an isolated test environment 
where each test is run inside a transaction, and the database is rolled back at the end of each test. 
This means that any data created during a test is not retained after the test completes.
'''

class FindPreviousMondayTest(TestCase):

    def test_find_previous_monday_on_monday(self):
        date_obj = datetime.date(2024, 5, 27)  # This is a Monday
        result = find_previous_monday(date_obj)
        self.assertEqual(result, date_obj)

    def test_find_previous_monday_on_tuesday(self):
        date_obj = datetime.date(2024, 5, 28)  # This is a Tuesday
        expected_date = datetime.date(2024, 5, 27)  # The previous Monday
        result = find_previous_monday(date_obj)
        self.assertEqual(result, expected_date)

    def test_find_previous_monday_on_sunday(self):
        date_obj = datetime.date(2024, 6, 2)  # This is a Sunday
        expected_date = datetime.date(2024, 5, 27)  # The previous Monday
        result = find_previous_monday(date_obj)
        self.assertEqual(result, expected_date)

    def test_find_previous_monday_on_wednesday(self):
        date_obj = datetime.date(2024, 5, 29)  # This is a Wednesday
        expected_date = datetime.date(2024, 5, 27)  # The previous Monday
        result = find_previous_monday(date_obj)
        self.assertEqual(result, expected_date)

class InterpolationTestCase(TestCase):
    def test_interpolate_age_within_range(self):
        self.assertAlmostEqual(interpolate_age(20), 0.5)
        self.assertAlmostEqual(interpolate_age(12), -0.5)
        self.assertAlmostEqual(interpolate_age(120), -0.5)

    def test_interpolate_age_out_of_range(self):
        with self.assertRaises(ValueError):
            interpolate_age(10)
        with self.assertRaises(ValueError):
            interpolate_age(130)

    def test_interpolate_bmi_positive_within_range(self):
        self.assertAlmostEqual(interpolate_bmi(10), -0.5)
        self.assertAlmostEqual(interpolate_bmi(18), 0.5)
        self.assertAlmostEqual(interpolate_bmi(24), 0.5)
        self.assertAlmostEqual(interpolate_bmi(40), -0.5)

    def test_interpolate_bmi_extremely_large_or_small(self):
        self.assertEqual(interpolate_bmi(4), -0.6)
        self.assertEqual(interpolate_bmi(46), -0.6)

    def test_interpolate_bmi_non_positive(self):
        with self.assertRaises(ValueError):
            interpolate_bmi(0)
        with self.assertRaises(ValueError):
            interpolate_bmi(-5)

class CalculateWeightTestCase(TestCase):

    @patch('testing.data_processors.ExperienceLevel.get_num')
    @patch('testing.data_processors.interpolate_age')
    @patch('testing.data_processors.interpolate_bmi')
    def test_calculate_weight_normalization(self, mock_interpolate_bmi, mock_interpolate_age, mock_get_num):
        # Mocking the dependencies
        mock_get_num.side_effect = lambda x: {'NEW': 0, 'INTERMEDIATE': 1, 'EXPERIENCED': 2, 'PROFESSIONAL': 3}[x.value]
        mock_interpolate_age.return_value = 0.1
        mock_interpolate_bmi.return_value = 0.1

        # Test cases
        result = calculate_weight('NEW', 25, 22, 'INTERMEDIATE')
        self.assertEqual(result, 0.85)
        
        result = calculate_weight('INTERMEDIATE', 25, 22, 'NEW')
        self.assertEqual(result, 0.55)

        result = calculate_weight('PROFESSIONAL', 70, 18, 'NEW')
        self.assertEqual(result, 0.3)

        result = calculate_weight('NEW', 30, 40, 'PROFESSIONAL')
        self.assertEqual(result, 1.1)

    @patch('testing.data_processors.ExperienceLevel.get_num')
    @patch('testing.data_processors.interpolate_age')
    @patch('testing.data_processors.interpolate_bmi')
    def test_calculate_weight_edge_cases(self, mock_interpolate_bmi, mock_interpolate_age, mock_get_num):
        # Mocking the dependencies
        mock_get_num.side_effect = lambda x: {'NEW': 0, 'INTERMEDIATE': 1, 'EXPERIENCED': 2, 'PROFESSIONAL': 3}[x.value]
        mock_interpolate_age.return_value = -0.5
        mock_interpolate_bmi.return_value = -0.5

        # Test cases for edge scenarios
        result = calculate_weight('NEW', 10, 5, 'PROFESSIONAL')
        self.assertEqual(result, 0.1)

        result = calculate_weight('PROFESSIONAL', 100, 45, 'NEW')
        self.assertEqual(result, 0.1)

        result = calculate_weight('NEW', 25, 22, 'INTERMEDIATE')
        self.assertEqual(result, 0.1)

    @patch('testing.data_processors.ExperienceLevel.get_num')
    @patch('testing.data_processors.interpolate_age')
    @patch('testing.data_processors.interpolate_bmi')
    def test_calculate_weight_exact_match(self, mock_interpolate_bmi, mock_interpolate_age, mock_get_num):
        # Mocking the dependencies
        mock_get_num.side_effect = lambda x: {'NEW': 0, 'INTERMEDIATE': 1, 'EXPERIENCED': 2, 'PROFESSIONAL': 3}[x.value]
        mock_interpolate_age.return_value = 0.0
        mock_interpolate_bmi.return_value = 0.0

        # Test case for exact match
        result = calculate_weight('INTERMEDIATE', 25, 22, 'INTERMEDIATE')
        self.assertEqual(result, 0.5)
        

class GetBest3WorkoutTest(TestCase):

    @patch('testing.data_processors.Workout')
    @patch('testing.data_processors.Disease')
    @patch('testing.data_processors.UserProfile')
    def test_get_best_3_workout(self, mock_user_profile, mock_disease, mock_workout):
        user_id = 1
        weightlifting = True
        trx = True

        # Mock user profile
        mock_user_profile_obj = Mock()
        mock_user_profile_obj.experiencelevel = ExperienceLevel.NEW.value
        mock_user_profile.objects.get.return_value = mock_user_profile_obj
        
        # Mock disease profile
        mock_disease_obj = Mock()
        mock_disease_obj.bad_knee = False
        mock_disease_obj.cardiovascular_d = False
        mock_disease_obj.asthma = False
        mock_disease_obj.osteoporosis = False
        mock_disease.objects.get.return_value = mock_disease_obj

        # Mock workouts
        mock_workout_1 = Mock()
        mock_workout_2 = Mock()
        mock_workout_3 = Mock()
        mock_workout_4 = Mock()
        mock_workout_5 = Mock()
        mock_workout_6 = Mock()

        mock_workout_queryset = MagicMock()
        mock_workout.objects.all.return_value = mock_workout_queryset
        mock_workout_queryset.exclude.return_value = mock_workout_queryset
        mock_workout_queryset.filter.return_value = mock_workout_queryset
        mock_workout_queryset.order_by.return_value = [mock_workout_1, mock_workout_2, mock_workout_3,mock_workout_4,mock_workout_5,mock_workout_6]
        mock_workout_queryset.count.return_value = 6

        from testing.data_processors import get_best_3_workout

        # Call the function
        result = get_best_3_workout(user_id, weightlifting, trx)
        
        # Assert the result
        self.assertEqual(len(result), 3)
        self.assertIsInstance(result, list)
        self.assertIn(mock_workout_1, result)
        self.assertIn(mock_workout_2, result)
        self.assertIn(mock_workout_3, result)