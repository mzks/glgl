#! /bin/sh

rm -rf dist
rm -rf rubis.egg-info

python3 setup.py bdist_wheel

echo Done.
echo local install
echo 'python3 -m pip install dist/glgl-*.whl --upgrade'
python -m pip uninstall glgl && python -m pip install dist/glgl-0.1.0-py3-none-any.whl
