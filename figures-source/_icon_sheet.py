import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from svgkit import SVG
import icons as I
svg = SVG(900, 260)
fns = [I.xray, I.blood_tube, I.test_strip, I.well_plate, I.pcr_box, I.clipboard, I.sequencer, I.document, I.lock, I.brain_chip, I.petri, I.table_icon]
for i, f in enumerate(fns):
    f(svg, 20 + i * 72, 20, 60)
mic = [I.bacterium, I.fungus, I.virus, I.yeast, I.mycobacterium]
for i, f in enumerate(mic):
    f(svg, 50 + i * 90, 140, 60)
I.check(svg, 520, 140, 40); I.cross(svg, 570, 140, 40); I.flag(svg, 620, 140, 40); I.person(svg, 690, 140, 60)
I.sieve(svg, 20, 210, 300, 22)
svg.save("/private/tmp/claude-501/-Users-ythuang-Desktop-Paper-multimodal/56e84147-d77c-4fe1-b57e-5430037f1d25/scratchpad/icons.svg")
