Photo-referenced widebody coupe, built in Blender from the supplied
`pexels-murdashots-611021625-17754630.jpg`.

- `reference_car.blend`: editable source, named parts, wheel pivots and driving loop.
- `reference_car.glb`: portable model with wheel animation.
- `reference_car.json`: evaluated Blender geometry used by the offline landing page.

Rebuild with Blender 4.2: `blender --background --python tools/build_ev.py`.

The exterior follows one photograph. Unseen surfaces and dimensions are approximated;
this is not manufacturer CAD or an exact replica. The battery, motor, inverter and
cooling assembly represent an illustrative electric conversion for the educational
tour, not verified internals of the photographed car.
