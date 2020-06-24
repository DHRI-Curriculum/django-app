

class CatchInternetExplorer:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        user_agent = request.META['HTTP_USER_AGENT'].lower()

        response = self.get_response(request)
        response.is_IE = ('trident' in user_agent) or ('msie' in user_agent)

        # Code to be executed for each request/response after
        # the view is called.

        return response