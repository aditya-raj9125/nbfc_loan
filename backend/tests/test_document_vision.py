"""
Document Processing & Vision Service Tests
Validates:
- PDF rendering and base64 payload generation via PyMuPDF
- Markdown-wrapped JSON response cleaning and resilience
- Document extraction handlers for Salary Slip, PAN, and Aadhaar
"""
import pytest
import os
from app.services.ocr_service import ocr_service, _file_to_payload, _clean_json_response
from tests.mock_documents import (
    create_mock_salary_slip,
    create_mock_pan_card,
    create_mock_aadhaar_card
)


@pytest.fixture(scope="module")
def mock_files():
    slip_path = create_mock_salary_slip("test_vision_salary.pdf", monthly_salary=95000.0)
    pan_path = create_mock_pan_card("test_vision_pan.pdf", pan="XYZPK9876Q")
    aadhaar_path = create_mock_aadhaar_card("test_vision_aadhaar.pdf", aadhaar="1234 5678 9012")
    return {
        "salary": slip_path,
        "pan": pan_path,
        "aadhaar": aadhaar_path
    }


class TestDocumentVisionService:
    """Tests document ingestion and OCR service pipelines"""

    def test_file_to_payload_valid_pdf(self, mock_files):
        """PyMuPDF should extract base64 PNG rendering and digital text"""
        payload = _file_to_payload(mock_files["salary"])
        assert payload is not None
        b64_str, mime_type, text_content = payload
        assert len(b64_str) > 500, "Base64 image string too short"
        assert mime_type == "image/png"
        assert text_content is not None
        assert "PAYSLIP" in text_content.upper() or "SALARY" in text_content.upper()

    def test_file_to_payload_non_existent_file(self):
        """Non-existent file must safely return None without throwing"""
        payload = _file_to_payload("non_existent_path_12345.pdf")
        assert payload is None

    def test_clean_json_response_clean_format(self):
        """Standard clean JSON string parsing"""
        raw = '{"name": "Rahul Sharma", "monthly_salary": 85000.0}'
        parsed = _clean_json_response(raw)
        assert parsed is not None
        assert parsed.get("name") == "Rahul Sharma"
        assert parsed.get("monthly_salary") == 85000.0

    def test_clean_json_response_markdown_code_fences(self):
        """JSON enclosed inside ```json ... ``` code blocks"""
        raw = """```json
{
  "document_type": "salary_slip",
  "monthly_salary": 75000
}
```"""
        parsed = _clean_json_response(raw)
        assert parsed is not None
        assert parsed.get("document_type") == "salary_slip"
        assert parsed.get("monthly_salary") == 75000

    def test_clean_json_response_embedded_in_prose(self):
        """JSON surrounded by model conversational text"""
        raw = "Certainly! Here are the extracted fields from the document:\n{\"pan_number\": \"ABCDE1234F\"}\nPlease let me know if you need more info."
        parsed = _clean_json_response(raw)
        assert parsed is not None
        assert parsed.get("pan_number") == "ABCDE1234F"

    def test_clean_json_response_malformed(self):
        """Malformed non-JSON string should safely return None"""
        raw = "This is not json at all."
        parsed = _clean_json_response(raw)
        assert parsed is None

    @pytest.mark.asyncio
    async def test_extract_salary_slip(self, mock_files):
        """Extract salary slip details from synthetic PDF"""
        result = await ocr_service.extract_salary_slip(mock_files["salary"])
        assert result.get("success") is True
        assert result.get("monthly_salary") is not None
        assert result["monthly_salary"] > 0

    @pytest.mark.asyncio
    async def test_extract_pan(self, mock_files):
        """Extract PAN card details from synthetic PDF"""
        result = await ocr_service.extract_pan(mock_files["pan"])
        assert result.get("success") is True
        assert result.get("pan_number") is not None

    @pytest.mark.asyncio
    async def test_extract_aadhaar(self, mock_files):
        """Extract Aadhaar details from synthetic PDF"""
        result = await ocr_service.extract_aadhaar(mock_files["aadhaar"])
        assert result.get("success") is True
        assert result.get("aadhaar_number") is not None
