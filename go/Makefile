.PHONY: format
format:
	gofmt -tabs=false -tabwidth=2 -w `find src -name '*.go'`

.PHONY: test
test:
	GOPATH="$(PWD)" go test `find src -mindepth 2 -type d  -printf '%P\n'`
