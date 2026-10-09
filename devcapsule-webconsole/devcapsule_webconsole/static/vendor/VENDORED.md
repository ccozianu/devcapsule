# Vendored browser libraries

The console renders markdown and DOT in the browser with two libraries
vendored here, as the work order's binding decision 5 requires: no build
step and no Node in the capsule. Each file is the package's own browser
build, unchanged. A test checks the digests below against the files.

| File | Package | Version | License | Source | SHA-256 |
|---|---|---|---|---|---|
| `markdown-it-15.0.2.umd.min.js` | markdown-it | 15.0.2 | MIT | `dist/browser/markdown-it.umd.min.js` of the npm package, the website's pinned renderer | `635972b985228e8af9f0143647c68616b7a3bb09f6946e7e4a52e43dcf5e7be5` |
| `viz-3.31.0.global.js` | @viz-js/viz | 3.31.0 | MIT (bundles Graphviz, EPL-1.0, and Expat, MIT, as WebAssembly) | `dist/viz-global.js` of the npm package; tarball integrity `sha512-r7zlQdRvcwvIpjHGgs+KNWHeE/P5/Dq7k8ZAKaMCbZqomxCBJV78gVuQYaHzFVca+kB0mX0fMW9UFevCOBG50A==`, SLSA provenance in the package's `lib/provenance.json` | `c9e0b310f9883910e01c66054b48b7ff4be3d8695141116635e72b0af152692e` |

To upgrade one: fetch the package with `npm pack <name>@<version>`, verify
the registry's integrity string, copy the browser build under the new
versioned name, update this table, and delete the old file.

The wheel includes `static/vendor/*`. Check the built wheel as well as the
source tree when changing these assets.

Use `markdown-it` with raw HTML disabled. Render Graphviz SVG as an image,
not as inline SVG: DOT can supply active links through its `URL` attributes.
SVG image mode disables scripts, links and external resources, as specified
by [SVG processing modes](https://www.w3.org/TR/SVG/conform.html#processing-modes).
Keep the raw route's sandbox and `nosniff` headers when serving project SVG.
The digest check establishes file identity; it does not sanitize rendered content.
