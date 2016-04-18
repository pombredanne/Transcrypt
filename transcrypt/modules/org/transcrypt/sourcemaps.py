import os
import math
import collections
import json
import shutil

from org.transcrypt import utils

# Tools to embed source map info in target code

lineNrMarker = chr (27)
maxNrOfSourceLinesPerModule = 1000000000
lineNrLength = 11

# Tools to encode numbers as base 64 variable length quantities

class GetBase64Vlq:
	def __init__ (self):
		self.nBits32 = 5
		self.encoding = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
		
		# The most used vlq's are prefabricated
		self.prefabSize = 256
		self.prefab = [self (i, True) for i in range (self.prefabSize)]
	
	def __call__ (self, anInteger, init = False):
		if not init and 0 < anInteger < self.prefabSize:
			return self.prefab [anInteger]
		else:
			signed = bin (abs (anInteger)) [2 : ] + ('1' if anInteger < 0 else '0')
			nChunks = math.ceil (len (signed) / float (self.nBits32))
			padded = (self.nBits32 * '0' + signed) [-nChunks * self.nBits32 : ]
			chunks = [('1' if iChunk else '0') + padded [iChunk * self.nBits32 : (iChunk + 1) * self.nBits32] for iChunk in range (nChunks - 1, -1, -1)]
			return ''.join ([self.encoding [int (chunk, 2)] for chunk in chunks])

getBase64Vlq = GetBase64Vlq ()	# Instantiation of functor

# Tools to create and combine sourcemaps

mapVersion = 3

class ModuleMapperMixin:
	def generateMap (self, fake = False):
		self.rawMap = collections.OrderedDict ([
			('version', mapVersion),
			('file', self.metadata.targetPath),
			('sources', [self.metadata.mapSourceFileName]),
			('mappings', (
				';'.join (['AACA'] * self.targetCode.count ('\n'))
			) if fake else (
				';'.join ([
					'AA{}A'.format (getBase64Vlq (sourceLineNrDelta))
					for sourceLineNrDelta in [
						self.sourceLineNrs [index] - (self.sourceLineNrs [index - 1] if index else 0)
						for index in range (len (self.sourceLineNrs))
					]
				])
			))
		])
		
		with utils.create (self.metadata.mapPath) as aFile:
			aFile.write (json.dumps (self.rawMap, indent = '\t'))
		
		shutil.copyfile (self.metadata.sourcePath, self.metadata.mapSourcePath)
	
	def loadOrFakeMap (self):
		if (
			not (os.path.isfile (self.metadata.mapPath) and os.path.isfile (self.metadata.mapSourcePath))	# Both files are needed, and one may have been thrown away
			or
			(utils.commandArgs.build and self.metadata.sourcePath.endswith ('.js'))	# In case of a build and a JavaScript only module, force generation of new fake map
		):
			self.generateMap (True)
		else:	
			with open (self.metadata.mapPath) as aFile:
				self.rawMap = json.loads (aFile.read ())
				
class ProgramMapperMixin:
	def generateMap (self)	:	
		totalOffset = 0
		rawSections = []
		
		for module in self.allModules:
			if module.rawMap:
				rawSections.append (collections.OrderedDict ([
					('offset', collections.OrderedDict ([
						('line', totalOffset),
						('column', 0)
					])),
					('map',  module.rawMap)
				]))		
				
				if module.metadata.name != self.mainModuleName:
					shutil.copy (module.metadata.mapSourcePath, self.moduleDict [self.mainModuleName] .metadata.mapDir)

			totalOffset += module.targetCode.count ('\n')
			
		with utils.create (self.mapPath) as aFile:
			aFile.write (json.dumps (collections.OrderedDict ([
				('version', mapVersion),
				('file', self.targetPath),
				('sections', rawSections)
			]), indent = '\t'))
			
		for module in self.allModules:
			if module.metadata.name != self.mainModuleName:
				shutil.copy (module.metadata.mapSourcePath, self.moduleDict [self.mainModuleName] .metadata.mapDir)
