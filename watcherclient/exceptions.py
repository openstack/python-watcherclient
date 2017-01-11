#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from watcherclient.common.apiclient import exceptions


# NOTE(akurilin): This alias is left here since v.0.1.3 to support backwards
# compatibility.
InvalidEndpoint = exceptions.EndpointException
CommunicationError = exceptions.ConnectionRefused
HTTPBadRequest = exceptions.BadRequest
HTTPInternalServerError = exceptions.InternalServerError
HTTPNotFound = exceptions.NotFound
HTTPServiceUnavailable = exceptions.ServiceUnavailable


CommandError = exceptions.CommandError
"""Error in CLI tool.

An alias of :py:exc:`watcherclient.common.apiclient.CommandError`
"""

Unauthorized = exceptions.Unauthorized
"""HTTP 401 - Unauthorized.

Similar to 403 Forbidden, but specifically for use when authentication
is required and has failed or has not yet been provided.
An alias of :py:exc:`watcherclient.common.apiclient.Unauthorized`
"""

InternalServerError = exceptions.InternalServerError
"""HTTP 500 - Internal Server Error.

A generic error message, given when no more specific message is suitable.
An alias of :py:exc:`watcherclient.common.apiclient.InternalServerError`
"""

ValidationError = exceptions.ValidationError
"""Error in validation on API client side.

A generic error message, given when no more specific message is suitable.
An alias of :py:exc:`watcherclient.common.apiclient.ValidationError`
"""

Conflict = exceptions.Conflict
ConnectionRefused = exceptions.ConnectionRefused
EndpointException = exceptions.EndpointException
EndpointNotFound = exceptions.EndpointNotFound
ServiceUnavailable = exceptions.ServiceUnavailable


class UnsupportedVersion(Exception):
    """Unsupported API Version

    Indicates that the user is trying to use an unsupported version of the API.
    """
    pass


class AmbiguousAuthSystem(exceptions.ClientException):
    """Could not obtain token and endpoint using provided credentials."""
    pass

# Alias for backwards compatibility
AmbigiousAuthSystem = AmbiguousAuthSystem


class InvalidAttribute(exceptions.ClientException):
    pass


def from_response(response, message=None, traceback=None, method=None,
                  url=None):
    """Return an HttpError instance based on response from httplib/requests."""

    error_body = {}
    if message:
        error_body['message'] = message
    if traceback:
        error_body['details'] = traceback

    if hasattr(response, 'status') and not hasattr(response, 'status_code'):
        # NOTE(akurilin): These modifications around response object give
        # ability to get all necessary information in method `from_response`
        # from common code, which expecting response object from `requests`
        # library instead of object from `httplib/httplib2` library.
        response.status_code = response.status
        response.headers = {
            'Content-Type': response.getheader('content-type', "")}

    if hasattr(response, 'status_code'):
        # NOTE(hongbin): This allows SessionClient to handle faultstring.
        response.json = lambda: {'error': error_body}

    if (response.headers.get('Content-Type', '').startswith('text/') and
            not hasattr(response, 'text')):
        # NOTE(clif_h): There seems to be a case in the
        # common.apiclient.exceptions module where if the
        # content-type of the response is text/* then it expects
        # the response to have a 'text' attribute, but that
        # doesn't always seem to necessarily be the case.
        # This is to work around that problem.
        response.text = ''

    return exceptions.from_response(response, method, url)
