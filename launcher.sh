#!/usr/bin/env bash
docker build -t anime_dubbing_alpha .
docker run --rm -it -p 5000:5000 -v "$(pwd)":/app anime_dubbing_alpha