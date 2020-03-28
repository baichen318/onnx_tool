import onnx
from onnx import helper
from onnx import AttributeProto, TensorProto, GraphProto
from utils import logging, try_int
import sys
import os

class ONNXGraph(object):
	"""Add layers to be splitted for ONNXGraph"""
	layer = ["Upsample", "InstanceNormalization", "ConvTranspose", \
		"Constant", "Exp", "ReduceSum", "Div", "Shape"]

	def __init__(self, model, prefix, output_path):
		super(ONNXGraph, self).__init__()
		self.model = model
		self.prefix = prefix
		self.output_path = output_path
		self.init()
		self.cnt = 0
		self.repeat = []

	def init(self):
		self.node = None
		self.input_name = None
		self.output_name = None
		self.inp_tvi = []
		self.oup_tvi = []
		self.tensor = []

	def get_input_value_info(self):
		for i in self.input_name:
			for inp in self.model.graph.input:
				if inp.name == i:
					self.inp_tvi.append(inp)
			for vi in self.model.graph.value_info:
				if vi.name == i:
					self.inp_tvi.append(vi)

	def get_output_value_info(self):
		for i in self.output_name:
			for oup in self.model.graph.value_info:
				if oup.name == i:
					self.oup_tvi.append(oup)
			if i == self.model.graph.output[0].name:
				self.oup_tvi.append(self.model.graph.output[0])

	def get_tensor(self):
		for i in self.input_name:
			for init in self.model.graph.initializer:
				if init.name == i:
					self.tensor.append(init)

	def generate_onnx(self, name):
		graph = helper.make_graph([self.node],
			name, inputs=self.inp_tvi,
			outputs=self.oup_tvi,
			initializer=self.tensor)
		model = helper.make_model(graph,
			producer_name="CUDA-FPGA")
		if len(self.repeat) > 0 and self.repeat[-1] == name:
			self.cnt += 1
		else:
			self.cnt = 0
		save_path = os.path.join(self.output_path,
			self.prefix + "_" + name + "_" + str(self.cnt) + ".onnx")
		onnx.save(model, save_path)
		logging("save the model in %s." % save_path, level="info")
		self.init()
		self.repeat.append(name)

	def extract_layer(self, name):
		for i in range(len(self.model.graph.node)):
			if self.model.graph.node[i].op_type == name:
				self.node = self.model.graph.node[i]
				self.input_name = self.model.graph.node[i].input
				self.output_name = self.model.graph.node[i].output
				self.get_input_value_info()
				self.get_output_value_info()
				self.get_tensor()
				self.generate_onnx(self.model.graph.node[i].op_type)

	def split(self):
		for i in ONNXGraph.layer:
			self.extract_layer(i)

