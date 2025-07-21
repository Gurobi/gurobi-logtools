import re
from typing import List, Tuple

import plotly.express as px

from gurobi_logtools import constants, gurobi_colors


class CustomPalettes:
    def __init__(self):
        self.palette_names = []

    def add_palette(self, name, colors):
        if not isinstance(colors, (list, tuple)):
            return ValueError("palette must be given as a list or tuple")
        for color in colors:
            if not isinstance(color, str) or not re.fullmatch(
                r"#[A-Fa-f0-9]{6}",
                color,
            ):
                raise ValueError(f"color {color} not a 6 digit hex string")
        setattr(self, name, colors)
        self.palette_names.append(name)


_custom_palette = CustomPalettes()


def register_custom_palette(name: str, colors: "List[str] | Tuple[str]") -> None:
    """Add a custom palette to the "Custom" palette group

    Parameters
    ----------
    name : str
        Name of the palette
    colors : List[str] | Tuple[str]
        A list or tuple of hexadecimal strings, eg ("#DD2113",  "#4E5059", "#00ff00")

    """
    _custom_palette.add_palette(name, colors)


def reset_custom_palettes() -> None:
    """Removes all registered custom palettes"""
    global _custom_palette
    _custom_palette = CustomPalettes()


def _get_palette(palette_type, palette):
    # used by the plotting functions in .plotting.py
    family = {
        constants.PaletteType.SEQUENTIAL: px.colors.sequential,
        constants.PaletteType.DIVERGING: px.colors.diverging,
        constants.PaletteType.QUALITATIVE: px.colors.qualitative,
        constants.PaletteType.GUROBI: gurobi_colors,
        constants.PaletteType.CUSTOM: _custom_palette,
    }[palette_type]
    try:
        return getattr(family, palette)
    except AttributeError:
        return px.colors.qualitative.Plotly


def _get_palettes(type_name):
    # used by the plotting functions in .plotting.py
    return {
        constants.PaletteType.SEQUENTIAL: _sequential_plotly_palettes,
        constants.PaletteType.DIVERGING: _diverging_plotly_palettes,
        constants.PaletteType.QUALITATIVE: _qualitative_plotly_palettes,
        constants.PaletteType.GUROBI: _gurobi_palettes,
        constants.PaletteType.CUSTOM: _custom_palette.palette_names,
    }[type_name]


def _get_default_palette(type_name):
    # used by the plotting functions in .plotting.py
    return {
        constants.PaletteType.SEQUENTIAL: "Plotly3",
        constants.PaletteType.DIVERGING: "Picnic",
        constants.PaletteType.QUALITATIVE: "Plotly",
        constants.PaletteType.GUROBI: "Gurobi_0",
        constants.PaletteType.CUSTOM: "",
    }[type_name]


_diverging_plotly_palettes = [
    "Armyrose",
    "Armyrose_r",
    "BrBG",
    "BrBG_r",
    "Earth",
    "Earth_r",
    "Fall",
    "Fall_r",
    "Geyser",
    "Geyser_r",
    "PRGn",
    "PRGn_r",
    "PiYG",
    "PiYG_r",
    "Picnic",
    "Picnic_r",
    "Portland",
    "Portland_r",
    "PuOr",
    "PuOr_r",
    "RdBu",
    "RdBu_r",
    "RdGy",
    "RdGy_r",
    "RdYlBu",
    "RdYlBu_r",
    "RdYlGn",
    "RdYlGn_r",
    "Spectral",
    "Spectral_r",
    "Tealrose",
    "Tealrose_r",
    "Temps",
    "Temps_r",
    "Tropic",
    "Tropic_r",
    "balance",
    "balance_r",
    "curl",
    "curl_r",
    "delta",
    "delta_r",
    "oxy",
    "oxy_r",
]

_qualitative_plotly_palettes = [
    "Alphabet",
    "Alphabet_r",
    "Antique",
    "Antique_r",
    "Bold",
    "Bold_r",
    "D3",
    "D3_r",
    "Dark2",
    "Dark24",
    "Dark24_r",
    "Dark2_r",
    "G10",
    "G10_r",
    "Light24",
    "Light24_r",
    "Pastel",
    "Pastel1",
    "Pastel1_r",
    "Pastel2",
    "Pastel2_r",
    "Pastel_r",
    "Plotly",
    "Plotly_r",
    "Prism",
    "Prism_r",
    "Safe",
    "Safe_r",
    "Set1",
    "Set1_r",
    "Set2",
    "Set2_r",
    "Set3",
    "Set3_r",
    "T10",
    "T10_r",
    "Vivid",
    "Vivid_r",
]

_sequential_plotly_palettes = [
    "Aggrnyl",
    "Aggrnyl_r",
    "Agsunset",
    "Agsunset_r",
    "Blackbody",
    "Blackbody_r",
    "Bluered",
    "Bluered_r",
    "Blues",
    "Blues_r",
    "Blugrn",
    "Blugrn_r",
    "Bluyl",
    "Bluyl_r",
    "Brwnyl",
    "Brwnyl_r",
    "BuGn",
    "BuGn_r",
    "BuPu",
    "BuPu_r",
    "Burg",
    "Burg_r",
    "Burgyl",
    "Burgyl_r",
    "Cividis",
    "Cividis_r",
    "Darkmint",
    "Darkmint_r",
    "Electric",
    "Electric_r",
    "Emrld",
    "Emrld_r",
    "GnBu",
    "GnBu_r",
    "Greens",
    "Greens_r",
    "Greys",
    "Greys_r",
    "Hot",
    "Hot_r",
    "Inferno",
    "Inferno_r",
    "Jet",
    "Jet_r",
    "Magenta",
    "Magenta_r",
    "Magma",
    "Magma_r",
    "Mint",
    "Mint_r",
    "OrRd",
    "OrRd_r",
    "Oranges",
    "Oranges_r",
    "Oryel",
    "Oryel_r",
    "Peach",
    "Peach_r",
    "Pinkyl",
    "Pinkyl_r",
    "Plasma",
    "Plasma_r",
    "Plotly3",
    "Plotly3_r",
    "PuBu",
    "PuBuGn",
    "PuBuGn_r",
    "PuBu_r",
    "PuRd",
    "PuRd_r",
    "Purp",
    "Purp_r",
    "Purples",
    "Purples_r",
    "Purpor",
    "Purpor_r",
    "Rainbow",
    "Rainbow_r",
    "RdBu",
    "RdBu_r",
    "RdPu",
    "RdPu_r",
    "Redor",
    "Redor_r",
    "Reds",
    "Reds_r",
    "Sunset",
    "Sunset_r",
    "Sunsetdark",
    "Sunsetdark_r",
    "Teal",
    "Teal_r",
    "Tealgrn",
    "Tealgrn_r",
    "Turbo",
    "Turbo_r",
    "Viridis",
    "Viridis_r",
    "YlGn",
    "YlGnBu",
    "YlGnBu_r",
    "YlGn_r",
    "YlOrBr",
    "YlOrBr_r",
    "YlOrRd",
    "YlOrRd_r",
    "algae",
    "algae_r",
    "amp",
    "amp_r",
    "deep",
    "deep_r",
    "dense",
    "dense_r",
    "gray",
    "gray_r",
    "haline",
    "haline_r",
    "ice",
    "ice_r",
    "matter",
    "matter_r",
    "solar",
    "solar_r",
    "speed",
    "speed_r",
    "swatches",
    "swatches_continuous",
    "tempo",
    "tempo_r",
    "thermal",
    "thermal_r",
    "turbid",
    "turbid_r",
]

_gurobi_palettes = [
    "Gurobi_0",
    "Gurobi_1",
    "Gurobi_2",
    "Gurobi_3",
    "Gurobi_4",
    "Gurobi_5",
    "Gurobi_6",
    "Gurobi_7",
    "Gurobi_8",
    "Gurobi_9",
    "Gurobi_10",
    "Gurobi_11",
    "Gurobi_12",
    "Gurobi_13",
    "Gurobi_14",
    "Gurobi_15",
    "Gurobi_16",
    "Gurobi_17",
    "Gurobi_18",
    "Gurobi_19",
    "Gurobi_20",
    "Gurobi_21",
    "Gurobi_22",
    "Gurobi_23",
]


def show_palettes():
    px.colors.diverging.swatches().show()
    px.colors.qualitative.swatches().show()
    px.colors.sequential.swatches().show()
