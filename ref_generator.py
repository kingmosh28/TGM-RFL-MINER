import asyncio
import logging
from datetime import datetime
from src.auth.telethon_handler import TelegramAuth
from src.proxies.manager import ProxyManager
from src.monitor.metrics import MetricsTracker

class ReferralGenerator:
    def __init__(self, target_refs=5000, batch_size=500, delay=0.5):
        self.auth = TelegramAuth()
        self.proxies = ProxyManager()
        self.metrics = MetricsTracker()
        self.target_refs = target_refs
        self.batch_size = batch_size
        self.delay = delay
        self.retry_limit = 3
        self.success_streak = 0
        
    async def generate_referral(self, target_link, attempt=0):
        try:
            proxy = await self.proxies.get_valid_proxy()
            if not proxy:
                raise Exception("No valid proxies available")
            
            client, account = await self.auth.create_account(proxy)
            if client and account:
                # Smart delay based on success streak
                smart_delay = max(0.1, self.delay - (self.success_streak * 0.05))
                await asyncio.sleep(smart_delay)
                
                await client.send_message(
                    target_link.split('?start=')[0],
                    '/start ' + target_link.split('?start=')[1]
                )
                
                self.success_streak += 1
                self.metrics.log_success()
                logging.info(f"[+] Referral {self.metrics.referrals}/{self.target_refs} | Proxy: {proxy}")
                return True
                
        except Exception as e:
            self.success_streak = 0
            if attempt < self.retry_limit:
                logging.warning(f"[-] Attempt {attempt + 1}/{self.retry_limit} failed: {str(e)}")
                return await self.generate_referral(target_link, attempt + 1)
            logging.error(f"[-] Final attempt failed: {str(e)}")
            return False
            
    async def start_campaign(self, target_link):
        campaign_start = datetime.now()
        logging.info(f"""
        [+] 🚀 CAMPAIGN LAUNCHED 🚀
        Target: {target_link}
        Goal: {self.target_refs} referrals
        Batch Size: {self.batch_size}
        Base Delay: {self.delay}s
        """)
        
        while self.metrics.referrals < self.target_refs:
            batch_start = datetime.now()
            tasks = []
            batch_size = min(self.batch_size, self.target_refs - self.metrics.referrals)
            
            for _ in range(batch_size):
                task = asyncio.create_task(self.generate_referral(target_link))
                tasks.append(task)
                
            results = await asyncio.gather(*tasks, return_exceptions=True)
            successful = sum(1 for r in results if r is True)
            
            batch_time = (datetime.now() - batch_start).total_seconds()
            logging.info(f"""
            [+] Batch Summary:
            Success Rate: {successful}/{batch_size} ({(successful/batch_size)*100:.2f}%)
            Time: {batch_time:.2f}s
            Speed: {successful/batch_time:.2f} refs/s
            """)
            
            if successful < batch_size * 0.5:  # Less than 50% success
                logging.warning("[!] Low success rate - adjusting delay...")
                self.delay *= 1.2
            
        campaign_time = (datetime.now() - campaign_start).total_seconds()
        logging.info(f"""
        [+] 💎 CAMPAIGN COMPLETE 💎
        Total Time: {campaign_time:.2f}s
        Average Speed: {self.target_refs/campaign_time:.2f} refs/s
        """)
        self.metrics.show_final_stats()
