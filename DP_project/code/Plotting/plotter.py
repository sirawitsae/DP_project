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
        infiles = 'bg_sig.json'
        plotSignal = True 
        ratio_string  = ''

        # Lepton Jet Kinematics
        self.newplot(infiles, 'LJjet1_pt*0.001', 'Leading Lepton Jet p_{T}', 'GeV', 'vbffilter', 50, 0, 0.8e3)
        self.newplot(infiles, 'LJjet1_eta', 'Leading Lepton Jet #eta', '', 'vbffilter', 50, -3, 3)
        # self.newplot(infiles, 'LJjet1_phi', 'Leading Lepton Jet #phi', 'rad', 'vbffilter', 50, -3.5, 3.5)
        self.newplot(infiles, 'LJjet1_m*0.001', 'Leading Lepton Jet Mass', 'GeV', 'vbffilter', 50, 0, 50)
        
        # Lepton Jet Shape and Composition
        self.newplot(infiles, 'LJjet1_width', 'Leading Lepton Jet Width', '', 'vbffilter', 50, 0, 0.3)
        self.newplot(infiles, 'LJjet1_EMfrac', 'Leading Lepton Jet EM Fraction', '', 'vbffilter', 50, 0, 0.4)

        
        # Lepton Jet Timing and Vertexing
        # self.newplot(infiles, 'LJjet1_timing', 'Leading Lepton Jet Timing', 'ns', 'vbffilter', 50, -40, 40)
        self.newplot(infiles, 'LJjet1_jvt', 'Leading Lepton Jet JVT', '', 'vbffilter', 50, -0.2, 1.3)

        # self.newplot(infiles, 'LJjet1_jvt', 'Leading Lepton Jet JVT', '', 'vbffilter', 50, -0.2, 1.3)

    def newplot(self, files, variable, variablename, units, region, nbins, xmin, xmax, ymin = 0, ymax = 0, PLOTSIGNALS = True, ratioplot = '',forcebins=False, plotLOG=True):
      
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
