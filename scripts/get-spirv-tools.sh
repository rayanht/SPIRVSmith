#!bash
cd bin
wget -nd -m https://storage.googleapis.com/spirv-tools/badges/build_link_$1_clang_release.html
rm *.html
tar -xvf install.tgz
rm install.tgz
cp install/bin/spirv-* .
rm -rf install
cd ..
