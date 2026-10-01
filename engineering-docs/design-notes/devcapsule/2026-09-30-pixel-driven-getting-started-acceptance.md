# Spike: Driving The Getting-Started Scenario Through Pixels

Date: 2026-09-30. Status: **spike passed; design idea, not scheduled**.
Owner of the idea: `project-management`, as item 8 of the user-docs
improvement list, "executed documentation"; the tooling would belong to the
workstream that picks it up.

## The Idea

The first-session guide becomes an acceptance test that an agent runs
against the real product surface. The surface is a VNC desktop in a browser
tab, a single canvas with no DOM to click, so the loop is: screenshot the
canvas, hand the image and the current step of a Markdown script to a vision
model, act on the coordinates it returns with Playwright's mouse and
keyboard, screenshot again, repeat until the step's expected pixels are on
screen. Evidence is the screenshots. Runs nest: a DevCapsule launched from
inside a DevCapsule, so the test can run wherever the project runs.

## What The Spike Established, On 0.2.15

Run from inside a 0.2.15 capsule with host Docker and host networking, on a
fresh project under the persistent home, with Playwright and Chromium from
`/opt/xtras`. Every fact below was observed, not inferred.

1. **A nested launch works.** `project init --need frontend-ide --need node`
   with `--creator` and `--authorize base-image <digest>` initializes
   non-interactively from inside a capsule; `project run` reports "bind
   sources were translated to their host paths", reuses the built Codium
   environment, and publishes the desktop on the host loopback, which a
   host-networked capsule reaches. This checkout's own run is refused, by
   design: its configuration belongs to the host launcher.
2. **Pixels capture.** noVNC draws on a 2D canvas; Playwright's
   `locator('canvas').screenshot()` captures it as rendered.
3. **Coordinates need no mapping.** The URL carries `resize=remote`, so the
   remote framebuffer takes the browser's size: with a 1600×1000 viewport
   the canvas reports a 1600×1000 framebuffer at CSS scale 1. Fix the
   viewport and framebuffer coordinates are page coordinates.
4. **Mouse delivery is exact.** `page.mouse.click(615, 47)` on the
   Restricted Mode banner's "Manage" opened the Workspace Trust editor;
   `(554, 598)` on "Trust" trusted the folder.
5. **Keyboard delivery needs focus, not a click.** Keys pressed before the
   canvas had focus went nowhere. `canvas.focus()` before `keyboard.press`
   fixed it: `Control+\`` opened the integrated terminal, typing `node -v`
   and `Enter` printed `v22.23.1`. A click to focus would move keyboard
   focus inside the IDE, so the driver focuses the element and the script
   decides where to click.
6. **A fresh browser per action is fine.** Each driver invocation opened a
   new headless browser to the same URL; noVNC reconnected to the running
   desktop with its state intact. This makes the loop restartable.
7. **The vision step worked with a general model.** The coordinates above
   were read off the screenshots by the agent in the loop, without a grid
   overlay, at 1600×1000. Accuracy was sufficient for menu-bar and button
   targets; smaller targets may need the grid-and-zoom mitigation.

Also learned and fixed in the docs: a project initialized with
`frontend-ide` and `node` does not declare the `network` authorization, so
`init` does not ask about it and `project run --authorize network host` is
refused for that project; run-once answers exist only for authorizations the
project declares.

## The Driver Used

One action per invocation; `node vncdrive.mjs <url> <outdir> <cmd> [args]`.

```javascript
// Pixel driver for the spike: one action per invocation against a noVNC desktop URL.
// usage: node vncdrive.mjs <url> <outdir> <cmd> [args]
//   info                      canvas framebuffer size vs displayed size, scale
//   shot <name>               screenshot of the canvas to <outdir>/<name>.png
//   click <x> <y> [<name>]    click at framebuffer coordinates, then screenshot
//   dblclick <x> <y> [<name>]
//   type <text> [<name>]      type text into the desktop, then screenshot
//   key <Key> [<name>]        press a key (Playwright key name), then screenshot
import { chromium } from '/opt/xtras/playwright/lib/node_modules/playwright/index.mjs';
const [url, outdir, cmd, ...args] = process.argv.slice(2);
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const b = await chromium.launch();
const ctx = await b.newContext({ viewport: { width: 1600, height: 1000 } });
const page = await ctx.newPage();
await page.goto(url, { waitUntil: 'load' });
const canvas = page.locator('canvas').first();
await canvas.waitFor({ state: 'visible', timeout: 60000 });
await sleep(1500);
async function geometry() {
  return canvas.evaluate((c) => {
    const r = c.getBoundingClientRect();
    return { fbW: c.width, fbH: c.height, cssW: r.width, cssH: r.height, left: r.left, top: r.top };
  });
}
async function shot(name) {
  if (!name) return;
  await sleep(800);
  await canvas.screenshot({ path: `${outdir}/${name}.png` });
  const g = await geometry();
  console.log(`shot ${name}.png fb=${g.fbW}x${g.fbH} css=${Math.round(g.cssW)}x${Math.round(g.cssH)}`);
}
function toPage(g, x, y) {  // framebuffer -> page coordinates
  return { px: g.left + x * (g.cssW / g.fbW), py: g.top + y * (g.cssH / g.fbH) };
}
const g = await geometry();
if (cmd === 'info') {
  console.log(JSON.stringify({ ...g, scaleX: g.cssW / g.fbW, scaleY: g.cssH / g.fbH }));
} else if (cmd === 'shot') {
  await shot(args[0] || 'shot');
} else if (cmd === 'click' || cmd === 'dblclick') {
  const { px, py } = toPage(g, Number(args[0]), Number(args[1]));
  await page.mouse.move(px, py); await sleep(150);
  if (cmd === 'click') await page.mouse.click(px, py); else await page.mouse.dblclick(px, py);
  console.log(`${cmd} fb(${args[0]},${args[1]}) -> page(${px.toFixed(1)},${py.toFixed(1)})`);
  await shot(args[2]);
} else if (cmd === 'type') {
  await canvas.evaluate((c) => c.focus());
  await sleep(200);
  await page.keyboard.type(args[0], { delay: 40 });
  console.log(`typed ${JSON.stringify(args[0])}`);
  await shot(args[1]);
} else if (cmd === 'key') {
  await canvas.evaluate((c) => c.focus());
  await sleep(200);
  await page.keyboard.press(args[0]);
  console.log(`pressed ${args[0]}`);
  await shot(args[1]);
}
await b.close();
```

## First Step Taken: The IDE Smoke (2026-10-01)

The deterministic half is now a test: `tests/e2e/test_ide_comes_alive.py`
with `tests/e2e/ide_session.py`, run by `nox -s ide-smoke`. Per IDE surface
it initializes a fresh project with the executable under test, launches it,
and proves the IDE came alive without a vision model: the desktop URL
answers, and the capsule's display holds an X11 top-level window of the
IDE's class, read through the minimal X client. With `--display` it also
keeps a Playwright screenshot and a distinct-colour count as evidence. The
surfaces are a table, so a new IDE is one row. The scripted journey below
builds on this session helper.

## What A Runner Would Add

- A Markdown script format: one step per heading, the action in the
  agent's words, the expected screen in the agent's words; the loop stops
  on the first step whose expectation is not met within its timeout.
- "Wait until the screenshot stops changing" as the wait primitive.
- The vision call as a headless agent invocation with a strict answer
  schema: `click x y`, `type text`, `key name`, `wait`, or `done`, plus one
  sentence of reasoning kept as evidence.
- The nested launch and teardown, from the smoke runner's session facts.
- A grid overlay and region zoom when a target is small.

## Cost And Risk

The spike took under an hour including the launch. The delicate part is
the vision step's coordinate accuracy on small targets and the timing of an
asynchronous desktop, both mitigated above. Nothing in the product changes;
the runner reads the guide and the screen.
