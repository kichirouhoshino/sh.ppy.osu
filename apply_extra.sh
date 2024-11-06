#!/bin/bash
cd ./layer/usr/share/vulkan/implicit_layer.d
sed -i -E "s|                \"library_path\": \"/usr/lib/x86_64-linux-gnu/liblatencyflex_layer.so\",|                \"library_path\": \"/app/lib/liblatencyflex_layer.so\",|g" latencyflex.json
