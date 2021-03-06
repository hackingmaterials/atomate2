"""Functions for manipulating VASP files."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional, Sequence, Union

from atomate2.common.file import copy_files, get_zfile, gunzip_files, rename_files
from atomate2.utils.file_client import FileClient, auto_fileclient
from atomate2.utils.path import strip_hostname

__all__ = ["copy_vasp_outputs", "get_largest_relax_extension"]

logger = logging.getLogger(__name__)


@auto_fileclient
def copy_vasp_outputs(
    src_dir: Union[Path, str],
    src_host: Optional[str] = None,
    additional_vasp_files: Sequence[str] = tuple(),
    contcar_to_poscar: bool = True,
    file_client: FileClient = None,
):
    """
    Copy VASP output files to the current directory.

    For folders containing multiple calculations (e.g., suffixed with relax1, relax2,
    etc), this function will only copy the files with the highest numbered suffix and
    the suffix will be removed. Additional vasp files will be also be  copied with the
    same suffix applied. Lastly, this function will gunzip any gzipped files.

    Parameters
    ----------
    src_dir
        The source directory.
    src_host
        The source hostname used to specify a remote filesystem. Can be given as
        either "username@remote_host" or just "remote_host" in which case the username
        will be inferred from the current user. If ``None``, the local filesystem will
        be used as the source.
    additional_vasp_files
        Additional files to copy, e.g. ["CHGCAR", "WAVECAR"].
    contcar_to_poscar
        Move CONTCAR to POSCAR (original POSCAR is not copied).
    file_client
        A file client to use for performing file operations.
    """
    src_dir = strip_hostname(src_dir)  # TODO: Handle hostnames properly.

    logger.info(f"Copying VASP inputs from {src_dir}")

    relax_ext = get_largest_relax_extension(src_dir, src_host, file_client=file_client)
    directory_listing = file_client.listdir(src_dir, host=src_host)

    # find required files
    files = ("INCAR", "OUTCAR", "CONTCAR", "vasprun.xml") + tuple(additional_vasp_files)
    required_files = [get_zfile(directory_listing, r + relax_ext) for r in files]

    # find optional files; do not fail if KPOINTS is missing, this might be KSPACING
    # note: POTCAR files never have the relax extension, whereas KPOINTS files should
    optional_files = []
    for file in ["POTCAR", "POTCAR.spec", "KPOINTS" + relax_ext]:
        found_file = get_zfile(directory_listing, file, allow_missing=True)
        if found_file is not None:
            optional_files.append(found_file)

    # check at least one type of POTCAR file is included
    if len([f for f in optional_files if "POTCAR" in f.name]) == 0:
        raise FileNotFoundError("Could not find POTCAR file to copy.")

    copy_files(
        src_dir,
        src_host=src_host,
        include_files=required_files + optional_files,
        file_client=file_client,
    )

    gunzip_files(
        include_files=required_files + optional_files,
        allow_missing=True,
        file_client=file_client,
    )

    # rename files to remove relax extension
    if relax_ext:
        all_files = optional_files + required_files
        files_to_rename = {
            k.name.replace(".gz", ""): k.name.replace(relax_ext, "").replace(".gz", "")
            for k in all_files
        }
        rename_files(files_to_rename, allow_missing=True, file_client=file_client)

    if contcar_to_poscar:
        rename_files({"CONTCAR": "POSCAR"}, file_client=file_client)

    logger.info("Finished copying inputs")


@auto_fileclient
def get_largest_relax_extension(
    directory: Union[Path, str],
    host: Optional[str] = None,
    file_client: FileClient = None,
) -> str:
    """
    Get the largest numbered relax extension of files in a directory.

    For example, if listdir gives ["vasprun.xml.relax1.gz", "vasprun.xml.relax2.gz"],
    this function will return ".relax2".

    Parameters
    ----------
    directory
        A directory to search.
    host
        The hostname used to specify a remote filesystem. Can be given as either
        "username@remote_host" or just "remote_host" in which case the username will be
        inferred from the current user. If ``None``, the local filesystem will be used.
    file_client
        A file client to use for performing file operations.

    Returns
    -------
    str
        The relax extension or an empty string if there were not multiple relaxations.
    """
    relax_files = file_client.glob(Path(directory) / "*.relax*", host=host)
    if len(relax_files) == 0:
        return ""

    numbers = [re.search(r".relax(\d+)", file.name).group(1) for file in relax_files]
    max_relax = max(numbers, key=lambda x: int(x))
    return f".relax{max_relax}"
