# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import json
from typing import Iterable, List, Optional


from .. import _ffi
from .._dispatcher import Dispatcher
from ..testing import ErrorType


from .lifetime import Lifetime


class StringListMetricType:
    """
    This implements the developer facing API for recording string list metrics.

    Instances of this class type are automatically generated by
    `glean.load_metrics`, allowing developers to record values that were
    previously registered in the metrics.yaml file.

    The stringlist API only exposes the `StringListMetricType.set` and
    `StringListMetricType.add` methods, which takes case of validating the
    input data and making sure that limits are enforced.
    """

    def __init__(
        self,
        disabled: bool,
        category: str,
        lifetime: Lifetime,
        name: str,
        send_in_pings: List[str],
    ):
        self._disabled = disabled
        self._send_in_pings = send_in_pings

        self._handle = _ffi.lib.glean_new_string_list_metric(
            _ffi.ffi_encode_string(category),
            _ffi.ffi_encode_string(name),
            _ffi.ffi_encode_vec_string(send_in_pings),
            len(send_in_pings),
            lifetime.value,
            disabled,
        )

    def __del__(self):
        if getattr(self, "_handle", 0) != 0:
            _ffi.lib.glean_destroy_string_list_metric(self._handle)

    def add(self, value: str) -> None:
        """
        Appends a string value to one or more string list metric stores. If the
        string exceeds the maximum string length or if the list exceeds the
        maximum length it will be truncated.

        Args:
            value (str): The is the user defined string value.
        """
        if self._disabled:
            return

        @Dispatcher.launch
        def set():
            _ffi.lib.glean_string_list_add(self._handle, _ffi.ffi_encode_string(value))

    def set(self, value: Iterable[str]) -> None:
        """
        Sets a string list to one or more metric stores. If any string exceeds
        the maximum string length or if the list exceeds the maximum length it
        will be truncated.

        Args:
            value (iterator over str): This is a user-defined string list.
        """
        if self._disabled:
            return

        @Dispatcher.launch
        def set():
            values = list(value)
            _ffi.lib.glean_string_list_set(
                self._handle, _ffi.ffi_encode_vec_string(values), len(values)
            )

    def test_has_value(self, ping_name: Optional[str] = None) -> bool:
        """
        Tests whether a value is stored for the metric for testing purposes
        only.

        Args:
            ping_name (str): (default: first value in send_in_pings) The name
                of the ping to retrieve the metric for.

        Returns:
            has_value (bool): True if the metric value exists.
        """
        if ping_name is None:
            ping_name = self._send_in_pings[0]

        return bool(
            _ffi.lib.glean_string_list_test_has_value(
                self._handle, _ffi.ffi_encode_string(ping_name)
            )
        )

    def test_get_value(self, ping_name: Optional[str] = None) -> List[str]:
        """
        Returns the stored value for testing purposes only.

        Args:
            ping_name (str): (default: first value in send_in_pings) The name
                of the ping to retrieve the metric for.

        Returns:
            value (bool): value of the stored metric.
        """
        if ping_name is None:
            ping_name = self._send_in_pings[0]

        if not self.test_has_value(ping_name):
            raise ValueError("metric has no value")

        return json.loads(
            _ffi.ffi_decode_string(
                _ffi.lib.glean_string_list_test_get_value_as_json_string(
                    self._handle, _ffi.ffi_encode_string(ping_name)
                )
            )
        )

    def test_get_num_recorded_errors(
        self, error_type: ErrorType, ping_name: Optional[str] = None
    ) -> int:
        """
        Returns the number of errors recorded for the given metric.

        Args:
            error_type (ErrorType): The type of error recorded.
            ping_name (str): (default: first value in send_in_pings) The name
                of the ping to retrieve the metric for.

        Returns:
            num_errors (int): The number of errors recorded for the metric for
                the given error type.
        """
        if ping_name is None:
            ping_name = self._send_in_pings[0]

        return _ffi.lib.glean_string_list_test_get_num_recorded_errors(
            self._handle,
            error_type.value,
            _ffi.ffi_encode_string(ping_name),
        )


__all__ = ["StringListMetricType"]
