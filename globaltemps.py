import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import imageio.v2 as imageio
import itertools

spinner = itertools.cycle(['-', '/', '|', '\\'])

# Read the datasets
df = pd.read_csv('iso3change.csv')
world_temp = pd.read_csv('worldtemp.csv', index_col=0)

# Extract the world average change for each year
world_avg_change = world_temp.loc['world', df.columns[1:]].values

# Melt the dataframe to long format
df_melted = df.melt(id_vars=['iso3'], var_name='year', value_name='change_index')

# Read the world map shapefile using geopandas
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

# Loop over each year and create the corresponding map
images = []
for year in df.columns[1:]:
    print(f"\r{next(spinner)} Running year {year}...", end="")
    # Merge the map with the dataset for the current year
    merged = world.merge(df_melted[df_melted['year']==year], left_on='iso_a3', right_on='iso3', how='left')
    
    # Plot the map for the current year
    fig, ax = plt.subplots(figsize=(10, 5), facecolor='#2c2c2c')
    merged.plot(column='change_index', cmap='coolwarm', vmin=-2, vmax=2, ax=ax)
    ax.axis('off')
    ax.set_title(f'Global Surface Temperature Change ({year})', color='white')
    # Add color bar to the plot
    cax = fig.add_axes([0.2, 0.15, 0.6, 0.02]) # [left, bottom, width, height]
    im = ax.collections[0]
    cb = plt.colorbar(im, cax=cax, orientation='horizontal', label='Global Average Change')
    cb.ax.xaxis.label.set_color('white')  # set the color of the label to white
    cb.ax.tick_params(colors='white')

    # Get the current world average temperature change for the year
    world_avg_temp = world_temp.loc['world', year]

    # Add a marker on the color bar for the world average temperature change
    cb.ax.plot([world_avg_temp], [1.5], 'v', color='black', markeredgecolor='black', markersize=20)
    cb.ax.axvline(world_avg_temp, color='black', lw=1.5)
    cb.ax.annotate(f'{world_avg_temp:.2f}', xy=(world_avg_temp, 1.5), xytext=(world_avg_temp, 1.7),
                   fontsize=8, ha='center', va='center',
                   arrowprops=dict(arrowstyle='->', color='black', lw=0.5))
    
    # Set the title below the color bar
    plt.suptitle(f'Celsius', fontsize=8, y=0.05, color='white')
    
    # Save the map as an image file
    filename = f'./images/{year}.png'
    plt.savefig(filename, dpi=300)
    images.append(imageio.imread(filename))
    plt.close()
# Create the animated gif from the images
imageio.mimsave('./gif/temperature_change_FINAL.gif', images, fps=1.75)