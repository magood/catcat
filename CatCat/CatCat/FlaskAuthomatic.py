from authomatic import Authomatic
from authomatic.adapters import WerkzeugAdapter

#No longer necessary since nginx is fixed...
class FlaskAuthomatic(Authomatic):

    class ForceHTTPSWerkzeugAdapter(WerkzeugAdapter):
        @property
        def url(self):
            import re
            return re.sub(r'^http://', 'https://', self.request.base_url)

    result = None

    def login(self, *login_args, **login_kwargs):
        """
        Decorator for Flask view functions.
        """

        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                self.response = make_response()
                adapter = self.ForceHTTPSWerkzeugAdapter(request, self.response)
                login_kwargs.setdefault('session', session)
                login_kwargs.setdefault('session_saver', self.session_saver)
                self.result = super(FlaskAuthomatic, self).login(adapter, *login_args, **login_kwargs)
                return f(*args, **kwargs)
            return decorated
        return decorator

    def session_saver(self):
        session.modified = True