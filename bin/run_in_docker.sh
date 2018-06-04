#! /bin/bash

docker build . -t worldengine

XPLAT_TMP_DIR=$(python -c "import tempfile; print(tempfile.gettempdir())")

echo ''
echo '---------------------------'
echo 'Running worldengine'
echo ''
echo "PNGs will be output in the $XPLAT_TMP_DIR directory"
echo '---------------------------'
echo ''

docker run -v $XPLAT_TMP_DIR:/tmp -it worldengine python worldengine -o /tmp
