"""Where the app's own platform keeps the uploaded files: a directory, or an S3 bucket where the app is deployed."""

from pathlib import Path
from typing import Protocol

from qubit_notes.settings import Settings


class Files(Protocol):
    def put(self, key: str, content: bytes, content_type: str) -> None: ...

    def get(self, key: str, offset: int = 0, length: int = 0) -> bytes | None:
        """length bytes of the file from offset, to its end if length is 0; None if there's no such file"""
        ...

    def delete(self, key: str) -> None: ...

    def check(self) -> str | None:
        """why the files can't be kept, or None if they can"""
        ...


class DirectoryFiles:
    def __init__(self, directory: str):
        self._directory = Path(directory)

    def _path(self, key: str) -> Path:
        return self._directory / key

    def put(self, key: str, content: bytes, content_type: str) -> None:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        # written whole, then moved into place, so a file is never read half written
        partial = path.with_name(path.name + ".partial")
        partial.write_bytes(content)
        partial.replace(path)

    def get(self, key: str, offset: int = 0, length: int = 0) -> bytes | None:
        try:
            with self._path(key).open("rb") as file:
                file.seek(offset)
                return file.read(length) if length else file.read()
        except FileNotFoundError:
            return None

    def delete(self, key: str) -> None:
        self._path(key).unlink(missing_ok=True)

    def check(self) -> str | None:
        try:
            self._directory.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            return f"cannot keep files in {self._directory}: {e}"
        return None


class S3Files:
    def __init__(self, bucket: str):
        import boto3

        self._bucket = bucket
        self._s3 = boto3.client("s3")

    def put(self, key: str, content: bytes, content_type: str) -> None:
        self._s3.put_object(Bucket=self._bucket, Key=key, Body=content, ContentType=content_type)

    def get(self, key: str, offset: int = 0, length: int = 0) -> bytes | None:
        arguments = {"Bucket": self._bucket, "Key": key}
        if offset or length:
            arguments["Range"] = f"bytes={offset}-{offset + length - 1 if length else ''}"
        try:
            return self._s3.get_object(**arguments)["Body"].read()
        except self._s3.exceptions.NoSuchKey:
            return None
        except self._s3.exceptions.ClientError as e:
            # a range that starts at the file's end has no bytes
            if e.response.get("Error", {}).get("Code") == "InvalidRange":
                return b""
            raise

    def delete(self, key: str) -> None:
        self._s3.delete_object(Bucket=self._bucket, Key=key)

    def check(self) -> str | None:
        try:
            self._s3.head_bucket(Bucket=self._bucket)
        except Exception as e:
            return f"cannot reach the bucket {self._bucket}: {e}"
        return None


def files_from(settings: Settings) -> Files:
    return S3Files(settings.files_bucket) if settings.files_bucket else DirectoryFiles(settings.files_dir)
