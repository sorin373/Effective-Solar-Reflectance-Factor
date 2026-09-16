from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go


# ============================================================
# Paths
# ============================================================

INPUT_FILE = Path("results/plane_sweeps.csv")
OUTPUT_DIR = Path("results/animations")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_FILE)


# ============================================================
# CubeSat geometry
#
# Schematic 3U-like cuboid.
# This is VISUAL ONLY, not your exact CAD geometry.
# ============================================================

HALF_X = 0.55
HALF_Y = 0.55
HALF_Z = 1.60


vertices = np.array([
    [-HALF_X, -HALF_Y, -HALF_Z],
    [ HALF_X, -HALF_Y, -HALF_Z],
    [ HALF_X,  HALF_Y, -HALF_Z],
    [-HALF_X,  HALF_Y, -HALF_Z],

    [-HALF_X, -HALF_Y,  HALF_Z],
    [ HALF_X, -HALF_Y,  HALF_Z],
    [ HALF_X,  HALF_Y,  HALF_Z],
    [-HALF_X,  HALF_Y,  HALF_Z],
])


# Triangles making up cuboid faces
I = [
    0, 0,   # -Z
    4, 4,   # +Z
    0, 0,   # -Y
    3, 3,   # +Y
    0, 0,   # -X
    1, 1    # +X
]

J = [
    1, 2,
    5, 6,
    1, 5,
    2, 6,
    3, 7,
    2, 6
]

K = [
    2, 3,
    6, 7,
    5, 4,
    6, 7,
    7, 4,
    6, 5
]


# ============================================================
# Static CubeSat
# ============================================================

def cubesat_trace():
    return go.Mesh3d(
        x=vertices[:, 0],
        y=vertices[:, 1],
        z=vertices[:, 2],

        i=I,
        j=J,
        k=K,

        opacity=0.55,

        flatshading=True,

        name="CubeSat",

        hoverinfo="skip"
    )


# ============================================================
# Axis traces
# ============================================================

def axis_traces():
    length = 2.2

    traces = []

    axes = [
        ("+X", [0, length], [0, 0], [0, 0]),
        ("+Y", [0, 0], [0, length], [0, 0]),
        ("+Z", [0, 0], [0, 0], [0, length]),
    ]

    for name, x, y, z in axes:
        traces.append(
            go.Scatter3d(
                x=x,
                y=y,
                z=z,

                mode="lines+text",

                text=["", name],

                line=dict(width=5),

                showlegend=False,

                hoverinfo="skip"
            )
        )

    return traces


# ============================================================
# Incoming solar ray
#
# IMPORTANT:
# k is your propagation vector Sun -> spacecraft.
#
# Therefore the ray starts at -k and points towards the origin.
# ============================================================

def sun_line(kx, ky, kz):

    scale = 2.7

    sun_x = -scale * kx
    sun_y = -scale * ky
    sun_z = -scale * kz

    return go.Scatter3d(
        x=[sun_x, 0],
        y=[sun_y, 0],
        z=[sun_z, 0],

        mode="lines+markers",

        line=dict(
            width=8
        ),

        marker=dict(
            size=[9, 3]
        ),

        name="Incoming solar radiation",

        hoverinfo="skip"
    )


# ============================================================
# Arrow head
# ============================================================

def sun_arrow(kx, ky, kz):

    # Place arrow near spacecraft.
    pos_scale = 0.9

    x = -pos_scale * kx
    y = -pos_scale * ky
    z = -pos_scale * kz

    return go.Cone(
        x=[x],
        y=[y],
        z=[z],

        u=[kx],
        v=[ky],
        w=[kz],

        sizemode="absolute",
        sizeref=0.35,

        showscale=False,

        name="k",

        hoverinfo="skip"
    )


# ============================================================
# Sun marker
# ============================================================

def sun_marker(kx, ky, kz):

    scale = 2.7

    return go.Scatter3d(
        x=[-scale * kx],
        y=[-scale * ky],
        z=[-scale * kz],

        mode="markers+text",

        text=["SUN"],
        textposition="top center",

        marker=dict(
            size=18,
            symbol="circle"
        ),

        name="Sun",

        hoverinfo="skip"
    )


# ============================================================
# Create one animation
# ============================================================

def create_animation(plane):

    data = df[df["plane"] == plane].copy()

    # 720 steps is nice for calculations but excessive for animation.
    # Keep every 4th point -> about 180 frames.
    data = data.iloc[::4].reset_index(drop=True)

    first = data.iloc[0]

    # --------------------------------------------------------
    # Initial figure
    # --------------------------------------------------------

    fig = go.Figure()

    fig.add_trace(cubesat_trace())

    for trace in axis_traces():
        fig.add_trace(trace)

    # Index 4
    fig.add_trace(
        sun_line(
            first["kx"],
            first["ky"],
            first["kz"]
        )
    )

    # Index 5
    fig.add_trace(
        sun_arrow(
            first["kx"],
            first["ky"],
            first["kz"]
        )
    )

    # Index 6
    fig.add_trace(
        sun_marker(
            first["kx"],
            first["ky"],
            first["kz"]
        )
    )


    # ========================================================
    # Frames
    # ========================================================

    frames = []

    for index, row in data.iterrows():

        kx = row["kx"]
        ky = row["ky"]
        kz = row["kz"]

        q = row["q"]

        A_proj_m2 = (
            row["A_proj"]
            / 1e6
        )

        force_factor_m2 = (
            row["force_factor"]
            / 1e6
        )

        angle = row["angle_deg"]

        frame_name = f"{index}"

        title = (
            f"Solar Direction Sweep – {plane} Plane"
            f"<br>"
            f"Angle = {angle:.1f}°"
            f" | q = {q:.3f}"
            f" | A<sub>proj</sub> = {A_proj_m2:.4f} m²"
            f" | A<sub>proj</sub>(1+q) = "
            f"{force_factor_m2:.4f} m²"
        )

        frame = go.Frame(

            # Only replace sun line, cone, and sun marker.
            data=[
                sun_line(kx, ky, kz),
                sun_arrow(kx, ky, kz),
                sun_marker(kx, ky, kz)
            ],

            traces=[4, 5, 6],

            name=frame_name,

            layout=go.Layout(
                title=dict(
                    text=title
                )
            )
        )

        frames.append(frame)

    fig.frames = frames


    # ========================================================
    # Slider
    # ========================================================

    slider_steps = []

    for index, row in data.iterrows():

        slider_steps.append(
            dict(
                method="animate",

                args=[
                    [str(index)],

                    dict(
                        mode="immediate",

                        frame=dict(
                            duration=0,
                            redraw=True
                        ),

                        transition=dict(
                            duration=0
                        )
                    )
                ],

                label=f"{row['angle_deg']:.0f}°"
            )
        )


    sliders = [
        dict(
            active=0,

            currentvalue=dict(
                prefix="Angle: "
            ),

            pad=dict(
                t=50
            ),

            steps=slider_steps
        )
    ]


    # ========================================================
    # Play/Pause controls
    # ========================================================

    updatemenus = [
        dict(
            type="buttons",

            direction="left",

            x=0.05,
            y=0.02,

            buttons=[

                dict(
                    label="▶ Play",

                    method="animate",

                    args=[
                        None,

                        dict(
                            frame=dict(
                                duration=40,
                                redraw=True
                            ),

                            transition=dict(
                                duration=0
                            ),

                            fromcurrent=True,

                            mode="immediate"
                        )
                    ]
                ),

                dict(
                    label="⏸ Pause",

                    method="animate",

                    args=[
                        [None],

                        dict(
                            frame=dict(
                                duration=0,
                                redraw=False
                            ),

                            mode="immediate"
                        )
                    ]
                )
            ]
        )
    ]


    # ========================================================
    # Layout
    # ========================================================

    fig.update_layout(

        title=(
            f"Solar Direction Sweep – {plane} Plane"
        ),

        scene=dict(

            xaxis=dict(
                title="X",
                range=[-3.1, 3.1]
            ),

            yaxis=dict(
                title="Y",
                range=[-3.1, 3.1]
            ),

            zaxis=dict(
                title="Z",
                range=[-3.1, 3.1]
            ),

            aspectmode="cube",

            camera=dict(
                eye=dict(
                    x=1.7,
                    y=1.7,
                    z=1.35
                )
            )
        ),

        width=1100,
        height=850,

        sliders=sliders,

        updatemenus=updatemenus,

        margin=dict(
            l=0,
            r=0,
            b=100,
            t=100
        ),

        showlegend=False
    )


    # ========================================================
    # Save HTML
    # ========================================================

    output = (
        OUTPUT_DIR
        / f"sun_sweep_{plane}.html"
    )

    fig.write_html(
        output,
        auto_open=False
    )

    print(
        f"Created: {output}"
    )


# ============================================================
# Generate all three
# ============================================================

for plane in ["XY", "XZ", "YZ"]:
    create_animation(plane)


print("\nDone.")
print(
    "Open the HTML files in results/animations/"
)