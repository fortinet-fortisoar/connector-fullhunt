""" Copyright start
  Copyright (C) 2008 - 2023 Fortinet Inc.
  All rights reserved.
  FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
  Copyright end """
import requests
from connectors.core.connector import get_logger, ConnectorError
from requests import exceptions as req_exceptions
logger = get_logger('fullhunt')


class FullHunt(object):

    def __init__(self, config):
        self.server_url = config.get('server_url').strip()
        self.api_key = config.get('api_key')
        self.headers = {'accept': 'application/json', 'X-API-KEY': self.api_key}
        if not self.server_url.startswith('https://'):
            self.server_url = 'https://{0}'.format(self.server_url)
        if self.server_url.endswith('/'):
            self.server_url = self.server_url[:-1]

    def make_api_call(self, endpoint=None, method='GET', headers=None, health_check=False):
        url = self.server_url + endpoint
        if headers:
            self.headers.update(headers)
        try:
            logger.debug('Making a request with {0} - {1} and headers - {2}'.format(method, url, self.headers))
            response = requests.request(method, url, headers=self.headers)
            if health_check and response.status_code == 200:
                return response
            elif response.status_code in (200, 400, 404):
                try:
                    return response.json()
                except Exception:
                    raise ConnectorError({'status_code': str(response.status_code), 'response': response.content})
            else:
                logger.error('Failed with response {0}'.format(response))
                raise ConnectorError(
                    {'status': 'Failure', 'status_code': str(response.status_code), 'response': response.content})
        except req_exceptions.SSLError:
            logger.error('An SSL error occurred')
            raise ConnectorError('An SSL error occurred')
        except req_exceptions.ConnectionError:
            logger.error('A connection error occurred')
            raise ConnectorError('A connection error occurred')
        except req_exceptions.Timeout:
            logger.error('The request timed out')
            raise ConnectorError('The request timed out')
        except req_exceptions.RequestException:
            logger.error('There was an error while handling the request')
            raise ConnectorError('There was an error while handling the request')
        except Exception as err:
            raise ConnectorError(str(err))


def get_domain_details(config, params):
    """
    Retrieves a list of all details, subdomains, associated hosts, DNS records, exposed ports from fullhunt.
    :param config: config
    :param params: params
    :return: List of all details, subdomains, associated hosts, DNS records, exposed ports from fullhunt Feed.
    """
    obj = FullHunt(config)
    endpoint = '/api/v1/domain/{0}/details'.format(params.get('domain'))
    return obj.make_api_call(endpoint=endpoint)


def get_subdomain_of_domain(config, params):
    """
    Retrieves a list of all discovered subdomains/hosts for a given domain from fullhunt.
    :param config: config
    :param params: params
    :return: List of all discovered subdomains/hosts for a given domain from fullhunt Feed.
    """
    obj = FullHunt(config)
    endpoint = '/api/v1/domain/{0}/subdomains'.format(params.get('domain'))
    return obj.make_api_call(endpoint=endpoint)


def get_specific_host_details(config, params):
    """
    Retrieves details for a given host from fullhunt.
    :param config: config
    :param params: params
    :return: Details for a given host from fullhunt Feed.
    """
    obj = FullHunt(config)
    endpoint = '/api/v1/host/{0}'.format(params.get('host'))
    return obj.make_api_call(endpoint=endpoint)


def _check_health(config):
    try:
        obj = FullHunt(config)
        obj.make_api_call(endpoint='/api/v1/auth/status', health_check=True)
        return True
    except Exception as err:
        logger.exception('Health check failed with: {0}'.format(err))
        raise ConnectorError('Health check failed with: {0}'.format(err))


operations = {
    'get_domain_details': get_domain_details,
    'get_subdomain_of_domain': get_subdomain_of_domain,
    'get_specific_host_details': get_specific_host_details
}
