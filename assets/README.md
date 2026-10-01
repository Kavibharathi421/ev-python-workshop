The landing page opens with the approved generated picture, `reference-car-hero.png`, embedded locally. The studio view uses gentle image motion and pointer tilt, with a pause control and reduced-motion support. It is a two-dimensional image, not a reconstructed mesh.

The 3D assembly button switches to the Blender-built widebody coupe based on the user's supplied photograph. Its dark body, bolted fender flares, split-spoke wheels, swept headlights, low splitter and rear spoiler follow that reference. See `models/README.md` for the editable source and the accuracy limits of a single view. The model's animation pauses while the studio image is displayed.

Streamlit embeds `models/reference_car.json` and the local Three.js 0.160.1 engine (`vendor/three.min.js`, MIT license in `vendor/THREE-LICENSE.txt`) directly. No network loader or API key is required.

Drag or use arrow keys to rotate the focused canvas; use + / - or scroll on the focused canvas to zoom. Controls enable driving, rotation, and a transparent battery view. Automatic rotation respects reduced-motion preferences. WebGL is required for the vehicle; the simulations remain available without it.

Other diagrams are rendered with HTML/CSS or Matplotlib.

The Blender model runs the existing 80-second disassembly and reassembly tour of eight assemblies: exterior, cabin, wheels, chassis, battery, motor, inverter, and cooling. EV internals are illustrative. Pause or scrub the timeline, or use Disassemble / Reassemble. Camera framing follows the model bounds. Drive spins separate Blender wheel groups at a speed matched to the road. Reduced-motion preferences disable autoplay and make assembly commands instant.
