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

### Ansible Galaxy

The [Ansible Galaxy][] is a collection of third-party roles for ansible. You
can install ansible-cloudflare from the galaxy by executing the following command:

    ansible-galaxy install DrMegahertz.cloudflare

Please note that you'll have to add the role `DrMegahertz.cloudflare` to your
playbook to make use of the `cloudflare_domain` task.


### As a Git submodule

If you'd rather have all your provisioning code in one place you could also
add it to your playbook-repository as a [git submodule][].
This method doesn't require that you specify the role `DrMegahertz.cloudflare`
in your playbook. Just use the `cloudflare_domain` task directly.

    cd playbook-directory
    mkdir vendor
    git submodule add https://github.com/DrMegahertz/ansible-cloudflare.git vendor/ansible-cloudflare
    mkdir library
    ln -s vendor/ansible-cloudflare/library/cloudflare_domain.py library/cloudflare_domain.py

Playbook example
----------------

Save the following configuration into files with the specified names:

**cloudflare.yaml:**

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

**hosts:**

    # Dummy inventory for ansible
    localhost

Then run the playbook with the following command:

    ansible-playbook -i hosts cloudflare.yaml

The email and token parameters can also be specified by setting the
`CLOUDFLARE_API_EMAIL` and `CLOUDFLARE_API_TOKEN` environment variables.

[CloudFlare Client API documentation]: https://www.cloudflare.com/docs/client-api.html
[Ansible Galaxy]: https://galaxy.ansible.com/
[git submodule]: http://git-scm.com/book/en/v2/Git-Tools-Submodules
