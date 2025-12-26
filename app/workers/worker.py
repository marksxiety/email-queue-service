from app.utils.logger import print_logging
from app.utils.database_connect import connect
import pandas as pd
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("app/templates"))

def get_on_queue_emails():
    conn = connect()
    if conn is None:
        print_logging("error", "Failed to connect to database")
        return False

    cursor = None
    try:
        query = """
            SELECT email_type, subject, email_template, email_data 
            FROM email_queues 
            WHERE status = 0 
            ORDER BY priority_level ASC
        """
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        # Convert to Pandas DataFrame
        emails_df = pd.DataFrame(results, columns=columns)
        return emails_df

    except Exception as e:
        print_logging("error", f"Error querying emails: {str(e)}")
        return False

    finally:
        if cursor:
            cursor.close()
        conn.close()

# Example usage
if __name__ == "__main__":
    emails_df = get_on_queue_emails()
    print(emails_df)
