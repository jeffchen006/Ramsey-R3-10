# Source this file: . ./tools/env.sh
T=./tools
export PATH="$T/bin:$T/opt/rust/cargo/bin:$PATH"
export RUSTUP_HOME="$T/opt/rust/rustup" CARGO_HOME="$T/opt/rust/cargo"
export CPATH="$T/opt/cadical/include:$T/opt/kissat/include:$T/opt/nauty/include${CPATH:+:$CPATH}"
export LIBRARY_PATH="$T/opt/cadical/lib:$T/opt/kissat/lib:$T/opt/nauty/lib:$T/opt/sms/lib${LIBRARY_PATH:+:$LIBRARY_PATH}"
unset T
