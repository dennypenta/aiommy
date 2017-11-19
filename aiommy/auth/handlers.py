import hashlib
import hmac
import json
from urllib import error, parse, request

PROVIDERS = (
    'facebook',
    'google'
)


class OAuthException(Exception):
    pass


class ApiDeprecatedError(Exception):
    pass


class OAuthProfile(object):
    def __init__(self, oauth_id=None, first_name=None, last_name=None,
                 email=None, photo=None, thumbnail=None):
        if not oauth_id:
            RuntimeError('You should transfer "oauth_id " param, usualy "id"')

        self.oauth_id = oauth_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.photo = photo
        self.thumbnail = thumbnail

    def __eq__(self, other):
        if not isinstance(other, OAuthProfile):
            return False

        return all([self.oauth_id == other.oauth_id,
                    self.first_name == other.first_name,
                    self.last_name == other.last_name,
                    self.email == other.email,
                    self.photo == other.email,
                    self.thumbnail == other.thumbnail])

    def to_dict(self):
        return dict(
            oauth_id=self.oauth_id,
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            photo=self.photo,
            thumbnail=self.thumbnail,
        )


class BaseOAuthGateway(object):
    def make_request(self, url, method):
        raise NotImplementedError

    def error_handler(self, err):
        raise NotImplementedError


class OAuthGateway(BaseOAuthGateway):
    def make_request(self, url, method):
        req = request.Request(
            url,
            method=method
        )

        try:
            response = self._send_request(req)
        except error.HTTPError as err:
            self.error_handler(err)

        data = response.read()
        response.close()
        return data

    def error_handler(self, err):
        err.close()
        raise OAuthException()

    def _send_request(self, req):
        return request.urlopen(req)


class FacebookOAuthGateway(OAuthGateway):
    def error_handler(self, err):
        msg = err.read().decode('utf-8')
        err.close()
        raise OAuthException(msg)


class GoogleOAuthGateway(OAuthGateway):
    def error_handler(self, err):
        err.close()
        raise OAuthException('{"error": {"message": "Google oauth wrong token"}}')


class AbstractOAuthDispatcher(object):
    oauth_gateway = OAuthGateway()

    def __init__(self, id, secret, oauth_gateway=None):
        self.id = id,
        self.secret = secret
        if oauth_gateway:
            self.oauth_gateway = oauth_gateway

    def normalize(self, profile):
        raise NotImplementedError()

    def me(self, access_token):
        raise NotImplementedError()


class FacebookDispatcher(AbstractOAuthDispatcher):
    url = 'https://graph.facebook.com/v2.11/'
    oauth_gateway = FacebookOAuthGateway()

    def normalize(self, profile):
        thumbnail = profile.get('picture').get('data').get('url') or \
                    f'{self.url}{profile.get("id")}/picture?type=normal'
        return OAuthProfile(
            oauth_id=profile.get('id'),
            first_name=profile.get('first_name'),
            last_name=profile.get('last_name'),
            email=profile.get('email'),
            photo=f'{self.url}{profile.get("id")}/picture?width=320&height=480',
            thumbnail=thumbnail,
        )

    def me(self, access_token):
        profile = self._fetch_profile(access_token)
        return self.normalize(profile)

    def _make_secret_proof(self, token):
        return hmac.new(
            self.secret.encode('utf-8'),
            msg=token.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

    def _fetch_id(self, access_token):
        query_string = parse.urlencode(dict(
            access_token=access_token,
            appsecret_proof=self._make_secret_proof(access_token),
            batch='[{"method": "GET", "relative_url":"me"}]'
        ))
        url = f'{self.url}?{query_string}'

        data = self._make_request(url, 'POST')

        try:
            data = json.loads(data)[0]
            body = json.loads(data.get('body'))
        except (IndexError, json.JSONDecodeError) as err:
            raise ApiDeprecatedError(err)

        return body.get('id')

    def _fetch_profile(self, access_token):
        id = self._fetch_id(access_token)
        fields = 'first_name,last_name,email,picture'
        url = f'{self.url}{id}/?fields={fields}&access_token={access_token}&' \
              f'appsecret_proof={self._make_secret_proof(access_token)}'

        data = self.oauth_gateway.make_request(url, 'GET')
        data = json.loads(data)
        return data

    def _make_request(self, url, method):
        return self.oauth_gateway.make_request(url, method)


class GoogleDispatcher(AbstractOAuthDispatcher):
    oauth_gateway = GoogleOAuthGateway()

    def normalize(self, profile):
        return OAuthProfile(
            oauth_id=profile.get('id'),
            first_name=profile.get('given_name'),
            last_name=profile.get('family_name'),
            email=profile.get('email'),
            photo=profile.get('picture'),
            thumbnail=profile.get('picture'),
        )

    def me(self, access_token):
        profile = self._fetch_profile(access_token)
        return self.normalize(profile)

    def _fetch_profile(self, access_token):
        url = f'https://www.googleapis.com/oauth2/v1/userinfo?' \
              f'alt=json&access_token={access_token}'
        data = self.oauth_gateway.make_request(url, 'GET')
        return json.loads(data.decode('utf-8'))


class OAuthUrlDispatcher(object):
    def __init__(self, facebook=None, google=None):
        if facebook:
            if not isinstance(facebook, FacebookDispatcher):
                raise TypeError('`facebook` argument should be '
                                'instance of `FacebookDispatcher`')
            self.facebook = facebook

        if google:
            if not isinstance(google, GoogleDispatcher):
                raise TypeError('`google` argument should be instance '
                                'of `GoogleDispatcher`')
            self.google = google

    def get_dispatcher(self, provider):
        self._check_provider(provider)

        if not hasattr(self, provider):
            raise AttributeError(f'You should set provider {provider}')

        return getattr(self, provider)

    def _check_provider(self, provider):
        if provider not in PROVIDERS:
            raise TypeError(f'Provider should be one of {PROVIDERS}')
