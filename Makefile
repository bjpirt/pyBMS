.PHONY: test
test:
	python -m unittest --verbose

.PHONY: integration-test
integration-test:
	python -m unittest discover -p '*integration*' --verbose 

.PHONY: module-fake-serial
module-fake-serial:
	socat  -d -d pty,rawer,echo=0,link=port1-end-a pty,rawer,echo=0,link=port1-end-b

.PHONY: pack-fake-serial
pack-fake-serial:
	socat  -d -d pty,rawer,echo=0,link=port1-end-a pty,rawer,echo=0,link=port1-end-b &
	socat  -d -d pty,rawer,echo=0,link=port2-end-a pty,rawer,echo=0,link=port2-end-b &
	socat  -d -d pty,rawer,echo=0,link=port3-end-a pty,rawer,echo=0,link=port3-end-b &

.PHONY: kill-socat
kill-socat:
	killall socat
