import requests


class Prime(object):
    def __init__(self, pi_node, pi_user, pi_pass, verify=False, disable_warnings=False, timeout=2):
        """

        :param pi_node:
        :param pi_user:
        :param pi_pass:
        :param verify:
        :param disable_warnings:
        :param timeout:
        :return:
        """
        self.pi_node = pi_node
        self.pi_user = pi_user
        self.pi_pass = pi_pass

        self.url_base = 'https://{0}/webacs/api/v1/data'.format(self.pi_node)
        self.pi = requests.session()
        self.pi.auth = (self.pi_user, self.pi_pass)
        self.pi.verify = verify  # http://docs.python-requests.org/en/latest/user/advanced/#ssl-cert-verification
        self.disable_warnings = disable_warnings
        self.timeout = timeout
        self.pi.headers.update({'Connection': 'keep_alive'})

        if self.disable_warnings:
            requests.packages.urllib3.disable_warnings()

    def get_devices(self):
        """
        Get all devices
        :return: result dictionary
        """
        self.pi.headers.update({'Accept': 'application/json'})

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        resp = self.pi.get('{0}/Devices'.format(self.url_base))

        if resp.status_code == 200:
            result['success'] = True
            result['response'] = [i['$'] for i in resp.json()['queryResponse']['entityId']]
            return result
        else:
            result['response'] = 'Error'
            result['error'] = resp.status_code
            return result

    def get_device(self, ip_address):
        """
        Get device details
        :param ip_address: Device IP address
        :return: Result dictionary
        """
        self.pi.headers.update({'Accept': 'application/json'})

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        resp = self.pi.get('{0}/Devices?ipAddress="{1}"'.format(self.url_base, ip_address))

        if resp.status_code == 200 and resp.json()['queryResponse']['@count'] == '1':
            dev_id = resp.json()['queryResponse']['entityId'][0]['$']
            resp = self.pi.get('{0}/Devices/{1}'.format(self.url_base, dev_id))
            if resp.status_code == 200:
                result['success'] = True
                result['response'] = resp.json()
                return result
            elif resp.status_code == 404:
                result['response'] = '{0} not found'.format(dev_id)
                result['error'] = resp.status_code
                return result
            else:
                result['response'] = resp.text
                result['error'] = resp.status_code
                return result
        elif resp.status_code == 200 and resp.json()['queryResponse']['@count'] == '0':
            result['response'] = '{0} not found'.format(ip_address)
            result['error'] = resp.status_code
            return result
        else:
            result['response'] = resp.text
            result['error'] = resp.status_code
            return result
