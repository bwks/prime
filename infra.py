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

        self.pi.headers.update({'Accept': 'application/json'})

        return self.pi.get('{0}/Devices'.format(self.url_base))
