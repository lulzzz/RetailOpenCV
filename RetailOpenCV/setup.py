from distutils.core import setup
import py2exe

setup(console=['RetailOpenCV.py'],
        options={
            "py2exe": {
                "dll_excludes": ["MSVFW32.dll",
                                 "AVIFIL32.dll",
                                 "AVICAP32.dll",
                                 "ADVAPI32.dll",
                                 "CRYPT32.dll",
                                 "WLDAP32.dll"]
                }



},)