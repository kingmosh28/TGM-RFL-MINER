import aiohttp
import asyncio
from typing import List, Set
import logging
from datetime import datetime, timedelta
import random

class ProxyManager:
    def __init__(self):
        self.proxy_apis = [
            "https://raw.githubusercontent.com/casals-ar/proxy-list/main/socks4",
            "https://raw.githubusercontent.com/casals-ar/proxy-list/main/socks5",
            "https://raw.githubusercontent.com/casals-ar/proxy-list/main/http",
            "https://raw.githubusercontent.com/casals-ar/proxy-list/main/https",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
            "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt"
        ]
        
        self.proxies: Set[str] = set()
        self.working_proxies: List[dict] = []
        self.last_refresh = datetime.now()
        self.refresh_interval = timedelta(minutes=3)
        self.max_fails = 3
        
        self.backup_proxies = [
            "socks5://51.222.13.193:10084",
            "socks5://51.222.13.193:10085", 
            "socks5://51.222.13.193:10086",
            "socks5://144.91.95.238:1080",
            "socks5://138.68.109.12:39023"
        ]

    async def fetch_proxies_from_api(self, api_url: str) -> Set[str]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, timeout=15) as response:
                    if response.status == 200:
                        proxy_list = await response.text()
                        return {self.format_proxy(p) for p in proxy_list.split('\n') if p.strip()}
        except Exception as e:
            logging.warning(f"API fetch failed: {api_url} | {str(e)}")
        return set()

    async def load_proxies(self):
        tasks = [self.fetch_proxies_from_api(api) for api in self.proxy_apis]
        proxy_sets = await asyncio.gather(*tasks)
        
        self.proxies = set().union(*proxy_sets)
        if not self.proxies:
            self.load_backup_proxies()
            
        logging.info(f"[+] Loaded {len(self.proxies)} proxies")
        self.last_refresh = datetime.now()

    def format_proxy(self, proxy: str) -> str:
        try:
            if '://' in proxy:
                return proxy.strip()
            ip, port = proxy.strip().split(':')
            protocol = random.choice(['socks5', 'socks4', 'http'])
            return f"{protocol}://{ip}:{port}"
        except:
            return None

    def load_backup_proxies(self):
        self.proxies = set(self.backup_proxies)
        logging.info(f"[+] Using {len(self.proxies)} premium backup proxies!")

    async def verify_proxy(self, proxy: str) -> bool:
        test_urls = [
            'https://api.ipify.org',
            'http://ip-api.com/json',
            'https://ifconfig.me/ip'
        ]
        
        for url in test_urls:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url,
                        proxy=proxy,
                        timeout=10,
                        ssl=False
                    ) as response:
                        if response.status == 200:
                            return True
            except:
                continue
        return False

    async def get_valid_proxy(self) -> str:
        if datetime.now() - self.last_refresh > self.refresh_interval:
            await self.refresh_proxies()

        if not self.working_proxies:
            await self.validate_proxies()

        working = [p for p in self.working_proxies if p['fails'] < self.max_fails]
        if working:
            proxy_info = random.choice(working)
            return proxy_info['proxy']
            
        return None

    async def validate_proxies(self):
        tasks = [self.verify_proxy(proxy) for proxy in self.proxies]
        results = await asyncio.gather(*tasks)
        
        self.working_proxies = [
            {'proxy': proxy, 'fails': 0}
            for proxy, is_valid in zip(self.proxies, results)
            if is_valid
        ]
        
        random.shuffle(self.working_proxies)

    async def refresh_proxies(self):
        await self.load_proxies()
        await self.validate_proxies()
        logging.info(f"[+] Refreshed! Working proxies: {len(self.working_proxies)}")

    def mark_proxy_failed(self, proxy: str):
        for p in self.working_proxies:
            if p['proxy'] == proxy:
                p['fails'] += 1
                if p['fails'] >= self.max_fails:
                    self.working_proxies.remove(p)
                break

    async def __aenter__(self):
        await self.load_proxies()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
        
    @classmethod
    async def create(cls):
        manager = cls()
        await manager.load_proxies()
        return manager

async def main():
    async with ProxyManager() as proxy_manager:
        proxy = await proxy_manager.get_valid_proxy()
        if proxy:
            logging.info(f"Using proxy: {proxy}")
        else:
            logging.error("No valid proxies available!")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s'
    )
    asyncio.run(main())
