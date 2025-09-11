import requests
from lxml import html
import dotenv
import os
import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scraping_utils import get_url, parse

class TidesDataCollector:
    """Tides data collector class"""
    
    def __init__(self):
        # Load environment variables
        dotenv.load_dotenv()
        self.year = int(os.getenv('YEAR', 2024))
        self.filename = os.getenv('FILENAME', "crawled-page-{year}.html").format(year=self.year)
        self.data = []
        
    def collect_data(self):
        """Collect tides data"""
        try:
            # Get page
            page = get_url(os.getenv('URL'), self.filename)
            
            # Parse page to HTML
            tree = parse(page, 'html')
            
            # Initialize row counter
            row_num = 0
            
            # Iterate over table rows
            for row in tree.xpath(os.getenv('ROW_XPATH')):
                columns = row.xpath(os.getenv('COL_XPATH'))
                columns = [column.text_content() for column in columns]
                columns = [column.strip() for column in columns]
                row_string = " ".join(columns).strip()
                
                # Skip empty rows
                if row_string.strip() == "":
                    continue
                
                row_num += 1
                print(f'Processing Row {row_num}: {row_string}')
                
                if len(columns) >= 2:
                    try:
                        month = int(columns[0])
                        day = int(columns[1])
                        
                        # Process time and value pairs
                        for i in range(2, len(columns), 2):
                            if i + 1 < len(columns) and columns[i] != "":
                                # Get time in HHMM format
                                time_str = columns[i]
                                if len(time_str) >= 4:
                                    hour = time_str[:2]
                                    minute = time_str[2:]
                                    
                                    dt = datetime.datetime(self.year, month, day, int(hour), int(minute))
                                    value = columns[i+1]
                                    
                                    if value and value.replace('.', '').replace('-', '').isdigit():
                                        print(f'{dt} - {value}')
                                        self.data.append((dt, float(value)))
                    except (ValueError, IndexError) as e:
                        print(f"Error processing row {row_num}: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error collecting data: {e}")
            
        print(f"Successfully collected {len(self.data)} tide records")
        return self.data
    
    def save_to_csv(self, filename='tides.csv'):
        """Save data to CSV file"""
        if not self.data:
            print("No data to save")
            return
            
        try:
            # Clear existing file
            with open(filename, 'w') as f:
                f.write('')  # Clear file
                
            # Write data
            with open(filename, 'a', encoding='utf-8') as f:
                for record in self.data:
                    f.write(f'{record[0].strftime("%Y-%m-%d %H:%M")},{record[1]}\n')
                    
            print(f"Data saved to {filename}")
            
        except Exception as e:
            print(f"Error saving to CSV: {e}")
    
    def create_basic_plot(self):
        """Create basic plot"""
        if not self.data:
            print("No data to plot")
            return
            
        try:
            # Prepare data
            dates = [record[0] for record in self.data]
            values = [record[1] for record in self.data]
            
            # Create plot
            plt.figure(figsize=(15, 8))
            
            # Main plot
            plt.subplot(2, 1, 1)
            plt.plot(dates, values, 'b-', linewidth=1, alpha=0.7, label='Tide Level')
            plt.title('Hong Kong Tides Data Visualization', fontsize=16, fontweight='bold')
            plt.xlabel('Date')
            plt.ylabel('Tide Level (m)')
            plt.grid(True, alpha=0.3)
            plt.legend()
            
            # Add moving average
            if len(values) > 10:
                # Calculate moving average
                window = min(50, len(values) // 10)
                df = pd.DataFrame({'values': values})
                moving_avg = df['values'].rolling(window=window, center=True).mean()
                plt.plot(dates, moving_avg, 'r-', linewidth=2, alpha=0.8, label=f'{window}-point Moving Average')
                plt.legend()
            
            # Distribution plot
            plt.subplot(2, 1, 2)
            plt.hist(values, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
            plt.title('Tide Level Distribution')
            plt.xlabel('Tide Level (m)')
            plt.ylabel('Frequency')
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig('tides_basic_plot.png', dpi=300, bbox_inches='tight')
            plt.show()
            
        except Exception as e:
            print(f"Error creating plot: {e}")

def main():
    """Main function"""
    print("=== Tides Data Collection and Visualization System ===")
    
    # Create data collector
    collector = TidesDataCollector()
    
    # Collect data
    print("Step 1: Collecting tide data...")
    data = collector.collect_data()
    
    if data:
        # Save to CSV
        print("\nStep 2: Saving data to CSV...")
        collector.save_to_csv()
        
        # Create basic plot
        print("\nStep 3: Creating basic visualization...")
        collector.create_basic_plot()
        
        print("\nBasic processing complete!")
        print("Next, run 'python enhanced_tides_visualization.py' for advanced visualizations")
        
    else:
        print("No data collected. Please check your .env configuration and internet connection.")

if __name__ == "__main__":
    main()