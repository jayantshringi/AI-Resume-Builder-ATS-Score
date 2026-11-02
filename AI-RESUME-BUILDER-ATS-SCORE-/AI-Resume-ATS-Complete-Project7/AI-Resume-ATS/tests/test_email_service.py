import os
from unittest.mock import MagicMock, patch
from backend.email_service import send_contact_notification

@patch("backend.email_service.load_dotenv")
def test_missing_settings(mock_dotenv, monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "")
    ok, msg = send_contact_notification("John", "john@example.com", "Feedback", "Hello", "My msg", "admin@example.com", "support@example.com")
    assert not ok
    assert "missing" in msg.lower()

@patch("backend.email_service.load_dotenv")
@patch("smtplib.SMTP")
def test_routing_suggestion_and_technical(mock_smtp, mock_dotenv, monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.test.com")
    monkeypatch.setenv("SMTP_USERNAME", "sender@test.com")
    monkeypatch.setenv("SMTP_PASSWORD", "secret")
    monkeypatch.setenv("MAIL_FROM", "sender@test.com")

    # Suggestion
    send_contact_notification("Alice", "alice@example.com", "Suggestion", "Idea", "Text", "mohitki7780264@gmail.com", "adityasing9508@gmail.com")
    server_instance = mock_smtp.return_value.__enter__.return_value
    sent_msg = server_instance.send_message.call_args[0][0]
    assert sent_msg["To"] == "mohitki7780264@gmail.com"
    assert sent_msg["Cc"] == "adityasing9508@gmail.com"

    # Technical Issues
    send_contact_notification("Alice", "alice@example.com", "Technical Issues", "Bug", "Text", "mohitki7780264@gmail.com", "adityasing9508@gmail.com")
    sent_msg = server_instance.send_message.call_args[0][0]
    assert sent_msg["To"] == "mohitki7780264@gmail.com"
    assert sent_msg["Cc"] == "adityasing9508@gmail.com"

@patch("backend.email_service.load_dotenv")
@patch("smtplib.SMTP")
def test_routing_complaint_and_general(mock_smtp, mock_dotenv, monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.test.com")
    monkeypatch.setenv("SMTP_USERNAME", "sender@test.com")
    monkeypatch.setenv("SMTP_PASSWORD", "secret")
    monkeypatch.setenv("MAIL_FROM", "sender@test.com")

    # Complaint
    send_contact_notification("Bob", "bob@example.com", "Complaint", "Issue", "Text", "mohitki7780264@gmail.com", "adityasing9508@gmail.com")
    server_instance = mock_smtp.return_value.__enter__.return_value
    sent_msg = server_instance.send_message.call_args[0][0]
    assert sent_msg["To"] == "adityasing9508@gmail.com"
    assert sent_msg["Cc"] == "mohitki7780264@gmail.com"

    # General Query
    send_contact_notification("Bob", "bob@example.com", "General Query", "Question", "Text", "mohitki7780264@gmail.com", "adityasing9508@gmail.com")
    sent_msg = server_instance.send_message.call_args[0][0]
    assert sent_msg["To"] == "adityasing9508@gmail.com"
    assert sent_msg["Cc"] == "mohitki7780264@gmail.com"
