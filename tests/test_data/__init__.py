from zipfile import ZipFile

with ZipFile(r"tests\archives\source_STORE copy.zip", "w") as archive:
    with archive.open("pyanilist-main/README.md", "w") as file:
        file.write(b"gay")