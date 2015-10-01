# Need to redefine these dumb environment-tweaking functions which are defined
# in a "normal" ATLAS environment and used by some of the setup scripts.
insertPath()
{
    if eval test -z \${$1}; then
        eval "$1=$2"
        export $1
    elif ! eval test -z \"\${$1##$2}\" -o -z \"\${$1##\*:$2:\*}\" -o -z \"\${$1%%\*:$2}\" -o -z \"\${$1##$2:\*}\" ; then
        local alrb_thePath=$1
        local alrb_cmd="\echo \$$alrb_thePath"
        local alrb_thePathVal=`eval $alrb_cmd`
        eval "$alrb_thePath=$2:$alrb_thePathVal"
        export $alrb_thePath
    fi
}
deletePath()
{
    eval "$1=\$(\echo \$$1 | \sed -e s%\^$2\$%% -e s%\^$2\:%% -e s%:$2\:%:%g -e s%:$2\\\$%%)"
    export $1
}

export ATLAS_LOCAL_ROOT_BASE="/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase"

# Set up GCC. This sets up required standard libs.
source ${ATLAS_LOCAL_ROOT_BASE}/packageSetups/atlasLocalGccSetup.sh --gccVersion gcc484_x86_64_slc6
echo .
echo .

# Setup python in standard way.
source ${ATLAS_LOCAL_ROOT_BASE}/packageSetups/atlasLocalPythonSetup.sh 2.7.4-x86_64-slc6-gcc48

# Try setting up ROOT (manually; bypassing standard setup)
source /cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/x86_64/root/6.02.12-x86_64-slc6-gcc48-opt/bin/thisroot.sh
# Standard ROOT setup fails with current analysis image (missing cvmfs directories)
#source ${ATLAS_LOCAL_ROOT_BASE}/packageSetups/atlasLocalROOTSetup.sh --rootVersion 6.02.12-x86_64-slc6-gcc48-opt
echo .
echo .

# Try setting up the analysis release using my pre-built workdir.
cd ..
source /cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/x86_64/rcSetup/current/rcSetup.sh
echo .
echo .
cd run_edison
