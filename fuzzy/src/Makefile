Pyfuzzy.so:	Pyfuzzy.py 
		cp Pyfuzzy.py Pyfuzzy.pyx
		python3 setup.py build
		# cp build/lib.linux-x86_64-2.7/Pyfuzzy.so ./Pyfuzzy.so
		cp build/lib.linux-x86_64-3.8/*.so ./Pyfuzzy.so

clean:		
		rm *.so
		rm *.c
		rm Pyfuzzy.pyx
