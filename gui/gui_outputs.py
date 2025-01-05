from tkinter import ttk


def update_tiles(jet_props, pilot_results, coflow_results, mix_results):
    update_flow_tile(jet_props, pilot_results, coflow_results)
    update_thermal_tile(jet_props, pilot_results, coflow_results)
    update_performance_tile(jet_props, pilot_results, coflow_results)
    update_mixing_tile(mix_results)


def add_label(parent, text):
    ttk.Label(parent, text=text, style='TileValue.TLabel').pack()


def update_flow_tile(flow_tile, jet_props, pilot_results, coflow_results):
    # Example of adding values to a tile
    mass_flow_frame = ttk.Frame(flow_tile)
    mass_flow_frame.pack(fill='x', pady=5)

    ttk.Label(mass_flow_frame, text="Mass Flows", style='TileHeader.TLabel').pack()

    add_label(flow_tile, f"Jet Mass Flow       :  {jet_props.mass_flow_total * 1000:.2f} g/s")
    add_label(flow_tile, f"Pilot Fuel Mass Flow:  {pilot_results.fuel_mass_flow * 1000:.2f} g/s")
    add_label(flow_tile, f"Pilot Air Mass Flow :  {pilot_results.air_mass_flow * 1000:.2f} g/s")
    add_label(flow_tile, f"Co-Flow Mass Flow   : {coflow_results.mass_flow * 1000:.2f} g/s")

    vol_flow_frame = ttk.Frame(flow_tile)
    vol_flow_frame.pack(fill='x', pady=5)

    ttk.Label(vol_flow_frame, text="Volume Flow", style='TileHeader.TLabel').pack()
    add_label(flow_tile, f"Jet Volume Flow       :  {jet_props.v_total_real * 60000:.1f} [LPM]")
    add_label(flow_tile, f"Pilot Fuel Volume Flow:   {pilot_results.fuel_volume_flow * 60000:.1f} [LPM]")
    add_label(flow_tile, f"Pilot Air Volume Flow :  {pilot_results.air_volume_flow * 60000:.1f} [LPM]")
    add_label(flow_tile, f"Co-Flow Volume Flow   : {coflow_results.volume_flow * 60000:.1f} [LPM]")

    vol_flow_frame_std = ttk.Frame(flow_tile)
    vol_flow_frame_std.pack(fill='x', pady=5)

    ttk.Label(vol_flow_frame_std, text="Volume Flow Standard", style='TileHeader.TLabel').pack()
    add_label(flow_tile, f"Jet Volume Flow       :  {jet_props.v_total_std * 60000:.1f} [LPM]")
    add_label(flow_tile, f"Pilot Fuel Volume Flow:   {pilot_results.fuel_volume_flow_std * 60000:.1f} [LPM]")
    add_label(flow_tile, f"Pilot Air Volume Flow :  {pilot_results.air_volume_flow_std * 60000:.1f} [LPM]")
    add_label(flow_tile, f"Co-Flow Volume Flow   : {coflow_results.std_volume_flow * 60000:.1f} [LPM]")


def update_thermal_tile(thermal_tile, jet_props, pilot_results, coflow_results):
    pass


def update_performance_tile(performance_tile, jet_props, pilot_results, coflow_results):
    pass


def update_mixing_tile(mixing_tile, mix_results):
    pass
