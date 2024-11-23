# context_processors.py
from .models import SiteStatus

def site_status(request):
    # Lấy bản ghi đầu tiên của SiteStatus (trạng thái trang web)
    site_status = SiteStatus.objects.first()

    # Nếu có bản ghi, trả về trạng thái của nó, nếu không thì coi như trang web không bị khóa
    return {
        'is_site_locked': not site_status.status if site_status else False
    }
