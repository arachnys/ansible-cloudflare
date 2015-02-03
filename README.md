ansible-cloudflare
==================

An ansible module for managing CloudFlare DNS records.

This module makes use of the rec\_new, rec\_edit, and rec\_delete API
calls, with the following parameters: z, type, id, name, content, ttl.
Other methods and parameters of the API have yet to be implemented.

Please see the [CloudFlare Client API documentation][] for more
information about the different methods and parameters available.

Installation
------------

    ansible-galaxy install DrMegahertz.cloudflare

Playbook example
----------------

Save the following configuration into files with the specified names:

**cloudflare.yaml**

    - hosts: localhost
      connection: local
      gather_facts: no
      roles:
        - DrMegahertz.cloudflare
      tasks:
        - name: Create DNS record www.example.com
          cloudflare_domain: >
            state=present
            name=www
            zone=example.com
            type=A
            content=127.0.0.1
            email=joe@example.com
            token=77a54a4c36858cfc10321fcfce22378e19e20

**hosts**

    # Dummy inventory for ansible
    localhost

Then run the playbook with the following command:

    ansible-playbook -i hosts cloudflare.yaml

The email and token parameters can also be specified by setting the
`CLOUDFLARE_API_EMAIL` and `CLOUDFLARE_API_TOKEN` environment variables.

  [CloudFlare Client API documentation]: https://www.cloudflare.com/docs/client-api.html
