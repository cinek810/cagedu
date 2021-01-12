#!/bin/sh

DU="/bin/du-analyzer"
PATH_TO_SCAN="##PATH_TO_SCAN##"
DEBUGGING=1
OUT_PREFIX="##OUTPUT_SVG_FILES##"

function log {
    echo "$@"
}

function runAndLog {
    if [ $DEBUGGING -gt 0 ]
    then
        log "executing: \"$@\""
    fi

    eval "$@"
}

OUT=${OUT_PREFIX}"/"$(date +%Y-%m-%d)

if [ -d $OUT ]
then
    echo "Output directory allready exists, removing it"
    rm -rf "${$OUT}"
fi

mkdir "${OUT}"

TEMPDIR=$(mktemp -d )
cd ${TEMPDIR}

runAndLog ${DU} scan -path ${PATH_TO_SCAN}
runAndLog ${DU} dotexport  -path ${PATH_TO_SCAN} -out ${OUT}

runAndLog "cd \"${OUT}\""
for dotFile in $(ls ./*dot)
do
    withoutDot=${dotFile%.dot}
    runAndLog "dot -T svg $dotFile -o $withoutDot.svg"
done

cd -
cd ..
rm -rf ${TEMPDIR}

