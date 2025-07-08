from flask import Flask, request, render_template_string
import threading
from .pipeline import run_pipeline
app=Flask(__name__)
PAGE="""<h1>Anime Dubbing Alpha</h1>
<form method='post'>
Video path: <input name='video' value='Input/' size='60'><br>
Output dir: <input name='outdir' value='output' size='30'><br><br>
<button type='submit'>Start dubbing</button>
</form>
{% if msg %}<p>{{msg}}</p>{% endif %}
"""
@app.route('/',methods=['GET','POST'])
def index():
    msg=None
    if request.method=='POST':
        vid=request.form['video']; out=request.form['outdir']
        threading.Thread(target=lambda:run_pipeline(vid,out),daemon=True).start()
        msg='Processing started. Monitor console/output directory.'
    return render_template_string(PAGE,msg=msg)
if __name__=='__main__':
    app.run(host='0.0.0.0',port=5000)