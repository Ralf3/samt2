grid.so:	grid.py
		cp grid.py grid.pyx
		python3 setup.py build
		cp build/lib.linux-x86_64-3.6/grid.cpython-36m-x86_64-linux-gnu.so grid.so

clean:		
		rm grid.so
		rm grid.c
		rm grid.pyx
		rm *~

