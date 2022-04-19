#!bash
cd bin
[ $? -eq 0 ] && wget -nd -m https://storage.googleapis.com/spirv-tools/badges/build_link_$1_clang_release.html
[ $? -eq 0 ] && tar -xvf install.tgz
[ $? -eq 0 ] && cp install/bin/spirv-* .
rm *.html
rm install.tgz
rm -rf install
git clone https://github.com/KhronosGroup/SPIRV-Cross.git
[ $? -eq 0 ] && cd SPIRV-Cross
[ $? -eq 0 ] && make
[ $? -eq 0 ] && cp spirv-cross ../spirv-cross-bin
cd ..
rm -rf SPIRV-Cross
mv spirv-cross-bin spirv-cross
cd ..
