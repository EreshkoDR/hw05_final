from django.utils import timezone


def year(request):
    """Добавляет переменную с текущим годом."""
    date = timezone.now()
    return {
        'year': date.year,
    }
