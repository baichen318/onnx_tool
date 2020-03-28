import onnx
import argparse
import os
import sys
from onnx import shape_inference
from collections import OrderedDict
from ONNXGraph import ONNXGraph
from utils import logging, if_exist_with_create

def parse():
	parser = argparse.ArgumentParser()

	parser.add_argument("-i", "--onnx_model",
		type=str,
		default="onnx_model/holedetect.onnx",
		help="input the path of onnx model")
	parser.add_argument("-o", "--output",
		type=str,
		default="output",
		help="input the path to save models")
	parser.add_argument("-d", "--f-delete",
		action='store_true',
        help='delete output before running \
        	if --f-delete is set')

	argv = parser.parse_args()

	return argv

def parse_onnx(argv):

	def set_up(model):
		if_exist_with_create(argv.output, argv.f_delete)

		if hasattr(onnx.checker, "check_model"):
			try:
				onnx.checker.check_model(model)
			except onnx.onnx_cpp2py_export.checker.ValidationError as e:
				import warnings
				warnings.warn(str(e))

		inferred_model = shape_inference.infer_shapes(model)

		return inferred_model

	if not os.path.exists(argv.onnx_model):
		logging("%s not found." % model, level="ERROR")
		sys.exit()

	model = onnx.load(argv.onnx_model)
	inferred_model = set_up(model)
	name = os.path.basename(argv.onnx_model).rsplit(".", -1)[0]

	g = ONNXGraph(inferred_model, name, argv.output)
	g.split()

if __name__ == "__main__":
	argv = parse()

	parse_onnx(argv)

