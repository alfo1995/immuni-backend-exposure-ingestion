#    Copyright (C) 2020 Presidenza del Consiglio dei Ministri.
#    Please refer to the AUTHORS file for more information.
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

import logging

import requests
from immuni_common.core.exceptions import UnauthorizedOtpException, ApiException

from immuni_exposure_ingestion.core import config

_LOGGER = logging.getLogger(__name__)


def verify_cun(cun_sha: str, last_his_number: str) -> str:
    """
    Return the response after validating the CUN and the last 8 char of HIS card
    from external HIS Service.
    The request should use mutual TLS authentication.

    :param cun_sha: the unique national code in sha256 format released by the HIS.
    :param last_his_number: the last 8 chars of the HIS card.
    :return: the id_transaction.
    """
    #remote_url = f"https://{config.HIS_VERIFY_EXTERNAL_URL}"
    remote_url = f"http://{config.HIS_VERIFY_EXTERNAL_URL}"
    body = dict(cun=cun_sha, last_his_number=last_his_number)

    _LOGGER.info("Requesting validation with external HIS service.", extra=body)

    response = requests.post(
        remote_url,
        json=body
        #verify=config.HIS_SERVICE_CA_BUNDLE,
        #cert=config.HIS_SERVICE_CERTIFICATE,
    )
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise ApiException

    json_response = response.json()

    if not json_response or json_response.id_transazione == "":
        raise UnauthorizedOtpException

    _LOGGER.info("Response received from external service.", extra=json_response)
    return json_response.id_transazione
