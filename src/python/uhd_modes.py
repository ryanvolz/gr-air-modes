#!/usr/bin/env python

from gnuradio import gr, gru, optfir, eng_notation, blks2, air
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from optparse import OptionParser
import time, os, sys
from string import split, join
from usrpm import usrp_dbid
from modes_print import modes_print
from modes_sql import modes_sql
import gnuradio.gr.gr_threading as _threading
import MySQLdb


class top_block_runner(_threading.Thread):
    def __init__(self, tb):
        _threading.Thread.__init__(self)
        self.setDaemon(1)
        self.tb = tb
        self.done = False
        self.start()

    def run(self):
        self.tb.run()
        self.done = True


"""

The following are optional command line parameters:

-R SUBDEV    Daughter board specification, defaults to first found
-f FREQ      USRP receive frequency (1090 MHz Default)
-g GAIN      Daughterboard gain setting. Defaults to mid-range.
-r RATE      USRP sample rate
-t THRESH    Receiver valid pulse threshold
-a           Output all frames. Defaults only output frames

Once the program is running, ctrl-break (Ctrl-C) stops operation.
"""

class adsb_rx_block (gr.top_block):

	def __init__(self, options, args, queue):
		gr.top_block.__init__(self)

		self.options = options
		self.args = args

		if options.filename is None:
			self.u = uhd.simple_source("", uhd.io_type_t.COMPLEX_FLOAT32)

			if(options.rx_subdev_spec is None):
				options.rx_subdev_spec = ""
			self.u.set_subdev_spec(options.rx_subdev_spec)

			rate = options.rate
			self.u.set_samp_rate(rate)
			rate = int(self.u.get_samp_rate()) #retrieve actual

			if options.gain is None: #set to halfway
				g = self.u.get_gain_range()
				options.gain = (g[0]+g[1]) / 2.0

			if not(self.tune(options.freq)):
				print "Failed to set initial frequency"

			print "Setting gain to %i" % (options.gain,)
			self.u.set_gain(options.gain)
#			self.subdev.set_bw(self.options.bandwidth) #only for DBSRX

		else:
			rate = options.rate
			self.u = gr.file_source(gr.sizeof_gr_complex, options.filename)

		print "Rate is %i" % (rate,)
		print "Gain is %i" % (self.u.get_gain(),)
		pass_all = 0
		if options.output_all :
			pass_all = 1

		self.demod = gr.complex_to_mag()
		self.avg = gr.moving_average_ff(100, 1.0/100, 400);
		self.preamble = air.modes_preamble(rate, options.threshold)
		self.framer = air.modes_framer(rate)
		self.slicer = air.modes_slicer(rate, queue)

#		if options.rate < 16:
				#there's a really nasty spur at 1088 caused by a multiple of the USRP xtal. if you use a decimation of 16, it gets filtered out by the CIC. if not, it really fucks with you unless you filter it out.
#				filter_coeffs = gr.firdes.band_reject(1.0, rate, 1.7e6, 2.3e6, 0.5e6, gr.firdes.WIN_HAMMING)
#				self.filt = gr.fir_filter_ccf(1, filter_coeffs)
#				self.connect(self.u, self.filt)
#		else:
		self.filt = self.u

		self.connect(self.filt, self.demod)
		self.connect(self.demod, self.avg)
		self.connect(self.demod, (self.preamble, 0))
		self.connect(self.avg, (self.preamble, 1))
		self.connect(self.demod, (self.framer, 0))
		self.connect(self.preamble, (self.framer, 1))
		self.connect(self.demod, (self.slicer, 0))
		self.connect(self.framer, (self.slicer, 1))

	def tune(self, freq):
		result = self.u.set_center_freq(freq)
		return result


if __name__ == '__main__':
	usage = "%prog: [options] output filename"
	parser = OptionParser(option_class=eng_option, usage=usage)
	parser.add_option("-R", "--rx-subdev-spec", type="subdev",
		      help="select USRP Rx side A or B", metavar="SUBDEV")
	parser.add_option("-f", "--freq", type="eng_float", default=1090e6,
                      help="set receive frequency in Hz [default=%default]", metavar="FREQ")
	parser.add_option("-g", "--gain", type="int", default=None,
                      help="set RF gain", metavar="dB")
	parser.add_option("-r", "--rate", type="int", default=4000000,
                      help="set ADC sample rate [default=%default]")
	parser.add_option("-T", "--threshold", type="eng_float", default=3.0,
                      help="set pulse detection threshold above noise in dB [default=%default]")
	parser.add_option("-a","--output-all", action="store_true", default=False,
                      help="output all frames")
	parser.add_option("-b","--bandwidth", type="eng_float", default=5e6,
		      help="set DBSRX front-end bandwidth in Hz [default=5e6]")
	parser.add_option("-F","--filename", type="string", default=None,
					  help="read data from file instead of USRP")
	parser.add_option("-D","--database", action="store_true", default=False,
											help="send to database instead of printing to screen")
	(options, args) = parser.parse_args()
#	if len(args) != 1:
#		parser.print_help()
#		sys.exit(1)

#	filename = args[0]

	queue = gr.msg_queue()

	if options.database is True:
		db = MySQLdb.connect(host="localhost", user="planes", passwd="planes", db="planes")

	fg = adsb_rx_block(options, args, queue)
	runner = top_block_runner(fg)

	while 1:
		try:
			if queue.empty_p() == 0 :
				while queue.empty_p() == 0 :
					msg = queue.delete_head() #blocking read
					if options.database is False:					
						print modes_print(msg.to_string())
					else:
						query = modes_sql(msg.to_string())
						if query is not None:
							c = db.cursor()
							c.execute(query)

			elif runner.done:
				break
			else:
				time.sleep(0.1)

		except KeyboardInterrupt:
			fg.stop()
			runner = None
			break
