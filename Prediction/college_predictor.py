import mysql.connector
from tabulate import tabulate

def get_college_predictions(rank, category="OPEN", gender="Gender-Neutral", Quota="AI"):
    try:
        # Connect to database
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Mysql-aadil',
            database='college_admissions'
        )
        cursor = conn.cursor()

        # Query to fetch colleges where closing rank is greater than or equal to input rank
        query = """
                SELECT 
                Institute,
                `Academic Program Name`,
                MIN(`Opening Rank`) AS `Opening Rank`,
                MAX(`Closing Rank`) AS `Closing Rank`
                FROM 2024_seat_allocation
                WHERE `Closing Rank` >= %s
                    AND `Seat Type` = %s
                    AND Gender = %s
                    AND Quota = %s
                GROUP BY Institute, `Academic Program Name`, Quota
                ORDER BY (ABS(MIN(`Opening Rank`) - %s) + ABS(MAX(`Closing Rank`) - %s)) ASC;

                """

        
        cursor.execute(query, (rank, category, gender, Quota,rank,rank))
        results = cursor.fetchall()

        if not results:
            print(f"\nNo colleges found for rank {rank} in category {category} for {gender}")
            return

        # Format and display results
        headers = ["Institute", "Program", "Opening Rank", "Closing Rank"]
        print(f"\nPossible colleges for rank {rank} in category {category} for {gender}:")
        print(tabulate(results[:10], headers=headers, tablefmt='grid'))
        print(f"\nTotal programs available: {len(results)}")

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def main():
    while True:
        try:
            # Get user input
            rank = int(input("\nEnter your rank: "))
            
            # Show available categories
            print("\nAvailable categories:")
            print("1. OPEN (General)")
            print("2. OBC-NCL")
            print("3. SC")
            print("4. ST")
            print("5. EWS")
            category = input("Enter category (press Enter for OPEN): ").upper() or "OPEN"
            
            # Show gender options
            print("\nGender options:")
            print("1. Gender-Neutral")
            print("2. Female-only")
            gender = input("Enter gender (press Enter for Gender-Neutral): ") or "Gender-Neutral"

            # Show quota options
            print("\nQuota options:")
            print("1. AI")
            print("2. HS")
            print("3. OS")
            print("4. GO")
            print("5. JK")
            print("6. LA")
            quota = input("Enter quota (press Enter for AI): ") or "AI"
            
            # Get college predictions
            get_college_predictions(rank, category, gender, quota)
            
            # Ask if user wants to continue
            if input("\nWould you like to try another rank? (y/n): ").lower() != 'y':
                break
                
        except ValueError:
            print("Please enter a valid rank (numeric value)")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    print("Welcome to College Admission Predictor")
    print("=====================================")
    main()
    print("\nThank you for using College Admission Predictor!")