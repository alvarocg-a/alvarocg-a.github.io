# ACGA Screen Waypoint Markers

A screen-space marker that follows a world target and pins itself to the edge of the viewport when
the target leaves the frame — **including when it is behind you**, which is the case most systems
in this category get wrong.

- **Engine:** UE 5.6, 5.7, 5.8
- **Type:** C++ code plugin, source included
- **Dependencies:** Core, CoreUObject, Engine, UMG, Slate, SlateCore, DeveloperSettings. The plugin
  also lists Enhanced Input, which only the deletable demo module uses; the waypoint itself never
  reads a key.
- **Replication:** nothing here replicates. It is client-side presentation.


---

## Installing

1. **Install it to your engine from Fab:** Epic Games Launcher > Library > Fab Library, find
   *ACGA Screen Waypoint Markers*, choose *Install to Engine* and pick your engine version. Fab
   installs it as an engine plugin, already compiled, so Blueprint-only projects work as they are.
2. **Enable it in your project:** Edit > Plugins, search for *ACGA Waypoint*, tick it and restart
   the editor.
3. **Show its content:** in the Content Browser, Settings > tick *Show Engine Content* and *Show
   Plugin Content*. The plugin's assets are then under *ACGA Screen Waypoint Markers Content*.

> The C++ source ships with the plugin. If you would rather keep a copy inside one project, copy the
> installed `ACGAWaypoint` folder into `MyProject/Plugins/`; the project then has to be a C++
> project, because Unreal compiles a project plugin itself.

## Try it first: the demo map

`/ACGAWaypoint/Demo/Maps/DemoMap_ACGA_Waypoint` is playable exactly as it arrives. Open it and
press Play. There is a character on it, an input setup and a GameMode override, so nothing in your
project has to be configured first and nothing in your project is touched.

The map is a walled district with seven waypoints spread around it at different distances and
bearings.

| Key | What it does |
|---|---|
| WASD, mouse | Move and look. The demo is first person. |
| Space | Jump. |
| **K** | Switch every waypoint in the level off and back on. |
| **H** | The plugin debug draw: every waypoint, its state, its bearing, its widget class and the icon it resolved to. |

**Turn around before you do anything else.** There is a waypoint directly behind the spawn, and
its marker was already clamped to the edge of your screen on the first frame. That is the case
section 6 is about, and the one most off-screen indicators draw nothing for.

Two more worth walking to:

- **Occluded** is behind a wall to your left, with *Check Occlusion* ticked. Its marker changes
  tint when the wall is between you and it, and goes back when you step around.
- **Tower** is the far corner of the map, high up. Watch the bearing stay correct as you circle it.

The waypoints are `BP_ACGA_WaypointDemoPOI`, which is nothing more than the shipped
`BP_ACGA_Waypoint` with a post added so there is something to walk to. Each instance differs only
in its *Label* and its *Icon Id*, set in the Details panel — no Blueprint graph anywhere.

> **The demo is a separate module.** `Source/ACGAWaypointDemo` and `Content/Demo` exist only for
> this map, and the dependency runs one way: the demo uses the product, the product never uses the
> demo. Delete both folders, remove the `ACGAWaypointDemo` entry from `ACGAWaypoint.uplugin`, and
> the plugin still compiles and still works. That module is also the only reason this plugin lists
> Enhanced Input as a dependency — the waypoint itself never reads a key.

## 1. Two-minute setup

**The short version:** drag `BP_ACGA_Waypoint` from `/ACGAWaypoint/Blueprints/` into your level,
type a label on it, press Play.

**On your own actor:** add an **ACGA Screen Waypoint** component. That is it — the component ships
with a marker widget already assigned, so it draws something immediately. Move the component up in
the viewport to put the marker over the actor's head.

> Attach it under a root component rather than making it the actor's root. The plugin recommends
> it, `BP_ACGA_Waypoint` is built that way, and section 6 explains why.

Set **Label** to the name you want drawn, and **Icon Id** to one of `Default`, `Question`, `Alert`
or `Dot`.

---

## 2. What it does, and what it deliberately does not

The component **publishes state**; the widget **draws itself**. The component works out whether the
target is on screen, whether the marker is pinned to an edge, which way to point, how far away the
target is and whether anything is in the way — and hands all of that to a widget.

It never wraps your widget. That matters: wrapping forces a `SetSlateWidget()` call, which empties
`UWidgetComponent`'s private widget pointer and makes `Get User Widget Object` return None for the
rest of the session, with no error. This component never calls it, so `Get User Widget Object`
keeps working.

**The bearing convention:** `Bearing Degrees` is **0 when the target is straight up** and grows
**clockwise**. Draw your arrow texture pointing up and feed the bearing straight into a render
transform angle. There is no rotation-offset property, no invert-rotation property and no
spin-for-debugging property, because there is nothing to correct.

---

## 3. Every setting

### On the component

| Setting | What it does |
|---|---|
| **Label** | Drawn on the marker by the shipped widget. Empty draws no label. |
| **Icon Id** | Which icon from the set, chosen from a dropdown of the names in the project's default icon set. See [Icons](#4-icons-adding-your-own). |
| **Icon Set** | Icons this waypoint may choose from. Empty uses the project's. |
| **Style** | How this marker looks. Empty uses the project's. See [Styles](#5-styles-changing-the-look). |
| **Start Active** | Whether the waypoint starts switched on. Turn it off for a marker that appears when something happens — an objective accepted, a place discovered, a marker picked on the map — and call `Set Waypoint Active` when it should show. Prefer this over unticking the scene component's own *Visible*: that hides the widget but leaves `Is Waypoint Active` saying the opposite. |
| **Clamp To Screen** | Pin to the viewport edge instead of letting the marker slide off. |
| **Clamp Shape** | `Rectangle` — pinned to the margin rectangle, what most HUDs want. `Ellipse` — reads better on a circular HUD. |
| **Clamp Margin** | Inset from the viewport edge, in slate units. |
| **Visibility Mode** | `Always`, `When On Screen`, or `When Clamped` (an off-screen indicator and nothing else). |
| **Target Actor Override** | Track another actor instead of the owner. The component's own transform is still what gets projected. |
| **Max Visible Distance** | Hidden past this, in cm. 0 disables. |
| **Fade Start Distance** | `Distance Alpha` falls from 1 here to 0 at *Max Visible Distance*. |
| **Priority** | Higher wins when more than *Max On Screen* waypoints compete. Ties break on distance, nearest first. |
| **Check Occlusion** | Trace from camera to target and report whether something is in the way. |
| **Occlusion Channel** | Which channel that trace uses. |
| **Hide When Occluded** | Hide entirely while occluded, rather than just reporting it. |

There is deliberately **no world-offset property**. This is a scene component: move it where you
want the marker, exactly as with the engine's own `UWidgetComponent`.

### Project Settings > Plugins > ACGA Waypoint

| Setting | What it does |
|---|---|
| **Update Hz** | How often distance, occlusion and the on-screen cap are re-evaluated. The clamp itself runs every frame regardless, so the marker never lags the camera. |
| **Max On Screen** | Most markers allowed on screen at once. 0 means no limit. |
| **Occlusion Traces Per Pass** | Traces allowed per pass, shared across every waypoint. The difference between a hundred waypoints costing a hundred traces a frame and costing this many. |
| **Default Style** | The look every waypoint without its own uses. |
| **Default Icon Set** | The icon library every waypoint without its own uses. |
| **Default Marker Widget Class** | Your own widget for every waypoint still carrying the shipped one. |
| **Debug Draw** | Prints every waypoint's live state on screen. Also `ACGA.Waypoint.DebugDraw 1`. |

---

## 4. Icons: adding your own

Icons live in an **`ACGA Waypoint Icon Set`** data asset. The plugin ships
`/ACGAWaypoint/Icons/DA_ACGA_WaypointIcons_Default` with `Default`, `Question`, `Alert` and `Dot`.

1. Duplicate `DA_ACGA_WaypointIcons_Default` into your own Content folder.
2. Add a row: an **Icon Id** (the name components ask for), a **Texture**, and optionally **Size**
   and **Tint**.
3. Point Project Settings > Plugins > ACGA Waypoint > **Default Icon Set** at your copy — or set
   *Icon Set* on a single component for a one-off.
4. The name is now in the **Icon Id** dropdown on every waypoint.

> The dropdown lists the names in the **project default** set, because it is filled before anything
> knows which component is being edited. A component pointing at its own icon set still works at
> runtime; its names just are not the ones offered in the list.

Any waypoint can then use that name, from the Details panel or from `Set Icon Id` at runtime. A
name that is not in the set falls back to the style's own Icon brush, so a typo shows a marker
rather than nothing.

> The ACGA Minimap plugin has an icon set with the same shape and the same starter names, so a
> project can use one vocabulary across both. They are two separate assets on purpose: each plugin
> has to keep working with the other one deleted.

---

## 5. Styles: changing the look

A **`ACGA Waypoint Style`** data asset holds everything that is not the icon: the arrow, the tints
per state, the fonts, and how the distance is written. Ships as
`/ACGAWaypoint/Styles/DA_ACGA_WaypointStyle_Default`.

| Group | What is in it |
|---|---|
| **Icon** | The fallback icon brush, and whether to hide the icon while clamped. |
| **Arrow** | The arrow brush; whether it shows when clamped and when on screen; how far out it orbits (*Arrow Distance*, and *Arrow Clears Marker* + *Arrow Clearance*, which push it out past the label automatically); whether it turns to the bearing. |
| **Colour** | *On Screen Tint*, *Clamped Tint*, *Occluded Tint*, and the floor on the distance fade. |
| **Text** | Whether to draw the label and the distance, their fonts and colours, the **Distance Format** (`{0}` is the number — write `"{0} ft"` and set *Distance Scale* for feet), and the decimals. |

Three levels, in increasing effort:

1. **Edit a style.** Your own icons and colours, no UMG at all.
2. **Several styles.** One per marker kind, assigned per component.
3. **Your own widget.** Set *Widget Class* on the component to any `UUserWidget`. Derive it from
   **ACGA Waypoint Widget** to get the state pre-bound — `Get Waypoint State`, `Get Bearing
   Degrees`, `Get Distance Meters`, `Is Clamped`, `Is Occluded`, plus `On Waypoint Clamp Changed`,
   `On Waypoint Occlusion Changed` and `On Waypoint Bound`. Or use any widget at all and subscribe
   to the component's delegates.

---

## 6. The behind-camera case

This is the feature, so it is worth saying how it works.

Unreal's screen-space widget layer projects a widget component with
`FSceneView::ProjectWorldToScreen`, which returns false for anything behind the camera plane — and
on false it collapses the widget and returns. No clamping code written downstream of that call can
ever run. That is why so many off-screen indicators simply vanish when the target is behind you.

While a target is behind the camera, this plugin parks the component's *cached* world transform in
front of the camera so the projection succeeds, then discards the resulting screen position and
uses the view-space direction instead. It writes only the cached transform — the relative transform
is untouched, no child transform is propagated, and the owning actor never moves.

The one arrangement it stays out of is a waypoint component that is its owner's **root**, since
there the component's transform is the actor's. Put it under a root component and it is safe;
`BP_ACGA_Waypoint` is built that way, and the plugin logs a warning if it finds otherwise.

---

## 7. Blueprint API

**`ACGA Waypoint Library`** — static nodes. **`UACGA_WaypointSubsystem`** — registered waypoints,
the on-screen count, the view target, `Set Max On Screen`, and `Get Waypoints By Distance`.

**`IACGA_WaypointTargetInterface`** — optional, implement it on an actor to override the tracked
location, the priority, or whether the waypoint is visible for a given viewer. Every call is
guarded, so not implementing it costs nothing.

---

## 8. Troubleshooting

Turn on `ACGA.Waypoint.DebugDraw 1`. It lists every registered waypoint with its state, bearing,
distance, **the widget class that was created for it** and **the icon its style resolved to** —
because "my marker does not show up" has two common answers and those are them.

**Nothing at all.** No widget was created: check *Widget Class* on the component, and that the
component is not disabled.

**The marker draws but has no icon.** The icon resolved to `NONE`: either *Icon Id* is not a name
in the set, or the set has no texture in that row.

**It vanishes when the target is behind me.** Check the component is not the actor's root — see
section 6.

**The arrow sits on top of the label.** *Arrow Clears Marker* in the style should handle it; if you
turned it off, raise *Arrow Distance*.

**Markers flicker on and off.** *Max On Screen* is lower than the number competing. Raise it, or
use *Priority* to decide who wins.

**Labels overlap at a screen edge.** Markers pinned to the same edge are not spread apart in this
version, so several targets off-screen in the same direction draw over each other. Lower *Max On
Screen* and raise *Priority* on the ones that matter, or set *Visibility Mode* to `When On Screen`
on markers that do not need an off-screen indicator.

---

## 9. Removing the plugin

Delete the components, then disable the plugin. Nothing subclasses or replaces an engine class,
nothing is required in your GameMode or PlayerController, and no engine content is modified. Fix
any references to the plugin's own assets first, as with any other asset.
