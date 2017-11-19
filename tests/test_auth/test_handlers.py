import io
import json
import unittest
from unittest import mock
from urllib import error

from aiommy.auth.handlers import (ApiDeprecatedError, FacebookDispatcher,
                                  GoogleDispatcher, OAuthException,
                                  OAuthGateway, OAuthProfile)


class OtherOAuthGatewayTestCase(unittest.TestCase):
    gateway = OAuthGateway()

    url = 'http://url'
    method = 'GET'

    def test_make_request_ok(self):
        def send_request(request):
            return io.BytesIO(expected)

        expected = b'response'

        with mock.patch.object(self.gateway,
                               '_send_request',
                               side_effect=send_request) as mocked_response:
            data = self.gateway.make_request(self.url, self.method)
            self.assertEqual(expected, data)

            mocked_response.assert_called_once()

    def test_make_request_oauth_exception(self):
        def send_request(request):
            raise error.HTTPError(self.url, 400, 'msg', {}, io.BytesIO(b'msg'))

        with mock.patch.object(self.gateway,
                               '_send_request',
                               side_effect=send_request) as mocked_response:
            with self.assertRaises(OAuthException):
                self.gateway.make_request(self.url, self.method)

            mocked_response.assert_called_once()

    def test_error_handler(self):
        with self.assertRaises(OAuthException):
            self.gateway.error_handler(io.BytesIO())

    def test_error_handler_closing_error(self):
        http_err = error.HTTPError('url', 'GET', 400, {}, io.BytesIO())
        self.assertFalse(http_err.closed)

        try:
            self.gateway.error_handler(http_err)
        except OAuthException:
            self.assertTrue(http_err.closed)


class OAuthProfileTestCase(unittest.TestCase):
    def test_profile(self):
        expected = dict(
            oauth_id='oauth_id',
            first_name='first_name',
            last_name='last_name',
            email='email',
            photo='photo',
            thumbnail='thumbnail',
        )
        profile = OAuthProfile(**expected)

        self.assertEqual(profile.to_dict(), expected)

    def test_empty_profile(self):
        expected = dict(
            oauth_id=None,
            first_name=None,
            last_name=None,
            email=None,
            photo=None,
            thumbnail=None,
        )
        profile = OAuthProfile()

        self.assertEqual(profile.to_dict(), expected)


class FacebookDispatcherTestCase(unittest.TestCase):
    dispatcher = FacebookDispatcher('id', 'secret')

    def test_me(self):
        data = dict(oauth_id=123)
        expected = OAuthProfile(**data)
        access_token = 'access_token'

        with mock.patch.object(self.dispatcher,
                               '_fetch_profile',
                               return_value=data) as mocked_fetch, \
                mock.patch.object(self.dispatcher,
                                  'normalize',
                                  side_effect=lambda p: OAuthProfile(**p)) as mocked_normalize:
            me = self.dispatcher.me(access_token)

            mocked_fetch.assert_called_once_with(access_token)
            mocked_normalize.assert_called_once_with(data)

        self.assertEqual(expected, me)

    def test_normalize(self):
        profile_keys = ('oauth_id', 'first_name', 'last_name', 'email', 'photo', 'thumbnail')
        profile = dict(
            oauth_id='oauth_id',
            first_name='first_name',
            last_name='last_name',
            email='email',
            picture=dict(data=dict(url='url'))
        )
        normalized = self.dispatcher.normalize(profile).to_dict()
        for key in profile_keys:
            self.assertIn(key, normalized)

    def test_oauth_exception(self):
        err_msg = b'msg'

        def raiser(req):
            raise error.HTTPError('url', 400, 'msg', {}, io.BytesIO(err_msg))

        with mock.patch.object(self.dispatcher.oauth_gateway,
                               '_send_request',
                               side_effect=raiser) as mocked_request:
            with self.assertRaises(OAuthException):
                self.dispatcher.me('access_token')

            mocked_request.assert_called_once()

    def test_oauth_exception_message_proxied(self):
        err_msg = b'msg'

        def raiser(req):
            raise error.HTTPError('url', 400, 'msg', {}, io.BytesIO(err_msg))

        with mock.patch.object(self.dispatcher.oauth_gateway,
                               '_send_request',
                               side_effect=raiser) as mocked_request:
            try:
                self.dispatcher.me('access_token')
            except OAuthException as err:
                self.assertEqual(str(err), err_msg.decode('utf-8'))
            mocked_request.assert_called_once()

    def test_api_deprecated_error(self):
        def raiser(t):
            raise ApiDeprecatedError('msg')
        access_token = 'access_token'

        with mock.patch.object(self.dispatcher,
                               '_fetch_id',
                               side_effect=raiser) as mocked_fetch:
            with self.assertRaises(ApiDeprecatedError):
                self.dispatcher.me(access_token)

            mocked_fetch.assert_called_once_with(access_token)


class GoogleDispatcherTestCase(unittest.TestCase):
    dispatcher = GoogleDispatcher('id', 'secret')

    def test_me(self):
        data = dict(oauth_id=123)
        expected = OAuthProfile(**data)
        access_token = 'access_token'

        with mock.patch.object(self.dispatcher,
                               '_fetch_profile',
                               return_value=data) as mocked_fetch, \
                mock.patch.object(self.dispatcher,
                                  'normalize',
                                  side_effect=lambda p: OAuthProfile(**p)) as mocked_normalize:
            me = self.dispatcher.me(access_token)

            mocked_fetch.assert_called_once_with(access_token)
            mocked_normalize.assert_called_once_with(data)

        self.assertEqual(expected, me)

    def test_normalize(self):
        profile_keys = ('oauth_id', 'first_name', 'last_name', 'email', 'photo', 'thumbnail')
        profile = dict(
            oauth_id='oauth_id',
            first_name='first_name',
            last_name='last_name',
            email='email',
            picture=dict(data=dict(url='url'))
        )
        normalized = self.dispatcher.normalize(profile).to_dict()
        for key in profile_keys:
            self.assertIn(key, normalized)

    def test_oauth_exception(self):
        err_msg = b'msg'

        def raiser(req):
            raise error.HTTPError('url', 400, 'msg', {}, io.BytesIO(err_msg))

        with mock.patch.object(self.dispatcher.oauth_gateway,
                               '_send_request',
                               side_effect=raiser) as mocked_request:
            with self.assertRaises(OAuthException):
                self.dispatcher.me('access_token')

            mocked_request.assert_called_once()

    def test_oauth_exception_message(self):
        def raiser(req):
            raise error.HTTPError('url', 400, 'msg', {}, io.BytesIO(b'ANY MESSAGE'))

        with mock.patch.object(self.dispatcher.oauth_gateway,
                               '_send_request',
                               side_effect=raiser) as mocked_request:
            try:
                self.dispatcher.me('access_token')
            except OAuthException as err:
                err_msg = json.loads(str(err))
                self.assertIn('error', err_msg)
                self.assertIn('message', err_msg.get('error'))
            mocked_request.assert_called_once()

    def test_api_deprecated_error(self):
        def raiser(t):
            raise ApiDeprecatedError('msg')
        access_token = 'access_token'

        with mock.patch.object(self.dispatcher,
                               '_fetch_profile',
                               side_effect=raiser) as mocked_fetch:
            with self.assertRaises(ApiDeprecatedError):
                self.dispatcher.me(access_token)

            mocked_fetch.assert_called_once_with(access_token)
