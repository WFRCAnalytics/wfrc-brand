"""Checks for the wfrc-brand extension that do not need Quarto.

    pip install pytest pyyaml matplotlib          # the optional tests also use:
    pip install plotly brand-yml "shiny[theme]"   # brand.yml schema, Shiny theme

Quarto renders are checked separately by .github/workflows/check.yml.
"""
import re
import sys
from pathlib import Path

import pytest
import yaml

EXT = Path(__file__).resolve().parent.parent / "_extensions/wfrc-brand"
THEME = EXT / "assets/theme"
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")

sys.path.insert(0, str(EXT / "assets/charts"))
import wfrc_charts as wfrc  # noqa: E402


def load(name):
    return yaml.safe_load((EXT / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def brand():
    return load("brand.yml")


def references(value):
    """Every string leaf of a nested mapping (a role's light and dark values both count)."""
    if isinstance(value, dict):
        for v in value.values():
            yield from references(v)
    elif isinstance(value, str):
        yield value


def test_palette_values_are_hex_or_resolve_to_a_palette_name(brand):
    palette = brand["color"]["palette"]
    for name, value in palette.items():
        assert HEX.match(value) or value in palette, f"{name}: {value!r} is neither a hex code nor a palette name"


def test_palette_aliases_have_no_cycles(brand):
    palette = brand["color"]["palette"]
    for name in palette:
        seen, cur = set(), name
        while not HEX.match(palette[cur]):
            assert cur not in seen, f"alias cycle at {name}"
            seen.add(cur)
            cur = palette[cur]


def test_color_roles_reference_palette_names(brand):
    palette = brand["color"]["palette"]
    for role, value in brand["color"].items():
        if role == "palette":
            continue
        for ref in references(value):
            assert HEX.match(ref) or ref in palette, f"color.{role}: {ref!r} is not in the palette"


def test_typography_colors_reference_palette_names(brand):
    palette = brand["color"]["palette"]
    for element, spec in brand["typography"].items():
        if not isinstance(spec, dict) or element == "fonts":
            continue
        for key in ("color", "background-color"):
            for ref in references(spec.get(key, {})):
                assert ref in palette, f"typography.{element}.{key}: {ref!r} is not in the palette"


def test_logo_paths_exist_and_have_alt_text(brand):
    for name, image in brand["logo"]["images"].items():
        assert (EXT / image["path"]).is_file(), f"{name}: {image['path']} is missing"
        assert image.get("alt"), f"{name}: logo needs alt text"


def test_scss_only_uses_palette_names_brand_yml_defines(brand):
    """The theme maps roles onto $brand-<name>; a typo would fail the whole Sass compile."""
    palette = brand["color"]["palette"]
    # brand.yml also exports the role colors, e.g. $brand-primary.
    known = set(palette) | {k for k in brand["color"] if k != "palette"}
    for scss in THEME.glob("*.scss"):
        for name in re.findall(r"\$brand-([a-z0-9-]+)", scss.read_text(encoding="utf-8")):
            assert name in known, f"{scss.name} uses $brand-{name}, which brand.yml does not define"


def test_offline_brand_points_at_font_files_that_exist():
    offline = load("brand-offline.yml")
    files = [f["path"] for fam in offline["typography"]["fonts"] for f in fam["files"]]
    assert files
    for rel in files:
        assert (EXT / rel).is_file(), f"{rel} is missing; run scripts/fetch-fonts.py"
    assert {Path(f).suffix for f in files} == {".woff2", ".ttf"}


def test_variants_share_the_palette(brand):
    for name in ("brand-offline.yml", "brand-flat.yml"):
        assert load(name)["color"]["palette"] == brand["color"]["palette"], f"{name} is stale; run scripts/build-brand-variants.py"


def test_flat_brand_has_no_light_dark_pairs():
    def walk(node, path=""):
        if isinstance(node, dict):
            assert set(node) != {"light", "dark"}, f"{path} still has a light/dark pair"
            for k, v in node.items():
                walk(v, f"{path}.{k}")

    walk(load("brand-flat.yml"))


def test_flat_brand_validates_against_the_brand_yml_schema():
    brand_yml = pytest.importorskip("brand_yml")
    parsed = brand_yml.Brand.from_yaml(EXT / "brand-flat.yml")
    assert parsed.color.primary == "#00395B"


def test_flat_brand_builds_a_shiny_theme():
    pytest.importorskip("sass")
    shiny = pytest.importorskip("shiny")
    css = shiny.ui.Theme.from_brand(str(EXT / "brand-flat.yml")).to_css()
    assert "#00395b" in css.lower()
    assert "poppins" in css.lower()


def test_chart_palette_is_five_distinct_colors_per_mode():
    for mode in ("light", "dark"):
        colors = wfrc.palette(5, mode)
        assert len(colors) == len(set(colors)) == 5
        assert all(HEX.match(c) for c in colors)
    assert wfrc.palette(5, "light") != wfrc.palette(5, "dark")


def test_chart_palette_refuses_more_than_five():
    with pytest.raises(ValueError):
        wfrc.palette(6)


def test_chart_helpers_read_the_flat_and_offline_brands_too():
    for name in ("brand-flat.yml", "brand-offline.yml"):
        assert wfrc.palette(5, "light", EXT / name) == wfrc.palette(5, "light", EXT / "brand.yml")


def test_matplotlib_style_uses_the_brand_cycle():
    mpl = pytest.importorskip("matplotlib")
    mpl.use("Agg")
    wfrc.use_style("light")
    cycle = [c["color"].upper() for c in mpl.rcParams["axes.prop_cycle"]]
    assert cycle[:5] == wfrc.palette(5, "light")


def test_plotly_template_colorway_matches_the_palette():
    for mode in ("light", "dark"):
        assert wfrc.plotly_template(mode)["layout"]["colorway"] == wfrc.palette(5, mode)


def test_plotly_accepts_the_template():
    go = pytest.importorskip("plotly.graph_objects")
    fig = go.Figure(go.Scatter(x=[1, 2], y=[1, 2]), layout=dict(template=wfrc.plotly_template()))
    assert fig.layout.template.layout.colorway[0] == wfrc.palette(5)[0]
