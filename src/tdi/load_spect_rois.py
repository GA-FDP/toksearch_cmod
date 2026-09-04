import numpy
import MDSplus as MDS

def load_spect_rois(starts,widths,pixels):
	rois = numpy.empty([len(starts),6],dtype=numpy.int32)
	for i in range(len(starts)):
		rois[i,0]=0
		rois[i,1]=pixels.data()
		rois[i,2]=1
		rois[i,3]=starts.data()[i]
		rois[i,4]=widths.data()[i]
		rois[i,5]=widths.data()[i]
	return MDS.makeArray(rois) 
