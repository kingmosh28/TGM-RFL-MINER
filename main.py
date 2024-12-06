import asyncio
import os
import logging
from datetime import datetime
from pathlib import Path
from src.core.ref_generator import ReferralGenerator
from src.core.setup_dirs import create_directories
from typing import List, Dict

class ProfitMachine:
    def __init__(self):
        self.logger = self._setup_logging()
        self.campaigns: Dict[str, ReferralGenerator] = {}
        self.base_config = {
            'target_refs': 5000,
            'batch_size': 500,
            'delay': 0.5
        }
        
    def _setup_logging(self):
        log_path = Path("logs")
        log_path.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(message)s',
            handlers=[
                logging.FileHandler(log_path / f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)

    async def launch_campaign(self, target: str, custom_config: dict = None):
        config = self.base_config.copy()
        if custom_config:
            config.update(custom_config)
            
        generator = ReferralGenerator(**config)
        self.campaigns[target] = generator
        
        try:
            await generator.start_campaign(target)
        except Exception as e:
            self.logger.error(f"Campaign error for {target}: {str(e)}")
            
    async def launch_multi_campaign(self, targets: List[str], configs: List[dict] = None):
        tasks = []
        for i, target in enumerate(targets):
            config = configs[i] if configs and i < len(configs) else None
            tasks.append(self.launch_campaign(target, config))
            
        await asyncio.gather(*tasks)
        
    def stop_campaign(self, target: str):
        if target in self.campaigns:
            self.campaigns[target].stop()
            self.logger.info(f"Campaign stopped: {target}")
            
    def stop_all(self):
        for target in self.campaigns:
            self.stop_campaign(target)

async def main():
    # Initialize our MONEY PRINTER
    profit_machine = ProfitMachine()
    
    # Create necessary directories
    create_directories()
    profit_machine.logger.info("🚀 SYSTEM INITIALIZED 🚀")
    
    # Campaign Configurations
    campaigns = [
        {
            'target': 't.me/btc_farm_real_mining_bot?start=6865449437',
            'config': {
                'target_refs': 5000,
                'batch_size': 500,
                'delay': 0.5
            }
        },
        # Add more campaigns here!
    ]
    
    try:
        # UNLEASH THE BEAST!
        await profit_machine.launch_multi_campaign(
            targets=[c['target'] for c in campaigns],
            configs=[c.get('config') for c in campaigns]
        )
        
    except KeyboardInterrupt:
        profit_machine.logger.warning("⚠️ Emergency Stop Triggered!")
        profit_machine.stop_all()
    except Exception as e:
        profit_machine.logger.error(f"💥 Critical Error: {str(e)}")
    finally:
        profit_machine.logger.info("Campaign Status Report Generated!")

if __name__ == "__main__":
    asyncio.run(main())
