import ROOT
import os
import math
import re
from ROOT import TFile, TCanvas, TLorentzVector, gStyle

def add_overflow_to_last_bin(hist):

    num_bins = hist.GetNbinsX()
    overflow_content = hist.GetBinContent(num_bins + 1)
    if overflow_content > 0:
        last_bin_content = hist.GetBinContent(num_bins)
        hist.SetBinContent(num_bins, last_bin_content + overflow_content)
        hist.SetBinContent(num_bins + 1, 0) # Clear the overflow bin

input_base_dir = '/Users/sirawitsae/Desktop/project/DarkPhoton/vbfskim/'
# This will process all 'frvz_' files found in the directory
input_file_paths = [os.path.join(input_base_dir, f) for f in os.listdir(input_base_dir) if f.startswith('frvz_') and f.endswith('.root')]

if not input_file_paths:
    print(f"Error: No signal files ('frvz_*.root') found in {input_base_dir}")
    exit()

for path in input_file_paths:
    print("-" * 50)
    print(f"Processing file: {path}")

    myfile = TFile.Open(path, "READ")
    tree = myfile.Get("miniT")
    if not tree:
        print(f"Warning: TTree 'miniT' not found in {path}. Skipping.")
        continue

    print("Pass 1: Collecting data to determine histogram ranges...")
    all_values = {
        'pt': [], 'eta': [], 'phi': [], 'm': [], 'lxy': [], 'lz': [],
        'ctau': [], 'deltaR': [], 'approx_deltaR': []
    }
    for i in range(tree.GetEntries()):
        tree.GetEntry(i)
        dark_photon_indices = [j for j, pdgId in enumerate(tree.truthPdgId) if pdgId == 3000001]
        if not dark_photon_indices: continue

        for dp_idx in dark_photon_indices:
            p4 = TLorentzVector()
            p4.SetPtEtaPhiE(tree.truthPt[dp_idx] * 0.001, tree.truthEta[dp_idx], tree.truthPhi[dp_idx], tree.truthE[dp_idx] * 0.001)

            all_values['pt'].append(p4.Pt())
            all_values['eta'].append(p4.Eta())
            all_values['phi'].append(p4.Phi())
            all_values['m'].append(p4.M())

            dx = tree.truthDecayVtx_x[dp_idx]
            dy = tree.truthDecayVtx_y[dp_idx]
            dz = tree.truthDecayVtx_z[dp_idx]
            lxy = math.sqrt(dx**2 + dy**2)
            decay_length_3d = math.sqrt(dx**2 + dy**2 + dz**2)

            all_values['lxy'].append(lxy)
            all_values['lz'].append(abs(dz))

            if p4.P() > 0:
                all_values['ctau'].append((decay_length_3d / p4.P()) * p4.M())

            dp_barcode = tree.truthBarcode[dp_idx]
            daughters = []
            for k in range(len(tree.childPdgId)):
                if tree.childMomBarcode[k] == dp_barcode:
                    daughter_p4 = TLorentzVector()
                    daughter_p4.SetPtEtaPhiM(tree.childPt[k] * 0.001, tree.childEta[k], tree.childPhi[k], 0)
                    daughters.append(daughter_p4)

            if len(daughters) == 2:
                deltaR = daughters[0].DeltaR(daughters[1])
                all_values['deltaR'].append(deltaR)
                if p4.Pt() > 0:
                    all_values['approx_deltaR'].append((2 * p4.M()) / p4.Pt())

    # Create Histograms 
    base_name = os.path.basename(path).split('.')[0]
    outputDir = f"output_truth_{base_name}"
    os.makedirs(outputDir, exist_ok=True)
    outputRootPath = os.path.join(outputDir, f"histograms_{base_name}.root")
    outputFile = TFile(outputRootPath, "RECREATE")

    h_dp_pt = ROOT.TH1F("dp_pt", "dark photon pt; pT [GeV]; Events", 100, 0, max(all_values['pt'])*1.1 if all_values['pt'] else 500)
    h_dp_eta = ROOT.TH1F("dp_eta", "dark photon eta; #eta; Events", 100, -5, 5)
    h_dp_phi = ROOT.TH1F("dp_phi", "dark photon phi; #phi; Events", 100, -3.2, 3.2)
    h_dp_m = ROOT.TH1F("dp_m", "dark photon mass; Mass [GeV]; Events", 100, 0, max(all_values['m'])*1.2 if all_values['m'] else 1)
    h_dp_lxy = ROOT.TH1F("dp_lxy", "dark photon Lxy; Lxy [mm]; Events", 100, 0, 10000) # Fixed range of 10 meters
    h_dp_lz = ROOT.TH1F("dp_lz", "dark photon Lz; Lz [mm]; Events", 100, 0, max(all_values['lz'])*1.1) 
    h_dp_ctau = ROOT.TH1F("dp_ctau", "dark photon ctau; c#tau [mm]; Events", 100, 0, max(all_values['ctau'])*1.1 if all_values['ctau'] else 100)
    h_dp_deltaR = ROOT.TH1F("dp_deltaR", "dark photon #DeltaR; #DeltaR; Events", 100, 0, max(all_values['deltaR'])*1.1 if all_values['deltaR'] else 1.0)
    h_deltaR_vs_2mPt = ROOT.TH2F("deltaR_vs_2mPt", "True #DeltaR vs. 2m/p_{T} Approx.;Approximation (2m/p_{T});True #DeltaR",
                                 100, 0, max(all_values['approx_deltaR'])*1.1 if all_values['approx_deltaR'] else 1.0,
                                 100, 0, max(all_values['deltaR'])*1.1 if all_values['deltaR'] else 1.0)

    print("Pass 2: Filling histograms...")
    for i in range(len(all_values['pt'])):
        h_dp_pt.Fill(all_values['pt'][i]); h_dp_eta.Fill(all_values['eta'][i]);
        h_dp_phi.Fill(all_values['phi'][i]); h_dp_m.Fill(all_values['m'][i]);
        h_dp_lxy.Fill(all_values['lxy'][i]); h_dp_lz.Fill(all_values['lz'][i]);
        h_dp_ctau.Fill(all_values['ctau'][i]);

    for i in range(len(all_values['deltaR'])):
        h_dp_deltaR.Fill(all_values['deltaR'][i])
        h_deltaR_vs_2mPt.Fill(all_values['approx_deltaR'][i], all_values['deltaR'][i])

    add_overflow_to_last_bin(h_dp_pt)
    add_overflow_to_last_bin(h_dp_lxy)
    add_overflow_to_last_bin(h_dp_lz)
    add_overflow_to_last_bin(h_dp_ctau)


    outputFile.cd()
    h_dp_pt.Write(); h_dp_eta.Write(); h_dp_phi.Write(); h_dp_m.Write();
    h_dp_lxy.Write(); h_dp_lz.Write(); h_dp_ctau.Write(); h_dp_deltaR.Write();
    h_deltaR_vs_2mPt.Write()

    print("\n--- KINEMATIC VERIFICATION REPORT ---")
    mass_peak_bin = h_dp_m.GetMaximumBin()
    calculated_mass_peak = h_dp_m.GetXaxis().GetBinCenter(mass_peak_bin)
    print(f"Dark Photon Mass Peak: \t\t{calculated_mass_peak:.4f} GeV")
    calculated_eta_mean = h_dp_eta.GetMean()
    print(f"Dark Photon Eta Mean: \t\t{calculated_eta_mean:.4f} (Expected: ~0.0)")
    calculated_ctau_mean = h_dp_ctau.GetMean()
    print(f"Dark Photon c-tau Mean: \t{calculated_ctau_mean:.2f} mm")
    print("---------------------------------------")

    canvas = ROOT.TCanvas("canvas", "Canvas", 800, 600); gStyle.SetOptStat(0)
    canvas.SetLogy(1)

    def save_plot(hist, name, options=""):
        # Set log scale for 1D plots, but keep 2D plots linear
        is_1D = not hist.InheritsFrom(ROOT.TH2.Class())
        canvas.SetLogy(is_1D)
        
        canvas.Clear(); hist.Draw(options); canvas.Print(os.path.join(outputDir, f'{name}.png'))

    save_plot(h_dp_pt, 'dp_pt', "HIST"); save_plot(h_dp_eta, 'dp_eta', "HIST");
    save_plot(h_dp_phi, 'dp_phi', "HIST"); save_plot(h_dp_m, 'dp_mass', "HIST");
    save_plot(h_dp_lxy, 'dp_lxy', "HIST"); save_plot(h_dp_lz, 'dp_lz', "HIST");
    save_plot(h_dp_ctau, 'dp_ctau', "HIST"); save_plot(h_dp_deltaR, 'dp_deltaR', "HIST");
    save_plot(h_deltaR_vs_2mPt, 'deltaR_vs_2mPt', "COLZ");

    print(f"\nAll plots saved in {outputDir}")

    outputFile.Close()
    myfile.Close()

print("-" * 50)
print("All files processed.")