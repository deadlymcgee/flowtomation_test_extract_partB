part A test:
	_flowtomation_sample.json


Part B tests:

the numbers below correspond to configuration files in the 'test_files' directory unless stated otherwise
the following tests have 2 x files:
5
6




1. an empty json program configuration file (no text at all)
	Expected result: 
		log critical level message
		abort with message
		
2. an invalid json program configuration file (just bad json)
	Expected result: 
		log critical level message
		abort with message
		
3. an invalid program configuration (correct json, but bad key/values for this problem)
	Expected result: 
		log critical level message
		abort with message
		
4. a flow with only a single service
	Expected result:
		run the service
		exit the flow
		re-run the flow on next program run
		
5. a flow calling on a service that always returns an exit status of 1 (call the service "fail.py" if you like)
	Expected result: 
		flow will exit.
		log error containing service STDOUT
		log warning
		Program will run next flow or re-run flow if only one flow
		
6. a flow that runs successfully
	Expected result: 
		Program will run next flow or re-run flow if only one flow
		
7. a flow that calls services that take longer than one minute (have a service that does a time.sleep(60))
	Expected result: 
		program waits until service has finished
		Runs the next services in the flow straight away
		Program runs next flow on the next available minute
		
8. a file that includes multiple flows.
	Expected result:
		Runs one flow after another on each program run
9. Service that outputs invalid JSON
	Expected result: 
		log error
		Exit flow
10. Service that outputs JSON missing 'data' field
	Expected result:
		log error
		Exit flow
11. Error running service
	i.e.
		Permission issue
		File not found
	Expected result:
		Log error
		Exit flow
12. Input/Output data type verification failure
	Expected result:
		Log error
		Exit flow
13. Optional field verification failure - missing 'type' key
	Expected result:
		Log error
		do not load service
		Flow with service configured will be skipped
		
14. Optional field verification failure - unsupported input/ouput type
	Expected result:
		Log error
		do not load service
		Flow with service configured will be skipped
		
15. Optional field verification failure - parameter field type not 'string'
	Expected result:
		Log error
		do not load service
		Flow with service configured will be skipped

16. loading a service with the same name as service already present in running configuration 
	note: this test can be tested with any program file
	Expected result:
		Log error
		do not load service
		Flow with service configured will be skipped	

17. Mandatory field verification failure
	Expected result:
		Log error
		do not load service
		Flow with service configured will be skipped
18. Service received/sent data without input/output configuration
		Expected result:
			Log error
			exit flow


19. Invalid time received as output from a service
		Expected result:
			Log error
			exit flow

21. test service name and directory name mismatch
	note: tested by trying to load service 'test 21'
		Expected result:
			log error
			do not load service
			
22. test cleanup running-configuration (remove uninstalled services)
	note: tested by removing directory 'test 22' after first run with 'debug' logging enabled (see program README.txt)
	Expected result:
		log 'debug' level log
		
23. service configured in flow missing from running-configuration
	note: tested by running program with default configuration
		expected result:
			log warning
			do not run (skip) flow
		