import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Define container sizes in mm
CONTAINERS = {
    "20ft": (5898, 2352, 2393),
    "40ft": (12032, 2352, 2393),
    "40ft HC": (12032, 2352, 2700)
}

# Load CSV and validate
@st.cache_data
def load_csv(file):
    df = pd.read_csv(file)
    expected_cols = ["ItemID", "Length", "Width", "Height", "Weight", "Quantity", "Stackable (yes/no)", "Fragile (yes/no)"]
    if not all(col in df.columns for col in expected_cols):
        st.error("CSV missing one or more required columns.")
        return None
    return df

# Placeholder 3D item placement logic (naive stack)
def pack_items(df, container_dims):
    items = []
    x, y, z = 0, 0, 0
    max_x, max_y, max_z = container_dims
    layer_height = 0

    for _, row in df.iterrows():
        for _ in range(int(row["Quantity"])):
            l, w, h = row["Length"], row["Width"], row["Height"]
            if x + l > max_x:
                x = 0
                y += w
            if y + w > max_y:
                y = 0
                z += layer_height
                layer_height = 0
            if z + h > max_z:
                break  # skip if over limit

            items.append((x, y, z, l, w, h, row["ItemID"]))
            x += l
            layer_height = max(layer_height, h)
    return items

# 3D plot using Plotly
def plot_items(items, container_dims):
    fig = go.Figure()
    for x, y, z, l, w, h, label in items:
        fig.add_trace(go.Mesh3d(
            x=[x, x+l, x+l, x, x, x+l, x+l, x],
            y=[y, y, y+w, y+w, y, y, y+w, y+w],
            z=[z, z, z, z, z+h, z+h, z+h, z+h],
            opacity=0.5,
            color='blue',
            name=label
        ))
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[0, container_dims[0]]),
            yaxis=dict(range=[0, container_dims[1]]),
            zaxis=dict(range=[0, container_dims[2]])
        ),
        width=900,
        margin=dict(r=10, l=10, b=10, t=10)
    )
    st.plotly_chart(fig)

# Streamlit UI
st.title("Local Container Load Optimization Tool")
st.write("Upload your CSV and select a container size.")

container_type = st.selectbox("Choose container type:", list(CONTAINERS.keys()))
container_dims = CONTAINERS[container_type]

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
if uploaded_file:
    df = load_csv(uploaded_file)
    if df is not None:
        st.write("### Preview:", df.head())
        if st.button("Optimize and Visualize"):
            packed = pack_items(df, container_dims)
            st.success(f"Packed {len(packed)} items.")
            plot_items(packed, container_dims)
