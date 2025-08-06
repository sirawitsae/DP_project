import ROOT
import os
import math
import re
from array import array
from ROOT import TFile, TCanvas, TLorentzVector, gStyle

input_base_dir = '/Users/sirawitsae/Desktop/project/DarkPhoton/vbfskim/' 
input_file_paths = [os.path.join(input_base_dir, 'frvz_vbf_500760.root')] ######### Change here #########

# Main processing loop
for path in input_file_paths:
    print("-" * 50)
    print(f"Processing file: {path}")

    try:
        base_name = os.path.basename(path).split('.')[0]
        outputDir = f"2D_ctau_{base_name}"
        os.makedirs(outputDir, exist_ok=True)

        myfile = TFile.Open(path, "READ")
        tree = myfile.Get("miniT")
        if not tree: continue

        outputRootPath = os.path.join(outputDir, f"histograms_{base_name}.root")
        outputFile = TFile(outputRootPath, "RECREATE")
    except Exception as e:
        print(f"Error during setup for {path}: {e}")
        continue

    # Define Histograms (including the new 2D histogram) 
    h_dp_pt = ROOT.TH1F("dp_pt", "dark photon pt; pT [GeV]; Events", 100, 0, 500)
    h_dp_deltaR = ROOT.TH1F("dp_deltaR", "dark photon #DeltaR; #DeltaR; Events", 100, 0, 0.2)
    
    # Define the 2D Histogram
    # X-axis: The approximation 2*m/pT
    # Y-axis: The true Delta R
    h_deltaR_vs_2mPt = ROOT.TH2F("deltaR_vs_2mPt", "True #DeltaR vs. 2m/p_{T} Approximation;Approximation (2m/p_{T});True #DeltaR",
                                 100, 0, 0.2, 100, 0, 0.2)

    # Loop through events and fill all histograms 
    for i in range(tree.GetEntries()):
        tree.GetEntry(i)
        dark_photon_indices = [j for j, pdgId in enumerate(tree.truthPdgId) if pdgId == 3000001]
        if not dark_photon_indices: continue

        for dp_idx in dark_photon_indices:
            # Create the TLorentzVector from the correct branches
            p4 = TLorentzVector()
            p4.SetPtEtaPhiE(tree.truthPt[dp_idx] * 0.001, tree.truthEta[dp_idx], tree.truthPhi[dp_idx], tree.truthE[dp_idx] * 0.001)

            # Find daughters using the 'child' branches
            dp_barcode = tree.truthBarcode[dp_idx]
            daughters = []
            for k in range(len(tree.childPdgId)):
                if tree.childMomBarcode[k] == dp_barcode:
                    daughter_p4 = TLorentzVector()
                    daughter_p4.SetPtEtaPhiM(tree.childPt[k] * 0.001, tree.childEta[k], tree.childPhi[k], 0)
                    daughters.append(daughter_p4)
            
            if len(daughters) == 2:
                deltaR = daughters[0].DeltaR(daughters[1])
                
                # Calculate the approximation and fill the 2D plot
                if p4.Pt() > 0:
                    approx_deltaR = (2 * p4.M()) / p4.Pt()
                    h_deltaR_vs_2mPt.Fill(approx_deltaR, deltaR)

                # Fill 1D histograms as before
                h_dp_pt.Fill(p4.Pt())
                h_dp_deltaR.Fill(deltaR)


    # Write all objects to file and clean up
    outputFile.cd()
    h_dp_pt.Write()
    h_dp_deltaR.Write()
    h_deltaR_vs_2mPt.Write() # Save the new 2D histogram
    
    print(f"Histograms saved to {outputRootPath}")
    
    # Draw and save plots, including the new 2D plot 
    canvas = ROOT.TCanvas("canvas", "Canvas", 800, 600)
    gStyle.SetOptStat(0)
    canvas.cd()
    
    h_dp_pt.Draw("HIST")
    canvas.Print(os.path.join(outputDir, 'dp_pt.png'))

    h_dp_deltaR.Draw("HIST")
    canvas.Print(os.path.join(outputDir, 'dp_deltaR.png'))

    # Draw the 2D histogram using the "colz" option for a heat map 
    canvas.Clear()
    h_deltaR_vs_2mPt.Draw("COLZ")
    canvas.Print(os.path.join(outputDir, 'deltaR_vs_2mPt.png'))

    print(f"All plots saved in {outputDir}")

    outputFile.Close()
    myfile.Close()

print("-" * 50)
print("All files processed.")