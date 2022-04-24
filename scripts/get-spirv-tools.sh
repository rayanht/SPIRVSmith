#!bash
cd bin
[ $? -eq 0 ] && wget -nd -m https://storage.googleapis.com/spirv-tools/badges/build_link_$1_clang_release.html
[ $? -eq 0 ] && tar -xvf install.tgz
[ $? -eq 0 ] && rm spirv-*
[ $? -eq 0 ] && cp install/bin/spirv-* .
[ $? -eq 0 ] && rm *.html
[ $? -eq 0 ] && rm install.tgz
[ $? -eq 0 ] && rm -rf install
[ $? -eq 0 ] && git clone https://github.com/KhronosGroup/SPIRV-Cross.git
[ $? -eq 0 ] && cd SPIRV-Cross
[ $? -eq 0 ] && make
[ $? -eq 0 ] && cp spirv-cross ../spirv-cross-bin
[ $? -eq 0 ] && cd ..
[ $? -eq 0 ] && rm -rf SPIRV-Cross
[ $? -eq 0 ] && mv spirv-cross-bin spirv-cross
cd ..
