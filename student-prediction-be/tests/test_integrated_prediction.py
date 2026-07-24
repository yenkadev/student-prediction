"""Kiểm thử tích hợp hai nguồn dữ liệu và hai loại giải pháp."""

import asyncio
import unittest
from pathlib import Path

import pandas as pd
import httpx

from app.main import app
from app.services import risk_service


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SPLIT_DIR = PROJECT_ROOT / "outputs" / "splits"


class TestIntegratedPrediction(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.frames = {
            source: pd.read_csv(SPLIT_DIR / f"{source}_test.csv")
            for source in risk_service.DATA_SOURCES
        }

    async def asyncSetUp(self):
        # ML đầu tiên cần nạp model nên tăng ngưỡng cảnh báo tác vụ chậm của unittest.
        asyncio.get_running_loop().slow_callback_duration = 2.0
        transport = httpx.ASGITransport(app=app)
        self.client = httpx.AsyncClient(transport=transport, base_url="http://testserver")

    async def asyncTearDown(self):
        await self.client.aclose()

    def _features(self, source: str, solution: str, row_index: int = 0) -> dict:
        """Lấy đúng các trường bắt buộc từ một dòng test có sẵn."""
        row = self.frames[source].iloc[row_index]
        return {
            field: (None if pd.isna(row[field]) else row[field].item() if hasattr(row[field], "item") else row[field])
            for field in risk_service.required_fields(source, solution)
        }

    def _assert_contract(self, result: dict, source: str, solution: str) -> None:
        """Kiểm tra contract chuẩn và các trường tương thích frontend."""
        required = {
            "dataSource", "solutionType", "prediction", "riskScore", "riskLevel",
            "riskFactors", "recommendations", "scoreType", "statusLabel", "riskProb",
            "factors", "recommendation",
        }
        self.assertTrue(required.issubset(result))
        self.assertEqual(result["dataSource"], source)
        self.assertEqual(result["solutionType"], solution)
        self.assertIn(result["prediction"], {"Dropout", "No Dropout"})
        self.assertGreaterEqual(result["riskScore"], 0)
        self.assertLessEqual(result["riskScore"], 1)
        self.assertEqual(result["riskScore"], result["riskProb"])
        self.assertEqual(result["riskFactors"], result["factors"])
        self.assertGreater(len(result["recommendations"]), 0)

    async def test_single_prediction_for_all_four_combinations(self):
        """API một sinh viên phải chạy đủ hai nguồn nhân hai giải pháp."""
        for source in risk_service.DATA_SOURCES:
            for solution in risk_service.PREDICTION_TYPES:
                with self.subTest(source=source, solution=solution):
                    response = await self.client.post(
                        "/predict/single",
                        json={
                            "dataSource": source,
                            "predictionType": solution,
                            "features": self._features(source, solution),
                        },
                    )
                    self.assertEqual(response.status_code, 200, response.text)
                    self._assert_contract(response.json(), source, solution)

    async def test_sync_batch_for_all_four_combinations(self):
        """Upload đồng bộ phải trả đủ kết quả mà không cần MongoDB."""
        for source in risk_service.DATA_SOURCES:
            csv_bytes = self.frames[source].head(2).to_csv(index=False).encode("utf-8")
            for solution in risk_service.PREDICTION_TYPES:
                with self.subTest(source=source, solution=solution):
                    response = await self.client.post(
                        "/predict/batch/sync",
                        data={"dataSource": source, "predictionType": solution},
                        files={"file": (f"{source}.csv", csv_bytes, "text/csv")},
                    )
                    self.assertEqual(response.status_code, 200, response.text)
                    results = response.json()["results"]
                    self.assertEqual(len(results), 2)
                    for student in results:
                        self._assert_contract(student["assessment"], source, solution)
                        self.assertIn("features", student)
                        self.assertTrue(student["assessed_at"])

    async def test_missing_fields_return_422(self):
        """API phải báo rõ lỗi schema thay vì âm thầm tạo dự đoán sai."""
        response = await self.client.post(
            "/predict/single",
            json={
                "dataSource": "student_dropout",
                "predictionType": "rule_based",
                "features": {"GPA": 2.0},
            },
        )
        self.assertEqual(response.status_code, 422)
        self.assertIn("Thiếu trường", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
