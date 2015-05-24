#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib2
from operator import itemgetter
from urllib import urlencode

DOCUMENTATION = '''
---
module: cloudflare_domain
short_description: Create or delete Cloudflare DNS records.
description:
  - Create or delete Cloudflare DNS records.
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
    def __init__(self, email, token, zone):
        self.url   = 'https://www.cloudflare.com/api_json.html'
        self.email = email
        self.token = token
        self.zone = zone

    def request(self, **kwargs):
        kwargs.update(email=self.email, tkn=self.token, z=self.zone)

        req = urllib2.urlopen(self.url, urlencode(kwargs))
        response_json = json.loads(req.read())

        if response_json['result'] != 'success':
            raise CloudflareException(response_json['msg'])

        return response_json

    def rec_load_all(self):
        return self.request(a='rec_load_all')

    def rec_new(self, type, name, content, ttl=1):
        return self.request(
            a='rec_new',
            type=type,
            name=name,
            content=content,
            ttl=ttl
        )

    def rec_delete(self, id):
        return self.request(a='rec_delete', id=id)

def cloudflare_domain(module):
    cloudflare = Cloudflare(module.params['email'], module.params['token'], module.params['zone'])
    existing_records = cloudflare.rec_load_all()
    existing_records = existing_records['response']['recs']['objs']

    get_record_attributes = itemgetter('name', 'type', 'content')
    name, type, content = get_record_attributes(module.params)

    if name != module.params['zone']:
        name += '.' + module.params['zone']

    record = filter(lambda x: get_record_attributes(x) == (name, type, content), existing_records)

    if module.params['state'] == 'present':
        if record:
            module.exit_json(changed=False, name=name, type=type, content=content)

        if not module.check_mode:
            response = cloudflare.rec_new(
                module.params['type'],
                module.params['name'],
                module.params['content']
            )

        module.exit_json(
            changed=True,
            name=module.params['name'],
            content=module.params['content'],
            type=module.params['type']
        )

    elif module.params['state'] == 'absent':
        if record:
            if not module.check_mode:
                response = cloudflare.rec_delete(record[0]['rec_id'])

            module.exit_json(
                changed=True,
                delete=record[0]['rec_id'],
                record={
                    name: record[0]['name'],
                    content: record[0]['content'],
                    type: record[0]['type']
                }
            )

        module.exit_json(changed=False, name=name, type=type, content=content)

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
        ),
        supports_check_mode=True,
    )

    try:
        cloudflare_domain(module)
    except Exception as e:
        module.fail_json(msg=str(e))

from ansible.module_utils.basic import *
main()
