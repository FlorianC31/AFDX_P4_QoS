#!/usr/bin/env sh
# please don't `sudo` this script, that would be dangerous

if test 0 -eq $# || test '-h' = "$1"
	then
		echo "Usage: $0 <program.p4> [<dest.p4app/>]"
		exit 1
fi

set -ex
PROG=$1
APP=${2:-./dest.p4app}

[ -f "$PROG" ] || { echo "no such program.p4: '$PROG'"; exit 1; }
[ -d "$APP" ] || mkdir "$APP"

# rm -r $APP/* but somewhat safer
cd "$APP"
rm -r * 2>/dev/null || true
cd - >/dev/null

make_app() {
	cp common/p4app.json "$APP/p4app.json"
	cp common/topo.py "$APP/topo.py"
	cp "$PROG" "$APP/afdx.p4"

	# try to find (first-depth-) relative includes
	# delta=$(realpath --relative-to=$APP $(dirname "$PROG"))
	for file in $(sed -n 's|^\(\s*#include\s*\)"\(.*\)"|\2|p' "$PROG")
		do cp "$(dirname "$PROG")/$file" "$APP"
	done
}

make_topo() {
	TOPO_MAN=../../TopologyManager/TopoManager.py
	TOPO_DESC=../../TopologyManager/input_topo.txt # for now just uses this one

	# have yourself a p4app jic
	cp ../../p4app "$APP/p4app"

	# see with TopoManager directly as for the
	# few following `exports`

	export ACTION_NAME=Check_VL

	cp ../../TopologyManager/send_afdx_packet.py "$APP/send_afdx_packet.py"
	export MININET_SNIFFER_SCRIPT=send_afdx_packet.py
	cp ../../sniffer/sniffer_mininet.py "$APP/sniffer_mininet.py"
	export MININET_SNIFFER_SCRIPT=sniffer_mininet.py

	# in this case, the priority is used to indicate
	# weight for rr (in the p4's Check_VL action)
	export P4APP_PRIORITY=1

	python3 $TOPO_MAN $TOPO_DESC p4app "$APP"
}

run_app() {
	# a simple `p4app run <.p4app/>` may not work
	# without prior `p4app pack` (at least for me)

	# use a copy because `p4app pack` is inplace fsr (tar)
	_APP=$(dirname "$APP")/_$(basename "$APP")
	# (setup atexit to remove archive)
	trap "rm -f '$_APP'" EXIT

	rm -r "$_APP" 2>/dev/null || true
	cp -r "$APP" "$_APP"

	p4app pack "$_APP"
	read -p 'continue? (^M/^C)' _
	p4app run "$_APP"
}

make_app
make_topo
run_app
