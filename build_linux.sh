#!/bin/bash

out_folder='bin'
out_name='crescent'
src_files='crescent __main__.py'
zip_name='crescent.zip'

mkdir -p "$out_folder"
python3 -m zipfile -c "$out_folder"'/'"$zip_name" $src_files
echo '#!/usr/bin/env python3' > "$out_folder"'/'"$out_name"
cat "$out_folder"'/'"$zip_name" >> "$out_folder"'/'"$out_name"
chmod +x "$out_folder"'/'"$out_name"
