# -*- coding: utf-8 -*-
"""
OnionShare | https://onionshare.org/

Copyright (C) 2014-2021 Micah Lee, et al. <micah@micahflee.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import requests

from .meek import MeekNotRunning


class CensorshipCircumvention(object):
    """
    Connect to the Tor Moat APIs to retrieve censorship
    circumvention recommendations, over the Meek client.
    """

    def __init__(self, common, meek, domain_fronting=True):
        """
        Set up the CensorshipCircumvention object to hold
        common and meek objects.
        """
        self.common = common
        self.meek = meek
        self.common.log("CensorshipCircumvention", "__init__")

        # Bail out if we requested domain fronting but we can't use meek
        if domain_fronting and not self.meek.meek_proxies:
            raise MeekNotRunning()

    def request_map(self, country=False):
        """
        Retrieves the Circumvention map from Tor Project and store it
        locally for further look-ups if required.

        Optionally pass a country code in order to get recommended settings
        just for that country.

        Note that this API endpoint doesn't return actual bridges,
        it just returns the recommended bridge type countries.
        """
        endpoint = "https://bridges.torproject.org/moat/circumvention/map"
        data = {}
        if country:
            data = {"country": country}

        r = requests.post(
            endpoint,
            json=data,
            headers={"Content-Type": "application/vnd.api+json"},
            proxies=self.meek.meek_proxies,
        )
        if r.status_code != 200:
            self.common.log(
                "CensorshipCircumvention",
                "censorship_obtain_map",
                f"status_code={r.status_code}",
            )
            return False

        result = r.json()

        if "errors" in result:
            self.common.log(
                "CensorshipCircumvention",
                "censorship_obtain_map",
                f"errors={result['errors']}",
            )
            return False

        return result

    def request_settings(self, country=False, transports=False):
        """
        Retrieves the Circumvention Settings from Tor Project, which
        will return recommended settings based on the country code of
        the requesting IP.

        Optionally, a country code can be specified in order to override
        the IP detection.

        Optionally, a list of transports can be specified in order to
        return recommended settings for just that transport type.
        """
        endpoint = "https://bridges.torproject.org/moat/circumvention/settings"
        data = {}
        if country:
            data = {"country": country}
        if transports:
            data.append({"transports": transports})
        r = requests.post(
            endpoint,
            json=data,
            headers={"Content-Type": "application/vnd.api+json"},
            proxies=self.meek.meek_proxies,
        )
        if r.status_code != 200:
            self.common.log(
                "CensorshipCircumvention",
                "censorship_obtain_settings",
                f"status_code={r.status_code}",
            )
            return False

        result = r.json()

        if "errors" in result:
            self.common.log(
                "CensorshipCircumvention",
                "censorship_obtain_settings",
                f"errors={result['errors']}",
            )
            return False

        # There are no settings - perhaps this country doesn't require censorship circumvention?
        # This is not really an error, so we can just check if False and assume direct Tor
        # connection will work.
        if not "settings" in result:
            self.common.log(
                "CensorshipCircumvention",
                "censorship_obtain_settings",
                "No settings found for this country",
            )
            return False

        return result

    def request_builtin_bridges(self):
        """
        Retrieves the list of built-in bridges from the Tor Project.
        """
        endpoint = "https://bridges.torproject.org/moat/circumvention/builtin"
        r = requests.post(
            endpoint,
            headers={"Content-Type": "application/vnd.api+json"},
            proxies=self.meek.meek_proxies,
        )
        if r.status_code != 200:
            self.common.log(
                "CensorshipCircumvention",
                "censorship_obtain_builtin_bridges",
                f"status_code={r.status_code}",
            )
            return False

        result = r.json()

        if "errors" in result:
            self.common.log(
                "CensorshipCircumvention",
                "censorship_obtain_builtin_bridges",
                f"errors={result['errors']}",
            )
            return False

        return result
