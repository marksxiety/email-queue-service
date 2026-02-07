import pytest


class TestRateLimitConfig:
    """Test rate limiting configuration values"""

    def test_rate_limit_enabled_type(self):
        """Test rate limit enabled is a boolean"""
        from app.config import config
        assert isinstance(config.RATE_LIMIT_ENABLED, bool)

    def test_rate_limit_per_minute_positive(self):
        """Test rate limit per minute is positive"""
        from app.config import config
        assert config.RATE_LIMIT_PER_MINUTE > 0

    def test_rate_limit_per_hour_positive(self):
        """Test rate limit per hour is positive"""
        from app.config import config
        assert config.RATE_LIMIT_PER_HOUR > 0

    def test_rate_limit_hour_greater_than_minute(self):
        """Test hourly limit is greater than per-minute limit"""
        from app.config import config
        assert config.RATE_LIMIT_PER_HOUR >= config.RATE_LIMIT_PER_MINUTE

    def test_rate_limit_grace_period_non_negative(self):
        """Test grace period is non-negative"""
        from app.config import config
        assert config.RATE_LIMIT_GRACE_PERIOD_SECONDS >= 0

    def test_rate_limit_values_are_integers(self):
        """Test that rate limit values are integers"""
        from app.config import config

        assert isinstance(config.RATE_LIMIT_PER_MINUTE, int)
        assert isinstance(config.RATE_LIMIT_PER_HOUR, int)
        assert isinstance(config.RATE_LIMIT_GRACE_PERIOD_SECONDS, int)

    def test_global_rate_limits_exist(self):
        """Test that global rate limit config values exist"""
        from app.config import config

        assert hasattr(config, 'RATE_LIMIT_GLOBAL_PER_MINUTE')
        assert hasattr(config, 'RATE_LIMIT_GLOBAL_PER_HOUR')
        assert config.RATE_LIMIT_GLOBAL_PER_MINUTE > 0
        assert config.RATE_LIMIT_GLOBAL_PER_HOUR > 0

    def test_global_rate_limits_are_reasonable(self):
        """Test that global rate limits are higher than per-IP limits"""
        from app.config import config

        assert config.RATE_LIMIT_GLOBAL_PER_MINUTE >= config.RATE_LIMIT_PER_MINUTE
        assert config.RATE_LIMIT_GLOBAL_PER_HOUR >= config.RATE_LIMIT_PER_HOUR
