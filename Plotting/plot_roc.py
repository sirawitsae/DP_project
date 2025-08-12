import ROOT, argparse
from ROOT import TFile, TTree, TH1D, TCanvas, THStack, gROOT, TLegend, TPad, TLine, TArrow

import os
import sample
import plotutils as plotutils

class plotter:

    def __init__(self):

        self.REGIONS_FILE = 'regions.json'

        # NORMALISATIONS
        #self.MCWEIGHTSTRING = 'xsec * lumi * WeightEvents * WeightSF_e * WeightSF_mu * WeightEventsSherpa * WeightPileUp * jvfSF * PassTruthMetFilter * WeightTrigger_DiLep * (1./SumOfWeights)'
        self.MCWEIGHTSTRING = '1'
        self.DATAWEIGHTSTRING = '1'   

        # SETTINGS

        self.ATLASLABEL = 'Internal'
        self.PLOTLOG = True
        self.PLOTSIGNALS = True
        self.PLOTARROWS = True
        self.blind = False 
        self.RATIOMIN = 0.0
        self.RATIOMAX = 10.0

    def run(self):

        # Set ATLAS style
        gROOT.LoadMacro("ATLAS_Style/atlasstyle-00-03-05/AtlasStyle.C")
        gROOT.LoadMacro("ATLAS_Style/atlasstyle-00-03-05/AtlasUtils.C")
        ROOT.SetAtlasStyle() 
        gROOT.SetBatch()

        # Run plotting
        #def newplot(self, files, variable, variablename, units, region, nbins, xmin, xmax, ymin = 0, ymax = 0, PLOTSIGNALS = False, ratioplot = '',forcebins=False, plotLOG=True):
        infiles = 'roc_curve.json'
        plotSignal = True 
        ratio_string  = ''

        self.newplot(infiles, 'LJjet1_BDT', 'BDT BG vs Signal', '', 'vbffilter', 50, -1., 1.)
        self.newplot(infiles, 'LJjet1_DPJtagger', 'DPJtagger BG vs Signal', '', 'vbffilter', 50, 0., 1.)
        self.newplot(infiles, 'mse', 'mse BG vs Signal', '', 'vbffilter', 50, 0., 5.)

    def newplot(self, files, variable, variablename, units, region, nbins, xmin, xmax, ymin = 0, ymax = 1, PLOTSIGNALS = True, ratioplot = '',forcebins=False, plotLOG=True):
      
        # Create directory for plots
        if region not in os.listdir('./'):
            os.system('mkdir ./{}'.format(region))

        # Create instance of plot utils
        pu = plotutils.plotutils()

        # Setup canvas
        c = TCanvas('c','c',800,600)
        # Setup TLegend
        pu.setuplegend(y0 = 0.6)

        # Setup TPad
        pu.setuppad(plotLOG, ratioplot)

        # Setup plotutils
        if ('SR' in region or 'sr' in region or 'Sr' in region):
            forceblind = True
        else:
            forceblind = False

        pu.setup(c, files, self.REGIONS_FILE, variable, variablename, units, region, self.MCWEIGHTSTRING, nbins, xmin, xmax, ymin, ymax, self.PLOTLOG, PLOTSIGNALS, self.PLOTARROWS, forceblind, forcebins)
        # Draw histograms
        pu.drawhists()
        #pu.fit('Data')

        # Draw legend
        pu.legend.Draw()

        # Do ratio plot
        if ratioplot != '':
            pu.plotdatamcratio(self.RATIOMIN, self.RATIOMAX, ratioplot.split(':')[0], ratioplot.split(':')[1])
            #pu.plotratioline(self.RATIOMIN, self.RATIOMAX, ['Data'], ['totalSM'], [1])
            #pu.plotratioline(self.RATIOMIN, self.RATIOMAX, ['single top'], ['Z+jets'],3,False)

        # Draw axis labels and ATLAS label    
        pu.decorate(self.ATLASLABEL, region)

        # Name output file
        suffix = ''
        if ratioplot != '':
            suffix = '_{}'.format(ratioplot)  
        filename_pdf = '{}_{}{}.pdf'.format(variable.split('*')[0], region, suffix)
        filename_png = '{}_{}{}.png'.format(variable.split('*')[0], region, suffix)
        c.SaveAs(filename_pdf)
        c.SaveAs(filename_png)

        # Move output file to region folder
        os.system('mv {} {}'.format(filename_pdf, region))
        os.system('mv {} {}'.format(filename_png, region))

if __name__=='__main__':
    plotter().run()    
