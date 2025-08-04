import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats


def load_and_analyze_data():
    """Load and analyze valve data"""
    
    # Read CSV file
    df = pd.read_csv('valve_data.csv')
    
    print("Data Overview:")
    print(f"Number of rows: {len(df)}")
    print(f"Number of columns: {len(df.columns)}")
    print("\nColumn names:")
    for i, col in enumerate(df.columns):
        print(f"{i+1}. {col}")
    
    print("\nFirst 5 rows:")
    print(df.head())
    
    print("\nStatistical information:")
    print(df.describe())
    
    return df

def plot_relationships(df):
    """Plot data relationships"""
    
    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    fig.suptitle('Valve Characteristics Analysis', fontsize=16)
    
    # 1. Voltage vs Spool Position
    axes[0, 0].plot(df['Voltage (volt)'], df['Spool Pos. (mm)'], 'b-o', linewidth=2, markersize=4)
    axes[0, 0].set_xlabel('Voltage (V)')
    axes[0, 0].set_ylabel('Spool Position (mm)')
    axes[0, 0].set_title('Voltage vs Spool Position')
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Voltage vs Orifice Area
    axes[0, 1].plot(df['Voltage (volt)'], df['Orifice Area (mm^2)'], 'r-o', linewidth=2, markersize=4)
    axes[0, 1].set_xlabel('Voltage (V)')
    axes[0, 1].set_ylabel('Orifice Area (mm²)')
    axes[0, 1].set_title('Voltage vs Orifice Area')
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Voltage vs Mass Flow Rate
    axes[1, 0].plot(df['Voltage (volt)'], df['Mass flow rate (g/sec)'], 'g-o', linewidth=2, markersize=4)
    axes[1, 0].set_xlabel('Voltage (V)')
    axes[1, 0].set_ylabel('Mass Flow Rate (g/s)')
    axes[1, 0].set_title('Voltage vs Mass Flow Rate')
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. Calculated vs Experimental Flow Rate
    axes[1, 1].plot(df['Cal. Vol. flow rate (l/min)'], df['Exp. Vol. flow rate (l/min)'], 'm-o', linewidth=2, markersize=4)
    axes[1, 1].plot([0, 100], [0, 100], 'k--', alpha=0.5, label='Ideal Line')
    axes[1, 1].set_xlabel('Calculated Volumetric Flow Rate (l/min)')
    axes[1, 1].set_ylabel('Experimental Volumetric Flow Rate (l/min)')
    axes[1, 1].set_title('Calculated vs Experimental Flow Rate')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('valve_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def calculate_accuracy(df):
    """Calculate model accuracy"""
    
    # Calculate relative error
    df['Relative Error (%)'] = ((df['Exp. Vol. flow rate (l/min)'] - df['Cal. Vol. flow rate (l/min)']) / 
                               df['Exp. Vol. flow rate (l/min)'] * 100)
    
    # Filter out zero values (avoid division by zero)
    valid_data = df[df['Exp. Vol. flow rate (l/min)'] > 0]
    
    print("\nModel Accuracy Analysis:")
    print(f"Mean relative error: {valid_data['Relative Error (%)'].mean():.2f}%")
    print(f"Maximum relative error: {valid_data['Relative Error (%)'].max():.2f}%")
    print(f"Minimum relative error: {valid_data['Relative Error (%)'].min():.2f}%")
    print(f"Relative error standard deviation: {valid_data['Relative Error (%)'].std():.2f}%")
    
    return valid_data

def find_linear_regions(df):
    """Find linear regions"""
    
    print("\nLinear Region Analysis:")
    
    # Analyze voltage-spool position relationship
    voltage = df['Voltage (volt)'].values
    spool_pos = df['Spool Pos. (mm)'].values
    
    # Find linear region (exclude saturation region)
    # Assume linear region before voltage 8.75V
    linear_mask = voltage <= 8.75
    linear_voltage = voltage[linear_mask]
    linear_spool = spool_pos[linear_mask]
    
    if len(linear_voltage) > 1:
        slope, intercept, r_value, p_value, std_err = stats.linregress(linear_voltage, linear_spool)
        
        print(f"Linear region (Voltage ≤ 8.75V):")
        print(f"  Slope: {slope:.4f} mm/V")
        print(f"  Intercept: {intercept:.4f} mm")
        print(f"  Correlation coefficient R²: {r_value**2:.4f}")
        print(f"  P-value: {p_value:.6f}")
        
        # Calculate linearity
        linearity = r_value**2 * 100
        print(f"  Linearity: {linearity:.2f}%")

def main():
    """Main function"""
    print("Valve Data Analysis Program")
    print("=" * 50)
    
    # Load data
    df = load_and_analyze_data()
    
    # Plot relationships
    plot_relationships(df)
    
    # Calculate accuracy
    valid_data = calculate_accuracy(df)
    
    # Find linear regions
    find_linear_regions(df)
    
    print("\nAnalysis complete! Chart saved as 'valve_analysis.png'")

if __name__ == "__main__":
    main() 