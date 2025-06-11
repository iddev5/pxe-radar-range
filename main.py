from flask import Flask, render_template, request
import plotly.graph_objs as go
import numpy as np

app = Flask(__name__)

def calculate_radar_range(Pt, G, lambd, sigma, Te, tau, F, L, Pmin, SNR):
    k = 1.38e-23
    B = 1 / tau
    denom = (4 * np.pi)**3 * k * Te * F * L * B * SNR
    num = Pt * G*2 * lambd*2 * sigma
    Rmax = (num / denom)**0.25
    return Rmax / 1000  # km

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    plot_snr = plot_rcs = ""
    if request.method == "POST":
        try:
            values = [float(request.form[key]) for key in [
                'Pt', 'G', 'lambd', 'sigma', 'Te', 'tau', 'F', 'L', 'Pmin', 'SNR'
            ]]
            Pt, G, lambd, sigma, Te, tau, F, L, Pmin, SNR = values
            result = calculate_radar_range(Pt, G, lambd, sigma, Te, tau, F, L, Pmin, SNR)

            # SNR vs Range
            snr = np.logspace(-2, 2, 100)
            k = 1.38e-23
            B = 1 / tau
            denom = (4 * np.pi)**3 * k * Te * F * L * B * snr
            num = Pt * G*2 * lambd*2 * sigma
            Rmax = (num / denom)**0.25 / 1000
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(x=Rmax, y=snr, mode='lines', name='SNR vs Range'))
            fig1.update_layout(title='SNR vs Radar Range', xaxis_title='Range (km)', yaxis_title='SNR')
            plot_snr = fig1.to_html(full_html=False)

            # RCS vs Range
            sigma_vals = np.logspace(-2, 2, 100)
            num_rcs = Pt * G*2 * lambd*2 * sigma_vals
            Rmax_rcs = (num_rcs / ((4 * np.pi)*3 * k * Te * F * L * B * SNR))*0.25 / 1000
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=Rmax_rcs, y=sigma_vals, mode='lines', name='RCS vs Range'))
            fig2.update_layout(title='RCS vs Radar Range', xaxis_title='Range (km)', yaxis_title='RCS (m²)')
            plot_rcs = fig2.to_html(full_html=False)

        except ValueError:
            result = "Invalid input!"
    return render_template("index.html", result=result, plot_snr=plot_snr, plot_rcs=plot_rcs)
