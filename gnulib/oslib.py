import subprocess
from typing import Iterable, Optional, Union, List
import re
import logging
from pathlib import Path
import shutil
import os


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def du(path: Union[str, Path], exclude: Iterable[str] = [], flags: str = "sb") -> int:
    """
    Get disk usage of a directory.

    Args:
        path (Union[str, Path]): Path to the directory.
        exclude (Iterable[str]): Patterns to exclude.
        flags (str): Flags for du command. Default is "sb" (summarize, bytes).

    Returns:
        int: Disk usage in bytes.

    Raises:
        subprocess.CalledProcessError: If du command fails.
    """
    path = str(Path(path).resolve())
    cmd = ["du", f"-{flags}", path] + [f"--exclude={e}" for e in exclude]
    try:
        du_output = subprocess.check_output(cmd, text=True)
        return int(du_output.split("\t")[0])
    except subprocess.CalledProcessError as e:
        logger.error(f"du command failed: {e}")
        raise


def tar(
    output_file: Union[str, Path],
    to_archive: Union[str, Path],
    exclude_patterns: Iterable[str] = [],
    compression: str = "gz",
) -> int:
    """
    Create a tar archive.

    Args:
        output_file (Union[str, Path]): Path to the output tar file.
        to_archive (Union[str, Path]): Path to the directory or file to archive.
        exclude_patterns (Iterable[str]): Patterns to exclude.
        compression (str): Compression type ('gz', 'bz2', 'xz', or '' for no compression).

    Returns:
        int: Number of bytes written.

    Raises:
        subprocess.CalledProcessError: If tar command fails.
        ValueError: If invalid compression type is provided.
    """
    output_file = str(Path(output_file).resolve())
    to_archive = str(Path(to_archive).resolve())

    compress_flag = {"gz": "z", "bz2": "j", "xz": "J", "": ""}.get(compression)

    if compress_flag is None:
        raise ValueError(f"Invalid compression type: {compression}")

    tar_cmd = (
        ["tar", "--totals", f"-c{compress_flag}f", output_file]
        + [f"--exclude={i}" for i in exclude_patterns]
        + [to_archive]
    )

    try:
        tar_output = subprocess.check_output(
            tar_cmd, stderr=subprocess.STDOUT, text=True
        )
        match = re.search(r"Total bytes written: (\d+)", tar_output)
        return int(match.group(1)) if match else -1
    except subprocess.CalledProcessError as e:
        logger.error(f"tar command failed: {e}")
        raise


def find(
    path: Union[str, Path],
    name: Optional[str] = None,
    type: Optional[str] = None,
    mtime: Optional[Union[int, str]] = None,
    maxdepth: Optional[int] = None,
) -> List[str]:
    """
    Find files or directories.

    Args:
        path (Union[str, Path]): Path to search.
        name (Optional[str]): Name pattern to match.
        type (Optional[str]): File type to match ('f' for files, 'd' for directories, etc.).
        mtime (Optional[Union[int, str]]): Modification time filter (e.g., "-7" for last 7 days).
        maxdepth (Optional[int]): Maximum depth to search.

    Returns:
        List[str]: List of found paths.

    Raises:
        subprocess.CalledProcessError: If find command fails.
    """
    path = str(Path(path).resolve())
    cmd = ["find", path]

    if maxdepth is not None:
        cmd.extend(["-maxdepth", str(maxdepth)])
    if name:
        cmd.extend(["-name", name])
    if type:
        cmd.extend(["-type", type])
    if mtime:
        cmd.extend(["-mtime", str(mtime)])

    try:
        output = subprocess.check_output(cmd, universal_newlines=True)
        return output.strip().split("\n")
    except subprocess.CalledProcessError as e:
        logger.error(f"find command failed: {e}")
        raise


def apt_update() -> str:
    """
    Update package lists using apt-get update.

    Returns:
        str: Output of the apt-get update command.

    Raises:
        subprocess.CalledProcessError: If the apt-get update command fails.
    """
    cmd = ["sudo", "apt-get", "update"]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"apt-get update failed: {e}")
        raise


def apt_install(packages: List[str], yes: bool = True) -> str:
    """
    Install packages using apt-get install.

    Args:
        packages (List[str]): List of package names to install.
        yes (bool): Automatically answer yes to prompts. Default is True.

    Returns:
        str: Output of the apt-get install command.

    Raises:
        subprocess.CalledProcessError: If the apt-get install command fails.
    """
    cmd = ["sudo", "apt-get", "install"]
    if yes:
        cmd.append("-y")
    cmd.extend(packages)

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"apt-get install failed: {e}")
        raise


# Example usage:
if __name__ == "__main__":
    try:
        # GNU utils examples
        usage = du("/home/user", exclude=["*.log"])
        print(f"Disk usage: {usage} bytes")

        archive_size = tar(
            "archive.tar.gz", "/home/user/documents", exclude_patterns=["*.tmp"]
        )
        print(f"Archive size: {archive_size} bytes")

        results = find("/home/user", name="*.py", type="f", mtime="-7", maxdepth=3)
        print("Found files:")
        for result in results:
            print(result)

        # APT examples
        update_output = apt_update()
        print("Update output:")
        print(update_output)

        install_output = apt_install(["python3-pip", "git"])
        print("\nInstall output:")
        print(install_output)

    except Exception:
        logger.exception("An error occurred")


def is_command_in_path(command: str) -> bool:
    """
    Check if a command is available in the system PATH.

    Args:
        command (str): The command to check.

    Returns:
        bool: True if the command is in PATH, False otherwise.
    """
    return shutil.which(command) is not None


def ensure_package(package: str) -> None:
    """
    Ensure a package is installed and available in the system PATH.

    Args:
        package (str): The package to ensure.

    Raises:
        RuntimeError: If the package couldn't be installed or isn't in PATH after installation.
    """
    if not is_command_in_path(package):
        logger.info(f"{package} not found in PATH. Attempting to install...")
        try:
            apt_install([package])
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to install {package}: {e}")

        if not is_command_in_path(package):
            raise RuntimeError(
                f"{package} was installed but is not in PATH. You may need to restart your shell."
            )
    else:
        logger.info(f"{package} is already installed and in PATH.")


def stow(source_dir: Union[str, Path], target_dir: Union[str, Path]) -> List[Path]:
    """
    Mimics basic GNU Stow functionality by creating symlinks.

    Args:
    source_dir (Union[str, Path]): The directory containing the files to stow.
    target_dir (Union[str, Path]): The target directory where symlinks will be created.

    Returns:
    List[Path]: List of created symlinks.

    Raises:
    FileNotFoundError: If source_dir doesn't exist.
    NotADirectoryError: If source_dir is not a directory.
    """
    source_path = Path(source_dir).resolve()
    target_path = Path(target_dir).resolve()

    if not source_path.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source_path}")
    if not source_path.is_dir():
        raise NotADirectoryError(f"Source is not a directory: {source_path}")

    created_symlinks = []

    for root, _, files in os.walk(source_path):
        for file in files:
            source_file = Path(root) / file
            relative_path = source_file.relative_to(source_path)
            target_file = target_path / relative_path

            # Create parent directories if they don't exist
            target_file.parent.mkdir(parents=True, exist_ok=True)

            # Create symlink
            if not target_file.exists():
                target_file.symlink_to(source_file)
                logger.info(f"Created symlink: {target_file} -> {source_file}")
                created_symlinks.append(target_file)
            else:
                logger.info(f"Skipped existing file: {target_file}")

    return created_symlinks
