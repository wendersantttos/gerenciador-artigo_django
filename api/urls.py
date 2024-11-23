from rest_framework.routers import DefaultRouter
from .views import ArtigoViewSet

router = DefaultRouter()
router.register(r'artigos', ArtigoViewSet)

urlpatterns = router.urls
