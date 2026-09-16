import pandas as pd
import plotly.graph_objects as go


df = pd.read_csv("results/final_samples.csv")


fig = go.Figure()

fig.add_trace(
    go.Scatter3d(
        x=df["kx"],
        y=df["ky"],
        z=df["kz"],

        mode="markers",

        marker=dict(
            size=2,
            color=df["q"],
            colorscale="Viridis",
            cmin=0,
            cmax=1,
            colorbar=dict(
                title="Reflectance q"
            )
        ),

        customdata=df[
            ["q", "A_proj", "force_factor"]
        ],

        hovertemplate=(
            "kx=%{x:.3f}<br>"
            "ky=%{y:.3f}<br>"
            "kz=%{z:.3f}<br>"
            "q=%{customdata[0]:.3f}<br>"
            "A_proj=%{customdata[1]:.0f} mm²<br>"
            "A_proj(1+q)=%{customdata[2]:.0f} mm²"
            "<extra></extra>"
        )
    )
)


# ============================================================
# Principal axes
# ============================================================

axes = [
    ("+X", 1, 0, 0),
    ("-X", -1, 0, 0),
    ("+Y", 0, 1, 0),
    ("-Y", 0, -1, 0),
    ("+Z", 0, 0, 1),
    ("-Z", 0, 0, -1)
]

for name, x, y, z in axes:
    fig.add_trace(
        go.Scatter3d(
            x=[0, 1.2*x],
            y=[0, 1.2*y],
            z=[0, 1.2*z],

            mode="lines+text",

            text=["", name],

            line=dict(
                width=5
            ),

            showlegend=False
        )
    )


fig.update_layout(
    title="Directional Effective Reflectance",

    scene=dict(
        xaxis_title="kx",
        yaxis_title="ky",
        zaxis_title="kz",

        aspectmode="cube"
    ),

    width=1000,
    height=850
)


fig.write_html(
    "results/plots/reflectance_sphere_3D.html"
)

fig.show()