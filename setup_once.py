import logging
from pathlib import Path
import json
import sys
from typing import Dict

class InitialSetup:
    def __init__(self):
        self.logger = self._setup_logging()
        self.system_dirs = {
            'sessions': {'purpose': 'Telethon sessions', 'required': True},
            'database': {'purpose': 'Campaign tracking', 'required': True},
            'proxies': {'purpose': 'Proxy storage', 'required': True},
            'logs': {'purpose': 'System logging', 'required': True},
            'metrics': {'purpose': 'Performance data', 'required': True},
            'backup': {'purpose': 'System backup', 'required': False}
        }
        
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(message)s'
        )
        return logging.getLogger(__name__)
        
    def create_directories(self) -> Dict[str, Path]:
        paths = {}
        for dir_name, config in self.system_dirs.items():
            path = Path(dir_name)
            try:
                path.mkdir(exist_ok=True, parents=True)
                paths[dir_name] = path
                self.logger.info(f"[+] {config['purpose']}: {path} ✅")
            except Exception as e:
                if config['required']:
                    self.logger.error(f"Failed to create {dir_name}: {e}")
                    sys.exit(1)
        return paths
        
    def verify_installation(self):
        try:
            import telethon
            import aiohttp
            import asyncio
            import cryptg
            self.logger.info("All dependencies verified! ✅")
            return True
        except ImportError as e:
            self.logger.error(f"Missing dependency: {e}")
            return False
            
    def initialize_system(self):
        self.logger.info("🚀 Initializing PROFIT SYSTEM 🚀")
        paths = self.create_directories()
        
        if not self.verify_installation():
            self.logger.error("System requirements not met!")
            sys.exit(1)
            
        config = {
            'system_ready': True,
            'paths': {k: str(v) for k, v in paths.items()},
            'initialized_at': datetime.now().isoformat()
        }
        
        with open('system_config.json', 'w') as f:
            json.dump(config, f, indent=2)
            
        self.logger.info("💎 PROFIT SYSTEM READY! 💎")

if __name__ == "__main__":
    setup = InitialSetup()
    setup.initialize_system()
