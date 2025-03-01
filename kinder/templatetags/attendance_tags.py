from django import template

register = template.Library()

@register.simple_tag
def get_attendance_color(day, attendance):
    """
    Returns a background color based on attendance status for a given day.
    """
    if day == 0:
        return 'transparent'  
    status = attendance.get(day, '')
    return {
        'present': '#d4edda', 
        'absent': '#f8d7da',   
    }.get(status, '#ffffff')   