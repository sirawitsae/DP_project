import ROOT
import os
import math
from ROOT import TFile, TCanvas, TLorentzVector, gStyle, TEfficiency

input_file_path = "/Users/sirawitsae/Desktop/project/DarkPhoton/vbfljetskim/frvz_vbf_500764.root" ####### Input file here ##########
output_dir = "output_eff_plot/eff_plots_64/" ####### directory name eff_plots_(DSID) ##########
    
print(f"--- Calculating Efficiency and Fake Rate for {os.path.basename(input_file_path)} ---")

os.makedirs(output_dir, exist_ok=True)
input_file = TFile.Open(input_file_path, "READ")
tree = input_file.Get("miniT")

output_file = TFile(os.path.join(output_dir, "eff_plots.root"), "RECREATE")

# Define Histograms 
lxy_bins = (20, 0, 5.0) 
pt_bins = (20, 0, 100) 

h_num_eff_lxy = ROOT.TH1F("h_num_eff_lxy", "", *lxy_bins)
h_den_eff_lxy = ROOT.TH1F("h_den_eff_lxy", "", *lxy_bins)
h_num_eff_pt = ROOT.TH1F("h_num_eff_pt", "", *pt_bins)
h_den_eff_pt = ROOT.TH1F("h_den_eff_pt", "", *pt_bins)

# Loop through events to fill all histograms
for i in range(tree.GetEntries()):
    tree.GetEntry(i)

    # Collect all truth DPs in the event
    truth_dps = []
    for j in range(len(tree.truthPdgId)):
        if tree.truthPdgId[j] == 3000001:
            if abs(tree.truthEta[j]) < 1.1 and tree.truthPt[j] > 20e3 and tree.truthDecayType[j] != 13: # PdgId = 13 is Muon
                p4 = TLorentzVector()
                p4.SetPtEtaPhiE(tree.truthPt[j]*0.001, tree.truthEta[j], tree.truthPhi[j], tree.truthE[j]*0.001)
                dx = tree.truthDecayVtx_x[j]; dy = tree.truthDecayVtx_y[j]
                truth_dps.append({'p4': p4, 'lxy': math.sqrt(dx**2 + dy**2)})
        
    if not truth_dps: continue # If no event collected

    # Denominator: Every truth DP that exists
    for dp in truth_dps:
        lxy_m = dp['lxy'] * 0.001 # convert to meters
        pt = dp['p4'].Pt()
        h_den_eff_lxy.Fill(lxy_m)
        h_den_eff_pt.Fill(pt)
            
        # Numerator: Check if this truth DP is matched to the reco jet
        if tree.nLJjets20 > 0: # Apply cuts to LJjet
            for k in range(len(tree.LJjet_index)):
                if tree.LJjet_EMfrac[k] < 0.4 and tree.LJjet_gapRatio[k] > 0.9 and tree.LJjet_pt[k] > 20e3:
                    reco_p4 = TLorentzVector()
                    # Use the correct array branches for the k-th jet
                    reco_p4.SetPtEtaPhiM(tree.LJjet_pt[k]*0.001, tree.LJjet_eta[k], tree.LJjet_phi[k], tree.LJjet_m[k]*0.001)
                    
            if dp['p4'].DeltaR(reco_p4) < 0.4:
                h_num_eff_lxy.Fill(lxy_m)
                h_num_eff_pt.Fill(pt)

# Create, Plot, and Save TEfficiency objects
canvas = TCanvas("c_plots", "Performance Canvas", 800, 600); gStyle.SetOptStat(0)
    
def create_and_save_plot(num, den, name, title, xtitle, ytitle):
    eff = TEfficiency(num, den)
    eff.SetName(name)
    eff.SetTitle(f"{title};{xtitle};{ytitle}")
    eff.Draw("AP"); canvas.Update(); eff.GetPaintedGraph().GetYaxis().SetRangeUser(0, 1.05)
    canvas.Print(os.path.join(output_dir, f"{name}.png"))
    output_file.cd(); eff.Write(name)

create_and_save_plot(h_num_eff_lxy, h_den_eff_lxy, "efficiency_vs_lxy", "Efficiency", "Truth DP L_{xy} [m]", "Efficiency")
create_and_save_plot(h_num_eff_pt, h_den_eff_pt, "efficiency_vs_pt", "Efficiency", "Truth DP p_{T} [GeV]", "Efficiency")
  
print(f"\nEfficiency plots saved to directory: {output_dir}")
output_file.Close(); input_file.Close()

