# (C) Copyright 2025, SECO Mind Srl
#
# SPDX-License-Identifier: Apache-2.0

import json
import sys
from pathlib import Path
from string import Template

from astarte.device import Interface, InterfaceFileDecodeError
from colored import fore, stylize

from .mapping import generate_mapping_definition

interface_definition_template = Template(
    r"""
static const astarte_mapping_t ${interface_name_sc}_mappings[${mappings_number}] = {
${mappings}
};

const astarte_interface_t ${interface_name_sc} = {
    .name = "${interface_name}",
    .major_version = ${version_major},
    .minor_version = ${version_minor},
    .type = ${type},
    .ownership = ${ownership},
    .aggregation = ${aggregation},
    .mappings = ${interface_name_sc}_mappings,
    .mappings_length = ${mappings_number}U,
};"""
)


def generate_interface_definition(interface: Interface):
    """
    Generates a C interface definition string from an Interface object.

    Parameters
    ----------
    interface : Interface
        An object representing the interface, containing details like name, version, type,
        ownership, aggregation, and mappings.

    Returns
    -------
    str
        A string containing the complete C interface definition.
    """
    mapping_definitions = [generate_mapping_definition(mapping) for mapping in interface.mappings]

    itype = "ASTARTE_INTERFACE_" + (
        "TYPE_PROPERTIES" if interface.is_type_properties() else "TYPE_DATASTREAM"
    )
    iownership = "ASTARTE_INTERFACE_" + (
        "OWNERSHIP_SERVER" if interface.is_server_owned() else "OWNERSHIP_DEVICE"
    )
    iaggregation = "ASTARTE_INTERFACE_" + (
        "AGGREGATION_OBJECT" if interface.is_aggregation_object() else "AGGREGATION_INDIVIDUAL"
    )
    return interface_definition_template.substitute(
        mappings_number=len(interface.mappings),
        interface_name_sc=interface.name.replace(".", "_").replace("-", "_"),
        interface_name=interface.name,
        version_major=interface.version_major,
        version_minor=interface.version_minor,
        type=itype,
        ownership=iownership,
        aggregation=iaggregation,
        mappings="".join(mapping_definitions),
    )


interface_header_template = Template(
    r"""/**
 * @file ${filename}.h
 * @brief Contains automatically generated interfaces.
 *
 * @warning Do not modify this file manually.
 *
 * @details The generated structures contain all information regarding each interface.
 * and are automatically generated from the json interfaces definitions.
 */

// NOLINTNEXTLINE This guard is clear enough.
#ifndef ${filename_cap}_H
#define ${filename_cap}_H

#include <astarte_device_sdk/interface.h>
#include <astarte_device_sdk/mapping.h>

// Interface names should resemble as closely as possible their respective .json file names.
// NOLINTBEGIN(readability-identifier-naming)
${declarations}
// NOLINTEND(readability-identifier-naming)

#endif /* ${filename_cap}_H */
"""
)

interface_source_template = Template(
    r"""/**
 * @file ${filename}.c
 * @brief Contains automatically generated interfaces.
 *
 * @warning Do not modify this file manually.
 */

#include "${filename}.h"

// Interface names should resemble as closely as possible their respective .json file names.
// NOLINTBEGIN(readability-identifier-naming)
${definitions}

// NOLINTEND(readability-identifier-naming)
"""
)

interface_declaration_template = Template(
    r"""extern const astarte_interface_t ${interface_name_sc};"""
)


def convert_interface_from_json_to_c(
    json_files: list[Path], output_base_name: str
) -> tuple[str, str]:
    """
    Processes JSON interface files and generates the corresponding C header and source strings.

    Parameters
    ----------
    json_files : list[Path]
        List of individual .json file paths.
    output_base_name : str
        Base name for the generated .h and .c files.

    Returns
    -------
    Tuple[str, str]
        A tuple containing the generated C header string and C source string.
    """

    declarations = []
    definitions = []
    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as json_fp:
            try:
                interface = Interface(json.load(json_fp))
            except InterfaceFileDecodeError as e:
                print(stylize(f"Error parsing interface file {json_file}: {e}", fore("red")))
                sys.exit(1)

            definitions.append(generate_interface_definition(interface))

            declaration = interface_declaration_template.substitute(
                interface_name_sc=interface.name.replace(".", "_").replace("-", "_")
            )
            declarations.append(declaration)

    header = interface_header_template.substitute(
        filename=output_base_name,
        filename_cap=output_base_name.upper(),
        declarations="\n".join(declarations),
    )

    source = interface_source_template.substitute(
        filename=output_base_name, definitions="\n".join(definitions)
    )

    return header, source
