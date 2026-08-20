import csv
import matplotlib.pyplot as plt

def read_csv(filename):
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

# Read final waypoints
wp_data = read_csv('final_waypoints.csv')
wp_lat = [float(row['latitude']) for row in wp_data if row['latitude']]
wp_lon = [float(row['longitude']) for row in wp_data if row['longitude']]
wp_alt = [float(row['altitude']) for row in wp_data if row['altitude']]

# Read GNSS data
gnss_data = read_csv('round_reservoir_gnss_data.csv')
# Filter out rows with no fix
gnss_valid = [row for row in gnss_data if row.get('fix', '') == 'True' and row['latitude'] and row['longitude'] and row['altitude']]
gnss_lat = [float(row['latitude']) for row in gnss_valid]
gnss_lon = [float(row['longitude']) for row in gnss_valid]
gnss_alt = [float(row['altitude']) for row in gnss_valid]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))

# Subplot 1: Path Comparison
ax1.plot(gnss_lon, gnss_lat, marker='.', markersize=2, linestyle='-', color='lightblue', label='Raw GNSS Track', alpha=0.7)
ax1.plot(wp_lon, wp_lat, marker='.', markersize=6, linestyle='-', color='indigo', label='Final Waypoints')
ax1.set_title('Path Comparison: Raw GNSS vs Final Waypoints')
ax1.set_xlabel('Longitude')
ax1.set_ylabel('Latitude')
ax1.grid(True)
ax1.legend()

# Subplot 2: Elevation Profile
# To compare them despite different point counts, we normalize the x-axis to a percentage (0 to 100%)
wp_x = [i / (len(wp_alt) - 1) * 100 for i in range(len(wp_alt))] if len(wp_alt) > 1 else [0]
gnss_x = [i / (len(gnss_alt) - 1) * 100 for i in range(len(gnss_alt))] if len(gnss_alt) > 1 else [0]

ax2.plot(gnss_x, gnss_alt, color='lightblue', label='Raw GNSS Altitude', alpha=0.7)
ax2.plot(wp_x, wp_alt, marker='.', markersize=6, color='green', label='Final Waypoints Altitude')
ax2.set_title('Elevation Profile Comparison')
ax2.set_xlabel('Path Completion (%)')
ax2.set_ylabel('Altitude (m)')
ax2.grid(True)
ax2.legend()

plt.tight_layout()
plt.savefig('comparison_plot.png')
print("Plot saved as comparison_plot.png")
