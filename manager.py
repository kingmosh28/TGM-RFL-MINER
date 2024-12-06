import aiohttp
import asyncio
from typing import List, Set
import logging
from datetime import datetime, timedelta

class ProxyManager:
    def __init__(self):
        self.proxy_apis = [
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=10000&country=all",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
            "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt"
        ]
        self.proxies: Set[str] = set()
        self.working_proxies: List[dict] = []
        self.last_refresh = datetime.now()
        self.refresh_interval = timedelta(minutes=5)
        self.backup_proxies = [
            "socks5://51.222.13.193:10084",
            "socks5://51.222.13.193:10085",
            "socks5://51.222.13.193:10086",
            "socks5://51.222.13.193:10087",
            "socks5://51.222.13.193:10088"
        ]
        
    async def fetch_proxies_from_api(self, api_url: str) -> Set[str]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, timeout=10) as response:
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
            return f"socks5://{ip}:{port}"
        except:
            return None
            
    def load_backup_proxies(self):
        self.proxies = set(self.backup_proxies)
        logging.info(f"[+] Using {len(self.proxies)} backup proxies!")
        
    async def verify_proxy(self, proxy: str) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'https://api.ipify.org',
                    proxy=proxy,
                    timeout=5,
                    ssl=False
                ) as response:
                    return response.status == 200
        except:
            return False
            
    async def get_valid_proxy(self) -> str:
        if datetime.now() - self.last_refresh > self.refresh_interval:
            await self.refresh_proxies()
            
        if not self.working_proxies:
            await self.validate_proxies()
            
        if self.working_proxies:
            proxy_info = self.working_proxies.pop(0)
            self.working_proxies.append(proxy_info)
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
        
    async def refresh_proxies(self):
        await self.load_proxies()
        await self.validate_proxies()
        logging.info(f"[+] Refreshed! Working proxies: {len(self.working_proxies)}")
