git clone https://github.com/ggml-org/whisper.cpp.git ~/whisper.cpp
cd ~/whisper.cpp
cmake -B build -DGGML_BLAS=1 -DCMAKE_BUILD_TYPE=Release
cmake --build build -j4 --config Release
bash models/download-ggml-model.sh base
