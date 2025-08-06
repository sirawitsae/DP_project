import ROOT
import os
from ROOT import TFile, TCanvas, gStyle, TLegend

files_to_compare = {
    'm=0.4 GeV, ctau=5 mm': 'output_truth_frvz_vbf_500759/histograms_frvz_vbf_500759.root',
    'm=0.4 GeV, ctau=50 mm':  'output_truth_frvz_vbf_500758/histograms_frvz_vbf_500758.root',
    'm=0.4 GeV, ctau=500 mm': 'output_truth_frvz_vbf_500760/histograms_frvz_vbf_500760.root'
}

X_AXIS_RANGES = {
    "dp_pt":    (0, 350),
    "dp_m":     (0, 15),  
    "dp_lxy":   (0, 10e3),
    "dp_deltaR":   (0, 4.5),
    "dp_lz":   (0, 1700e3),
    "dp_phi":   (-4, 4),
    "dp_ctau":  (0, 5000)
}

# Specify the directory to save the final overlay plots
outputPlotDir = "overlay_plots/"
if not os.path.isdir(outputPlotDir):
    os.makedirs(outputPlotDir)
print(f"Overlay plots will be saved to: {outputPlotDir}")


def plot_overlay(hist_name):
    histos = []
    names = []

    for name, file_path in files_to_compare.items():

        file = TFile.Open(file_path)
        tempHist = file.Get(hist_name)
        
        newHist = tempHist.Clone(f"histo_{hist_name}_{name}")
        newHist.SetDirectory(0)
        
        if newHist.Integral() > 0:
            newHist.Scale(1.0 / newHist.Integral())
            
        histos.append(newHist)
        names.append(name)
        file.Close()

    if not histos:
        print(f"No valid histograms found for '{hist_name}'.")
        return

    canvas = TCanvas(f"canvas_{hist_name}", f"Overlay for {hist_name}", 800, 600)
    gStyle.SetOptStat(0)
    canvas.cd()
    canvas.SetLogy(1)
    
    x_min, x_max = (0, 0)
    if hist_name in X_AXIS_RANGES:
        x_min, x_max = X_AXIS_RANGES[hist_name]
        print(f"Using predefined range for {hist_name}: ({x_min}, {x_max})")
    else:
        global_max_x = 0.0
        for h in histos:
            last_bin = h.FindLastBinAbove(0, 1)
            current_max = h.GetXaxis().GetBinUpEdge(last_bin)
            if current_max > global_max_x:
                global_max_x = current_max
        x_min = histos[0].GetXaxis().GetXmin()
        x_max = global_max_x * 1.05 # Add 5% buffer
        print(f"Using automatic range for {hist_name}: ({x_min:.2f}, {x_max:.2f})")

    # Create a dummy histogram to set the drawing frame correctly
    first_hist = histos[0]
    dummy_hist = ROOT.TH1F(f"dummy_{hist_name}", "", 100, x_min, x_max)
    dummy_hist.GetYaxis().SetTitle("Normalized Events")
    dummy_hist.GetXaxis().SetTitle(first_hist.GetXaxis().GetTitle())
    
    global_max_y = 0.0
    for h in histos:
        if h.GetMaximum() > global_max_y:
            global_max_y = h.GetMaximum()
    
    dummy_hist.SetMaximum(global_max_y * 1.5)
    dummy_hist.Draw("HIST")

    legend = TLegend(0.50, 0.70, 0.88, 0.88)
    legend.SetBorderSize(0); legend.SetTextFont(42); legend.SetTextSize(0.03); legend.SetFillStyle(0)

    # Draw the actual histograms on top of the dummy frame
    for idx, h in enumerate(histos):
        h.SetLineColor(idx + 2)
        h.SetLineWidth(2)
        legend.AddEntry(h, names[idx], "l")
        h.Draw("HIST SAME")

    legend.Draw()
    
    canvas.Print(os.path.join(outputPlotDir, f'overlay_{hist_name}.png'))
    print(f"Saved overlay plot for {hist_name}")

if __name__ == '__main__':
    kinematic_variables = [
        "dp_pt", "dp_eta", "dp_phi", "dp_m",
        "dp_lxy", "dp_lz", "dp_ctau", "dp_deltaR"
    ]
    
    for var in kinematic_variables:
        plot_overlay(var)
        
    print("-" * 50)
    print("All overlay plots have been created.")