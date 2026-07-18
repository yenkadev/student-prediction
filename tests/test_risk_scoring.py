import unittest

from src import calculate_risk


class TestRiskScoring(unittest.TestCase):

    def test_low_risk(self):
        student = {
            "GPA": 3.2,
            "Attendance_Rate": 90,
            "Stress_Index": 3,
            "Study_Hours_per_Day": 3,
            "Assignment_Delay_Days": 0,
            "Internet_Access": "Yes",
            "Part_Time_Job": "No",
        }

        result = calculate_risk(student)

        self.assertEqual(result["risk_score"], 0)
        self.assertEqual(result["risk_level"], "Thấp")

    def test_medium_risk(self):
        student = {
            "GPA": 2.3,
            "Attendance_Rate": 80,
            "Stress_Index": 5,
            "Study_Hours_per_Day": 3,
            "Assignment_Delay_Days": 0,
            "Internet_Access": "Yes",
            "Part_Time_Job": "No",
        }

        result = calculate_risk(student)

        self.assertEqual(result["risk_score"], 3)
        self.assertEqual(result["risk_level"], "Trung bình")

    def test_high_risk(self):
        student = {
            "GPA": 1.8,
            "Attendance_Rate": 70,
            "Stress_Index": 8,
            "Study_Hours_per_Day": 1,
            "Assignment_Delay_Days": 4,
            "Internet_Access": "No",
            "Part_Time_Job": "Yes",
        }

        result = calculate_risk(student)

        self.assertEqual(result["risk_score"], 11)
        self.assertEqual(result["risk_level"], "Cao")
        self.assertGreater(len(result["risk_reasons"]), 0)
        self.assertGreater(len(result["recommendations"]), 0)

    def test_missing_required_field(self):
        student = {
            "Attendance_Rate": 90,
            "Stress_Index": 3,
            "Study_Hours_per_Day": 3,
            "Assignment_Delay_Days": 0,
            "Internet_Access": "Yes",
            "Part_Time_Job": "No",
        }

        with self.assertRaisesRegex(ValueError, "GPA"):
            calculate_risk(student)


if __name__ == "__main__":
    unittest.main()