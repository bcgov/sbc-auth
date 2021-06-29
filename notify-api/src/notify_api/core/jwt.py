"""Generic middleware."""
import json
import logging

import jwt
from jwt.algorithms import RSAAlgorithm
from six.moves.urllib.request import urlopen
from starlette.authentication import AuthCredentials, AuthenticationBackend, AuthenticationError, BaseUser
from werkzeug.contrib.cache import SimpleCache

from notify_api.core.settings import get_api_settings


logger = logging.getLogger(__name__)


class JWTUser(BaseUser):
    """JWT User."""

    def __init__(self, username: str, token: str, payload: dict) -> None:
        """Init."""
        self.username = username
        self.token = token
        self.payload = payload

    @property
    def is_authenticated(self) -> bool:
        """Authenticated."""
        return True

    @property
    def display_name(self) -> str:
        """Display name."""
        return self.username

    @property
    def identity(self) -> str:
        """Identity."""
        raise NotImplementedError()  # pragma: no cover


class JWTWrapper:  # pylint: disable=too-few-public-methods
    """Singleton wrapper for Flask JWTAuthenticationBackend."""

    __instance = None

    @staticmethod
    def get_instance():
        """Retrieve singleton JWTAuthenticationBackend."""
        if JWTWrapper.__instance is None:
            JWTWrapper()
        return JWTWrapper.__instance

    def __init__(self):
        """Virtually private constructor."""
        if JWTWrapper.__instance is not None:
            raise AuthenticationError('Attempt made to create multiple JWTWrappers')

        JWTWrapper.__instance = JWTAuthenticationBackend()


class JWTAuthenticationBackend(AuthenticationBackend):  # pylint: disable=too-many-instance-attributes
    """JWT authentication backend for AuthenticationMiddleware."""

    def __init__(self):
        """Initize app."""
        self.algorithm = 'RS256'
        self.prefix = 'bearer'
        self.well_known_config = None
        self.well_known_obj_cache = None
        self.jwks_uri = None
        self.issuer = None
        self.audience = None
        self.client_secret = None
        self.cache = None
        self.caching_enabled = False
        self.jwt_oidc_test_mode = False
        self.jwt_oidc_test_public_key_pem = None
        self.jwt_oidc_test_private_key_pem = None

    def init_app(self, test_mode: bool = False):
        """Initize app."""
        self.jwt_oidc_test_mode = test_mode
        #
        # CHECK IF WE'RE RUNNING IN TEST_MODE!!
        #
        if not self.jwt_oidc_test_mode:
            self.algorithm = get_api_settings().JWT_OIDC_ALGORITHMS

            # If the WELL_KNOWN_CONFIG is set, then go fetch the JWKS & ISSUER
            self.well_known_config = get_api_settings().JWT_OIDC_WELL_KNOWN_CONFIG
            if self.well_known_config:
                # try to get the jwks & issuer from the well known config
                with urlopen(url=self.well_known_config) as jurl:
                    self.well_known_obj_cache = json.loads(jurl.read().decode('utf-8'))

                self.jwks_uri = self.well_known_obj_cache['jwks_uri']
                self.issuer = self.well_known_obj_cache['issuer']
            else:

                self.jwks_uri = get_api_settings().JWT_OIDC_JWKS_URI
                self.issuer = get_api_settings().JWT_OIDC_ISSUER

            # Setup JWKS caching
            self.caching_enabled = get_api_settings().JWT_OIDC_CACHING_ENABLED
            if self.caching_enabled:
                self.cache = SimpleCache(default_timeout=get_api_settings().JWT_OIDC_JWKS_CACHE_TIMEOUT)

            self.audience = get_api_settings().JWT_OIDC_AUDIENCE
            self.client_secret = get_api_settings().JWT_OIDC_CLIENT_SECRET

    @classmethod
    def get_token_from_header(cls, authorization: str, prefix: str):
        """Get token from header."""
        try:
            scheme, token = authorization.split()
        except ValueError:
            raise AuthenticationError('Could not separate Authorization scheme and token')
        if scheme.lower() != prefix.lower():
            raise AuthenticationError(f'Authorization scheme {scheme} is not supported')
        return token

    async def authenticate(self, request):  # pylint: disable=arguments-renamed
        """Authenticate the token."""
        if 'Authorization' not in request.headers:
            return None

        auth = request.headers['Authorization']
        token = self.get_token_from_header(authorization=auth, prefix=self.prefix)

        if self.jwt_oidc_test_mode:
            # in test mode, use a publick key to decode token directly.
            try:
                payload = jwt.decode(str.encode(token), self.jwt_oidc_test_public_key_pem, algorithms=self.algorithm)
            except jwt.InvalidTokenError as e:
                raise AuthenticationError(str(e))
        else:
            #  in production mod, get the public key from jwks_url
            try:
                unverified_header = jwt.get_unverified_header(token)
            except jwt.PyJWTError:
                raise AuthenticationError('Invalid header: Use an RS256 signed JWT Access Token')
            if unverified_header['alg'] == 'HS256':
                raise AuthenticationError('Invalid header: Use an RS256 signed JWT Access Token')
            if 'kid' not in unverified_header:
                raise AuthenticationError('Invalid header: No KID in token header')

            rsa_key = self.get_rsa_key(self.get_jwks(), unverified_header['kid'])

            if not rsa_key and self.caching_enabled:
                # Could be key rotation, invalidate the cache and try again
                self.cache.delete('jwks')
                rsa_key = self.get_rsa_key(self.get_jwks(), unverified_header['kid'])

            if not rsa_key:
                raise AuthenticationError('invalid_header: Unable to find jwks key referenced in token')

            public_key = RSAAlgorithm.from_jwk(json.dumps(rsa_key))

            try:
                payload = jwt.decode(token, public_key, algorithms=self.algorithm, audience=self.audience)
            except jwt.InvalidTokenError as e:
                raise AuthenticationError(str(e))

        return AuthCredentials(['authenticated']), JWTUser(username=payload['username'], token=token,
                                                           payload=payload)

    def get_jwks(self):
        """Get jwks from well known config endpoint."""
        if self.caching_enabled:
            return self._get_jwks_from_cache()

        return self._fetch_jwks_from_url()

    def _get_jwks_from_cache(self):
        jwks = self.cache.get('jwks')
        if jwks is None:
            jwks = self._fetch_jwks_from_url()
            self.cache.set('jwks', jwks)
        return jwks

    def _fetch_jwks_from_url(self):
        with urlopen(url=self.jwks_uri) as jsonurl:
            return json.loads(jsonurl.read().decode('utf-8'))

    def get_rsa_key(self, jwks, kid):  # pylint: disable=no-self-use
        """Get a public key."""
        rsa_key = {}
        for key in jwks['keys']:
            if key['kid'] == kid:
                rsa_key = {
                    'kty': key['kty'],
                    'kid': key['kid'],
                    'use': key['use'],
                    'n': key['n'],
                    'e': key['e']
                }
        return rsa_key

    def create_testing_jwt(self, claims, header):
        """Create test jwt token."""
        token = jwt.encode(claims, self.jwt_oidc_test_private_key_pem, headers=header, algorithm='RS256')
        return token.decode('utf-8')

    def set_testing_keys(self, private_key, public_key):
        """Set test keys."""
        self.jwt_oidc_test_private_key_pem = private_key
        self.jwt_oidc_test_public_key_pem = public_key
