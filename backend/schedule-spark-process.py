import time
import schedule
from subprocess import call
import logging
import schedule

# Set up logging
logging.basicConfig(
    filename='scheduler.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def run_spark_job():
    try:
        logging.info("Starting Spark job")
        call([
            "docker", "run", "-it", 
            "-v", "C:\\Users\\HP\\Desktop\\BigData-Project\\backend:/app", 
            "bitnami/spark:latest", "spark-submit", "/app/process_logs.py"
        ])
        logging.info("Spark job completed successfully")
    except Exception as e:
        logging.error(f"Error running Spark job: {str(e)}")

def main():
    # Schedule the job to run every hour
    schedule.every().hour.at(":00").do(run_spark_job)
    # schedule.every(60).seconds.do(run_spark_job)
    
    # Run the job immediately when starting
    run_spark_job()
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every 1 min

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Scheduler stopped by user")
    except Exception as e:
        logging.error(f"Scheduler error: {str(e)}")