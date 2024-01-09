#!/bin/bash -       
#title           :Create a new script
#description     :This script will make a header for a bash script called by albert launcher
#author		 : bgw, modfied by rokdd
#date            :20231118
#version         :0.1
#usage		 :bash new_script.sh
#notes           :
#bash_version    :4.1.5(1)-release
#==============================================================================

today=$(date +%Y%m%d)
div=======================================

/usr/bin/clear

if [[ -n "$POEM_PATH_DEFAULT_SHELL" ]]; then
cd $POEM_PATH_DEFAULT_SHELL
echo "Create script in $POEM_PATH_DEFAULT_SHELL"
fi

_select_title(){

    # Get the user input.
    printf "Enter a title: " ; read -r title

    # Remove the spaces from the title if necessary.
    title=${title// /_}

    # Convert uppercase to lowercase.
    title=${title,,}

    filename=${title}

    # Add .sh to the end of the title if it is not there already.
    [ "${title: -3}" != '.sh' ] && filename=${title}.sh

    # Check to see if the file exists already.
    if [ -e $filename ] ; then 
        printf "\n%s\n%s\n\n" "The script \"$filename\" already exists." \
        "Please select another title."
        _select_title
    fi

}

_select_title

printf "Enter a description: " ; read -r dscrpt
printf "Enter your name: " ; read -r name
printf "Enter the version number: " ; read -r vnum

# Format the output and write it to a file.
printf "%-16s\n\
%-16s%-8s\n\
%-16s%-8s\n\
%-16s%-8s\n\
%-16s%-8s\n\
%-16s%-8s\n\
%-16s%-8s\n\
%-16s%-8s\n\
%-16s%-8s\n\
%s\n\n\n" '#!/bin/sh -' '#title' ":$title" '#description' \
":${dscrpt}" '#author' ":$name" '#date' ":$today" '#version' \
":$vnum" '#usage' ":./$filename" '#notes' ':' '#bash_version' \
":${BASH_VERSION}" \#$div${div} > $filename

echo "usage() {
  [ "\$*" ] && echo "\$0: \$*"
  sed -n '/^##/,/^$/s/^## \{0,1\}//p' "\$0"
  exit 2
} 2>/dev/null

main() {
  while [ \$# -gt 0 ]; do
    case \$1 in
    (-n) DRY_RUN=1;;
    (-h|--help) usage 2>&1;;
    (--) shift; break;;
    (-*) usage "\$1: unknown option";;
    (*) break;;
    esac
  done
  : do stuff." >> $filename
if [[ -n "$POEM_PATH_ALIAS" ]]; then
 #echo "     shopt -s expand_aliases  source $POEM_PATH_ALIAS  "  >> $filename
fi
echo "}

main \"\$@\"" >> $filename


# Make the file executable.
chmod +x $filename

/usr/bin/clear

_select_editor(){

    # Select between Vim or Emacs.
    printf "%s\n%s\n%s\n%s\n%s\n%s\n%s\n" "Select an editor." "1 for Vim." "2 for Emacs." "3 for Nano." "4 for gedit." "5 for visual studio code." "6 for visual studio code insiders."
    read -r editor

    # Open the file with the cursor on the twelth line.
    case $editor in
        1) vim +12 $filename
            ;;
        2) emacs +12 $filename &
            ;;
        3) nano $filename
            ;;
        4) gedit $filename
            ;;
        5) code $filename
            ;;
        6) code-insiders $filename
            ;;
        *) /usr/bin/clear
           printf "%s\n%s\n\n" "I did not understand your selection." \
               "Press <Ctrl-c> to quit."
           _select_editor
            ;;
    esac

}

_select_editor
