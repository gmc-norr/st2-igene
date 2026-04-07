from typing import Any, Dict, Optional, Tuple

import requests
from simplejson import JSONDecodeError
from st2common.runners.base_action import Action


class iGeneAPIRequest(Action):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = requests.Session()

    def run(
        self,
        endpoint: str,
        api_key: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Tuple[bool, Dict[str, Any]]:

        req = self.generate_request(endpoint, api_key, params)
        self.logger.info(
            f"igene request url={req.url} method={req.method} data={req.body}"
        )

        res = self.session.send(req, verify="/etc/ssl/certs/ca-certificates.crt")

        try:
            body = res.json()
        except JSONDecodeError:
            body = res.text

        if res.status_code != 200:
            self.logger.error(
                f"request failed status={res.status_code} body={res.text}"
            )
            return False, {
                "error": "igene request failed",
                "status_code": res.status_code,
                "body": body,
            }
        return True, {
            "message": "igene request succeeded",
            "status_code": res.status_code,
            "body": body,
        }

    def generate_request(
        self,
        endpoint: str,
        api_key: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> requests.PreparedRequest:
        headers = {
            "Accept": "application/json",
        }
        headers["Api-Key"] = api_key

        clean_params = None
        if params is not None:
            clean_params = {}
            for k, v in params.items():
                if v:
                    clean_params[k] = v

        url = f"{self.config.get('base_url', '')}/{endpoint}"
        return requests.Request(
            url=url, method="GET", params=clean_params, headers=headers,
        ).prepare()
