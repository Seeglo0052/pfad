import drawsvg as draw
import numpy as np
import math

def create_flowing_tides_svg():
    """Create flowing tides SVG animation"""
    
    # Create main canvas
    d = draw.Drawing(800, 600, origin='center')
    
    # Add deep blue background
    d.append(draw.Rectangle(-400, -300, 800, 600, fill='#001133'))
    
    # Create multi-layer waves
    def create_wave(amplitude, frequency, phase, color, opacity, stroke_width):
        points = []
        for x in range(-400, 401, 5):
            y = amplitude * math.sin(frequency * x * 0.01 + phase)
            points.extend([x, y])
        
        return draw.Lines(*points, close=False, 
                         fill='none', stroke=color, 
                         stroke_width=stroke_width, opacity=opacity)
    
    # Main wave layers
    d.append(create_wave(80, 2, 0, '#00CCFF', 0.8, 4))
    d.append(create_wave(60, 3, 0.5, '#66DDFF', 0.6, 3))
    d.append(create_wave(40, 4, 1.0, '#99EEFF', 0.4, 2))
    
    # Add particle effects (bubbles)
    for i in range(30):
        x = np.random.uniform(-380, 380)
        y = np.random.uniform(-280, 280)
        radius = np.random.uniform(3, 12)
        opacity = np.random.uniform(0.2, 0.7)
        
        d.append(draw.Circle(x, y, radius, 
                           fill='white', opacity=opacity,
                           stroke='cyan', stroke_width=1))
    
    # Add title
    d.append(draw.Text('Flowing Tides Visualization', 24, 0, 250, 
                      fill='white', text_anchor='middle', 
                      font_family='Arial', font_weight='bold'))
    
    d.append(draw.Text('Hong Kong Tides Data Flow', 16, 0, 220, 
                      fill='#CCCCCC', text_anchor='middle', 
                      font_family='Arial'))
    
    # Add decorative elements
    # Create fish outline
    fish_points = [-50, -20, -30, -10, -10, -5, 10, 0, 30, 5, 40, 0, 30, -5, 10, -10, -10, -15, -30, -20]
    d.append(draw.Lines(*fish_points, close=True,
                       fill='#4488CC', opacity=0.7,
                       stroke='#66AADD', stroke_width=2))
    
    # Fish eye
    d.append(draw.Circle(-20, -15, 3, fill='white'))
    d.append(draw.Circle(-20, -15, 1, fill='black'))
    
    # Save SVG
    d.save_svg('flowing_tides_enhanced.svg')
    print("Enhanced SVG saved as 'flowing_tides_enhanced.svg'")

def create_tide_clock_svg():
    """Create tide clock SVG"""
    d = draw.Drawing(400, 400, origin='center')
    
    # Background
    d.append(draw.Circle(0, 0, 180, fill='#001122', stroke='#004466', stroke_width=4))
    
    # Clock markings
    for i in range(12):
        angle = i * 30 * math.pi / 180
        x1, y1 = 160 * math.cos(angle), 160 * math.sin(angle)
        x2, y2 = 140 * math.cos(angle), 140 * math.sin(angle)
        
        d.append(draw.Line(x1, y1, x2, y2, stroke='white', stroke_width=2))
        
        # Numbers
        text_x, text_y = 130 * math.cos(angle), 130 * math.sin(angle)
        d.append(draw.Text(str(i if i > 0 else 12), 12, text_x, text_y, 
                          fill='white', text_anchor='middle', font_family='Arial'))
    
    # Tide pointer (simulate high tide time)
    high_tide_angle = 45 * math.pi / 180  # Example angle
    x_end = 100 * math.cos(high_tide_angle)
    y_end = 100 * math.sin(high_tide_angle)
    
    d.append(draw.Line(0, 0, x_end, y_end, stroke='cyan', stroke_width=6))
    d.append(draw.Circle(x_end, y_end, 8, fill='cyan'))
    
    # Center
    d.append(draw.Circle(0, 0, 10, fill='white'))
    
    # Title
    d.append(draw.Text('Tide Clock', 16, 0, -220, fill='white', 
                      text_anchor='middle', font_family='Arial'))
    
    d.save_svg('tide_clock.svg')
    print("Tide clock SVG saved as 'tide_clock.svg'")

def main():
    """Main function"""
    print("Creating enhanced SVG visualizations...")
    
    # Create flowing tides SVG
    create_flowing_tides_svg()
    
    # Create tide clock SVG
    create_tide_clock_svg()
    
    print("All SVG visualizations created successfully!")

if __name__ == "__main__":
    main()