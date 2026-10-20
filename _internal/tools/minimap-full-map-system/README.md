# ACGA Minimap & Map System

A HUD minimap and a full-screen map, sharing one registry, one coordinate system and one set of
icons. Drop a component on an actor and it is on the map. Nothing to place in the level except the
capture actor that says how big the world is.

- **Engine:** UE 5.6, 5.7, 5.8
- **Type:** C++ code plugin, source included
- **Dependencies:** Core, CoreUObject, Engine, UMG, Slate, SlateCore, DeveloperSettings, InputCore.
  No GameplayTags, no Niagara, no GameplayAbilities. The plugin also lists Enhanced Input, which
  only the deletable demo module uses; the minimap itself never reads a key.
- **Replication:** nothing in this plugin replicates. It is client-side presentation of state your
  game already has. See [Multiplayer](#multiplayer).


---

## Installing

1. **Install it to your engine from Fab:** Epic Games Launcher > Library > Fab Library, find
   *ACGA Minimap & Map System*, choose *Install to Engine* and pick your engine version. Fab
   installs it as an engine plugin, already compiled, so Blueprint-only projects work as they are.
2. **Enable it in your project:** Edit > Plugins, search for *ACGA Minimap*, tick it and restart
   the editor.
3. **Show its content:** in the Content Browser, Settings > tick *Show Engine Content* and *Show
   Plugin Content*. The plugin's assets are then under *ACGA Minimap & Map System Content*.

> The C++ source ships with the plugin. If you would rather keep a copy inside one project, copy the
> installed `ACGAMinimap` folder into `MyProject/Plugins/`; the project then has to be a C++
> project, because Unreal compiles a project plugin itself.

## Try it first: the demo map

`/ACGAMinimap/MinimapSystem/Demo/Maps/DemoMap_ACGA_Minimap` is playable exactly as it arrives. Open it and press
Play. There is a character on it, an input setup and a GameMode override, so nothing in your
project has to be configured first and nothing in your project is touched.

The map is a walled district with five landmarks, a road grid, and twenty-four scattered caches.

| Key | What it does |
|---|---|
| WASD, mouse | Move and look. The demo is first person. |
| Space | Jump. |
| **M** | Open and close the full screen map. |
| **N** | Turn the minimap off and back on at runtime. |
| Left mouse, on the full map | Select a marker. Selected markers get a ring. |

Things worth doing while you are in there:

- **Turn on the spot** and watch the minimap. Whether it rotates with you or stays north-up is
  Project Settings > Plugins > ACGA Minimap > *Minimap Defaults* > *Rotation*. Change it and press
  Play again — and while you are in there, everything else about how the minimap looks is in the
  same block.
- **Select several markers** on the full map. Once you pass *Max Selected Markers* the oldest
  selection is dropped, which is the behaviour section 5 describes.
- **Load it up.** Open the console (the `` ` `` key) and type `ACGA.Minimap.Demo.Bench show 2000`.
  The full map opens with two thousand markers moving across it and a readout of what they cost
  per frame. `ACGA.Minimap.Demo.Bench show 2000 widgets` draws the same markers as one UMG widget
  each, for comparison; `ACGA.Minimap.Demo.Bench stop` ends it. See
  [Performance, measured](#performance-measured).

Two assets are worth opening:

- `BP_ACGA_MapPOI` — a post with an **ACGA Map Marker** component on it. That component, on an
  actor, is what puts something on the map. There is nothing else to it.
- `BP_ACGA_MinimapDemoCharacter` — the player. Note that it does two separate things: it carries a
  map marker so the player appears on the map, and it creates a HUD widget so the map appears on
  the screen. The plugin never adds a widget to your viewport by itself; in a project that already
  has a UMG HUD, you drag an **ACGA Map View** into it and write no code at all.

> **The demo is a separate module.** `Source/ACGAMinimapDemo` and `Content/MinimapSystem/Demo` exist only for
> this map, and the dependency runs one way: the demo uses the product, the product never uses the
> demo. Delete both folders, remove the `ACGAMinimapDemo` entry from `ACGAMinimap.uplugin`, and the
> plugin still compiles and still works. That module is also the only reason this plugin lists
> Enhanced Input as a dependency — the minimap itself never reads a key.

## 1. Five-minute setup

1. **Enable the plugin.** Edit > Plugins > ACGA > ACGA Minimap. Restart when asked.

2. **Place one `ACGA Map Capture` in your level.** Search the Place Actors panel for *ACGA Map
   Capture*. Scale its **Bounds Box** until it covers the playable area — the box is the map. You
   are looking down at it from above, so the box's X and Y matter and its Z only has to contain
   the geometry you want photographed.

3. **Put a map on screen.** In any UMG widget, drag **ACGA Map View** out of the palette (it is
   under *ACGA*). Size it, and set *Zoom World Radius* to how many centimetres either side of the
   player you want to see — 3000–8000 suits most minimaps. Add that widget to the viewport the way
   you normally would.

4. **Mark something.** Add an **ACGA Map Marker** component to any actor. Set its *Icon Id* to
   `Objective`. That actor is now on the map.

5. **Mark the player.** Same component on your pawn, *Icon Id* `Player`, *Update Policy*
   `Every Frame`, *Rotate With Actor* on.

That is the whole integration. If you can see the map but no markers, jump to
[Troubleshooting](#troubleshooting).

### Opening the full map

Bind a key to **Toggle Full Map** (ACGA Minimap library, or the subsystem). It shows a full-screen
map, takes the input mode and cursor while it is open, and gives both back exactly as it found
them when it closes. Point *Full Map Widget Class* in Project Settings at your own widget when you
want your own design; leave it empty to use the one that ships.

---

## 2. How it fits together

```
AACGA_MapCaptureActor        the box that defines the mapped area, and the camera that photographs it
        |
        | projection + background texture
        v
UACGA_MinimapSubsystem       the registry: every marker, the projection, the selection
        ^                    one per world, created with the world - nothing to place, nothing to initialise
        |
        | register / unregister
        |
UACGA_MapMarkerComponent     one per actor that appears on the map
        |
        | render snapshot (flat array, 24 bytes per marker)
        v
UACGA_MapViewWidget          a UMG widget. A minimap is one; a full map is another with different settings.
```

Two things are worth knowing because they explain most of the design:

**Markers are not widgets.** The subsystem keeps a flat array of 24-byte render states with no
pointers in it, and the view draws straight from that array. Nothing dereferences a UObject while
painting, and there is no widget per marker to lay out. That is why two thousand moving markers cost
about a third of a millisecond per frame (see below), and it is why a marker's update policy is the
performance knob rather than the marker count.

**There is exactly one coordinate conversion.** `FACGA_MapProjection` turns a world location into
normalised map space and back, and everything — the view, the hit test, the Blueprint library —
goes through it. The capture actor's box is the only place the mapped area is stated, so the pixels
in the background and the positions of the markers cannot drift apart.

### Performance, measured

The demo module includes the benchmark these numbers come from, so you can run it on your own
machine. It opens the full map and moves N markers across it every frame, first through this
plugin's registry, then as one UMG Image per marker on a Canvas Panel — the usual way a map is built
in UMG. The comparison is written in C++, moves each Image with *Set Render Translation* and marks
it hit-test invisible, which is the cheapest way to do it in UMG; a Blueprint widget per marker with
its own Tick costs more.

Game-thread cost per frame of drawing and moving the markers, with the cost of the empty full map
taken off. Median of 400 frames, mean of three runs. UE 5.6, Development build, 1920x1080,
Intel Core i5-13400F, GeForce RTX 5070:

| Markers | This plugin | One UMG widget per marker |
|---:|---:|---:|
| 250 | 0.04 ms | 0.60 ms |
| 500 | 0.07 ms | 0.99 ms |
| 1 000 | 0.18 ms | 1.89 ms |
| 2 000 | 0.34 ms | 3.76 ms |
| 4 000 | 0.73 ms | 7.25 ms |

At 4 000 markers the whole frame takes 4.9 ms with this plugin, the same as with no markers at all,
and 9.9 ms with a widget per marker. Run it yourself with
`ACGA.Minimap.Demo.Bench sweep` from the console on the demo map: it takes about a minute and writes
a JSON and a CSV to `Saved/ACGA_MinimapBench/` in your project. Add `quit` to close the game when it
finishes, and marker counts to choose your own (`ACGA.Minimap.Demo.Bench sweep 1000 8000`).

Markers that sit still cost less again: registered `Static`, a marker is never re-read, and only
its drawing remains.

---

## 3. Every setting

### Project Settings > Plugins > ACGA Minimap

| Setting | What it does |
|---|---|
| **Default Icon Set** | The icon library every view uses. Points at the shipped set. See [Icons](#4-icons-adding-your-own). |
| **Snapshot Hz** | How often moving markers are re-read. 30 is indistinguishable from 240 and costs an eighth as much. Static markers ignore it entirely. |
| **Move Threshold** | How far an `On Move` marker must travel, in cm, before its entry is rewritten. A squared-distance compare, no UObject work. |
| **Initial Marker Capacity** | Slots reserved at world start. Going past it grows the array once. Size it to your real marker count and even that stops happening. |
| **Poll Marker Interface** | Ask actors implementing `IACGA_MapMarkerInterface` for icon, tint and visibility every snapshot. Off is cheaper; on is needed if those change during play. |
| **Selection Radius** | How close a click has to be, as a fraction of the view, to select a marker. |
| **Max Selected Markers** | How many markers may be selected at once. **0 means no limit.** See [Selection](#5-selection). |
| **Minimap Defaults** | The whole look of every `Minimap`-role view: shape, rotation, zoom, clamping, icon scale, void colour, border, selection ring. Views with *Use Project Defaults* ticked — the default — read this instead of their own values. *Rotation* in here is the one an options menu changes at runtime. |
| **Minimap Enabled** | Whether the minimap is on screen when a level starts. Only the starting state — see [Switching them off](#6-switching-them-off). |
| **Full Map Enabled** | Whether the full map may be opened at all. Off makes `Open Full Map` return false and do nothing. |
| **Full Map Defaults** | The same block again, for every `FullMap`-role view. This is what restyles the shipped full map, which you never place yourself and so could not otherwise reach. |
| **Full Map Widget Class** | Your own full-map widget. Empty uses the one that ships. |
| **Full Map Z Order** | Viewport Z order the full map is added at. |
| **Full Map Manages Input Mode** | Show the cursor and switch to UI input while the map is open, and put both back on close. Turn it off if your game owns input modes itself. |
| **Debug Draw** | Also available at runtime as `ACGA.Minimap.DebugDraw 1`. |

### On the `ACGA Map Capture` actor

| Setting | What it does |
|---|---|
| **Bounds Box** | *The map.* Scale it to the playable area. Everything else follows from it. |
| **Background Source** | `Baked Capture` renders once at level start. `Live Capture` re-renders every frame — for destructible or procedurally built worlds. `Supplied Texture` uses hand-painted art and keeps the box only for its bounds. |
| **Render Target** | Left empty, one is created at the right size and aspect ratio. |
| **Supplied Texture** | Used by `Supplied Texture` mode. |
| **Capture Resolution** | Resolution of the **longer** side. The shorter side follows the box's aspect ratio automatically. |
| **Flatten Capture For Map** | Capture without fog, bloom, motion blur, vignette or auto exposure. On by default: a capture with full post-processing is a photograph taken from above, not a map. |
| **Capture Exposure Bias** | Exposure compensation for the capture, in stops. Negative is darker. Adjust if the baked map is too bright or too dark for your lighting. |
| **Rebake Delay** | Re-bake once, this many seconds in. The first frame of a level is the worst moment to photograph it — shaders compiling, textures at their lowest mip — and a bad bake is permanent. 0 disables. |
| **Capture Height** | How high the camera sits above the box. Must clear your tallest geometry. |
| **Bake Background** | A button. Bakes now, from the editor. |

### On the `ACGA Map Marker` component

| Setting | What it does |
|---|---|
| **Icon Id** | Which icon from the set, chosen from a dropdown of the names in the project's default icon set. A name, not an index - an index breaks the first time somebody reorders the list. |
| **Tint** | Multiplied with the icon's own tint. |
| **Scale** | Multiplied with the icon's size. |
| **Update Policy** | `Static` — read once at registration, never again, costs nothing per frame. `On Move` — re-read on the registry tick, written only if it actually moved. `Every Frame` — for pawns and vehicles. |
| **Category** | Free-form grouping for a view's category filter. Empty means always shown. |
| **Clamp When Off Map** | Pin to the view edge when off-view, if the view's clamp mode allows it. |
| **Rotate With Actor** | Turn the icon with the owner's yaw. On for pawns, off for pins. |
| **Selectable** | Can be picked by a click on a map view. |
| **Start Visible** | Register but start hidden. |
| **Auto Register On Begin Play** | Off for markers that appear when something unlocks. |

### On the `ACGA Map View` widget

**Read this first: by default these values are not the ones in use.** *Use Project Defaults* is on
out of the box, and a view with it on takes everything below from Project Settings > Plugins >
ACGA Minimap — from *Minimap Defaults* if its *Role* is `Minimap`, from *Full Map Defaults* if its
Role is `FullMap`. That is what lets you restyle the shipped full map, which you never place and
so could never otherwise reach, and it is what makes "rotate the minimap" one switch for the whole
game rather than one per widget.

Untick it and the values below are used instead. A view whose Role is `Custom` ignores the project
blocks entirely and always uses its own. *Role* itself is never taken from the project block, since
Role is what chooses the block.

Calling `Set View Settings`, `Set Zoom World Radius` or `Set Category Filter` at runtime also turns
it off — an explicit call wins — and it copies the project values in first, so changing the zoom
does not snap everything else back to whatever the widget was authored with. `Refresh Project
Defaults` re-reads them, which is what an options menu calls after it changes one.

A minimap is a circle with a small radius; a full map is a rectangle with `Zoom World Radius` 0 —
which means "the whole captured world".

| Setting | What it does |
|---|---|
| **Use Project Defaults** | Take everything below from Project Settings instead. On by default. |
| **Role** | What this view is for, and therefore which visibility switch it obeys: `Minimap` (the default), `FullMap`, or `Custom` — neither, for a map inside a terminal or a table that should never be hidden by a HUD toggle. |
| **Shape** | `Circle` or `Rectangle`. The circle is real geometry — no mask material needed. |
| **Rotation** | `North Up`, `Follow View Target`, or `Use Project Default` (the default), which defers to *Minimap Defaults > Rotation* and to `Set Minimap Rotation` at runtime. |
| **Zoom World Radius** | Radius in world centimetres. **0 shows the whole captured world.** The shorter side of the widget shows exactly this many cm either side of the centre, whatever the aspect ratios. |
| **Follow View Target** | Keep the view centred on the player. Off pins it to the centre of the captured world. |
| **Clamp Mode** | What happens to markers outside the view: not drawn, pinned, or pinned and swapped for the icon's clamped texture rotated to the true bearing. |
| **Clamp Padding** | How far in from the edge clamped markers sit. |
| **Icon Scale** | Multiplies every icon in this view. Minimaps usually want less than 1. |
| **Draw View Target Icon** | The player arrow. With *Follow View Target* on it sits dead centre and points up, because the map is what turned. |
| **View Target Icon Id** | Which icon that arrow uses. |
| **Allow Selection** | Let clicks select markers. Usually only the full map. |
| **Category Filter** | Only these categories are drawn. Empty draws everything. |
| **Void Color** | Fills the view where the map does not reach. |
| **Draw Border**, **Border Color**, **Border Thickness** | Outline of the view's shape. |
| **Circle Segments** | Smoothness of a circular view. |
| **Draw Selection Highlight**, **Selection Color**, **Selection Thickness**, **Selection Padding**, **Selection Segments** | The ring around a selected marker. |

---

## 4. Icons: adding your own

Icons live in a **`ACGA Map Icon Set`** data asset. The plugin ships
`/ACGAMinimap/MinimapSystem/Icons/DA_ACGA_MapIcons_Default` with `ViewTarget`, `Player`, `Objective`, `Default`,
`Question`, `Alert` and `Dot`.

To add your own:

1. Duplicate `DA_ACGA_MapIcons_Default` into your own Content folder. *(Editing the shipped asset
   works too, but a plugin update would overwrite it.)*
2. Add a row. Give it an **Icon Id** — that name is what markers ask for — and a **Texture**.
3. The name appears in the Icon Id dropdown on every marker as soon as the asset is saved.
4. Optionally set **Clamped Texture** (drawn instead when the marker is pinned to the edge,
   normally an arrow), **Size**, **Tint**, **Draw Priority** (higher draws on top) and
   **Rotate Clamped Icon To Bearing**.
5. Point Project Settings > Plugins > ACGA Minimap > **Default Icon Set** at your copy.

Any marker can now use that name. A texture that fails to load draws a plain tinted quad rather
than a broken reference, so a half-configured icon is visible instead of invisible.

> The ACGA Waypoint plugin has an icon set with the same shape and the same starter names, so a
> project can use one vocabulary across both. They are two separate assets on purpose: each plugin
> has to keep working with the other one deleted.

---

## 5. Selection

Selection lives on the subsystem, not on a widget, so a minimap and a full map always agree about
it.

- **`Select Marker`** / **`Unselect Marker`** / **`Toggle Marker Selection`** — a click on a map
  view calls the last of these.
- **`Set Selected Marker`** selects exactly one and drops the rest.
- **`Clear Selection`**, **`Is Marker Selected`**, **`Get Selected Markers`** (oldest first),
  **`Get Selected Marker`** (the newest).

**The limit.** *Max Selected Markers* in Project Settings decides how many may be selected at once;
0 means no limit. Selecting one more than the limit drops the marker that was selected **longest
ago** — not the nearest, not the newest — and that marker gets a full unselect event. A limit of 1
behaves exactly like a plain single selection. `Set Max Selected Markers` overrides it at runtime
and trims the current selection immediately if the new limit is lower.

**Events**, on both the subsystem and the marker component:

| Event | Fires when |
|---|---|
| `On Marker Selected` | A marker becomes selected. |
| `On Marker Unselected` | A marker stops being selected — clicked again, pushed out by the limit, or unregistered while selected. |
| `On Marker Selection Changed` | Both of the above, with a `bSelected` bool, for a listener that handles them the same way. |

Selected markers are ringed in the view. The ring is drawn as geometry, so it works with any icon
including one you add later, and scales with the icon rather than needing a matching highlight
image per size. Turn it off with *Draw Selection Highlight* if you would rather draw your own.

---

## 6. Switching them off

Both are a project setting for the starting state and a runtime call for everything after.

| | Setting | Runtime | Event |
|---|---|---|---|
| Minimap | *Minimap Enabled* | `Set Minimap Enabled` / `Is Minimap Enabled` | `On Minimap Enabled Changed` |
| Full map | *Full Map Enabled* | `Set Full Map Enabled` / `Is Full Map Enabled` | `On Full Map Enabled Changed` |

`Set Minimap Enabled(false)` takes **every** view whose *Role* is `Minimap` off screen at once,
wherever it sits in your HUD — a photo mode or a cutscene is one call, not a hunt for the widget
that happens to contain the map. Views with role `Custom` are never affected.

`Set Full Map Enabled(false)` also closes the map if it is open, so locking the map during a chase
does not need you to also intercept the key that opens it.

The events are there so a project can react — fade a HUD frame, stop a background task — rather
than polling.

---

## 7. Blueprint API

**`ACGA Minimap Library`** — static nodes, no "get subsystem" first:

- `Get Map Marker Component`
- `Drop Map Pin` / `Remove Map Pin` — a marker at a world location with no actor behind it.
  Registered `Static`, so any number of them cost nothing per frame.
- `World To Normalized Map` / `Normalized Map To World`
- `Get Bearing To Location` — everything a compass needs, without a second projection.
- `Get Registered Marker Count`
- `Toggle Full Map` / `Open Full Map` / `Close Full Map` / `Is Full Map Open`
- `Set Minimap Rotation` / `Get Minimap Rotation`

**`UACGA_MinimapSubsystem`** — `Get` it from any world context. Registration, selection, the
projection, the icon set, the view target, and the full map.

**`IACGA_MapMarkerInterface`** — optional. Implement it on an actor to override its icon, tint or
visibility per viewer. Every call is guarded, so not implementing it costs nothing and is the
normal case.

---

## 8. Multiplayer

Nothing here replicates, deliberately. A minimap draws state your game already has; replicating a
second copy of it inside a UI plugin would be a second source of truth to keep in sync.

Markers follow actors, so an actor that is replicated to a client produces a marker on that
client's map with no extra work. For something a client should see on the map but that is not
replicated to it — a teammate's ping, an objective revealed by a scan — replicate your own state and
call `Drop Map Pin` when it arrives.

---

## 9. Troubleshooting

**The map is blank / no background.**
Is there an `ACGA Map Capture` in the level? Is its *Background Source* `Baked Capture`? Press
*Bake Background* on it and look at the render target in the content browser. If that is black, the
capture camera is not seeing anything — check *Capture Height* clears your geometry.

**The background is there but very bright or very dark.**
*Capture Exposure Bias* on the capture actor. Negative is darker.

**No markers at all.**
Almost always no icon set. `ACGA.Minimap.DebugDraw 1` reports the marker count. Check Project
Settings > Plugins > ACGA Minimap > *Default Icon Set* is filled in.

**One marker is missing.**
Its *Icon Id* is not a name in the set, or its *Category* is not in the view's *Category Filter*,
or *Start Visible* is off, or it is outside the capture box and the view's *Clamp Mode* is `None`.

**Markers are offset from the terrain.**
Rebake the background: the box was probably rescaled after the last bake. If it persists, the
capture actor has been rotated — that is supported, but the map is then rotated too.

**The minimap looks stretched.**
It should not be able to. The view uses one scale for both axes. If you see this, please report it
with the box's extents and the widget's size.

**The full map does not open.**
`Open Full Map` needs a local player controller. Check the return value — it is `false` when there
is not one yet.

---

## 10. Removing the plugin

Delete markers' components and the capture actor, then disable the plugin. Nothing in this plugin
subclasses or replaces an engine class, nothing is required in your GameMode, PlayerController or
GameState, and no engine content is modified. A project that removes it still opens.

If you referenced the plugin's own assets — its icon set, its widget — from your content, fix those
references first, exactly as with any other asset.

---

## 11. Support

Bug reports are most useful with: engine version, whether it reproduces in a blank project, the
output of `ACGA.Minimap.DebugDraw 1`, and the capture actor's box extents.
