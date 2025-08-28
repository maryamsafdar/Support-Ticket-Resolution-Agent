# API Errors
- 401 Unauthorized: Verify API key/permissions.
- 403 Forbidden: Check role scopes for the endpoint.
- 429 Too Many Requests: Respect rate limits, exponentially backoff, and reduce concurrency.
