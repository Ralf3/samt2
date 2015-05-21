grid.so:	grid.py
		cp grid.py grid.pyx
		python setup.py build
		cp build/lib.linux-x86_64-2.7/grid.so .

clean:		
		rm *~

