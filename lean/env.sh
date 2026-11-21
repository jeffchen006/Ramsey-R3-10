if [ -z "${ELAN_HOME:-}" ]; then
    if [ -x ./tools/elan/bin/elan ]; then
        ELAN_HOME=./tools/elan
    else
        ELAN_HOME="$HOME/.elan"
    fi
fi
export ELAN_HOME
export PATH="$ELAN_HOME/bin:$PATH"
