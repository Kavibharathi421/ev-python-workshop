"""Run with Blender: blender --background --python tools/build_ev.py.

Builds a photo-referenced widebody coupe and an offline web mesh from Blender
geometry. X is forward, Y is left, Z is up. Dimensions are in metres.
"""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pack_mesh import pack_meshes

OUT = Path(__file__).resolve().parents[1] / "assets" / "models"
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
MATERIALS = {}


def material(name, color, metal=0, rough=.4, emission=0, exterior=False):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metal
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Coat Weight'].default_value = .45 if exterior else .1
    bsdf.inputs['Emission Color'].default_value = (*color, 1)
    bsdf.inputs['Emission Strength'].default_value = emission
    MATERIALS[name] = dict(color=list(color), metalness=metal, roughness=rough,
                           emission=emission, exterior=exterior)
    return mat


paint = material('Graphite metallic body', (.055, .064, .076), .82, .22, exterior=True)
glass = material('Smoked panoramic glass', (.018, .042, .052), .45, .16, exterior=True)
rubber = material('Tyre rubber', (.012, .017, .016), .05, .82)
trim = material('Graphite trim', (.023, .031, .029), .4, .36, exterior=True)
alloy = material('Brushed aluminium', (.56, .64, .63), .85, .23)
dark_alloy = material('Wheel recess', (.036, .048, .047), .75, .33)
white = material('Ice white LEDs', (.66, .94, 1), .1, .18, 3, True)
red = material('Ruby rear LEDs', (.8, .009, .02), .1, .2, 3, True)
cells = material('Battery modules', (.38, .8, .12), .35, .3, .25)
copper = material('High voltage copper', (1, .24, .025), .45, .28)
caliper = material('Orange brake calipers', (.85, .12, .018), .4, .26)


def finish(obj, name, mat, group='body', bevel=0):
    obj.name = name
    obj.data.materials.append(mat)
    obj['web_group'] = group
    if bevel:
        mod = obj.modifiers.new('Manufactured edge radii', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        mod = obj.modifiers.new('Weighted surface normals', 'WEIGHTED_NORMAL')
        mod.keep_sharp = True
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def box(name, location, size, mat, bevel=.025, group='body'):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, mat, group, bevel)


def mesh(name, verts, faces, mat, bevel=0, group='body'):
    data = bpy.data.meshes.new(name)
    data.from_pydata(verts, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    return finish(obj, name, mat, group, bevel)


def line(name, points, radius, mat, group='body'):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 2
    curve.bevel_depth = radius
    curve.bevel_resolution = 3
    spline = curve.splines.new('POLY')
    spline.points.add(len(points)-1)
    for p, co in zip(spline.points, points):
        p.co = (*co, 1)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    curve.materials.append(mat)
    obj['web_group'] = group
    return obj


def cylinder(name, location, radius, depth, mat, group='body'):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=radius, depth=depth,
                                      location=location, rotation=(math.pi/2, 0, 0))
    return finish(bpy.context.object, name, mat, group, .008)


def torus(name, location, major, minor, mat, group='body'):
    bpy.ops.mesh.primitive_torus_add(major_segments=64, minor_segments=12,
        location=location, rotation=(math.pi/2, 0, 0), major_radius=major, minor_radius=minor)
    return finish(bpy.context.object, name, mat, group)


# Sculpted cross-sections make a continuous, closed body shell.
sections = [(-2.4,.72,.83),(-2.32,.86,.94),(-2.1,.93,1.0),
            (-1.7,.96,1.04),(-1.25,.96,1.045),(-.7,.945,1.035),
            (0,.935,1.025),(.65,.95,1.015),(1.25,.965,.995),
            (1.7,.955,.94),(2.13,.90,.875),(2.35,.80,.79),(2.4,.69,.71)]
verts=[]
for x,w,h in sections:
    for y,z in [(0,.33),(.80*w,.33),(.98*w,.40),(w,.63),(.985*w,h-.12),
                (.87*w,h-.015),(.48*w,h+.015),(0,h+.022),
                (-.48*w,h+.015),(-.87*w,h-.015),(-.985*w,h-.12),
                (-w,.63),(-.98*w,.40),(-.80*w,.33)]:
        verts.append((x,y,z))
n=14
faces=[tuple(reversed(range(n)))]
for j in range(len(sections)-1):
    for k in range(n):
        faces.append((j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k))
faces.append(tuple(range((len(sections)-1)*n,len(sections)*n)))
body=mesh('Continuous sculpted body',verts,faces,paint)
bpy.context.view_layer.objects.active=body
sub=body.modifiers.new('Smooth body surfaces','SUBSURF');sub.levels=2
bpy.ops.object.modifier_apply(modifier=sub.name)
# Real openings in the body, instead of wheels pasted over solid panels.
for x in [-1.51,1.49]:
    cutter=cylinder('Wheel arch cutting tool',(x,0,.40),.445,3,rubber)
    bpy.context.view_layer.objects.active=body
    mod=body.modifiers.new('Open wheel arch','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)

# Cabin: rear screen, panoramic roof and swept windscreen.
cabin_sections=[(-1.52,.77,1.04),(-.90,.71,1.43),(-.53,.69,1.51),
                (.30,.68,1.50),(.57,.70,1.41),(1.10,.79,1.025)]
v=[]
for x,w,h in cabin_sections:
    v.extend([(x,-.825,1.005),(x,-w,h-.055),(x,-w*.82,h),
              (x,0,h+.025),(x,w*.82,h),(x,w,h-.055),(x,.825,1.005)])
f=[]
for j in range(len(cabin_sections)-1):
    for k in range(6):f.append((j*7+k,j*7+k+1,(j+1)*7+k+1,(j+1)*7+k))
f.extend([tuple(reversed(range(7))),tuple(range(35,42))])
mesh('Continuous panoramic glazing',v,f,glass,.018,'glazing')
# Follow the glazing crown with a separate, offset quad surface. A flat roof
# intersects the curved glass at its ends and creates flickering reflections.
roof_vertices=[]
for x,w,h in cabin_sections[1:-1]:
    roof_vertices.extend((x,y,z+.014) for y,z in
                         [(-w,h-.055),(-w*.82,h),(0,h+.025),(w*.82,h),(w,h-.055)])
roof_faces=[(row*5+col,row*5+col+1,(row+1)*5+col+1,(row+1)*5+col)
            for row in range(3) for col in range(4)]
mesh('Metal roof',roof_vertices,roof_faces,paint,group='glazing')
for side in [-1,1]:
    line('Roof rail',[(x,side*w,h-.045) for x,w,h in cabin_sections],.025,paint,'glazing')
    line('Window belt',[(x,side*.831,1.014) for x in [-1.50,-.8,0,.6,1.08]],.014,trim,'glazing')
    line('A pillar',[(.30,side*.69,1.50),(.57,side*.735,1.38),(1.10,side*.825,1.02)],.031,paint,'glazing')
    line('Rear pillar',[(-1.50,side*.81,1.03),(-.90,side*.72,1.415),(-.53,side*.70,1.50)],.065,paint,'glazing')
    line('B pillar',[(-.65,side*.832,1.02),(-.65,side*.71,1.48)],.03,trim,'glazing')
    # Thin door shut-lines and flush handles on both sides.
    for x in [-.67,.99]:
        line('Door seam',[(x,side*.943,.98),(x+.015,side*.946,.82),
                          (x-.035,side*.943,.53),(x-.13,side*.921,.40)],.004,trim)
    line('Sill accent',[(-1.02,side*.952,.385),(.97,side*.952,.385)],.022,trim)
    box('Recessed door handle',(-.48,side*.947,.942),(.20,.026,.035),alloy,.012)
    line('Mirror stem',[(.77,side*.83,1.06),(.72,side*1.01,1.12)],.024,trim)
    box('Aero mirror',(.68,side*1.04,1.14),(.23,.16,.09),paint,.04)
    box('Mirror glass',(.567,side*1.04,1.145),(.01,.125,.052),glass,.018)
    # Bolted-on widebody fenders follow the wheel opening and flare outward.
    for x in [-1.51,1.49]:
        vs=[]
        for i in range(49):
            a=-.18+i*(math.pi+.36)/48
            for r,y in [(.446,1.066),(.49,1.082),(.59,.97)]:
                vs.append((x+r*math.cos(a),side*y,.40+r*math.sin(a)))
        fs=[]
        for i in range(48):
            for j in range(2):fs.append((i*3+j,(i+1)*3+j,(i+1)*3+j+1,i*3+j+1))
        if side<0:fs=[tuple(reversed(f)) for f in fs]
        mesh('Widebody overfender',vs,fs,paint,.004)
        line('Fender outer seam',[(x+.591*math.cos(a),side*.974,.40+.591*math.sin(a))
             for a in [i*math.pi/48 for i in range(49)]],.004,trim)
        for i in range(9):
            a=.06+i*(math.pi-.12)/8
            cylinder('Exposed fender fastener',(x+.572*math.cos(a),side*.989,.40+.572*math.sin(a)),.009,.012,alloy)
    box('Extended side skirt',(0,side*.992,.265),(2.27,.17,.12),paint,.014)
    box('Carbon sill blade',(0,side*1.047,.192),(2.45,.17,.035),trim,.008)
    line('Front fender vent',[(.91,side*.986,.86),(.81,side*.991,.74),(.70,side*.98,.50)],.025,trim)
    box('Fender vent trim',(.86,side*.985,.867),(.20,.025,.035),alloy,.006)

box('Front upper grille',(2.386,0,.66),(.065,.86,.18),trim,.045)
box('Front lower intake',(2.365,0,.405),(.085,1.33,.18),trim,.022)
box('Front splitter',(2.28,0,.19),(.44,2.13,.038),trim,.012)
box('Rear diffuser',(-2.30,0,.24),(.21,1.72,.13),trim,.025)
for y in [-.65,-.32,0,.32,.65]:box('Diffuser fin',(-2.28,y,.21),(.33,.026,.14),trim,.005)
for y in [-.61,.61]:
    line('Splitter brace',[(2.45,y,.22),(2.34,y,.41)],.009,alloy)
    box('Grille vertical support',(2.414,y,.41),(.075,.045,.20),paint,.012)
for i in range(12):box('Grille mesh slat',(2.423,-.36+i*.066,.655),(.008,.009,.125),dark_alloy,.002)
for side in [-1,1]:
    # Swept, triangular headlamp housings with separate projector details.
    hp=[(2.32,side*.48,.81),(2.22,side*.84,.84),(1.59,side*.914,1.00),(1.92,side*.66,.95)]
    if side<0:hp.reverse()
    mesh('Swept headlamp lens',hp,[(0,1,2,3)],glass,.008)
    line('Headlight outline',hp+[hp[0]],.009,alloy)
    line('Headlight LED',[(2.27,side*.52,.829),(2.17,side*.82,.865),(1.65,side*.911,1.01)],.012,white)
    for x,y,z in [(2.16,.70,.881),(1.97,.81,.929)]:
        box('Headlight projector',(x,side*y,z),(.08,.09,.022),white,.02)
    box('Front corner air curtain',(2.25,side*.83,.45),(.095,.18,.24),trim,.025)
    for height in [.30,.43]:
        box('Front bumper canard',(2.16,side*.97,height),(.31,.20,.025),trim,.008)
    for y in [.43,.72]:
        tail=torus('Round rear tail lamp',(-2.337,side*y,.78),.084,.018,red)
        tail.rotation_euler=(0,math.pi/2,0)
    box('Spoiler pedestal',(-1.94,side*.60,1.08),(.15,.06,.19),trim,.018)
box('Rear deck wing',(-2.04,0,1.19),(.39,2.09,.055),paint,.022)
line('Raised spoiler trailing edge',[(-2.22,-1.04,1.21),(-2.26,-.65,1.24),
                                    (-2.26,.65,1.24),(-2.22,1.04,1.21)],.022,paint)
box('Rear plate recess',(-2.395,0,.60),(.025,.42,.105),trim,.018)
box('Charge port door',(-1.11,-.949,.927),(.18,.015,.115),paint,.022)
line('Hood left crease',[(1.04,-.58,1.006),(1.60,-.57,.958),(2.10,-.51,.876)],.003,trim)
line('Hood right crease',[(1.04,.58,1.006),(1.60,.57,.958),(2.10,.51,.876)],.003,trim)

wheel_origins={}
for axle,x in [('rear',-1.51),('front',1.49)]:
    for side in [-1,1]:
        group=f'wheel_{axle}_{"left" if side>0 else "right"}'
        y=side*.995
        wheel_origins[group]=(x,y,.40)
        torus('Rounded tyre',(x,y,.40),.303,.091,rubber,group)
        cylinder('Aero rim barrel',(x,y,.40),.294,.18,dark_alloy,group)
        outside=y+side*.103
        torus('Polished rim edge',(x,outside,.40),.275,.012,alloy,group)
        cylinder('Brake rotor',(x,y+side*.072,.40),.223,.015,alloy,group)
        cylinder('Dark wheel face',(x,outside-.014*side,.40),.252,.013,dark_alloy,group)
        # Ten forked spokes and polished lips reproduce the reference wheel style.
        for i in range(10):
            a=i*math.tau/10
            for spread in [-.10,.10]:
                line('Split mesh spoke',[(x+math.sin(a)*.063,outside+side*.023,.40+math.cos(a)*.063),
                     (x+math.sin(a+spread)*.17,outside+side*.025,.40+math.cos(a+spread)*.17),
                     (x+math.sin(a+spread*1.3)*.261,outside+side*.018,.40+math.cos(a+spread*1.3)*.261)],.012,alloy,group)
        cylinder('Red wheel centre',(x,outside+side*.032,.40),.050,.023,red,group)
        for i in range(30):
            a=i*math.tau/30
            cylinder('Rim fastener',(x+math.sin(a)*.263,outside+side*.025,.40+math.cos(a)*.263),.005,.008,alloy,group)
        for i in range(5):
            a=i*math.tau/5
            cylinder('Lug bolt',(x+math.sin(a)*.042,outside+side*.048,.40+math.cos(a)*.042),.008,.007,trim,group)
        # Circumferential tyre grooves keep tread lightweight for the browser.
        for offset in [-.042,0,.042]:
            torus('Tyre tread groove',(x,y+offset,.40),.389-abs(offset)*.12,.003,dark_alloy,group)

box('Battery tray',(0,0,.34),(2.50,1.43,.075),dark_alloy,.035,'battery')
box('Structural underfloor',(0,0,.255),(3.7,1.52,.09),dark_alloy,.035,'chassis')
for i in range(8):
    for j in range(4):
        box('Battery cell module',(-1.07+i*.305,-.51+j*.34,.445),(.278,.31,.13),cells,.018,'battery')
for y in [-.64,.64]:line('Copper busbar',[(-1.13,y,.525),(1.12,y,.525)],.015,copper,'battery')
cylinder('Rear electric drive unit',(-1.50,0,.46),.17,.61,alloy,'motor')
line('HV cable',[(1.08,.46,.50),(1.38,.46,.51),(1.48,.23,.48)],.02,copper,'battery')
box('Inverter housing',(1.37,0,.76),(.58,.62,.23),alloy,.03,'inverter')
for i in range(9):box('Inverter cooling fin',(1.13+i*.058,0,.888),(.023,.56,.026),dark_alloy,.004,'inverter')
box('Cooling radiator',(1.96,0,.60),(.12,1.12,.40),dark_alloy,.014,'cooling')
for i in range(12):box('Radiator fin',(2.029,0,.425+i*.03),(.012,1.07,.008),alloy,.002,'cooling')

# Save named wheel pivots and a reusable driving loop in the editable source.
for name,origin in wheel_origins.items():
    pivot=bpy.data.objects.new(name,None)
    bpy.context.collection.objects.link(pivot)
    pivot.location=origin
    bpy.context.view_layer.update()
    for obj in list(bpy.context.scene.objects):
        if obj.get('web_group')==name:
            world=obj.matrix_world.copy();obj.parent=pivot;obj.matrix_world=world
    pivot.rotation_euler.y=0;pivot.keyframe_insert(data_path='rotation_euler',frame=1)
    pivot.rotation_euler.y=math.tau*3;pivot.keyframe_insert(data_path='rotation_euler',frame=121)
    for fc in pivot.animation_data.action.fcurves:
        for key in fc.keyframe_points:key.interpolation='LINEAR'
        fc.modifiers.new('CYCLES')
scene=bpy.context.scene
scene.frame_end=120
scene.render.fps=30
scene.frame_set(1)
bpy.context.view_layer.update()

# Export evaluated surfaces grouped by material and animation pivot. This small
# format keeps the existing offline Three.js bundle without a network loader.
depsgraph=bpy.context.evaluated_depsgraph_get()
buckets={}
for obj in scene.objects:
    if obj.type not in {'MESH','CURVE'}:continue
    ev=obj.evaluated_get(depsgraph); data=ev.to_mesh(); data.calc_loop_triangles()
    group=obj.get('web_group','body')
    origin=Vector(wheel_origins.get(group,(0,0,0)))
    transform=obj.matrix_world
    normal_transform=transform.to_3x3().inverted().transposed()
    mat=obj.data.materials[0].name
    bucket=buckets.setdefault((group,mat),dict(group=group,material=mat,positions=[],normals=[]))
    for tri in data.loop_triangles:
        for vi in tri.vertices:
            p=transform@data.vertices[vi].co-origin
            normal=(normal_transform@data.vertices[vi].normal).normalized()
            bucket['positions'].extend(round(v,5) for v in (p.x,p.z,-p.y))
            bucket['normals'].extend(round(v,4) for v in (normal.x,normal.z,-normal.y))
    ev.to_mesh_clear()
payload=dict(name='Photo-referenced widebody coupe',materials=MATERIALS,
             wheels={k:[v[0],v[2],-v[1]] for k,v in wheel_origins.items()},
             meshes=list(buckets.values()),wheelRadius=.394)
(OUT/'reference_car.json').write_text(json.dumps(pack_meshes(payload),separators=(',',':')),encoding='utf-8')

# Studio setup for opening and reviewing the .blend file.
bpy.ops.object.camera_add(location=(6,-6,3.5))
camera=bpy.context.object
camera.rotation_euler=(Vector((0,0,.70))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.lens=52;scene.camera=camera
for loc,power,size in [((2,-4,6),1300,5),((-3,2,4),1100,4),((1,4,2),800,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc)
    light=bpy.context.object;light.data.energy=power;light.data.shape='DISK';light.data.size=size
    light.rotation_euler=(-light.location).to_track_quat('-Z','Y').to_euler()
scene.world.color=(.22,.22,.22)
scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'reference_car.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'reference_car.glb'),export_format='GLB',
                          export_animations=True,export_cameras=False,export_lights=False)
print(f'Exported {len(buckets)} mesh batches to {OUT}')
