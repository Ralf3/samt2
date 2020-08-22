grid.so:	grid.py
		cp grid.py grid.pyx
		python3 setup.py build
		cp build/lib.linux-x86_64-3.8/*.so grid.so

clean:		
		rm grid.so
		rm grid.c
		rm grid.pyx
		rm *~

