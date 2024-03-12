import sys
import argparse
import logging
import os
import shutil
import time

"""
Command structure (4 arguments): python sync.py source_path replica_path interval(integer) log_file
"""

# Synchronize folders both ways by adding and deleting files and directories
def synchronize_folders(source_path, replica_path):
    # Synchronize files from source to replica
    for root, dirs, files in os.walk(replica_path):
        relative_path = os.path.relpath(root, replica_path)
        source_root = os.path.join(source_path, relative_path)

        # Remove files from replica that don't exist in source
        for file_name in files:
            replica_file = os.path.join(root, file_name)
            source_file = os.path.join(source_root, file_name)
            if not os.path.exists(source_file):
                os.remove(replica_file)
                logging.info(f"Removed {replica_file}")

        # Remove directories from replica that don't exist in source
        for dir_name in dirs:
            replica_dir = os.path.join(root, dir_name)
            source_dir = os.path.join(source_root, dir_name)
            if not os.path.exists(source_dir):
                shutil.rmtree(replica_dir)
                logging.info(f"Removed directory {replica_dir}")

    # Copy files from source to replica
    for root, dirs, files in os.walk(source_path):
        relative_path = os.path.relpath(root, source_path)
        replica_root = os.path.join(replica_path, relative_path)
        
        # Ensure replica directory structure matches source
        for dir_name in dirs:
            replica_dir = os.path.join(replica_root, dir_name)
            if not os.path.exists(replica_dir):
                os.makedirs(replica_dir)

        # Copy files from source to replica
        for file_name in files:
            source_file = os.path.join(root, file_name)
            replica_file = os.path.join(replica_root, file_name)
            if not os.path.exists(replica_file) or (os.path.exists(replica_file) and os.stat(source_file).st_mtime - os.stat(replica_file).st_mtime > 1):
                shutil.copy2(source_file, replica_root)
                logging.info(f"Copied {source_file} to {replica_root}")

    logging.info("Files synchronized successfully.")

# Function to verify if a directory exists 
def verify_directory(path):
    if not os.path.exists(path):
        logging.error(f'Error: Path {path} not found')
        return False
    else:
        return True

# Function to verify log file path
def verify_logging(log_file):
    if not os.path.isfile(log_file):
        return False
    return True

# Configures logging to display informative messages to a log file
def setup_logging(log_file):
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

# Function to handle command line arguments using argparse library
def argument_split():
    parser = argparse.ArgumentParser(description="Synchronize")
    parser.add_argument("source_path", help="source folder path")
    parser.add_argument("replica_path", help="replica folder path")
    parser.add_argument("interval", type=int, help="interval minutes")
    parser.add_argument("log_file", help="log file path")
    return parser.parse_args()

# Main
if __name__ == "__main__":
    # Check for the number of arguments
    if len(sys.argv) != 5:
        print("Invalid number of arguments")
        sys.exit(1)

    # Parse arguments 
    args = argument_split()
    
    # Verify and setup logging
    if not verify_logging(args.log_file):
        print("log_file not found")
        sys.exit(1)
    setup_logging(args.log_file)
    
    # Check if paths exist
    if not verify_directory(args.source_path):
        logging.error("Please enter a valid source path")
        sys.exit(1)
    if not verify_directory(args.replica_path):
        logging.error("Please enter a valid replica path")
        sys.exit(1)
    
    # Synchronize folders periodically
    while True:
        synchronize_folders(args.source_path, args.replica_path)
        time.sleep(args.interval * 60)