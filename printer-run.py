import uvicorn

if __name__ == "__main__":
	# The Electron app is on this same Windows machine. Never expose the
	# printer agent to the LAN or internet through a wildcard interface.
	uvicorn.run("main:app", host="127.0.0.1", port=5000)
