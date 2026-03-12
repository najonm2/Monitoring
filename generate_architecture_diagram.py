"""
PASE Monitor Portal - Architecture Diagram Generator
Generates a professional architecture diagram in JPG format
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.lines as mlines

# Lumen color palette
LUMEN_BLUE = '#0066CC'
LUMEN_PURPLE = '#6B2D8E'
LUMEN_GRAY = '#333333'
LUMEN_LIGHT_GRAY = '#F5F5F5'
LUMEN_GREEN = '#00A650'
LUMEN_ORANGE = '#FF6B35'

def create_box(ax, x, y, width, height, text, color, text_color='white', fontsize=10, bold=False):
    """Create a rounded rectangle box with text"""
    box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.05",
        facecolor=color,
        edgecolor=LUMEN_GRAY,
        linewidth=2
    )
    ax.add_patch(box)
    
    weight = 'bold' if bold else 'normal'
    ax.text(
        x + width/2, y + height/2, text,
        ha='center', va='center',
        color=text_color,
        fontsize=fontsize,
        weight=weight,
        wrap=True
    )

def create_arrow(ax, x1, y1, x2, y2, style='->'):
    """Create an arrow between two points"""
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle=style,
        color=LUMEN_GRAY,
        linewidth=2,
        mutation_scale=20
    )
    ax.add_patch(arrow)

def create_architecture_diagram():
    """Create the main architecture diagram"""
    
    # Create figure with high DPI for quality
    fig, ax = plt.subplots(figsize=(16, 12), dpi=150)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(8, 11.5, 'PASE Monitor Portal', 
            ha='center', fontsize=24, weight='bold', color=LUMEN_BLUE)
    ax.text(8, 11, 'Technology Architecture', 
            ha='center', fontsize=16, color=LUMEN_GRAY)
    
    # Layer labels (left side)
    layer_y_positions = [9.5, 7.5, 5.5, 3.5, 1.5]
    layer_labels = ['USER LAYER', 'WEB LAYER', 'API/CACHE', 'DATA LAYER', 'INTEGRATION']
    
    for i, (y_pos, label) in enumerate(zip(layer_y_positions, layer_labels)):
        ax.text(0.5, y_pos, label, 
                ha='left', fontsize=9, weight='bold', 
                color=LUMEN_PURPLE, rotation=0)
    
    # ============ USER LAYER (Top) ============
    user_y = 9
    create_box(ax, 2, user_y, 2, 1, 'Data\nEngineers\n(15 users)', LUMEN_GREEN, fontsize=9)
    create_box(ax, 5, user_y, 2, 1, 'Operations\nTeam\n(15 users)', LUMEN_GREEN, fontsize=9)
    create_box(ax, 8, user_y, 2, 1, 'Business\nStakeholders\n(15 users)', LUMEN_GREEN, fontsize=9)
    create_box(ax, 11, user_y, 2, 1, 'Management\n& Auditors\n(Viewers)', LUMEN_GREEN, fontsize=9)
    
    # ============ WEB LAYER ============
    web_y = 7
    
    # IIS + Django box
    create_box(ax, 3, web_y, 4, 1.2, 
               'IIS Web Server\nDjango 5.1 Application\nWindows SSO Auth', 
               LUMEN_BLUE, fontsize=9, bold=True)
    
    # UI Components
    create_box(ax, 8, web_y, 2.5, 1.2, 
               'Web Portal UI\nBootstrap 5\nLumen Branded', 
               LUMEN_BLUE, fontsize=9)
    
    # REST API
    create_box(ax, 11, web_y, 2, 1.2, 
               'REST APIs\nJSON/JWT\nRBAC', 
               LUMEN_BLUE, fontsize=9)
    
    # Arrows from users to web layer
    for x_pos in [3, 6, 9, 12]:
        create_arrow(ax, x_pos, user_y, x_pos, web_y + 1.2)
    
    # ============ API/CACHE LAYER ============
    api_y = 5
    
    # Cache
    create_box(ax, 2, api_y, 2.5, 1.2, 
               'Cache Layer\n5-min TTL\n99% Perf Boost', 
               LUMEN_ORANGE, fontsize=9, bold=True)
    
    # Business Logic
    create_box(ax, 5, api_y, 2.5, 1.2, 
               'Business Services\nWorkflow Status\nBI Feeds', 
               LUMEN_PURPLE, fontsize=9)
    
    # LOB Handler
    create_box(ax, 8, api_y, 2.5, 1.2, 
               'LOB Handler\n10MB Errors\nEncoding Mgmt', 
               LUMEN_PURPLE, fontsize=9)
    
    # Timezone Handler
    create_box(ax, 11, api_y, 2.5, 1.2, 
               'Timezone Auto\nDST Handling\n0 Maintenance', 
               LUMEN_PURPLE, fontsize=9)
    
    # Arrows from web to API layer
    create_arrow(ax, 5, web_y, 5, api_y + 1.2)
    create_arrow(ax, 9.5, web_y, 9.5, api_y + 1.2)
    
    # ============ DATA LAYER ============
    data_y = 3
    
    # Oracle databases
    create_box(ax, 2, data_y, 2, 1.2, 
               'MAPDQPRD\nData Quality\nWorkflows', 
               '#CC0000', fontsize=9, bold=True)
    
    create_box(ax, 4.5, data_y, 2, 1.2, 
               'MAPDWPRD\nData Warehouse\nBI Feeds', 
               '#CC0000', fontsize=9, bold=True)
    
    create_box(ax, 7, data_y, 2, 1.2, 
               'MAPGPRD\nGeneral PASE\nWorkflows', 
               '#CC0000', fontsize=9, bold=True)
    
    create_box(ax, 9.5, data_y, 2, 1.2, 
               'ERP\nSAP Integration\nCAPEX', 
               '#CC0000', fontsize=9, bold=True)
    
    # Informatica source
    create_box(ax, 12, data_y, 2, 1.2, 
               'Informatica\nPowerCenter\nMetadata', 
               '#FF8C00', fontsize=9)
    
    # Arrows from API to Data layer
    for x_pos in [3, 5.5, 8, 10.5]:
        create_arrow(ax, x_pos + 3, api_y, x_pos, data_y + 1.2)
    
    # ============ INTEGRATION LAYER ============
    integration_y = 1
    
    create_box(ax, 2, integration_y, 3, 1, 
               'SSRS Reports\nEmbedded iframes\nAudit Lineage', 
               LUMEN_GRAY, fontsize=9)
    
    create_box(ax, 6, integration_y, 3, 1, 
               'Monitoring\nHealth Checks\nStructured Logs', 
               LUMEN_GRAY, fontsize=9)
    
    create_box(ax, 10, integration_y, 3, 1, 
               'Future: Alerts\nTeams/Slack/Email\nPagerDuty', 
               '#CCCCCC', text_color=LUMEN_GRAY, fontsize=9)
    
    # Arrows from web layer to integration
    create_arrow(ax, 3.5, web_y, 3.5, integration_y + 1)
    create_arrow(ax, 7.5, web_y, 7.5, integration_y + 1)
    
    # ============ KEY METRICS (Bottom right) ============
    metrics_x = 14
    metrics_y = 8
    
    metrics_text = """KEY METRICS:
    
• 99% Faster
  91s → <1s
  
• 92% Time Saved
  45 → 3.75 hrs/wk
  
• 95% Faster Detection
  2-4hrs → <5min
  
• $655K Annual Value
  3,461% ROI
  
• 0 Maintenance
  Auto DST"""
    
    # Metrics box
    box = FancyBboxPatch(
        (metrics_x - 1.5, metrics_y - 3), 2.8, 3.5,
        boxstyle="round,pad=0.1",
        facecolor=LUMEN_LIGHT_GRAY,
        edgecolor=LUMEN_BLUE,
        linewidth=3
    )
    ax.add_patch(box)
    
    ax.text(metrics_x, metrics_y - 1.5, metrics_text,
            ha='center', va='center',
            fontsize=8,
            color=LUMEN_GRAY,
            family='monospace')
    
    # ============ LEGEND (Bottom left) ============
    legend_x = 1
    legend_y = 0.2
    
    ax.text(legend_x, legend_y, 
            '■ Production (80% Complete)  ■ Planned (Roadmap)',
            fontsize=8, color=LUMEN_GRAY)
    
    # ============ FOOTER ============
    ax.text(8, 0.3, 
            'Data Engineering Team | March 2026 | Internal Use',
            ha='center', fontsize=8, color=LUMEN_GRAY, style='italic')
    
    # Save as high-quality JPG
    plt.tight_layout()
    plt.savefig('PASE_Monitor_Portal_Architecture.jpg', 
                format='jpg', 
                dpi=300, 
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none')
    
    print("✅ Architecture diagram created: PASE_Monitor_Portal_Architecture.jpg")
    print(f"   Size: 16x12 inches @ 300 DPI")
    print(f"   File location: {plt.gcf().canvas.get_default_filename()}")
    
    plt.close()

if __name__ == "__main__":
    print("Generating PASE Monitor Portal Architecture Diagram...")
    create_architecture_diagram()
    print("\n✨ Done! You can now embed this JPG in your Word document or PowerPoint.")
