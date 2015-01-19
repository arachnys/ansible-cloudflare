#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib2
from urllib import urlencode

DOCUMENTATION = '''
---
module: cloudflare_domain
short_description: Create, edit or delete Cloudflare DNS records.
description:
  - Create, edit or delete Cloudflare DNS records.
author: Marcus Fredriksson <drmegahertz@gmail.com>
options:
  state:
    description:
      - Whether or not this record should be present in the given zone.
    default: present
    choices: ['present', 'absent']

  name:
    description:
      - Name of the DNS record. For example: www
    required: true

  zone:
    description:
      - The target domain to add this record to.
    required: true
    aliases: ['z']

  type:
    description:
      - Type of DNS record.
    required: true
    choices: ['A', 'CNAME', 'MX', 'TXT', 'SPF', 'AAAA', 'NS', 'SRV', 'LOC']

  content:
    description:
      - The content of the DNS record, will depend on the the type of record being added.
    required: true

  token:
    description:
      - This is the API key made available on your CloudFlare account page.
      - This can also be provided by setting the CLOUDFLARE_API_TOKEN environment variable.
    required: true
    aliases: ['tkn']

  email:
    description:
      - The e-mail address associated with the API key.
      - This can also be provided by setting the CLOUDFLARE_API_EMAIL environment variable.
    required: true
'''

EXAMPLES = '''
- cloudflare_domain: >
    state=present
    name=www
    zone=example.com
    type=A
    content=127.0.0.1
    email=joe@example.com
    token=77a54a4c36858cfc10321fcfce22378e19e20
'''

class CloudflareException(Exception):
    pass

class Cloudflare(object):
    def __init__(self, email, token):
        self.url   = 'https://www.cloudflare.com/api_json.html'
        self.email = email
        self.token = token

    def request(self, data):
        data += [('email', self.email),
                 ('tkn', self.token)]

        req = urllib2.urlopen(self.url, urlencode(data))
        response_json = json.loads(req.read())

        if response_json['result'] != 'success':
            raise CloudflareException(response_json['msg'])

        return response_json

    def rec_load_all(self, zone):
        data = [('a', 'rec_load_all'),
                ('z', zone)]

        return self.request(data)

    def rec_new(self, zone, type, name, content, ttl=1):
        data = [('a',       'rec_new'),
                ('z',       zone),
                ('type',    type),
                ('name',    name),
                ('content', content),
                ('ttl',     ttl)]

        return self.request(data)

    def rec_edit(self, id, zone, type, name, content, ttl=1):
        data = [('a',       'rec_edit'),
                ('id',      id),
                ('z',       zone),
                ('type',    type),
                ('name',    name),
                ('content', content),
                ('ttl',     ttl)]

        return self.request(data)

    def rec_delete(self, id, zone):
        data = [('a',  'rec_delete'),
                ('id', id),
                ('z',  zone)]

        return self.request(data)

def cloudflare_domain(module):
    cloudflare = Cloudflare(module.params['email'], module.params['token'])
    existing_records = cloudflare.rec_load_all(module.params['zone'])
    existing_records = existing_records['response']['recs']['objs']

    name = module.params['name'] + '.' + module.params['zone']
    record = filter(lambda x: x['name'] == name, existing_records)

    if module.params['state'] == 'present':
        if record:
            response = cloudflare.rec_edit(
                record[0]['rec_id'],
                module.params['zone'],
                module.params['type'],
                module.params['name'],
                module.params['content']
            )

            if record[0]['rec_hash'] == response['response']['rec']['obj']['rec_hash']:
                module.exit_json(changed=False)

            module.exit_json(changed=True)

        response = cloudflare.rec_new(
            module.params['zone'],
            module.params['type'],
            module.params['name'],
            module.params['content']
        )

        module.exit_json(changed=True)

    elif module.params['state'] == 'absent':
        if record:
            response = cloudflare.rec_delete(
                record[0]['rec_id'],
                record[0]['zone_name'],
            )

            module.exit_json(changed=True)

        module.exit_json(changed=False)

    module.fail_json(msg='Unknown value "{0}" for argument state. Expected one of: present, absent.')

def main():
    domain_types = ['A', 'CNAME', 'MX', 'TXT', 'SPF', 'AAAA', 'NS', 'SRV', 'LOC']

    module = AnsibleModule(
        argument_spec = dict(
            state   = dict(default='present', choices=['present', 'absent']),
            name    = dict(required=True),
            zone    = dict(required=True, aliases=['z']),
            type    = dict(required=True, choices=domain_types),
            content = dict(required=True),
            email   = dict(no_log=True, default=os.environ.get('CLOUDFLARE_API_EMAIL')),
            token   = dict(no_log=True, default=os.environ.get('CLOUDFLARE_API_TOKEN'), aliases=['tkn']),
        )
    )

    try:
        cloudflare_domain(module)
    except Exception as e:
        module.fail_json(msg=str(e))

from ansible.module_utils.basic import *
main()