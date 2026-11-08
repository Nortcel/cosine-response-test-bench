"""Generate the documented V5.2.2 architecture, not a complete circuit schematic."""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

def main():
    fig,axes=plt.subplots(1,2,figsize=(12,6))
    for ax in axes:ax.set_xlim(-.3,10.3);ax.set_ylim(0,10);ax.axis('off')
    def box(ax,x,y,w,h,text,fc='#EAF1F5'):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.10',fc=fc,ec='#31546A',lw=1.5))
        ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=10)
    def arrow(ax,a,b):ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','color':'#555','lw':1.5})
    a,b=axes;a.set_title('A  Control architecture',loc='left',fontweight='bold')
    box(a,3.5,4,3,2,'Arduino Uno R3\nFirmware V5.2.2')
    for x,y,txt in [(0,7.5,'Start / Stop / Free\nphysical controls'),(0,4,'Home / end\noptical interrupters'),(0,0.8,'DHT11\nDetector input A1')]:
        box(a,x,y,2.8,1.5,txt);arrow(a,(x+2.8,y+.75),(3.5,5))
    for x,y,txt in [(7.2,7.5,'EasyDriver V4.4\nNEMA 17 motor'),(7.2,4,'650 nm laser\nswitching'),(7.2,.8,'V26.7 desktop app\nUSB serial, optional')]:
        box(a,x,y,2.8,1.5,txt);arrow(a,(6.5,5),(x,y+.75))
    a.text(5,-.45,'Functional connections only; not an as-built circuit schematic.',ha='center',fontsize=9)
    b.set_title('B  V5.2.2 normal operating paths',loc='left',fontweight='bold')
    box(b,3.4,7.5,3.2,1.3,'STANDBY');box(b,.2,4,3.3,1.3,'MEASURING');box(b,6.5,4,3.3,1.3,'FREE');box(b,3.4,1,3.2,1.3,'HOMING')
    arrow(b,(4,7.5),(1.85,5.3));arrow(b,(6,7.5),(8.15,5.3));arrow(b,(1.85,4),(4,2.3));arrow(b,(8.15,4),(6,2.3));arrow(b,(5,2.3),(5,7.5))
    b.text(1.8,6.5,'Start / START',ha='center',fontsize=9);b.text(8.2,6.5,'Free / FREE',ha='center',fontsize=9)
    b.text(1.9,2.7,'Complete / stop /\nforward end limit',ha='center',fontsize=9);b.text(8.3,2.8,'Stop / STOP',ha='center',fontsize=9)
    b.text(5.1,6.0,'Home\nconfirmed',fontsize=9)
    b.text(5,-.55,'Homing ignores STOP. No general scan timeout.\n15 s timeout applies to home/end moves. Fault paths omitted.',ha='center',fontsize=9,color='#8B3A17')
    fig.subplots_adjust(left=.03,right=.97,top=.90,bottom=.15,wspace=.15)
    out=Path(__file__).resolve().parent/'output'
    for ext in ['png','pdf','svg']:fig.savefig(out/f'Figure_3_control_architecture_and_states.{ext}',dpi=300)
    plt.close(fig)
if __name__=='__main__':main()
