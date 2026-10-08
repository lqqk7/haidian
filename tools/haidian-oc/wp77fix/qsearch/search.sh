#!/bin/zsh

HAIDIAN_TOOLCHAIN_ROOT="$(cd "$(dirname "$0")/../../" && pwd)"
HAIDIAN_PROJECT_ROOT="$(cd "$HAIDIAN_TOOLCHAIN_ROOT/../.." && pwd)"
export HAIDIAN_TOOLCHAIN_ROOT HAIDIAN_PROJECT_ROOT
# 在原始（未改文案）图版上反解 v7.6 的 PNG 量化配方：
# 目标 = 包内 land-use-structure.png（415127 B，8 位调色板 118 色，全 0 滤波）
cd "$(dirname "$0")"
RAW=../ctrl-png/land-use-structure-zh.raw.png
TGT=../../w81-basemap/png/land-use-structure-zh.q.png
TH=$(shasum -a256 $TGT | cut -c1-16)
echo "target $(stat -f%z $TGT) B  sha=$TH"
i=0
for q in 65-90 62-92 60-95 70-95 55-90; do
  for d in nofs fs; do
    for sp in 1 4; do
      i=$((i+1))
      args=(--quality=$q --speed $sp --force)
      [[ $d == nofs ]] && args+=(--nofs)
      pngquant $args --output p$i.png $RAW 2>/dev/null
      rc=$?
      if [[ $rc -ne 0 || ! -f p$i.png ]]; then echo "q=$q $d speed=$sp -> pngquant rc=$rc"; continue; fi
      pal=$(magick identify -format '%k' p$i.png 2>/dev/null)
      ps=$(stat -f%z p$i.png)
      # 无 zopfli 的直出，以及 zopfli filter-0 两档
      zopflipng -y --filters=0 p$i.png z$i.png >/dev/null 2>&1
      zs=$(stat -f%z z$i.png)
      zh=$(shasum -a256 z$i.png | cut -c1-16)
      mark=""
      [[ $zh == $TH ]] && mark="  <<<<<< BYTE MATCH"
      printf "q=%-6s %-4s sp=%s  pal=%-4s pngquant=%-8s zopfli0=%-8s%s\n" $q $d $sp "$pal" $ps $zs "$mark"
    done
  done
done
