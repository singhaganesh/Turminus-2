.PHONY: ship

ship:
	mkdir -p /app/bin
	# GOPROXY=off matches the image; go never fetches.
	GOPROXY=off /usr/local/go/bin/go build -o /app/bin/wickpane loft.local/wickpane/vatmill
	/app/bin/wickpane etch
	if [ -f /app/shardops/live/poison.stk ]; then mv /app/shardops/live/poison.stk /tmp/wick-ship-poison.stk; fi
	/app/bin/wickpane bin
	if [ -f /tmp/wick-ship-poison.stk ]; then mv /tmp/wick-ship-poison.stk /app/shardops/live/poison.stk; fi
