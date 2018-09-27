Pyfuzzy.so:	Pyfuzzy.py 
		cp Pyfuzzy.py Pyfuzzy.pyx
		python3 setup.py build
		# cp build/lib.linux-x86_64-2.7/Pyfuzzy.so ./Pyfuzzy.so
		cp build/lib.linux-x86_64-3.6/Pyfuzzy.cpython-36m-x86_64-linux-gnu.so ./Pyfuzzy.so

clean:		
		rm *.so
		rm *.c
		rm Pyfuzzy.pyx
