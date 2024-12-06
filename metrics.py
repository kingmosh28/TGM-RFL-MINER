import time
from datetime import datetime
import logging
from pathlib import Path
import json

class MetricsTracker:
    def __init__(self):
        self.start_time = time.time()
        self.referrals = 0
        self.failures = 0
        self.success_times = []
        self.hourly_stats = {}
        self.logs_path = Path("logs")
        self.logs_path.mkdir(exist_ok=True)
        
    def log_success(self):
        self.referrals += 1
        current_time = datetime.now()
        hour_key = current_time.strftime('%Y-%m-%d %H:00')
        
        # Track hourly performance
        if hour_key not in self.hourly_stats:
            self.hourly_stats[hour_key] = 0
        self.hourly_stats[hour_key] += 1
        
        # Calculate speed
        self.success_times.append(time.time())
        if len(self.success_times) > 10:
            self.success_times.pop(0)
            
        speed = self.calculate_speed()
        
        logging.info(f"""
        [+] 💎 Referral #{self.referrals} 💎
        Time: {current_time.strftime('%H:%M:%S')}
        Speed: {speed:.2f} refs/min
        Success Rate: {self.get_success_rate():.1f}%
        """)
        
        # Save metrics
        self.save_metrics()
        
    def log_failure(self):
        self.failures += 1
        self.save_metrics()
        
    def calculate_speed(self):
        if len(self.success_times) < 2:
            return 0
        time_diff = self.success_times[-1] - self.success_times[0]
        return (len(self.success_times) - 1) / (time_diff / 60)
        
    def get_success_rate(self):
        total = self.referrals + self.failures
        return (self.referrals / total * 100) if total > 0 else 0
        
    def save_metrics(self):
        metrics = {
            'referrals': self.referrals,
            'failures': self.failures,
            'success_rate': self.get_success_rate(),
            'hourly_stats': self.hourly_stats,
            'runtime': time.time() - self.start_time
        }
        
        with open(self.logs_path / 'metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2)
            
    def show_final_stats(self):
        runtime = time.time() - self.start_time
        hours = runtime / 3600
        
        logging.info(f"""
        🚀 CAMPAIGN COMPLETE 🚀
        ----------------------
        Total Referrals: {self.referrals}
        Success Rate: {self.get_success_rate():.1f}%
        Runtime: {hours:.1f} hours
        Average Speed: {self.referrals/hours:.1f} refs/hour
        ----------------------
        """)
