import unittest

from mock import Mock, patch

from cloudflare_domain import cloudflare_domain


class ModuleExit(Exception):
    pass

class ModuleFail(Exception):
    pass

class TestCloudflareDomain(unittest.TestCase):
    def get_mock_module(self, **kwargs):
        check_mode = kwargs.pop('check_mode', False)

        mock_module_params = {
            'email': 'joe@example.com',
            'token': 'fc683cd9ed1990ca2ea10b84e5e6fba048c24',
            'zone': 'example.com',
            'name': 'home',
            'state': 'present',
            'type': 'A',
            'content': '127.0.0.1',
            'mode': None
        }

        mock_module_params.update(kwargs)

        return Mock(**{
            'params': mock_module_params,
            'exit_json.side_effect': ModuleExit,
            'fail_json.side_effect': ModuleFail,
            'check_mode': check_mode,
        })

    def setUp(self):
        self.mock_cloudflare_instance = Mock(**{
            'rec_load_all.return_value': {
                "msg": None,
                "request": {
                    "act": "rec_load_all"
                },
                "response": {
                    "recs": {
                        "count": 1,
                        "has_more": False,
                        "objs": [
                            {
                                "auto_ttl": 1,
                                "content": "127.0.0.1",
                                "display_content": "127.0.0.1",
                                "display_name": "www",
                                "name": "www.example.com",
                                "prio": None,
                                "props": {
                                    "cf_open": 1,
                                    "cloud_on": 0,
                                    "expired_ssl": 0,
                                    "expiring_ssl": 0,
                                    "pending_ssl": 0,
                                    "proxiable": 1,
                                    "ssl": 1,
                                    "vanity_lock": 0
                                },
                                "rec_hash": "7f8e77bac02ba65d34e20c4b994a202c",
                                "rec_id": "16606009",
                                "service_mode": "0",
                                "ssl_expires_on": None,
                                "ssl_id": "214451",
                                "ssl_status": "V",
                                "ttl": "1",
                                "ttl_ceil": 86400,
                                "type": "A",
                                "zone_name": "example.com"
                            }
                        ]
                    }
                },
                "result": "success"
            },
        })

    @patch('cloudflare_domain.Cloudflare')
    def test_create_new_record(self, mock_cloudflare_cls):
        mock_cloudflare_cls.return_value = self.mock_cloudflare_instance
        mock_module = self.get_mock_module(
            zone='example.com',
            name='home',
            state='present',
            type='A',
            content='127.0.0.1'
        )

        # Perform the actual tests.
        with self.assertRaises(ModuleExit):
            cloudflare_domain(mock_module)

        # Call rec_load_all to determine whether we're creating a new entry or
        # editing an existing one.
        self.assertTrue(self.mock_cloudflare_instance.rec_load_all.called)

        # Since we're creating a new record, assert that rec_new() was called.
        self.mock_cloudflare_instance.rec_new.assert_called_once_with(
            mock_module.params['type'],
            mock_module.params['name'],
            mock_module.params['content'],
            mode=None
        )

        # Make sure that the module reported that changes were made.
        mock_module.exit_json.assert_called_once_with(
            changed=True,
            type=mock_module.params['type'],
            name=mock_module.params['name'],
            content=mock_module.params['content'],
            service_mode=None,
        )

    @patch('cloudflare_domain.Cloudflare')
    def test_existing_record_idempotency(self, mock_cloudflare_cls):
        mock_cloudflare_cls.return_value = self.mock_cloudflare_instance
        mock_module = self.get_mock_module(
            zone='example.com',
            name='www',
            state='present',
            type='A',
            content='127.0.0.1'
       )

        # Perform the actual tests.
        with self.assertRaises(ModuleExit):
            cloudflare_domain(mock_module)

        # Call rec_load_all to determine whether we're creating a new entry or
        # editing an existing one.
        self.assertTrue(self.mock_cloudflare_instance.rec_load_all.called)

        # Make sure that we're never calling rec_new or rec_edit, since no
        # changes have been made.
        self.assertFalse(self.mock_cloudflare_instance.rec_new.called)
        self.assertFalse(self.mock_cloudflare_instance.rec_edit.called)

        # Make sure that the module reported that no changes were made.
        mock_module.exit_json.assert_called_once_with(
            changed=False,
            type=mock_module.params['type'],
            name=mock_module.params['name'],
            content=mock_module.params['content'],
        )

    @patch('cloudflare_domain.Cloudflare')
    def test_remove_exiting_record(self, mock_cloudflare_cls):
        mock_cloudflare_cls.return_value = self.mock_cloudflare_instance
        mock_module = self.get_mock_module(
            zone='example.com',
            name='www',
            state='absent',
            type='A',
            content='127.0.0.1'
       )

        # Perform the actual tests.
        with self.assertRaises(ModuleExit):
            cloudflare_domain(mock_module)

        # Call rec_load_all to determine whether we're creating a new entry or
        # editing an existing one.
        self.assertTrue(self.mock_cloudflare_instance.rec_load_all.called)

        self.assertFalse(self.mock_cloudflare_instance.rec_new.called)
        self.assertFalse(self.mock_cloudflare_instance.rec_edit.called)

        self.mock_cloudflare_instance.rec_delete.assert_called_once_with(
            "16606009"
        )

        # Make sure that the module reported that no changes were made.
        mock_module.exit_json.assert_called_once_with(
            changed=True,
            delete="16606009",
            record=dict(
              type=mock_module.params['type'],
              name=mock_module.params['name'],
              content=mock_module.params['content'],
            )
        )

    @patch('cloudflare_domain.Cloudflare')
    def test_remove_non_existing_record(self, mock_cloudflare_cls):
        mock_cloudflare_cls.return_value = self.mock_cloudflare_instance
        mock_module = self.get_mock_module(
            zone='example.com',
            name='foo',
            state='absent',
            type='A',
            content='127.0.0.1'
       )

        # Perform the actual tests.
        with self.assertRaises(ModuleExit):
            cloudflare_domain(mock_module)

        # Call rec_load_all to determine whether we're creating a new entry or
        # editing an existing one.
        self.assertTrue(self.mock_cloudflare_instance.rec_load_all.called)

        # Make sure that we're never calling rec_new, rec_edit, or rec_delete
        # since no changes have been made.
        self.assertFalse(self.mock_cloudflare_instance.rec_new.called)
        self.assertFalse(self.mock_cloudflare_instance.rec_edit.called)
        self.assertFalse(self.mock_cloudflare_instance.rec_delete.called)

        # Make sure that the module reported that no changes were made.
        mock_module.exit_json.assert_called_once_with(
            changed=False,
            type=mock_module.params['type'],
            name=mock_module.params['name'],
            content=mock_module.params['content'],
        )


if __name__ == '__main__':
    unittest.main()
