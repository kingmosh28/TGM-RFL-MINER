from pathlib import Path
import logging
import json
from typing import Dict, List

class SystemSetup:
    def __init__(self):
        self.required_dirs = {
            'sessions': 'Telethon session storage',
            'database': 'Campaign tracking data',
            'proxies': 'Proxy list storage',
            'logs': 'System logging',
            'metrics': 'Performance tracking',
            'backup': 'System state backup'
        }
        
    def create_directories(self) -> Dict[str, Path]:
        paths = {}
        for dir_name, description in self.required_dirs.items():
            path = Path(dir_name)
            path.mkdir(exist_ok=True, parents=True)
            paths[dir_name] = path
            logging.info(f"[+] {description}: {path} ✅")
        return paths
        
    def verify_structure(self) -> bool:
        return all(Path(d).exists() for d in self.required_dirs)
        
    def clean_sessions(self, days_old: int = 7):
        session_dir = Path('sessions')
        if session_dir.exists():
            for session in session_dir.glob('*.session'):
                if session.stat().st_mtime < days_old * 86400:
                    session.unlink()
                    logging.info(f"Cleaned old session: {session}")

def create_directories():
    setup = SystemSetup()
    paths = setup.create_directories()
    setup.clean_sessions()
    return paths
