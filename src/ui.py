import streamlit as st

def poster_placeholder(title, genre):
    return f"""
    <div style="height:250px;border-radius:18px;background:linear-gradient(145deg,#3b1d5a,#152b55);
                display:flex;align-items:center;justify-content:center;text-align:center;
                padding:25px;border:1px solid #4c5480;">
        <div>
            <div style="font-size:55px">🎬</div>
            <div style="font-size:20px;font-weight:700">{title}</div>
            <div style="color:#aeb8d6">{genre}</div>
        </div>
    </div>
    """

def render_seat_map(rows, cols, booked, selected):
    selected = set(selected)
    for row in rows:
        st.markdown(f"**Row {row}**")
        seat_cols = st.columns(len(cols))
        for i, num in enumerate(cols):
            seat = f"{row}{num}"
            with seat_cols[i]:
                if seat in booked:
                    st.button("🔴", key=f"booked_{seat}", disabled=True, help=f"{seat} is booked")
                else:
                    label = "🔵" if seat in selected else "🟢"
                    if st.button(label, key=f"seat_{seat}", help=f"Seat {seat}"):
                        if seat in selected:
                            selected.remove(seat)
                        else:
                            selected.add(seat)
                        st.rerun()
    return sorted(selected, key=lambda x: (x[0], int(x[1:])))
