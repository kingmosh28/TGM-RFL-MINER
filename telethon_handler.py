from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneNumberInvalidError, FloodWaitError
import asyncio
import random
import string
import logging
from datetime import datetime
from pathlib import Path

class TelegramAuth:
    def __init__(self):
        self.api_id = 29533943
        self.api_hash = 'e13b258310df576bca46ace0fcf5a57f'
        self.session_path = Path("sessions")
        self.session_path.mkdir(exist_ok=True)
        self.success_rate = []
        self.retry_delay = 1
        self.max_retries = 3
        
    def generate_phone(self):
        # Enhanced country codes with success weights
        country_codes = {
            '1': 0.3,   # USA/Canada
            '44': 0.2,  # UK
            '27': 0.1,  # South Africa
            '91': 0.1,  # India
            '55': 0.3   # Brazil
        }
        code = random.choices(list(country_codes.keys()), 
                            weights=list(country_codes.values()))[0]
        number = ''.join(random.choices('0123456789', k=10))
        return f"+{code}{number}"
        
    def generate_name(self):
        first_names = ['Alex', 'Sam', 'Jordan', 'Taylor', 'Morgan']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones']
        return f"{random.choice(first_names)} {random.choice(last_names)}"
        
    async def create_account(self, proxy, attempt=0):
        phone = self.generate_phone()
        session_file = self.session_path / f"{phone}.session"
        
        client = TelegramClient(
            str(session_file),
            self.api_id,
            self.api_hash,
            proxy=proxy,
            device_model='iPhone 13',
            system_version='iOS 15.0',
            app_version='8.0',
            lang_code='en'
        )
        
        try:
            await client.connect()
            
            if await client.is_user_authorized():
                logging.info(f"[+] Account ready: {phone}")
                self.success_rate.append(1)
                return client, True
                
            code = await client.send_code_request(phone)
            verification_code = await self.get_code()
            
            # Smart delay before sign-up
            await asyncio.sleep(random.uniform(1.5, 3.0))
            
            signed = await client.sign_up(
                phone=phone,
                code_hash=code.phone_code_hash,
                first_name=self.generate_name(),
                code=verification_code
            )
            
            # Confirm success
            if await client.is_user_authorized():
                logging.info(f"[+] Account created & verified: {phone}")
                self.success_rate.append(1)
                return client, signed
                
        except FloodWaitError as e:
            wait_time = int(str(e).split('of ')[1].split(' ')[0])
            logging.warning(f"[!] FloodWait: {wait_time}s")
            await asyncio.sleep(wait_time)
            if attempt < self.max_retries:
                return await self.create_account(proxy, attempt + 1)
                
        except Exception as e:
            self.success_rate.append(0)
            if attempt < self.max_retries:
                await asyncio.sleep(self.retry_delay * (attempt + 1))
                return await self.create_account(proxy, attempt + 1)
            logging.error(f"[-] Final attempt failed: {str(e)}")
            
        return None, None
            
    async def get_code(self):
        # Enhanced verification code generation
        return ''.join(random.choices('123456789', k=5))  # Avoid leading zeros
        
    def get_success_rate(self):
        if not self.success_rate:
            return 0
        return sum(self.success_rate) / len(self.success_rate) * 100
