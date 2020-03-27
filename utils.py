import shutil
import os

def logging(msg, level="info"):
	prefix = ""
	if level == "info":
		prefix = "[INFO]: "
	elif level == "warn":
		prefix = "[WARNING]: "
	else:
		prefix = "[ERROR]: "
	print(prefix, msg)

def try_int(i, ret_value=False):
	try:
		r = int(i)
		if ret_value:
			return r
		else:
			return True
	except ValueError as e:
		if ret_value:
			return i
		else:
			return False

def if_exist_with_create(path, remove=False):
    if not os.path.exists(path):
        logging('create %s since it does not exist.' % \
            path, level='info')
    else:
        logging('%s already exists.' % path, level='info')
        if remove:
	        logging('delete %s.' % path, level='info')
	        shutil.rmtree('%s' % path)
	        logging('recreate %s.' % path)
    os.makedirs(path, exist_ok=True)

def if_exist(path):
    if not os.path.exists(path):
        logging('%s not found.' % path, level='error')
        sys.exit()
    else:
        pass
