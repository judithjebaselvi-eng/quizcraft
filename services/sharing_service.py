import qrcode
from io import BytesIO
import base64
from urllib.parse import urlencode
import json

class SharingService:
    """Handle test sharing and QR code generation"""
    
    @staticmethod
    def generate_qr_code(url):
        """
        Generate QR code for test URL.
        Returns base64 encoded PNG.
        """
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            img_io = BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            img_base64 = base64.b64encode(img_io.getvalue()).decode()
            
            return f"data:image/png;base64,{img_base64}"
        except Exception as e:
            return None
    
    @staticmethod
    def get_whatsapp_share_url(test_name, test_url):
        """
        Generate WhatsApp sharing URL.
        """
        message = f"""You're invited to take this QuizCraft test.

Test: {test_name}

Start here: {test_url}"""
        
        params = {'text': message}
        return f"https://wa.me/?{urlencode(params)}"
    
    @staticmethod
    def get_email_share_url(test_name, test_url):
        """
        Generate email share URL.
        """
        subject = f"QuizCraft Test Invitation — {test_name}"
        body = f"""You're invited to take a QuizCraft test.

Test: {test_name}

Click the link below to start:
{test_url}

Best regards,
QuizCraft"""
        
        params = {
            'subject': subject,
            'body': body
        }
        return f"mailto:?{urlencode(params)}"
    
    @staticmethod
    def get_gmail_share_url(test_name, test_url):
        """
        Generate Gmail compose URL.
        """
        subject = f"QuizCraft Test Invitation — {test_name}"
        body = f"""You're invited to take a QuizCraft test.

Test: {test_name}

Click the link below to start:
{test_url}

Best regards,
QuizCraft"""
        
        params = {
            'subject': subject,
            'body': body
        }
        return f"https://mail.google.com/mail/u/0/?{urlencode(params)}"
    
    @staticmethod
    def get_telegram_share_url(test_name, test_url):
        """
        Generate Telegram sharing URL.
        """
        message = f"""You're invited to take this QuizCraft test.

Test: {test_name}

Start here: {test_url}"""
        
        params = {'url': test_url, 'text': message}
        return f"https://t.me/share/url?{urlencode(params)}"
    
    @staticmethod
    def get_facebook_share_url(test_url):
        """
        Generate Facebook sharing URL.
        """
        params = {'u': test_url}
        return f"https://www.facebook.com/sharer/sharer.php?{urlencode(params)}"
    
    @staticmethod
    def get_twitter_share_url(test_name, test_url):
        """
        Generate Twitter/X sharing URL.
        """
        text = f"Check out this QuizCraft test: {test_name}"
        params = {'url': test_url, 'text': text}
        return f"https://twitter.com/intent/tweet?{urlencode(params)}"
    
    @staticmethod
    def get_linkedin_share_url(test_url):
        """
        Generate LinkedIn sharing URL.
        """
        params = {'url': test_url}
        return f"https://www.linkedin.com/sharing/share-offsite/?{urlencode(params)}"
