#!bash
cd bin
git clone https://github.com/google/amber.git
cd amber
./tools/git-sync-deps
mkdir -p out/Debug
cd out/Debug
cmake -DAMBER_SKIP_TESTS=True -DAMBER_SKIP_SHADERC=True ../..
make
# cp amber ../../../amber-bin
# cd ../../..
# rm -rf amber
# mv amber-bin amber
# cd ..
