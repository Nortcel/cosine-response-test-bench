"""Replot secondary transcriptions of historical graph labels, not raw observations.
Run from any directory: python optical_graph_reproduction.py
Requires numpy and matplotlib. Inputs and outputs resolve relative to this script.
"""
from pathlib import Path
import csv,json
import numpy as np
import matplotlib.pyplot as plt

def main():
    root=Path(__file__).resolve().parent.parent
    data=root/'data/optical_graph_transcription';out=root/'analysis/output';out.mkdir(exist_ok=True)
    with (data/'Optical_measurements_transcribed.csv').open(encoding='utf-8-sig') as f: rows=list(csv.DictReader(f))
    x=np.array([float(r['voltage_V']) for r in rows]);y=np.array([float(r['reference_reading']) for r in rows])
    assert len(x)==20 and np.isfinite(x).all() and np.isfinite(y).all()
    slope,intercept=np.polyfit(x,y,1);fit=slope*x+intercept
    r2=1-np.sum((y-fit)**2)/np.sum((y-y.mean())**2)
    result={'n':len(x),'slope':float(slope),'intercept':float(intercept),'r_squared':float(r2),'status':'Secondary transcription of graph labels; physical units and detector identity unresolved'}
    (out/'Optical_fit_from_transcribed_labels.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    with (out/'Optical_fit_residuals.csv').open('w',newline='',encoding='utf8') as f:
        w=csv.writer(f);w.writerow(['voltage_V','transcribed_reference_value','fitted_value','residual','units']);w.writerows(zip(x,y,fit,y-fit,['unresolved source scale']*len(x)))
    fig=plt.figure(figsize=(11,8));gs=fig.add_gridspec(2,3,height_ratios=[1,1.1],hspace=.23)
    for i,(name,label) in enumerate([('image4.png','A  Optical bench'),('image2.png','B  Reference detector'),('image3.png','C  Photodiode')]):
        ax=fig.add_subplot(gs[0,i]);ax.imshow(plt.imread(data/'source_images'/name));ax.axis('off');ax.set_title(label,loc='left',fontsize=11)
    ax=fig.add_subplot(gs[1,:]);ax.scatter(x,y,label='Transcribed numeric labels',s=28,color='#0072B2',zorder=3)
    ax.plot(x,fit,color='#D55E00',label=f'OLS fit: y = {slope:.4f}x + {intercept:.4f}; R² = {r2:.4f}')
    ax.set_xlabel('Readout voltage (V), as labelled in historical graph');ax.set_ylabel('Reference reading\n(source units unresolved)');ax.grid(alpha=.25);ax.legend(loc='upper left',frameon=False);ax.set_title('D  Reproduction of historical graph values',loc='left',fontsize=11)
    fig.subplots_adjust(left=.10,right=.98,top=.96,bottom=.13)
    fig.text(.10,.035,'Secondary transcription, not original instrument records. Historical axis: W/m²; later figure: mW.\nDetector labels conflict (985 / 958-1024-1-ND). No physical-unit conversion or calibration claim.',fontsize=9)
    for ext in ['png','pdf','svg']:fig.savefig(out/f'Figure_S2_optical_saturation_check.{ext}',dpi=300)
    plt.close(fig);print(json.dumps(result))
if __name__=='__main__':main()
