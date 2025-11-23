"""
Security Middleware for Herberry E-commerce
- Rate limiting
- IP blocking
- Suspicious activity detection
- Request logging
"""

import logging
import time
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings
from collections import defaultdict

logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """
    Rate limiting middleware - istekleri sınırlar

    Limitleri:
    - Genel: 100 istek / dakika / IP
    - Login: 5 deneme / 15 dakika / IP
    - Register: 3 kayit / saat / IP
    - API: 60 istek / dakika / IP
    """

    def __init__(self, get_response):
        self.get_response = get_response

        # Rate limit kuralları
        self.rate_limits = {
            'default': (100, 60),  # 100 istek / dakika
            'api': (60, 60),  # 60 istek / dakika
            'auth_login': (5, 900),  # 5 deneme / 15 dakika
            'auth_register': (3, 3600),  # 3 kayit / saat
            'cart': (30, 60),  # 30 istek / dakika
            'orders': (10, 60),  # 10 sipariş / dakika
        }

    def __call__(self, request):
        # Whitelist kontrolü (admin, static files)
        if self._is_whitelisted(request):
            return self.get_response(request)

        # IP al
        ip = self._get_client_ip(request)

        # IP blacklist kontrolü
        if self._is_blacklisted(ip):
            logger.warning(f"Blocked request from blacklisted IP: {ip}")
            return JsonResponse({
                'error': 'Access denied',
                'detail': 'Your IP has been blocked due to suspicious activity'
            }, status=403)

        # Rate limit kontrolü
        rate_limit_key = self._get_rate_limit_key(request)
        if self._is_rate_limited(ip, rate_limit_key):
            logger.warning(f"Rate limit exceeded for IP {ip} on {rate_limit_key}")
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'detail': 'Too many requests. Please try again later.'
            }, status=429)

        # Request logla
        self._log_request(request, ip)

        # Response
        response = self.get_response(request)

        # Rate limit header'ları ekle
        self._add_rate_limit_headers(response, ip, rate_limit_key)

        return response

    def _get_client_ip(self, request):
        """Gerçek IP adresini al"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def _is_whitelisted(self, request):
        """Whitelist kontrolü"""
        path = request.path

        # Static ve media dosyalar
        if path.startswith('/static/') or path.startswith('/media/'):
            return True

        # Admin paneli (opsiyonel - kaldırabilirsin)
        # if path.startswith('/admin/'):
        #     return True

        return False

    def _is_blacklisted(self, ip):
        """IP blacklist kontrolü"""
        blacklist_key = f'ip_blacklist:{ip}'
        return cache.get(blacklist_key, False)

    def _get_rate_limit_key(self, request):
        """Hangi rate limit kuralını kullanacağını belirle"""
        path = request.path

        if '/api/v1/auth/login' in path:
            return 'auth_login'
        elif '/api/v1/auth/register' in path:
            return 'auth_register'
        elif '/api/v1/cart' in path:
            return 'cart'
        elif '/api/v1/orders' in path:
            return 'orders'
        elif path.startswith('/api/'):
            return 'api'
        else:
            return 'default'

    def _is_rate_limited(self, ip, rate_limit_key):
        """Rate limit kontrolü"""
        max_requests, time_window = self.rate_limits.get(rate_limit_key, self.rate_limits['default'])

        cache_key = f'rate_limit:{rate_limit_key}:{ip}'

        # Mevcut istek sayısını al
        request_count = cache.get(cache_key, 0)

        if request_count >= max_requests:
            return True

        # İstek sayısını artır
        cache.set(cache_key, request_count + 1, time_window)

        return False

    def _log_request(self, request, ip):
        """Request logla (suspicious activity detection için)"""
        # Şüpheli aktivite tespiti
        suspicious = self._detect_suspicious_activity(request, ip)

        if suspicious:
            logger.warning(
                f"Suspicious activity detected - IP: {ip}, "
                f"Path: {request.path}, Method: {request.method}"
            )

            # 10 şüpheli aktivite = blacklist
            suspicious_count_key = f'suspicious_count:{ip}'
            suspicious_count = cache.get(suspicious_count_key, 0)

            if suspicious_count >= 10:
                blacklist_key = f'ip_blacklist:{ip}'
                cache.set(blacklist_key, True, 86400)  # 24 saat blacklist
                logger.error(f"IP {ip} has been blacklisted due to repeated suspicious activity")
            else:
                cache.set(suspicious_count_key, suspicious_count + 1, 3600)

    def _detect_suspicious_activity(self, request, ip):
        """Şüpheli aktivite tespiti"""
        suspicious = False

        # SQL injection patterns
        sql_patterns = ['SELECT', 'UNION', 'DROP', 'INSERT', '--', ';--']
        query_string = request.GET.urlencode().upper()

        if any(pattern in query_string for pattern in sql_patterns):
            suspicious = True

        # XSS patterns
        xss_patterns = ['<script', 'javascript:', 'onerror=', 'onload=']
        full_path = request.get_full_path().lower()

        if any(pattern in full_path for pattern in xss_patterns):
            suspicious = True

        # Unusual user agents
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        suspicious_agents = ['curl', 'wget', 'python-requests', 'bot', 'scanner']

        if any(agent in user_agent for agent in suspicious_agents):
            suspicious = True

        return suspicious

    def _add_rate_limit_headers(self, response, ip, rate_limit_key):
        """Rate limit bilgilerini response header'a ekle"""
        max_requests, time_window = self.rate_limits.get(rate_limit_key, self.rate_limits['default'])
        cache_key = f'rate_limit:{rate_limit_key}:{ip}'

        request_count = cache.get(cache_key, 0)
        remaining = max(0, max_requests - request_count)

        response['X-RateLimit-Limit'] = str(max_requests)
        response['X-RateLimit-Remaining'] = str(remaining)
        response['X-RateLimit-Reset'] = str(time_window)

        return response


class SecurityHeadersMiddleware:
    """
    Güvenlik header'ları ekler
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'

        # Content Security Policy (sadece production'da)
        if not settings.DEBUG:
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            )

        return response


class RequestLoggingMiddleware:
    """
    Tüm API isteklerini loglar (monitoring için)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Request başlangıç zamanı
        start_time = time.time()

        # IP al
        ip = self._get_client_ip(request)

        # Request işle
        response = self.get_response(request)

        # Süre hesapla
        duration = time.time() - start_time

        # Sadece API isteklerini logla
        if request.path.startswith('/api/'):
            logger.info(
                f"API Request - "
                f"IP: {ip} | "
                f"Method: {request.method} | "
                f"Path: {request.path} | "
                f"Status: {response.status_code} | "
                f"Duration: {duration:.2f}s | "
                f"User: {request.user if request.user.is_authenticated else 'Anonymous'}"
            )

        # Yavaş istekleri özellikle logla
        if duration > 2.0:
            logger.warning(
                f"Slow request detected - "
                f"Path: {request.path} | "
                f"Duration: {duration:.2f}s"
            )

        return response

    def _get_client_ip(self, request):
        """Gerçek IP adresini al"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip