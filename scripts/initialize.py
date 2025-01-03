import csv
import pymysql
from settings import DATA_SOURCE, DB_HOST, DB_NAME, DB_PASSWORD, DB_USER, SCHEMA_FILE

# Connect to the MySQL database
connection = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
def cleanup():
    """Cleanup tables"""
    try:
        with connection.cursor() as cursor:
            # Retrieve all table names
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            
            # Iterate over each table and drop it
            for (table_name,) in tables:
                cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`;")
                print(f"Table {table_name} has been dropped.")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

            connection.commit()
            print("All tables have been dropped successfully.")
    except Exception as e:
        print(f"An error occurred while dropping tables: {e}")

def init_db():
    """Create tables using the predefined schema.sql file."""
    try:
        with open(SCHEMA_FILE, 'r') as file:
            # Read the schema file and split statements by semicolons
            schema_sql = file.read()
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        with connection.cursor() as cursor:
            for statement in statements:
                cursor.execute(statement)  # Execute each statement
            connection.commit()
        print("Tables created successfully from schema.sql")
    except FileNotFoundError:
        print(f"Schema file '{SCHEMA_FILE}' not found.")
    except Exception as e:
        print(f"An error occurred while creating tables: {e}")

def insert_school(school_name: str):
    """Insert a school and return school ID."""
    with connection.cursor() as cursor:
        cursor.execute(f'INSERT IGNORE INTO schools (school_name) VALUES ("{school_name}")')
        connection.commit()
        cursor.execute(f'SELECT school_id FROM schools WHERE school_name = "{school_name}"')
        return cursor.fetchone()[0]

def insert_class(class_name):
    """Insert a class and return class ID."""
    with connection.cursor() as cursor:
        cursor.execute(f'INSERT IGNORE INTO classes (class_name) VALUES ("{class_name}")',)
        connection.commit()
        cursor.execute(f'SELECT class_id FROM classes WHERE class_name = "{class_name}"',)
        return cursor.fetchone()[0]

def clean_description(description: str):
    """
    Cleans the description text by removing unwanted symbols and formatting issues.
    
    Args:
        description (str): The original description text.
        
    Returns:
        str: The cleaned description.
    """
    if not description:
        return description  # Return as-is if description is None or empty
    
    # Remove unwanted symbols
    unwanted_symbols = ['"', "'", '\\', '%']  # Add more symbols if needed
    for symbol in unwanted_symbols:
        description = description.replace(symbol, '')
    
    # Optional: Replace multiple spaces with a single space
    description = ' '.join(description.split())
    
    # Optional: Trim leading/trailing spaces
    description = description.strip()
    
    return description

def insert_spell(row, school_id):
    """Insert a spell and return spell ID."""
    with connection.cursor() as cursor:
        description = clean_description(row['description'])
        cursor.execute(f"""
            INSERT INTO spells (name, level, school_id, cast_time, spell_range, duration, description)
            VALUES ("{row['name']}", "{row['level']}", "{school_id}", "{row['cast_time']}", "{row['range']}", "{row['duration']}", "{description}")
        """)
        connection.commit()
        cursor.execute("SELECT LAST_INSERT_ID()")
        return cursor.fetchone()[0]

def insert_components(spell_id, row):
    """Insert spell components."""
    with connection.cursor() as cursor:
        cursor.execute(f"""
            INSERT INTO spell_components (spell_id, verbal, somatic, material, material_cost)
            VALUES ("{spell_id}", "{row['verbal']}", "{row['somatic']}", "{row['material']}", "{row.get('material_cost')}")
        """)
        connection.commit()

def insert_spell_classes(spell_id, classes):
    """Insert class relationships for a spell."""
    with connection.cursor() as cursor:
        for class_name in classes.split(','):
            class_name = class_name.strip()
            class_id = insert_class(class_name)
            cursor.execute(f"""
                INSERT IGNORE INTO spells_classes (spell_id, class_id)
                VALUES ("{spell_id}", "{class_id}")
            """)
        connection.commit()

def populate_db():
    """Read spell source and populate the database."""

    with open(DATA_SOURCE, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(row)
            school_id = insert_school(row['school'])
            spell_id = insert_spell(row, school_id)
            insert_components(spell_id, row)
            insert_spell_classes(spell_id, row['classes'])

def main():
    """
    Entrypoint
    """
    try:
        cleanup()
        init_db()
        populate_db()
        print("Database populated successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        connection.close()
if __name__ == "__main__":
    main()
