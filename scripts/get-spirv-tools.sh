#!bash
cd bin
wget -nd -m https://storage.googleapis.com/spirv-tools/badges/build_link_$1_clang_release.html
rm *.html
tar -xvf install.tgz
rm install.tgz
cp install/bin/spirv-* .
rm -rf install
git clone https://github.com/KhronosGroup/SPIRV-Cross.git
cd SPIRV-Cross
make
cp spirv-cross ../spirv-cross-bin
cd ..
rm -rf SPIRV-Cross
mv spirv-cross-bin spirv-cross
cd ..
