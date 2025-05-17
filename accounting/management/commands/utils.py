import csv
import os
import logging
from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger(__name__)

def open_csv_with_different_encodings(file_path, delimiter=';'):
    """
    Try to open a CSV file with different encodings until one works.
    
    Args:
        file_path: Path to the CSV file
        delimiter: CSV delimiter character
        
    Returns:
        tuple: (reader, encoding) - CSV reader and the encoding that worked
        
    Raises:
        CommandError: If all encodings fail
    """
    encodings_to_try = ['latin1', 'cp1252', 'iso-8859-1', 'utf-8-sig', 'utf-8']
    
    for encoding in encodings_to_try:
        try:
            logger.info(f"Trying to open file with encoding: {encoding}")
            file = open(file_path, mode='r', encoding=encoding)
            reader = csv.DictReader(file, delimiter=delimiter)
            # Test reading the first row
            next(reader)
            # If successful, reset the file pointer
            file.seek(0)
            reader = csv.DictReader(file, delimiter=delimiter)
            return reader, file, encoding
        except UnicodeDecodeError:
            logger.warning(f"Failed to open file with encoding: {encoding}")
            continue
        except Exception as e:
            logger.error(f"Error opening file: {str(e)}")
            raise CommandError(f"Error opening file: {str(e)}")
    
    raise CommandError("Could not open file with any of the tried encodings")

def batch_process_objects(objects, batch_size=500, create_func=None):
    """
    Process objects in batches to avoid SQLite limitations.
    
    Args:
        objects: List of objects to process
        batch_size: Size of each batch
        create_func: Function to call for creating the objects (default: bulk_create)
        
    Returns:
        int: Number of objects processed
    """
    batches = [objects[i:i+batch_size] for i in range(0, len(objects), batch_size)]
    
    count = 0
    for batch in batches:
        if create_func:
            create_func(batch)
        else:
            # Default to bulk_create if no function is provided
            # This assumes objects have a common class/model
            if batch:
                batch[0].__class__.objects.bulk_create(batch)
        
        count += len(batch)
        
    return count
