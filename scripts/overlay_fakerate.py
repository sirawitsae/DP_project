import ROOT
import os
from ROOT import TFile, TCanvas, gStyle, TLegend

files_to_compare = {
    "Signal: m=0.1 GeV, ctau=15mm": "rates_plots_57/rates_plots.root",
    "Signal: m=0.4 GeV, ctau=50mm": "rates_plots_58/rates_plots.root",
    "Signal: m=10 GeV, ctau=900mm": "rates_plots_61/rates_plots.root"
}

plots_to_make = [
    {"name": "fake_rate_vs_pt", "title": "Fake Rate vs. p_{T}", "xtitle": "Reconstructed LJ p_{T} [GeV]", "ytitle": "Fake Rate"},
    {"name": "fake_rate_vs_eta", "title": "Fake Rate vs. #eta", "xtitle": "Reconstructed LJ #eta", "ytitle": "Fake Rate"},
    {"name": "fake_rate_vs_phi", "title": "Fake Rate vs. #phi", "xtitle": "Reconstructed LJ #phi", "ytitle": "Fake Rate"},
    {"name": "matched_rate_vs_pt", "title": "Matched Rate vs. p_{T}", "xtitle": "Reconstructed LJ p_{T} [GeV]", "ytitle": "Matched Rate"},
    {"name": "matched_rate_vs_eta", "title": "Matched Rate vs. #eta", "xtitle": "Reconstructed LJ #eta", "ytitle": "Matched Rate"},
    {"name": "matched_rate_vs_phi", "title": "Matched Rate vs. #phi", "xtitle": "Reconstructed LJ #phi", "ytitle": "Matched Rate"}
]

# Specify the directory to save the final overlay plots
outputPlotDir = "overlay_fakerate_benchmark/"
if not os.path.isdir(outputPlotDir):
    os.makedirs(outputPlotDir)
print(f"Overlay plots will be saved to: {outputPlotDir}")


def create_overlay(plot_info):

    plot_name = plot_info["name"]
    print(f"--- Creating overlay for: {plot_name} ---")

    canvas = TCanvas(f"canvas_{plot_name}", plot_info["title"], 800, 600)
    gStyle.SetOptStat(0)
    #legend = TLegend(0.45, 0.2, 0.88, 0.45) # Positioned bottom-right
    #legend.SetBorderSize(0)

    legend = TLegend(0.65, 0.75, 0.88, 0.88)
    legend.SetBorderSize(0)
    legend.SetTextSize(0.02)

    graphs_to_draw = []

    # Loop through the files to get the TEfficiency objects
    for name, file_path in files_to_compare.items():
        if not os.path.exists(file_path):
            print(f"Warning: Input file not found at {file_path}. Skipping.")
            continue

        file = TFile.Open(file_path)
        eff_obj = file.Get(plot_name)
        
        if not eff_obj:
            print(f"Warning: TEfficiency object '{plot_name}' not found in {file_path}. Skipping.")
            file.Close()
            continue
        
        # To draw multiple TEfficiency plots, we need to get their underlying TGraph
        graph = eff_obj.CreateGraph()
        graphs_to_draw.append((name, graph))
        file.Close()

    if not graphs_to_draw:
        print(f"No valid plots found for '{plot_name}'. Cannot create overlay.")
        return

    # Draw the graphs
    for idx, (name, graph) in enumerate(graphs_to_draw):
        graph.SetLineColor(idx + 2) # 2=red, 3=green, 4=blue
        graph.SetMarkerColor(idx + 2)
        graph.SetMarkerStyle(20 + idx)
        graph.SetLineWidth(2)
        
        legend.AddEntry(graph, name, "lp") # "lp" for line and points

        if idx == 0:
            # Use the first graph to set the axes and title
            graph.SetTitle(f"{plot_info['title']};{plot_info['xtitle']};{plot_info['ytitle']}")
            graph.GetYaxis().SetRangeUser(0, 1.0) # Set a sensible range for fake rates
            #canvas.SetLogy()
            graph.Draw("AP") # "A" for axes, "P" for points
        else:
            graph.Draw("P SAME")

    legend.Draw()
    
    # save the plot in both .png and .pdf format
    canvas.Print(os.path.join(outputPlotDir, f'overlay_{plot_name}.png'))
    canvas.Print(os.path.join(outputPlotDir, f'overlay_{plot_name}.pdf'))
    print(f"Saved .png and .pdf for {plot_name}")

if __name__ == '__main__':
    for plot_definition in plots_to_make:
        create_overlay(plot_definition)
        
    print("-" * 50)
    print("All overlay plots have been created.")