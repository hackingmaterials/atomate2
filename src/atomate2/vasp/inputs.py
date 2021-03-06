"""Functions for writing/reading input sets."""

from __future__ import annotations

import importlib
import logging
from typing import Optional

from pymatgen.core.structure import Structure

__all__ = ["write_vasp_input_set"]

logger = logging.getLogger(__name__)


def write_vasp_input_set(
    structure: Structure,
    input_set: str,
    input_set_kwargs: Optional[dict] = None,
    write_input_kwargs: Optional[dict] = None,
    from_prev: bool = False,
):
    """
    Write VASP input set.

    Parameters
    ----------
    structure
        A structure.
    input_set
        An input set, specified as a string. Can be an input set name from
        ``pymatgen.io.vasp.sets`` (e.g., "MPStaticSet") or a full python import path
        (e.g., "mypackage.mymodule.InputSet").
    input_set_kwargs
        Keyword arguments that will be passed to the input set constructor.
    write_input_kwargs
        Keyword arguments that will be passed to :obj:`.DictSet.write_input`.
    from_prev
        Whether to initialize the input set from a previous calculation.
    """
    input_set_kwargs = {} if input_set_kwargs is None else input_set_kwargs
    write_input_kwargs = {} if write_input_kwargs is None else write_input_kwargs

    if "." in input_set:
        module, input_set = input_set.rsplit(".", 1)
    else:
        module = "pymatgen.io.vasp.sets"

    try:
        vis_cls = getattr(importlib.import_module(module), input_set)
    except (ModuleNotFoundError, AttributeError, ImportError):
        raise ImportError(f"Could not import input set {input_set} from {module}.")

    # TODO: Make from_prev a standard method in dictset
    if from_prev and hasattr(vis_cls, "from_prev"):
        vis = vis_cls.from_prev(".", structure=structure, **input_set_kwargs)
    else:
        vis = vis_cls(structure, **input_set_kwargs)

    logger.info("Writing VASP input set.")
    vis.write_input(".", **write_input_kwargs)
