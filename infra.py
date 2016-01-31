"""
Class to configure Cisco Prime Infrastructure via the API

Required:
requests
 - http://docs.python-requests.org/en/latest/

Version: 0.1.4
"""
import requests


class Prime(object):
    def __init__(self, pi_node, pi_user, pi_pass, verify=False, disable_warnings=False, timeout=2):
        """
        Class to manage Cisco prime infrastructure via the REST API
        :param pi_node: Prime IP address
        :param pi_user: Prime API User
        :param pi_pass: Prime API Password
        :param verify: Verify SSL certificate
        :param disable_warnings: Disable SSL warnings
        :param timeout: Request timeout value
        """
        self.pi_node = pi_node
        self.pi_user = pi_user
        self.pi_pass = pi_pass

        self.url_base = 'https://{0}/webacs/api/v1'.format(self.pi_node)
        self.pi = requests.session()
        self.pi.auth = (self.pi_user, self.pi_pass)
        self.pi.verify = verify  # http://docs.python-requests.org/en/latest/user/advanced/#ssl-cert-verification
        self.disable_warnings = disable_warnings
        self.timeout = timeout
        self.pi.headers.update({
            'Accept': 'application/json',
            'Connection': 'keep_alive',
            'Content_type': 'application/json',
        })

        if self.disable_warnings:
            requests.packages.urllib3.disable_warnings()

    def get_devices(self):
        """
        Get all devices
        :return: result dictionary
        """

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        resp = self.pi.get('{0}/data/Devices'.format(self.url_base))
        num_devices = resp.json()['queryResponse']['@count']

        if resp.status_code == 200 and num_devices > '1':
            result['success'] = True
            result['response'] = [i['$'] for i in resp.json()['queryResponse']['entityId']]
            return result
        if resp.status_code == 200 and num_devices == '1':
            result['success'] = True
            result['response'] = [resp.json()['queryResponse']['entityId']['$']]
            return result
        if resp.status_code == 200 and num_devices == '0':
            result['success'] = True
            result['response'] = []
            return result
        else:
            result['response'] = resp.json()
            result['error'] = resp.status_code
            return result

    def get_device(self, ip_address):
        """
        Get device details
        :param ip_address: Device IP address
        :return: Result dictionary
        """

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        resp = self.pi.get('{0}/data/Devices?ipAddress="{1}"'.format(self.url_base, ip_address))
        num_devices = resp.json()['queryResponse']['@count']

        if resp.status_code == 200 and num_devices == '1':
            dev_id = resp.json()['queryResponse']['entityId'][0]['$']
            resp = self.pi.get('{0}/data/Devices/{1}'.format(self.url_base, dev_id))
            if resp.status_code == 200:
                result['success'] = True
                result['response'] = resp.json()
                return result
            elif resp.status_code == 404:
                result['response'] = '{0} not found'.format(dev_id)
                result['error'] = resp.status_code
                return result
            else:
                result['response'] = resp.json()
                result['error'] = resp.status_code
                return result
        elif resp.status_code == 200 and num_devices == '0':
            result['response'] = '{0} not found'.format(ip_address)
            result['error'] = 404
            return result
        else:
            result['response'] = resp.json()
            result['error'] = resp.status_code
            return result

    def add_device(self,
                   ip_address,
                   netmask,
                   snmp_community='',
                   snmp_retry='2',
                   snmp_timeout='10',
                   snmp_version='2c'):
        """
        Add device via bulk import
        Looks like to only current way to add a device through the API is
        with a bulk import (lame).
        :param ip_address: IP Address of the device
        :param netmask: Subnet mask
        :param snmp_community: SNMP community
        :param snmp_retry: Number of SNMP retries
        :param snmp_timeout: SNMP timeout value
        :param snmp_version: SNMP version
        :return: result dictionary with bulk import job name as result value
        """
        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        payload = {'devicesImport': {'devices': {'device': {
            # 'credentialProfileName': 'String value',
            'ipAddress': ip_address,
            'networkMask': netmask,
            # 'protocol': 'String value',
        }}}}

        if snmp_version == '2c':
            if snmp_community == '':
                result['response'] = 'Must provide SNMP community when using SNMP version 2c'
                result['error'] = 'SNMP community cannot be blank if using SNMP version 2c'
                return result
            else:
                payload['devicesImport']['devices']['device'].update({
                    'snmpCommunity': snmp_community,
                    'snmpRetries': snmp_retry,
                    'snmpTimeout': snmp_timeout,
                    'snmpVersion': snmp_version})

        resp = self.pi.put('{0}/op/devices/bulkImport'.format(self.url_base), json=payload)

        if resp.status_code == 200:
            result['success'] = True
            result['response'] = resp.json()['mgmtResponse']['bulkImportResult']['jobName']
            return result
        else:
            result['response'] = resp.text
            result['error'] = resp.status_code

    def delete_device(self, ip_address):
        """
        Delete a device
        :param ip_address: IP Address of the device to delete
        :return: result dictionary
        """
        payload = {'deviceDeleteCandidates': {'ipAddresses': {'ipAddress': '{0}'.format(ip_address)}}}
        resp = self.pi.put('{0}/op/devices/deleteDevices'.format(self.url_base), json=payload)

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        status = resp.json()['mgmtResponse']['deleteDeviceResult']['deleteStatuses']['deleteStatus']['status']

        if resp.status_code == 200 and status == 'Success':
            result['success'] = True
            result['response'] = '{0} successfully deleted'.format(ip_address)
            return result
        elif resp.status_code == 200 and status == 'Failure':
            result['response'] = '{0} not found'.format(ip_address)
            result['error'] = 404
            return result
        else:
            result['response'] = resp.text
            result['error'] = resp.status_code
