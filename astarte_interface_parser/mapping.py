# (C) Copyright 2025, SECO Mind Srl
#
# SPDX-License-Identifier: Apache-2.0

import sys
from string import Template

from astarte.device import Mapping
from colored import fore, stylize

mapping_definition_template = Template(
    r"""
    {
        .endpoint = "${endpoint}",
        .type = ${type},
        .reliability = ${reliability},
        .explicit_timestamp = ${explicit_timestamp},
        .allow_unset = ${allow_unset},
    },"""
)


def generate_mapping_definition(mapping: Mapping):
    """
    Generates a C mapping definition string from a Mapping object.

    Parameters
    ----------
    mapping : Mapping
        An object representing a data mapping, containing details like endpoint, type, reliability,
        explicit timestamp, and allow unset flags.

    Returns
    -------
    str
        A string containing the complete C mapping definition.
    """
    reliability_str = {
        0: "UNRELIABLE",
        1: "GUARANTEED",
        2: "UNIQUE",
    }.get(mapping.reliability)
    if reliability_str is None:
        print(stylize(f"Error: Unknown reliability value '{mapping.reliability}'", fore("red")))
        sys.exit(1)

    return mapping_definition_template.substitute(
        endpoint=mapping.endpoint,
        type="ASTARTE_MAPPING_TYPE_" + mapping.type.upper(),
        reliability="ASTARTE_MAPPING_RELIABILITY_" + reliability_str,
        explicit_timestamp="true" if mapping.explicit_timestamp else "false",
        allow_unset="true" if mapping.allow_unset else "false",
    )
