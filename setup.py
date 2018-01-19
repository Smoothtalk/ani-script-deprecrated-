import os
import subprocess

try:
    subprocess.call(["pip", "install", "bs4"])
except OSError as e:
	print (type(e))
	if e.errno == os.errno.ENOENT:
		print ("FNF")
	else:
		raise

# try:
#     subprocess.call([""])
# except OSError as e:
#     if e.errno == os.errno.ENOENT:
#         # handle file not found error.
#     else:
#         # Something else went wrong while trying to run `wget`
#         raise
#
# try:
#     subprocess.call([""])
# except OSError as e:
#     if e.errno == os.errno.ENOENT:
#         # handle file not found error.
#     else:
#         # Something else went wrong while trying to run `wget`
#         raise
#
# try:
#     subprocess.call([""])
# except OSError as e:
#     if e.errno == os.errno.ENOENT:
#         # handle file not found error.
#     else:
#         # Something else went wrong while trying to run `wget`
#         raise
#
# try:
#     subprocess.call([""])
# except OSError as e:
#     if e.errno == os.errno.ENOENT:
#         # handle file not found error.
#     else:
#         # Something else went wrong while trying to run `wget`
#         raise
#
# try:
#     subprocess.call([""])
# except OSError as e:
#     if e.errno == os.errno.ENOENT:
#         # handle file not found error.
#     else:
#         # Something else went wrong while trying to run `wget`
#         raise
