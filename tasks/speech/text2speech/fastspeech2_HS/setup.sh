#!/bin/bash

git clone -b New-Models https://github.com/smtiitm/Fastspeech2_HS
wget https://huggingface.co/smtiitm/FastSpeech2_HS_latest_models/resolve/main/hindi_latest/male/model/model.pth -P Fastspeech2_HS/hindi_latest/male/model/

cp *py Fastspeech2_HS/

cd Fastspeech2_HS