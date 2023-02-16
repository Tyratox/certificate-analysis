# Installation of Dependencies

Make sure to install the cryptography package at version `3.4.8`, for some reason newer version cannot parse certain certificates. (See https://github.com/eu-digital-green-certificates/dgc-testdata/issues/407)

`pip3 install --force-reinstall -v "cryptography==3.4.8"`

When using parquet, `pyarrow` and `fastparquet` are also required.