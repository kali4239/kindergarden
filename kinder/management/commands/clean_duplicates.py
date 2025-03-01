# management/commands/clean_duplicates.py
from django.core.management.base import BaseCommand
from kinder.models import Attendance
from django.db.models import Count

class Command(BaseCommand):
    help = 'Clean duplicate attendance records'

    def handle(self, *args, **kwargs):
        # Find duplicate attendance records
        duplicates = (
            Attendance.objects.values('student', 'date')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
        )

        for duplicate in duplicates:
            student_id = duplicate['student']
            date = duplicate['date']
            # Keep the first record and delete the rest
            records = Attendance.objects.filter(student_id=student_id, date=date).order_by('id')
            for record in records[1:]:
                record.delete()
            self.stdout.write(self.style.SUCCESS(f'Cleaned duplicates for student {student_id} on {date}'))

        self.stdout.write(self.style.SUCCESS('Duplicate cleaning complete'))