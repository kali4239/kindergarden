from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, None)

@register.filter
def get_attendance_for_student(attendance_records, student_id):
    return attendance_records.filter(student_id=student_id)

@register.filter
def get_attendance_for_date(attendance_records, date):
    return attendance_records.filter(date=date).first()

@register.filter
def get_attendance_color(attendance):
    if attendance.status == 'present':
        return 'green'
    elif attendance.status == 'absent':
        return 'red'
    else:
        return 'yellow'
