import http

import requests
from bs4 import BeautifulSoup



class AbstractStatefulScraper:
    main_url = None
    base_headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:67.0) Gecko/20100101 Firefox/67.0"
    }
    hidden_fields = {
        "view-state":  "__VIEWSTATE",
        "view-state-generator":  "__VIEWSTATEGENERATOR",
        "event-validation": "__EVENTVALIDATION",
        "event-target": "__EVENTTARGET",
        "event-argument": "__EVENTARGUMENT",
        "last-focus": "__LASTFOCUS",
        "view-state-generator": "__VIEWSTATEGENERATOR",
    }

    def __init__(self, do_initial_request=True, prev_session=None):
        # STATEFULL fields
        self.view_state = None
        self.view_state_generator = None
        self.event_validation = None
        ##
        if self.main_url is None:
            raise Exception("The main URL can't be None.")
        if prev_session is not None:
            self.req_session = prev_session
        else:
            self.req_session = requests.Session()
        self.req_session.headers.update(self.base_headers)

        if do_initial_request:
            self._do_initial_request()

    def _set_or_fail(self, soup, self_field_name, field_id):
        state_value = soup.select("#" + field_id).pop()["value"].strip()
        if state_value:
            setattr(self, self_field_name, state_value)
        else:
            raise Exception(
                "Unable to obtain the value of {}".format(self_field_name))

    def _update_internal_state(self, soup):
        self._set_or_fail(
            soup,
            "view_state",
            self.hidden_fields["view-state"]
        )
        self._set_or_fail(
            soup,
            "event_validation",
            self.hidden_fields["event-validation"]
        )
        self._set_or_fail(
            soup,
            "view_state_generator",
            self.hidden_fields["view-state-generator"]
        )

    def _make_stateful_request(self, method='get', **extr_params):
        """
        Make a http request (get/post) to the main URL `self.main_url`,
        update the internal state (view_state among other things),
        and return a BeatifulSoup instance with content.
        """
        norm_method = method.lower()
        if norm_method not in ('get', 'post'):
            raise Exception("The method {} is not supported".format(method))
        if method == 'get':
            response = self.req_session.get(self.main_url, **extr_params)
        else:
            response = self.req_session.post(self.main_url, **extr_params)
        if response.status_code != http.HTTPStatus.OK:
            breakpoint()
            raise Exception("Unable to obtain the initial page. {}".format(response))
        soup = BeautifulSoup(response.text, 'lxml')
        self._update_internal_state(soup)
        return soup

    def _do_initial_request(self):
        self._make_stateful_request()

    def _get_request_params(self, target, **fields):
        return {
            self.hidden_fields["event-target"]: target,
            self.hidden_fields["event-argument"]: "",
            self.hidden_fields["event-validation"]: self.event_validation,
            self.hidden_fields["last-focus"]: "",
            self.hidden_fields["view-state"]: self.view_state,
            self.hidden_fields["view-state-generator"]: self.view_state_generator,
            **fields
        }
