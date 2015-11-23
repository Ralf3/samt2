grid.so:	grid.py
		cp grid.py grid.pyx
		python3 setup.py build
		cp build/lib.linux-x86_64-3.4/grid.cpython-34m.so ./grid.so

clean:		
		rm grid.so
		rm grid.pyx
		rm grid.c
		rm *~

