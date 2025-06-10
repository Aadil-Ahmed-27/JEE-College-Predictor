import pandas as pd
import mysql.connector
import sys

def create_table_directly(cursor):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS 2024_seat_allocation (
        Institute VARCHAR(255),
        `Academic Program Name` VARCHAR(255),
        Quota VARCHAR(50),
        `Seat Type` VARCHAR(100),
        Gender VARCHAR(100),
        `Opening Rank` INT,
        `Closing Rank` INT
    ) ENGINE=InnoDB
    """
    cursor.execute(create_table_query)
    cursor.execute("TRUNCATE TABLE 2024_seat_allocation")

def insert_data_directly(cursor, conn, df, batch_size=100):
    total_rows = len(df)
    total_batches = (total_rows + batch_size - 1) // batch_size
    
    insert_query = """
    INSERT INTO 2024_seat_allocation 
    (Institute, `Academic Program Name`, Quota, `Seat Type`, Gender, `Opening Rank`, `Closing Rank`)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min((batch_num + 1) * batch_size, total_rows)
        
        batch_data = df.iloc[start_idx:end_idx]
        values = [tuple(row) for row in batch_data.values]
        
        try:
            cursor.executemany(insert_query, values)
            conn.commit()
            sys.stdout.write(f"\rProcessed {end_idx}/{total_rows} rows ({(end_idx/total_rows)*100:.1f}%)")
            sys.stdout.flush()
        except Exception as e:
            print(f"\nError in batch {batch_num + 1}: {str(e)}")
            print(f"First row in problematic batch: {values[0] if values else 'No values'}")
            raise

def load_data():
    print("\n=== Starting Data Load Process ===")
    
    try:
        print("1. Establishing MySQL connection...")
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='******',
            database='college_admissions',
            charset='utf8mb4',
            use_pure=True
        )
        cursor = conn.cursor()
        print("✓ Connection established")

        print("\n2. Reading CSV file...")
        df = pd.read_csv('reduced_josaa2024.csv')
        print(f"✓ CSV loaded: {len(df)} rows")
        
        print("\n3. Validating data types...")
        # Convert ranks to integers, handling any non-numeric values
        df['Opening Rank'] = pd.to_numeric(df['Opening Rank'], errors='coerce').fillna(0).astype(int)
        df['Closing Rank'] = pd.to_numeric(df['Closing Rank'], errors='coerce').fillna(0).astype(int)
        print("✓ Data types validated")

        print("\n4. Creating table...")
        create_table_directly(cursor)
        print("✓ Table created")

        print("\n5. Inserting data...")
        insert_data_directly(cursor, conn, df)
        print("\n✓ Data insertion complete")

        print("\n6. Verifying data...")
        cursor.execute("SELECT COUNT(*) FROM 2024_seat_allocation")
        count = cursor.fetchone()[0]
        print(f"✓ Verified: {count} rows in database")

    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()
            print("\n✓ Connections closed")

if __name__ == "__main__":
    load_data()