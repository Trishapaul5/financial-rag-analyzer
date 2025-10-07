import os
import shutil
import yaml

# This script provides a safe way to delete the ChromaDB vector database.

def clean_vector_database():
    """
    Reads the configuration to find the ChromaDB persistence directory
    and deletes it after user confirmation.
    """
    try:
        # Load the configuration to find the database path
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        db_path = config.get('vector_db', {}).get('persist_directory')

        if not db_path:
            print("❌ Error: Could not find 'persist_directory' in config/config.yaml")
            return

        print("-" * 50)
        print("🧹 Database Cleaning Utility")
        print("-" * 50)

        # Check if the directory actually exists
        if not os.path.exists(db_path):
            print(f"✅ The database directory ('{db_path}') does not exist. Nothing to clean.")
            return

        # SAFETY CHECK: Ask for user confirmation
        print(f"⚠️ You are about to permanently delete the vector database located at:")
        print(f"   '{os.path.abspath(db_path)}'")
        
        confirm = input("   Are you sure you want to continue? (y/n): ")

        if confirm.lower() == 'y':
            print(f"\n🗑️ Deleting directory: {db_path}...")
            shutil.rmtree(db_path)
            print("✅ Database cleaned successfully!")
        else:
            print("\n🚫 Operation cancelled by user.")

    except FileNotFoundError:
        print("❌ Error: 'config/config.yaml' not found. Make sure you are running this script from the project's root directory.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    clean_vector_database()