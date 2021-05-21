import json
import requests


class HTTPNitro():
    def __init__(self, nsip, nsuser='nsroot', nspass='', nitro_protocol='https', ns_api_path='nitro/v1/config'):
        self.nitro_protocol = nitro_protocol
        self.api_path = ns_api_path
        self.nsip = nsip
        self.nsuser = nsuser
        self.nspass = nspass
        self.ssl_verify = False  # FIXME: validate Certificate

        self.headers = {}
        self.headers['Content-Type'] = 'application/json'
        self.headers['X-NITRO-USER'] = self.nsuser
        self.headers['X-NITRO-PASS'] = self.nspass

    def construct_url(self, resource, id=None, action=None, args=None):
        # Construct basic get url
        url = '%s://%s/%s/%s' % (
            self.nitro_protocol,
            self.nsip,
            self.api_path,
            resource,
        )

        # Append resource id
        if id is not None:
            url = '%s/%s' % (url, id)

        # Append action
        if action is not None:
            url = '%s?action=%s' % (url, action)
        elif args is not None:
            url = '%s?args=%s' % (url, args)

        return url

    def check_connection(self):
        url = self.construct_url(resource='login')

        headers = {}
        headers['Content-Type'] = 'application/json'
        payload = {
            "login": {
                "username": self.nsuser,
                "password": self.nspass
            }
        }
        try:
            print('post_data: {}'.format(json.dumps(payload, indent=4)))
            print('HEADERS: {}'.format(
                json.dumps(self.headers, indent=4)))
            r = requests.post(url=url, headers=headers,
                              json=payload, verify=self.ssl_verify)
            response = r.json()
            print("do_login response: {}".format(
                json.dumps(response, indent=4)))
            if response['severity'] == 'ERROR':
                print('Could not login to {} with user:{} and passwd:{}'.format(
                    self.nsip, self.nsuser, self.nspass))
                print('{}: {}'.format(
                    response['errorcode'], response['message']))
                return False
            return True
        except Exception as e:
            print(
                'Node {} is not reachable. Reason:{}'.format(self.nsip, str(e)))
            return False

    def do_get(self, resource, id=None, action=None):
        url = self.construct_url(resource, id, action)
        print('GET {}'.format(url))
        print('HEADERS: {}'.format(json.dumps(self.headers, indent=4)))

        r = requests.get(
            url=url,
            headers=self.headers,
            verify=self.ssl_verify,
        )
        if r.status_code == 200:
            response = r.json()
            print("do_get response: {}".format(
                json.dumps(response, indent=4)))
            return response
        else:
            print('GET failed: {}'.format(r.text))
            return False

    def do_post(self, data, id=None, action=None):
        resource = list(data)[0]
        url = self.construct_url(resource, id, action)
        print('POST {}'.format(url))
        print('POST data: {}'.format(json.dumps(data, indent=4)))
        print('HEADERS: {}'.format(json.dumps(self.headers, indent=4)))

        r = requests.post(
            url=url,
            headers=self.headers,
            json=data,
            verify=self.ssl_verify
        )
        # print(r.text)
        print(r.status_code)
        if r.status_code == 201 or r.status_code == 200:
            return True
        else:
            print('POST failed: {}'.format(r.text))
            return False

    def do_put(self, data, id=None, action=None):
        resource = list(data)[0]
        url = self.construct_url(resource, id, action)
        print('PUT {}'.format(url))
        print('PUT data: {}'.format(json.dumps(data, indent=4)))
        print('HEADERS: {}'.format(json.dumps(self.headers, indent=4)))

        r = requests.put(
            url=url,
            headers=self.headers,
            json=data,
            verify=self.ssl_verify
        )
        if r.status_code == 201 or r.status_code == 200:
            return True
        else:
            print('PUT failed: {}'.format(r.text))
            return False

    def do_delete(self, resource, id=None, action=None, args=None):
        url = self.construct_url(resource, id, action, args)
        print('DELETE {}'.format(url))
        print('HEADERS: {}'.format(json.dumps(self.headers, indent=4)))

        r = requests.delete(
            url=url,
            headers=self.headers,
            verify=self.ssl_verify
        )
        # response = r.json()
        # print("do_delete response: {}".format(
        #     json.dumps(response, indent=4)))
        if r.status_code == 200:
            return True
        else:
            print('DELETE failed: {}'.format(r.text))
            return False
