"""
Script to fix field name inconsistencies in the TourTrip database.
Run this script with:
    python manage.py shell < fix_inconsistencies.py
"""

from django.db import connection

def fix_inconsistencies():
    """
    Fix the inconsistencies in field names by ensuring all relationships
    use tour_guide instead of guide.
    """
    # Define the changes needed
    changes = [
        {
            'table': 'tourguides_tourpackage',
            'old_field': 'guide_id',
            'new_field': 'tour_guide_id',
            'check_sql': "SELECT COUNT(*) FROM information_schema.columns WHERE table_name='tourguides_tourpackage' AND column_name='guide_id'",
            'alter_sql': "ALTER TABLE tourguides_tourpackage RENAME COLUMN guide_id TO tour_guide_id;"
        },
        {
            'table': 'tourguides_workschedule',
            'old_field': 'guide_id',
            'new_field': 'tour_guide_id',
            'check_sql': "SELECT COUNT(*) FROM information_schema.columns WHERE table_name='tourguides_workschedule' AND column_name='guide_id'",
            'alter_sql': "ALTER TABLE tourguides_workschedule RENAME COLUMN guide_id TO tour_guide_id;"
        },
        {
            'table': 'tourguides_review',
            'old_field': 'guide_id',
            'new_field': 'tour_guide_id',
            'check_sql': "SELECT COUNT(*) FROM information_schema.columns WHERE table_name='tourguides_review' AND column_name='guide_id'",
            'alter_sql': "ALTER TABLE tourguides_review RENAME COLUMN guide_id TO tour_guide_id;"
        }
    ]
    
    # Check each table and apply changes if needed
    with connection.cursor() as cursor:
        for change in changes:
            # Check if the field exists
            cursor.execute(change['check_sql'])
            field_exists = cursor.fetchone()[0]
            
            if field_exists:
                print(f"Fixing field in {change['table']}: {change['old_field']} -> {change['new_field']}")
                cursor.execute(change['alter_sql'])
                print(f"Successfully renamed {change['old_field']} to {change['new_field']} in {change['table']}")
            else:
                print(f"No inconsistency found in {change['table']}, field already named correctly as {change['new_field']}")
    
    print("Field inconsistency fixes completed.")

if __name__ == "__main__":
    print("Starting to fix field name inconsistencies...")
    fix_inconsistencies()
    print("Done.") 