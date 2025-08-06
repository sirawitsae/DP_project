import ROOT
import os
import math
from ROOT import TFile, TCanvas, TLorentzVector, gStyle, TEfficiency

input_file_path = "/Users/sirawitsae/Desktop/project/DarkPhoton/vbfljetskim/frvz_vbf_500757.root" ############# Change here ################
output_dir = "output_fake_plot/rates_plots_57/" ############# Change here ################
os.makedirs(output_dir, exist_ok=True)

input_file = TFile.Open(input_file_path, "READ")
tree = input_file.Get("miniT")

output_file = TFile(os.path.join(output_dir, "rates_plots.root"), "RECREATE")

# Define Histograms
eta_bins = (20, -2, 2)
phi_bins = (20, -3, 3)
pt_bins = (20, 0, 100)

# Denominator: All reconstructed Lepton Jets that pass the preselection
h_eta_all = ROOT.TH1F("h_eta_all", "Denominator for Rates vs Eta", *eta_bins)
h_phi_all = ROOT.TH1F("h_phi_all", "Denominator for Rates vs Phi", *phi_bins)
h_pt_all = ROOT.TH1F("h_pt_all", "Denominator for Rates vs Pt", *pt_bins)

# Numerator for Matched Rate
h_eta_match = ROOT.TH1F("h_eta_match", "Numerator for Matched Rate vs Eta", *eta_bins)
h_phi_match = ROOT.TH1F("h_phi_match", "Numerator for Matched Rate vs Phi", *phi_bins)
h_pt_match = ROOT.TH1F("h_pt_match", "Numerator for Matched Rate vs Pt", *pt_bins)

# Numerator for Fake Rate
h_eta_fake = ROOT.TH1F("h_eta_fake", "Numerator for Fake Rate vs Eta", *eta_bins)
h_phi_fake = ROOT.TH1F("h_phi_fake", "Numerator for Fake Rate vs Phi", *phi_bins)
h_pt_fake = ROOT.TH1F("h_pt_fake", "Numerator for Fake Rate vs Pt", *pt_bins)



# Loop through events to fill all histograms
for i in range(tree.GetEntries()):
    tree.GetEntry(i)

    # Apply your specified preselection cuts first 
    cuts = (tree.nLJjets20 > 0 and
            tree.LJjet1_pt > 20e3 and
            tree.LJjet1_EMfrac < 0.4 and
            tree.LJjet1_gapRatio > 0.9)
    
    # If the event does not pass the preselection, skip it
    if not cuts:
        continue

    # Denominator: Every reconstructed LJjet1 that passes the preselection goes here 
    reco_p4 = TLorentzVector()
    reco_p4.SetPtEtaPhiM(tree.LJjet1_pt*0.001, tree.LJjet1_eta, tree.LJjet1_phi, tree.LJjet1_m*0.001)
    
    h_eta_all.Fill(reco_p4.Eta())
    h_phi_all.Fill(reco_p4.Phi())
    h_pt_all.Fill(reco_p4.Pt())

    # Numerators: Check if the preselected reco jet is matched or fake
    # Collect all truth DPs in the event to check for a match
    truth_dps = []
    for j in range(len(tree.truthPdgId)):
        if tree.truthPdgId[j] == 3000001:
            p4 = TLorentzVector()
            p4.SetPtEtaPhiE(tree.truthPt[j]*0.001, tree.truthEta[j], tree.truthPhi[j], tree.truthE[j]*0.001)
            truth_dps.append(p4)

    # Determine if a match exists
    is_matched = False
    if truth_dps:
        for dp_p4 in truth_dps:
            if reco_p4.DeltaR(dp_p4) < 0.4:
                is_matched = True
                break # Found a match
    
    # Fill the correct numerator based on match status
    if is_matched:
        h_eta_match.Fill(reco_p4.Eta())
        h_phi_match.Fill(reco_p4.Phi())
        h_pt_match.Fill(reco_p4.Pt())
    else: # If not matched, it's a fake
        h_eta_fake.Fill(reco_p4.Eta())
        h_phi_fake.Fill(reco_p4.Phi())
        h_pt_fake.Fill(reco_p4.Pt())


# Create, Plot, and Save the Rate plots 
canvas = TCanvas("c_rates", "Rates Canvas", 800, 600); gStyle.SetOptStat(0)

def create_and_save_plot(num, den, name, title, xtitle, ytitle):
    eff = TEfficiency(num, den)
    eff.SetName(name)
    eff.SetTitle(f"{title};{xtitle};{ytitle}")
    eff.Draw("AP"); canvas.Update(); eff.GetPaintedGraph().GetYaxis().SetRangeUser(0, 1.05)
    canvas.Print(os.path.join(output_dir, f"{name}.png"))
    output_file.cd(); eff.Write()

# Create Matched Rate plots
create_and_save_plot(h_eta_match, h_eta_all, "matched_rate_vs_eta", "Matched Rate vs. #eta", "Reconstructed LJ #eta", "Matched Rate")
create_and_save_plot(h_phi_match, h_phi_all, "matched_rate_vs_phi", "Matched Rate vs. #phi", "Reconstructed LJ #phi", "Matched Rate")
create_and_save_plot(h_pt_match, h_pt_all, "matched_rate_vs_pt", "Matched Rate vs. #pt", "Reconstructed LJ #pt", "Matched Rate")
# Create Fake Rate plots
create_and_save_plot(h_eta_fake, h_eta_all, "fake_rate_vs_eta", "Fake Rate vs. #eta", "Reconstructed LJ #eta", "Fake Rate")
create_and_save_plot(h_phi_fake, h_phi_all, "fake_rate_vs_phi", "Fake Rate vs. #phi", "Reconstructed LJ #phi", "Fake Rate")
create_and_save_plot(h_pt_fake, h_pt_all, "fake_rate_vs_pt", "Fake Rate vs. #pt", "Reconstructed LJ #pt", "Fake Rate")

print(f"\nRate plots and ROOT file saved to directory: {output_dir}")
output_file.Close(); input_file.Close()