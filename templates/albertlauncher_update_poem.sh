#!/bin/bash -       
#title           : Update plugin from github
#description     : Update poe-m plugin from github
#author		 :bgw, modified by rokdd
#date            :20231118
#version         :0.1
#usage		 :bash albertlauncher_update_poem.sh
#notes           :Install git before, no checking for never releases
#bash_version    :4.1.5(1)-release
#==============================================================================

export POEM_DEFAULT_PLUGIN_DIR="$HOME_DIR/.local/share/albert/python/plugins/poe-m"

if [[ -z "${POEM_PLUGIN_DIR}" ]] && [ -d "${POEM_DEFAULT_PLUGIN_DIR}" ]; then
echo "No directory found, but default exists: ${POEM_DEFAULT_PLUGIN_DIR}"
export POEM_PLUGIN_DIR="${POEM_DEFAULT_PLUGIN_DIR}"
fi

if [[ -z "${POEM_PLUGIN_DIR}" ]]; then
  echo "No directory found"
  exit 1
fi

if [[ -f "${POEM_PLUGIN_DIR}/DEV.md" ]]; then
echo "We not update over the dev folder"
    exit 1
fi
cd "${POEM_PLUGIN_DIR}"
git fetch
