import imaplib2
import email
from email.header import decode_header
from email_class import EmailInfo
from langchain_core.tools import tool
from langchain_core.output_parsers import JsonOutputParser
from typing import Dict, List
from langchain_ollama import ChatOllama
import json
from state import AgentState
from langchain_core.messages import SystemMessage, HumanMessage
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

llm = ChatOllama(model="deepseek-llm:7b", temperature=0)
parser = JsonOutputParser(pydantic_object=EmailInfo)

def fetch_email() -> Dict:
    print("1st Node running:")
    try:
        imap = imaplib2.IMAP4_SSL("imap.gmail.com")
        EMAIL = "sgimodeltest@gmail.com"
        PASSWORD = "royh kilc adkx uymi"

        imap.login(EMAIL, PASSWORD)
        imap.select('"INBOX"')

        status, bi_msgs_num = imap.search(None, "SEEN")
        msgs = bi_msgs_num[0].decode().split()

        for num in msgs:
            _, msg = imap.fetch(num, "(RFC822)")
            message = email.message_from_bytes(msg[0][1])

            # Decode sender
            sender = message.get("From")

            # Decode subject
            subject, encoding = decode_header(message.get("Subject"))[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8")

            # Extract plain text body
            body = ""
            if message.is_multipart():
                for part in message.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        try:
                            body = part.get_payload(decode=True).decode()
                            break
                        except:
                            body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
            else:
                body = message.get_payload(decode=True).decode()

            email_info = EmailInfo(sender=sender, subject=subject, body=body.strip())
            imap.logout()
            print("1st Node Finished working:")
            return email_info.model_dump()
    except Exception as e:
        return {"error": str(e)}

@tool
def fetch_email_tool() -> Dict:
    """Fetch the latest unread emails from the Gmail inbox."""
    return fetch_email()


def extract_email_info(email: Dict) -> Dict:
    print("2nd Node running:")
    try:
        # Extract sender's email from header separately
        sender_header = email.get('sender', '')
        senders_email = extract_email_from_header(sender_header)
        
        # Process body content with LLM
        prompt = f"""
You are an information extraction system.

Analyze the following email BODY and extract:
- nic (National Identity Card number)
- contact_number
- client_name
- address

Rules:
1. Search ONLY in the email body below
2. If value not found, return null
3. Respond ONLY with valid JSON matching this schema:
{{
  "nic": "<string or null>",
  "contact_number": "<string or null>",
  "client_name": "<string or null>",
  "address": "<string or null>"
}}

Email Body:
{email.get('body', '')}
        """

        result = llm.invoke(prompt)
        extracted = parser.parse(result.content)
        
        # Add senders_email from header extraction
        extracted["senders_email"] = senders_email

        # print("Extracted data:", extracted)
        print("2nd Node Finished working:")
        return extracted

    except Exception as e:
        return {"error": f"Extraction failed: {str(e)}"}

# Helper function to extract email from header
def extract_email_from_header(header: str) -> str | None:
    """Extracts email address from 'Name <email@domain.com>' format"""
    import re
    match = re.search(r'<([^>]+)>', header)
    return match.group(1) if match else None

@tool
def extract_email_info_tool(raw_email: Dict) -> Dict:
    """Extracts senders_email, NIC, contact_number, client_name, and address from the email."""
    return extract_email_info(email=raw_email)

def check_all_info(state: Dict) -> List:
    missing_info = []
    if state["nic"] == '<null>' or state["nic"] is None:
        missing_info.append("nic")
    if state["client_name"] == '<null>' or state["client_name"] is None:
        missing_info.append("client_name")
    if state["contact_number"] == '<null>' or state["contact_number"] is None:
        missing_info.append("contact_number")
    if state["address"] == '<null>' or state["address"] is None:
        missing_info.append("address")

    return missing_info


def enquire_info(state: Dict) -> Dict:
    print("3rd Node running:")
    # Configuration
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587  # For TLS
    SENDER_EMAIL = "sgimodeltest@gmail.com"
    SENDER_PASSWORD = "royh kilc adkx uymi"
    RECIPIENT_EMAIL = state["senders_email"]

    missing_info = check_all_info(state=state)

    if not missing_info:
        # Create the email
        msg = MIMEMultipart()
        msg["Subject"] = "Information Read!"
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        body = "Your request for registering as a client is read."
        msg.attach(MIMEText(body, "plain"))
    else:
        # Create the email
        msg = MIMEMultipart()
        msg["Subject"] = "Enquiring Information"
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        body = f"Please send the following Information {missing_info}"
        msg.attach(MIMEText(body, "plain"))

    # Send the email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Enable TLS encryption
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        print("Email sent successfully!")
        print("3rd Node Finished working:")

        return {"email_sent": True}
    except Exception as e:  
        return {"error": e}      


@tool
def enquire_info_tool(data: Dict) -> bool:
    """sends email to the client for enquiring the missing information"""
    return enquire_info(state=data)
