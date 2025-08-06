import uproot
import matplotlib.pyplot as plt

# Define file and object names ---
file1_path = 'BDT_data_ee/roc_output_61/roc_curve.root'
file2_path = 'BDT_data_comb57_63/roc_output_61/roc_curve.root'
#file3_path = 'roc_output_61/roc_curve.root'
# file4_path = 'roc_output_64/roc_curve.root'

# Name of the TGraph object you want to plot from each file
curve_name1 = 'LJjet1_BDT'
#curve_name2 = 'LJjet1_DPJtagger'


try:
    # Uproot reads TGraphs into objects that provide x and y values
    with uproot.open(file1_path) as file1:
        x1, y1 = file1[curve_name1].values()

    with uproot.open(file2_path) as file2:
        x2, y2 = file2[curve_name1].values()

    # with uproot.open(file3_path) as file3:
      #  x3, y3 = file3[curve_name1].values()

    #with uproot.open(file4_path) as file3:
     #   x4, y4 = file3[curve_name1].values()

except FileNotFoundError as e:
    print(f"ERROR: Could not find a file. {e}")
    print("Please make sure your file paths are correct.")
    exit()
except KeyError:
    print(f"ERROR: Could not find the object '{curve_name1}' in one of the files.")
    exit()

# Create a figure and a set of axes
fig, ax = plt.subplots(figsize=(5, 4))

# Plot the curve from the first file
ax.plot(x1, y1, label=f'm 10 GeV, ctau 900 mm Incl (from ee)', color='r', linewidth=1.5)

ax.plot(x2, y2, label=f'm 10 GeV, ctau 900 mm Incl (from 57 + 63)', color='k', linestyle='--', linewidth=1.5)

# ax.plot(x3, y3, label=f'm 10 GeV, ctau 900 mm', color='b', linestyle='-.', linewidth=1.5)

# ax.plot(x4, y4, label=f'm 15 GeV, ctau 1000 mm (100% quarks)', color='g', linestyle=':', linewidth=1.5)


ax.set_xlabel('Signal Efficiency', fontsize=14)
ax.set_ylabel('Background Rejection', fontsize=14)
ax.set_title('Overlay of ROC Curves', fontsize=16)

# Set axis limits to the standard [0, 1] range for ROC curves
ax.set_xlim(0, 1)
ax.set_ylim(0, 1.05) # Add a little space at the top

ax.grid(True, linestyle=':', alpha=0.7)
ax.legend() # Display the legend

plt.tight_layout() # Adjusts plot to prevent labels from overlapping

# Save the figure to .png and .pdf files
plt.savefig('roc_overlay_eeVScomb.png')
plt.savefig('roc_overlay_eeVScomb.pdf')

print("Plot saved as roc_overlay.png and roc_overlay.pdf")

# Display the plot on screen
#plt.show()