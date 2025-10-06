A small notes file to keep track of the behaviors and quirks of different
archive formats, or the libraries I’m using for them, that I’ve discovered
during development.

I often found myself repeatedly testing various operations on each library to
see how they behave, and then weeks later, I would forget the results and do
it all over again. So I decided it is worth writing it all down in one place.

## Reading Non-Files (e.g., directories)

| Archive Type       | Behavior when attempting to read a directory |
| ------------------ | -------------------------------------------- |
| tarfile.TarFile    | Returns `None`                               |
| zipfile.ZipFile    | Returns empty `b""`                          |
| rarfile.RarFile    | Raises `io.UnsupportedOperation`             |
| py7zr.SevenZipFile | Raises `KeyError`                            |

I find returning empty bytes unacceptable, since you can no longer tell
apart an empty file and a directory. So I am left with either returning
`None` or raising an Exception. I ended up going with an Exception (I think
I'll call it `ArchiveMemberNotAFileError`) because 2 out of 4 libraries do
it and it seems the most "correct" behavior to me. Reading a directory is
an error (pathlib will also raise if you try reading a directory with
`.read_bytes()`) and it should be treated as such.

## Trailing `/` in Directory Names: Who Cares?

1. `tarfile.TarFile`

   - A trailing `/` doesn’t matter.
   - Methods like `getmember(name)` automatically strip it (See: [`tarfile.py#L2059`](https://github.com/python/cpython/blob/be388836c0d4a970e83ca5540c512d94afd13435/Lib/tarfile.py#L2059)).
   - `getnames()` and `TarInfo.name` never include the trailing `/`.

2. `zipfile.ZipFile`

   - A trailing `/` is significant.
   - `getinfo(name)` requires the exact directory name; omitting the `/` raises a `KeyError`.
   - `namelist()` and `ZipInfo.filename` preserve the trailing `/`.

3. `py7zr.SevenZipFile`

   - Behaves much like `tarfile.TarFile`.
   - `getinfo(name)` strips the trailing slash (See: [`py7zr.py#L944`](https://github.com/miurahr/py7zr/blob/9a5a5b9bc39bc0afaac60f3cc7ee6842bd167f35/py7zr/py7zr.py#L944)):
   - `namelist()` and `FileInfo.filename` do not include trailing `/`.

4. `rarfile.RarFile`
   - Strips trailing `/` for lookups (See: [`rarfile.py#L1093`](https://github.com/markokr/rarfile/blob/db1df339574e76dafb8457e848a09c3c074b03a0/rarfile.py#L1093)).
   - But `getinfo().filename` and `namelist()` keep the trailing `/`.

### Summary

| Archive Type       | `/` Stripped for Lookup | `/` Preserved in Listing |
| ------------------ | ----------------------- | ------------------------ |
| tarfile.TarFile    | ✅ Yes                  | ❌ No                    |
| zipfile.ZipFile    | ❌ No                   | ✅ Yes                   |
| py7zr.SevenZipFile | ✅ Yes                  | ❌ No                    |
| rarfile.RarFile    | ✅ Yes                  | ✅ Yes                   |

For `ArchiveFile`, I cannot simply discard the trailing `/`
because `zipfile.ZipFile` requires it. Under the hood,
names are normalized for lookups so that calls like:

```python
archive_file.get_member("foo/bar/")
```

will work regardless of the archive format.

However, normalization alone doesn’t solve everything.
Consider this snippet:

```python
member = archive_file.get_member("foo/bar/")
assert "foo/bar/" in archive_file.get_names()
assert member.name == "foo/bar/"
```

The goal is for this code to pass consistently,
no matter which archive format is used. This is achieved by:

1. Normalizing lookups according to the preferences of the underlying archive format.
   - For example, `/` is stripped for SevenZipFile, but kept for ZipFile.

2. Preserving trailing `/` in listings so that checks like:

   ```python
   "foo/bar/" in archive_file.get_names()
   archive_file.get_member("foo/bar/").name == "foo/bar/"
   ```
   work reliably. For formats that discard the `/` (TarFile and SevenZipFile), we add it back in.

Not doing this would force users to know the details of the
underlying archive format just to perform a simple check 
which would be tedious and error-prone.
